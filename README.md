# Agent KIO Intent Router

Agent KIO routes a customer message to Support (`0`) or Sales (`1`) using the Cloudflare Clef decision model. The Streamlit frontend and shared routing package are the implemented project scope. Support and Sales agents are simulated functions; the project does not send telecom alerts, use RAG, or provide chatbot answers.

## Structure

```text
data/             Frozen dataset
frontend/         Streamlit interface
kio/              Shared routing, validation, configuration, and instructions
decision_model/   Clef smoke test and evaluation
results/          Reserved for generated evaluation outputs
ml_model/         Reserved for Student 3
models/           Reserved for Student 3
comparison/       Reserved for Student 3
```

The ML, comparison, notebook, and archived generated artifacts were removed from this branch. The four reserved folders contain only `.gitkeep` files.

## Installation

Run commands from the `System` folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill the local `.env` with your own Cloudflare values. `.env` is ignored and must never be committed.

## Run the frontend

```powershell
streamlit run frontend/app.py
```

Mock mode is enabled by default in the UI and displays a visible mock-output warning. Set `KIO_MOCK=0` in `.env` and provide a permitted Cloudflare Workers AI token to use real Clef routing. The smoke test sends one invented message:

```powershell
python decision_model/smoke_test_clef.py
```

The decision-model evaluation uses the held-out split and should be run only when explicitly approved:

```powershell
python decision_model/evaluate_decision_model.py
python decision_model/evaluate_decision_model.py --dry-run
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
- ML, model artifacts, comparison scripts, and notebooks are intentionally not part of this branch. Student 3 can use the reserved folders later.
