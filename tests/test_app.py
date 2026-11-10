import socket
import subprocess
import sys
import time
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


class FruitParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fruits: list[str] = []
        self.in_heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h3":
            self.in_heading = True

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.fruits.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3":
            self.in_heading = False


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        cls.base_url = f"http://127.0.0.1:{port}"
        cls.server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(100):
            if cls.server.poll() is not None:
                raise RuntimeError("The test server exited before starting.")
            try:
                with urlopen(cls.base_url, timeout=1):
                    return
            except URLError:
                time.sleep(0.05)
        cls.server.terminate()
        cls.server.wait(timeout=5)
        raise RuntimeError("The test server did not start.")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.terminate()
        cls.server.wait(timeout=5)

    def test_home_lists_five_fruits(self) -> None:
        with urlopen(self.base_url) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("text/html", response.headers["Content-Type"])
            parser = FruitParser()
            parser.feed(response.read().decode("utf-8"))
        self.assertEqual(
            parser.fruits, ["Rambutan", "Mangosteen", "Durian", "Starfruit", "Papaya"]
        )

    def test_stylesheet_is_served(self) -> None:
        with urlopen(f"{self.base_url}/static/styles.css") as response:
            self.assertEqual(response.status, 200)
            self.assertIn("text/css", response.headers["Content-Type"])
            self.assertIn(b".fruit-grid", response.read())

    def test_missing_page_and_asset_return_404(self) -> None:
        for path in ("/missing", "/static/missing.css"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as error:
                    urlopen(f"{self.base_url}{path}")
                self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
