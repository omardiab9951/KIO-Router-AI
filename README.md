# Agent KIO Intent Router

Agent KIO routes customer messages to Support (`0`) or Sales (`1`) using a frozen traditional ML classifier, Cloudflare Clef, or an explicitly marked mock router. The downstream agents are simulated functions; this project does not implement RAG, chatbot answers, or telecom integration.

## Structure

```text
data/             Frozen dataset
frontend/         Streamlit interface
kio/              Shared routing, validation, configuration, and instructions
decision_model/   Clef smoke test and evaluation
results/          Reserved for generated evaluation outputs
ml_model/         Traditional ML pipeline and evaluation scripts
models/           Frozen ML model artifact
comparison/       ML/Clef comparison script
tests/            Router and regression tests
```

The frozen model artifact is stored at `models/ml_model.joblib`.

## Installation

Run commands from the `System` folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Clef-only values belong in the ignored `.env`: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, and optionally `KIO_CLEF_MODEL`. Traditional ML works offline. `KIO_DEFAULT_ROUTER` may be `ml`, `clef`, or `mock`.

## Run the frontend

```powershell
streamlit run frontend/app.py
```

The router selector offers Traditional ML, Clef decision model, and Mock keyword. Traditional ML is the default. Mock output is visibly labeled and is not model evidence. Clef requires valid Workers AI credentials. The smoke test sends one invented message:

```powershell
python decision_model/smoke_test_clef.py
```

The decision-model evaluation uses the held-out split and should be run only when explicitly approved:

```powershell
python decision_model/evaluate_decision_model.py
python decision_model/evaluate_decision_model.py --dry-run
```

Run ML evaluation, comparison, and tests from the System folder:

```powershell
python ml_model/evaluate_ml_model.py --dry-run
python ml_model/evaluate_ml_model.py --allow-overwrite
python comparison/compare_results.py
python -m pytest
```

## Dataset integrity

The protected workbook is `data/Agent_KIO_Dataset_FROZEN.xlsx`. Its canonical content hash is checked by `kio/data.py` before loading:

```text
9a655603b371639eafbef19719046355ed8759011cd5cf532cbce01dbf900484
```

Do not edit the workbook. Its redistribution, privacy, and course-licensing status is not documented here and must be reviewed before publishing it to GitHub.

## Limitations and troubleshooting

- Clef requires network access and a token with Workers AI permissions.
- API and malformed-response failures are returned as invalid router outputs; no label is selected silently.
- Mock mode is deterministic and is not real model output.
- The downstream agents are simulated and do not integrate with live telecom systems.
- ML evaluation uses the frozen Test split only; normal evaluation loads `models/ml_model.joblib` without retraining.
- The 2D boundary PNGs are illustrative TruncatedSVD projections, not the real decision boundary of the full TF-IDF model.
