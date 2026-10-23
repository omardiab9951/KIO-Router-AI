# Agent KIO Intent Router

Agent KIO routes a customer message to either Support (`0`) or Sales (`1`). The project includes a Streamlit frontend and two interchangeable router implementations: a scikit-learn router and a Cloudflare Clef decision-model router. The downstream Support and Sales agents are simulated functions; this project does not send telecom alerts, use RAG, or provide chatbot answers.

## Repository layout

```text
data/             Frozen dataset
frontend/         Streamlit interface
kio/              Shared routing, validation, configuration, and instructions
decision_model/   Clef smoke test and evaluation
ml_model/         ML training and evaluation scripts
comparison/       Result comparison script
notebooks/        Exploratory notebooks
results/          Generated evaluation outputs
models/           Local model artifacts
archive/          Retained historical ML artifacts
```

## Requirements

- Windows PowerShell
- Python 3.13 or newer
- Internet access and a Cloudflare Workers AI token for real Clef routing

## Installation

Run every command from this `System` folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally with your own credentials. Never commit `.env`; only `.env.example` belongs in GitHub.

## Run the frontend

```powershell
streamlit run frontend/app.py
```

The frontend offers ML, Clef, and comparison modes. If `models/ml_model.joblib` is absent, the ML column reports that the model must be trained; the archived model is retained under `archive/` and is not automatically restored.

## Clef configuration

For mock routing, set:

```env
KIO_MOCK=1
```

Mock mode uses a deterministic keyword rule and is not real model output. For real Clef routing, set `KIO_MOCK=0`, provide `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`, and optionally choose `KIO_CLEF_MODEL=clef` or `clef-flash`.

Run the one-message smoke test:

```powershell
python decision_model/smoke_test_clef.py
```

Run the decision-model evaluation only when intentionally evaluating the held-out split:

```powershell
python decision_model/evaluate_decision_model.py
python decision_model/evaluate_decision_model.py --dry-run
```

The real evaluation writes result files and requires explicit overwrite permission when an output already exists. The dry run uses mock data and writes nothing.

## Dataset integrity and limitations

The frozen workbook is `data/Agent_KIO_Dataset_FROZEN.xlsx`. `kio/data.py` verifies its canonical content hash before loading:

```text
9a655603b371639eafbef19719046355ed8759011cd5cf532cbce01dbf900484
```

The dataset contains customer-style messages and should be reviewed for redistribution, privacy, and course-licensing restrictions before publication. The project has no documented license for the dataset, so this remains a team review item.

Clef requires valid account permissions and network access. API failures are returned as invalid router outputs. The ML model is not currently present in `models/`; its historical artifacts are retained in `archive/`. No claim is made that either router is suitable for production use.

## Troubleshooting

- If `.env` is missing, copy `.env.example` and fill it locally.
- If the frontend reports a missing ML model, run `python ml_model/train_ml_model.py` only when training is approved.
- If Clef reports a network error, test HTTPS connectivity and Cloudflare permissions without exposing credentials.
- Do not edit the frozen dataset or routing instructions casually; both are integrity-sensitive project inputs.
