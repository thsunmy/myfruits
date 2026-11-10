# Buah Kita

A small FastAPI website introducing five Malaysian fruits: rambutan, mangosteen,
durian, starfruit and papaya. The page, illustrations and stylesheet are served
locally; no external services are required.

## Run locally

Python 3.10 or later is recommended. From the project directory on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop the server.
If PowerShell prevents virtual environment activation, run
`.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and
`.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000`
instead.

## Test

```powershell
python -m unittest discover -s tests -v
```