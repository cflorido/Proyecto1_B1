# Text Analytics Tool

End-to-end fake-news detection platform for Spanish-language content, implemented as a production-oriented ML service with:

- FastAPI inference and retraining API
- Flask web interface (single article classification, batch classification, model retraining)
- Client-side i18n (automatic browser language detection + manual language switch)

This repository documents both engineering delivery and data-science methodology, from data preparation to operational serving.

## 1. Executive Overview

The project addresses binary fake-news classification using textual fields from news records. The implementation is organized to support:

1. Reproducible local execution
2. Online inference for single and batch payloads
3. Controlled model updates via retraining endpoint
4. Transparent metrics reporting for train/validation phases

Core stack:

- API: FastAPI + Pydantic
- UI: Flask + Jinja templates
- ML: scikit-learn Pipeline + GradientBoostingClassifier
- Data handling: pandas

## 2. System Architecture

High-level flow:

1. User submits data in Flask UI
2. Flask routes transform form/CSV payloads into API-compatible JSON
3. FastAPI receives payloads, applies serialized pipeline, returns predictions/metrics
4. UI renders class labels and confidence values

Component responsibilities:

- `frontend/webapp/app.py`: route handling, file validation, API proxy calls, response rendering
- `backend/api/main.py`: prediction and retraining endpoints, model persistence
- `backend/api/preprocessing.py`: NLP preprocessing and vectorization helpers
- `backend/api/pipeline.joblib`: serialized feature+model pipeline used in production

## 3. Methodology Followed

The implementation follows a CRISP-DM-inspired lifecycle, adapted for iterative academic/engineering delivery.

### 3.1 Business and Problem Understanding

- Objective: detect whether a news item is likely fake or true.
- Task framing: supervised binary classification over text-rich records.
- Operational constraint: model must be consumable from an interactive UI and exposed through API endpoints.

### 3.2 Data Understanding and Analysis

Primary datasets are under `data/`:

- `fake_news_spanish.csv`
- `fake_news_test.csv`

Observed schema used by the system:

- `ID`
- `Titulo`
- `Descripcion`
- `Fecha`
- `Label` (required for training/retraining)

Data analysis and experimentation artifacts are included in `docs/phase1/`, with model comparison traces and notebook-based exploration.

### 3.3 Data Preparation Pipeline

Preprocessing logic is implemented in `backend/api/preprocessing.py` and applied inside the serialized sklearn pipeline.

Transformation stages:

1. Null handling and text construction
2. Drop rows with missing `Titulo` or `Descripcion`
3. Build consolidated text field from title + description
4. Normalization: lowercasing, digit removal, punctuation removal, non-ASCII filtering, Spanish stopword removal
5. Morphological normalization: Spanish stemming (Snowball) + lemmatization
6. Vectorization with pre-fitted artifacts from `vectorizer.joblib`
7. Conversion to dense numerical representation for classifier consumption

This pipeline is persisted and reused at inference time to guarantee training-serving consistency.

### 3.4 Modeling Strategy

Serving model: Gradient Boosting classifier integrated as the final step of the sklearn pipeline.

Retraining configuration in current API implementation:

- Estimator: `GradientBoostingClassifier`
- Hyperparameters:
	- `n_estimators=500`
	- `max_depth=5`
	- `criterion="friedman_mse"`
- Validation split: 80/20 via `train_test_split(random_state=42)`

The retraining endpoint updates the classifier in-pipeline and persists both:

- `pipeline.joblib`
- `model.joblib`

### 3.5 Evaluation Protocol

Metrics produced by retraining endpoint:

- F1 (weighted)
- Recall (weighted)
- Precision (weighted)
- Accuracy

Metrics are returned for both train and validation splits, enabling immediate quality inspection and overfitting checks.

## 4. API Contract

Main endpoints (FastAPI):

- `POST /predict/`: single-item prediction
- `POST /predictMany`: batch prediction
- `POST /retrain/`: model retraining with labeled records

Expected prediction payload structure:

```json
{
	"ID": "string",
	"Titulo": "string",
	"Descripcion": "string",
	"Fecha": "string"
}
```

Retraining payload requires all fields above plus integer `Label`.

## 5. Frontend Capabilities

The UI supports:

1. Single-article classification with probability display
2. Batch classification from CSV file
3. Model retraining from labeled CSV
4. Processing-state feedback during long-running operations
5. Internationalization with English auto-selection when the browser is in English
6. Manual language switch in the navigation bar

Legacy Spanish routes are preserved for backward compatibility while English routes are exposed as primary UX paths.

## 6. Run Locally (Windows + PowerShell)

### 6.1 Prerequisites

- Python 3.10+
- PowerShell
- Internet access on first run (package installation and NLTK resources)

### 6.2 Recommended Run (single command)

1. Open terminal at repository root
2. Create environment and install dependencies
3. Start services with script

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Open:

- Frontend: http://127.0.0.1:5000
- Backend docs: http://127.0.0.1:8000/docs

Stop services:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

### 6.3 Manual Run (two terminals)

Terminal 1 (backend):

```powershell
.\.venv\Scripts\python -m uvicorn backend.api.main:app --reload --port 8000
```

Terminal 2 (frontend):

```powershell
.\.venv\Scripts\python frontend\webapp\app.py
```

## 7. Operational Validation

Quick availability checks:

```powershell
Invoke-WebRequest http://127.0.0.1:5000 -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8000/docs -UseBasicParsing
```

Expected: HTTP 200 for both.

Generated logs:

- `.run\backend.log`
- `.run\backend.err.log`
- `.run\frontend.log`
- `.run\frontend.err.log`

## 8. Troubleshooting

### Frontend unavailable (ERR_CONNECTION_REFUSED)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
Invoke-WebRequest http://127.0.0.1:5000 -UseBasicParsing
```

### TemplateNotFound issues

Run frontend from project structure-aware path:

```powershell
.\.venv\Scripts\python frontend\webapp\app.py
```

### Port conflicts

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## 9. Repository Layout

```text
Text-Analytics-Tool/
├── backend/
│   └── api/
│       ├── main.py
│       ├── preprocessing.py
│       ├── pipeline.py
│       ├── pipeline.joblib
│       ├── model.joblib
│       └── vectorizer.joblib
├── frontend/
│   └── webapp/
│       ├── app.py
│       ├── templates/
│       └── static/
├── data/
├── docs/
├── scripts/
├── requirements.txt
└── README.md
```

## 10. Technical Notes and Limitations

- Retraining endpoint is currently open by default; for public deployment, add authentication/authorization.
- Current configuration is optimized for local reproducibility and academic/engineering demonstration.
- For production internet exposure, use environment variables for API base URL, hardened CORS policy, and request throttling.
