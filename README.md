# Text Analytics Tool

A professionalized repository structure for fake-news detection using a FastAPI backend and Flask frontend.

## Frontend Quick Start (Recommended)

If you only want to open the web UI fast:

1. Install dependencies once.
2. Run the one-command script.
3. Open the frontend URL.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Frontend URL: http://127.0.0.1:5000

To stop all services:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

Important:
- This app uses a backend API. If backend is not running, pages open but classify/retrain actions will fail.

## Project Structure

```text
Text-Analytics-Tool/
├── backend/
│   └── api/
│       ├── main.py
│       ├── preprocessing.py
│       ├── pipeline.py
│       ├── *.joblib
│       └── *.py
├── frontend/
│   └── webapp/
│       ├── app.py
│       ├── templates/
│       │   ├── base.html
│       │   ├── index.html
│       │   ├── classify.html
│       │   ├── classify_file.html
│       │   └── retrain.html
│       ├── static/
│       │   ├── js/i18n.js
│       │   └── ...
│       ├── classify_sample.csv
│       └── retrain_sample.csv
├── data/
│   ├── fake_news_spanish.csv
│   └── fake_news_test.csv
├── docs/
│   ├── phase1/
│   └── phase2-project-report.pdf
├── models/
│   ├── gradient_boosting_legacy.joblib
│   └── gradient_boosting_legacy.pkl
├── notebooks/
│   └── models-phase2-corrections.ipynb
├── requirements.txt
└── README.md
```

## Features

- FastAPI backend for prediction and retraining endpoints.
- Flask frontend with clean template inheritance.
- Client-side i18n:
  - auto-detects browser language (`en` -> English, otherwise Spanish)
  - language switcher in the top-right corner.
- Backward compatibility for old Spanish routes while exposing English routes.

## Manual Run (Windows / PowerShell)

### 1. Create and activate environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Start backend (terminal 1)

```powershell
.\.venv\Scripts\python -m uvicorn backend.api.main:app --reload --port 8000
```

### 3. Start frontend (terminal 2)

```powershell
.\.venv\Scripts\python frontend\webapp\app.py
```

### 4. Optional: stop old Python servers before restart

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## One-Command Start/Stop Scripts

Start backend + frontend:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Stop backend + frontend:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

Logs are written to:

- `.run\backend.log`
- `.run\backend.err.log`
- `.run\frontend.log`
- `.run\frontend.err.log`

### 5. Open the app

- Frontend: http://127.0.0.1:5000
- Backend: http://127.0.0.1:8000

## Troubleshooting

### Frontend does not open (ERR_CONNECTION_REFUSED)

Run this exact command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Then verify frontend:

```powershell
Invoke-WebRequest http://127.0.0.1:5000 -UseBasicParsing
```

If it still fails:

```powershell
Get-Content .\.run\frontend.err.log
Get-Content .\.run\backend.err.log
```

### Error: `jinja2.exceptions.TemplateNotFound: index.html`

Use these checks:

1. Run the frontend with the new path only:

```powershell
.\.venv\Scripts\python frontend\webapp\app.py
```

2. Do not run old paths from the previous structure (for example `Fase 2\Front\app.py`).

3. Confirm templates exist:

```powershell
Get-ChildItem frontend\webapp\templates
```

4. If needed, restart both services after killing old Python processes.

## Notes

- New English routes:
  - `/classify`
  - `/classify-file`
  - `/retrain`
- Legacy Spanish routes still work:
  - `/clasificar`
  - `/clasificarArchivo`
  - `/reentreno`
