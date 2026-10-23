# Agent KIO project structure

| Path | Description | Owner |
|---|---|---|
| `Agent_KIO_Dataset_FROZEN.xlsx` | Frozen source dataset | Shared |
| `Data_exploration.ipynb` | Dataset exploration notebook | Student 1 |
| `kio/` | Shared Python package | Shared |
| `kio/__init__.py` | Package marker | Shared |
| `kio/config.py` | Shared configuration and model settings | Shared |
| `kio/data.py` | Frozen dataset loading and validation | Student 1 |
| `kio/base.py` | Router interface and output record | Shared |
| `kio/validation.py` | Output and instruction validation | Shared |
| `kio/agents.py` | Simulated downstream agents | Shared |
| `kio/router.py` | Router dispatching | Shared |
| `kio/clef_router.py` | Cloudflare Clef router | Student 3 |
| `kio/ml_router.py` | Scikit-learn router | Student 2 |
| `kio/routing_instructions.md` | Frozen decision instructions | Shared |
| `models/` | Saved model artifacts | Student 2 |
| `models/.gitkeep` | Placeholder to preserve the models folder | Student 2 |
| `results/` | Training and evaluation artifacts | Shared |
| `results/.gitkeep` | Placeholder to preserve the results folder | Shared |
| `_archive/` | Archived generated ML artifacts | Shared |
| `_archive/models/ml_model.joblib` | Archived trained model | Student 2 |
| `_archive/results/ml_settings.json` | Archived training settings and CV results | Student 2 |
| `_archive/results/ml_boundary_train.png` | Archived training-boundary visualization | Student 2 |
| `_archive/results/ml_top_terms.csv` | Archived explainability terms | Student 2 |
| `frontend/` | Frontend application folder | Student 3 |
| `frontend/README.txt` | Frontend folder ownership placeholder | Student 3 |
| `frontend/app.py` | Application entry point | Student 3 |
| `ml_model/` | ML model folder | Student 2 |
| `ml_model/README.txt` | ML model folder ownership placeholder | Student 2 |
| `ml_model/train_ml_model.py` | ML training entry point | Student 2 |
| `ml_model/evaluate_ml_model.py` | ML evaluation entry point | Student 2 |
| `decision_model/` | Decision-model folder | Student 3 |
| `decision_model/README.txt` | Decision-model folder ownership placeholder | Student 3 |
| `decision_model/smoke_test_clef.py` | One real Clef request with an invented message | Student 2 |
| `decision_model/evaluate_decision_model.py` | Decision-model evaluation entry point | Student 3 |
| `comparison/` | Router comparison folder | Shared |
| `comparison/README.txt` | Comparison folder ownership placeholder | Shared |
| `comparison/compare_results.py` | Router comparison entry point | Shared |
| `requirements.txt` | Python dependencies | Shared |
| `.env.example` | Environment-variable template | Shared |
| `.gitignore` | Git ignore rules | Shared |
| `README.md` | Setup and usage guide | Shared |

## Where to put your files

| Student | Files owned |
|---|---|
| Student 1 | `Data_exploration.ipynb`, `kio/data.py` |
| Student 2 | `kio/ml_router.py`, `ml_model/train_ml_model.py`, `ml_model/evaluate_ml_model.py`, `decision_model/smoke_test_clef.py`, `models/` |
| Student 3 | `kio/clef_router.py`, `decision_model/evaluate_decision_model.py`, `frontend/` |
| Shared | `Agent_KIO_Dataset_FROZEN.xlsx`, `kio/`, `results/`, `comparison/`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md` |

## Team rules

1. Do not edit another student's files.
2. Tell the team before editing a shared file.
3. Every router must follow the shared interface in `kio/base.py`: message in, flag `0` or `1` out.

## Who edits what inside shared files

| File | Symbol | Owner |
|---|---|---|
| `kio/config.py` | `build_ml_pipeline()` | Student 3 |
| `kio/config.py` | `KIO_CLEF_MODEL`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `KIO_MOCK` | Student 2 |
| `kio/config.py` | `EXPECTED_CONTENT_HASH`, `PROJECT_DIR` | Shared, nobody edits |
| `kio/validation.py` | `check_instructions_clean()` | Student 2 |
| `kio/validation.py` | `validate_output()`, `LABEL_TO_FLAG`, `ALLOWED_LABELS` | Shared, nobody edits |

Edit only your own symbols. Tell the team before changing anything else in these files.

