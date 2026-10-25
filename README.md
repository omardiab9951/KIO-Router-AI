# Agent KIO Intent Router

Agent KIO reads a customer message and routes it to **Support (flag 0)** or **Sales (flag 1)**.
It compares three routers behind one interface:

| Router | How it decides | Needs internet? |
|---|---|---|
| **Traditional ML** (default) | TF-IDF + Logistic Regression, trained on 40 messages | No |
| **Cloudflare Clef** | Follows written routing instructions (no training) | Yes, plus an API token |
| **Mock keyword** | Three-keyword demo heuristic, **not a real model** | No |

The Support and Sales agents are simulated functions that print their names. This project does not include
RAG, chatbot answers, or telecom integration.

## Quick start

**Requirements:** Python 3.10 or newer (tested on Python 3.14) and Git.

```powershell
git clone https://github.com/omardiab9951/KIO-Router-AI.git
cd KIO-Router-AI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run frontend/app.py
```

Your browser opens the app. Pick a router in the sidebar, type a message, and click **Route**.

> **macOS / Linux:** use `python3 -m venv .venv`, `source .venv/bin/activate`, and `cp .env.example .env`.

## Try it

| Message | Expected route |
|---|---|
| My internet is down | Support (0) |
| I want a new fiber package | Sales (1) |

The Traditional ML router works immediately and offline.

## Using Clef (optional)

Add your Cloudflare Workers AI credentials to the local `.env` file (it is ignored by Git, so never commit it):

```text
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
```

Optional settings: `KIO_CLEF_MODEL` and `KIO_DEFAULT_ROUTER` (`ml`, `clef`, or `mock`).

Check the connection with one invented message:

```powershell
python decision_model/smoke_test_clef.py
```

## Tests and evaluation

```powershell
python -m pytest                                    # automated tests
python ml_model/evaluate_ml_model.py --dry-run      # safe ML check, writes nothing
python decision_model/evaluate_decision_model.py --dry-run   # safe Clef check (mock calls)
python comparison/compare_results.py                # rebuild results/comparison_summary.md
```

Saved test-set results (20 held-out messages) are in `results/`.

> **Do not** run `ml_model/train_ml_model.py` or add `--allow-overwrite`
> unless you intend to replace the frozen model and results.
> The test split is frozen and must not be used for tuning.

## Project structure

```text
data/             Frozen dataset (60 messages)
frontend/         Streamlit app
kio/              Routers, validation, agents, configuration, routing instructions
decision_model/   Clef smoke test and evaluation
ml_model/         Traditional ML pipeline and scripts
models/           Frozen ML model (ml_model.joblib)
comparison/       ML vs Clef comparison script
results/          Evaluation outputs
tests/            Automated tests
```

## Dataset

`data/Agent_KIO_Dataset_FROZEN.xlsx` has 60 synthetic messages (30 Support, 30 Sales; 40 train, 20 test).
`kio/data.py` checks its content hash before loading, so **do not edit the file**:

```text
9a655603b371639eafbef19719046355ed8759011cd5cf532cbce01dbf900484
```

Its redistribution, privacy, and course-licensing status has not been reviewed. Check this before publishing it.

## Troubleshooting

| Problem | Fix |
|---|---|
| `streamlit` is not recognized | Activate the virtual environment, or run `python -m streamlit run frontend/app.py` |
| Script blocked when activating `.venv` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try again |
| `No module named ...` | Run `python -m pip install -r requirements.txt` inside the activated environment |
| Clef returns an invalid result | Check `.env` credentials, network access, and Workers AI permissions |
| Dataset hash error | Restore the original workbook. It must not be modified |
| Model fails to load | Use the scikit-learn version pinned in `requirements.txt` |

## Limitations

- Only 20 test messages: each message changes accuracy by 5 percentage points, so results are not proof of real-world reliability.
- API and malformed-response failures return an **invalid** result. A label is never chosen silently.
- Mock mode is not real model output.
- The 2D boundary images are illustrative TruncatedSVD projections, not the model's real decision boundary.
- Simulated agents do not connect to any live system.
