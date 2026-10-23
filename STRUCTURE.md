# Agent KIO repository structure

| Path | Description | Owner |
|---|---|---|
| `data/` | Frozen input data | Shared |
| `data/Agent_KIO_Dataset_FROZEN.xlsx` | Integrity-checked dataset | Shared |
| `notebooks/` | Exploratory notebooks | Student 1 |
| `notebooks/Data_exploration.ipynb` | Dataset exploration notebook | Student 1 |
| `frontend/` | Streamlit interface | Student 3 |
| `frontend/app.py` | Frontend application | Student 3 |
| `frontend/README.md` | Frontend ownership note | Student 3 |
| `kio/` | Shared routing package | Shared |
| `kio/__init__.py` | Package marker | Shared |
| `kio/config.py` | Configuration and ML pipeline factory | Shared |
| `kio/data.py` | Dataset loading and integrity validation | Student 1 |
| `kio/base.py` | Router interface and output record | Shared |
| `kio/validation.py` | Output and instruction validation | Shared |
| `kio/agents.py` | Simulated Support and Sales agents | Shared |
| `kio/router.py` | Router dispatch | Shared |
| `kio/clef_router.py` | Cloudflare Clef router | Student 3 |
| `kio/ml_router.py` | Scikit-learn router | Student 2 |
| `kio/routing_instructions.md` | Frozen routing rules | Shared |
| `decision_model/` | Clef scripts | Student 3 |
| `decision_model/README.md` | Decision-model guide | Student 3 |
| `decision_model/smoke_test_clef.py` | One-message Clef smoke test | Student 2 |
| `decision_model/evaluate_decision_model.py` | Decision-model evaluation | Student 3 |
| `ml_model/` | ML scripts | Student 2 |
| `ml_model/README.md` | ML folder guide | Student 2 |
| `ml_model/train_ml_model.py` | ML training entry point | Student 2 |
| `ml_model/evaluate_ml_model.py` | ML evaluation entry point | Student 2 |
| `comparison/` | Result comparison | Shared |
| `comparison/README.md` | Comparison guide | Shared |
| `comparison/compare_results.py` | Comparison entry point | Shared |
| `models/` | Local model artifacts | Student 2 |
| `models/.gitkeep` | Models-folder placeholder | Student 2 |
| `results/` | Generated evaluation outputs | Shared |
| `results/README.md` | Results policy | Shared |
| `results/.gitkeep` | Results-folder placeholder | Shared |
| `archive/` | Retained historical artifacts | Shared |
| `archive/MANIFEST.md` | Archive inventory | Shared |
| `archive/models/ml_model.joblib` | Archived ML model | Student 2 |
| `archive/results/ml_settings.json` | Archived ML settings | Student 2 |
| `archive/results/ml_boundary_train.png` | Archived training plot | Student 2 |
| `archive/results/ml_top_terms.csv` | Archived explainability output | Student 2 |
| `README.md` | Project guide | Shared |
| `requirements.txt` | Python dependencies | Shared |
| `.env.example` | Safe environment template | Shared |
| `.gitignore` | GitHub exclusion rules | Shared |

## Ownership rules

| Student | Files/folders |
|---|---|
| Student 1 | `notebooks/`, `kio/data.py` |
| Student 2 | `ml_model/`, `kio/ml_router.py`, `decision_model/smoke_test_clef.py`, `models/` |
| Student 3 | `frontend/`, `decision_model/`, `kio/clef_router.py` |
| Shared | `data/`, `kio/` shared files, `results/`, `archive/`, documentation, configuration templates |

## Team rules

1. Do not edit another student's files.
2. Tell the team before editing a shared file.
3. Every router follows `kio/base.py`: message in, flag `0` or `1` out.

## Shared-file symbols

| File | Symbol | Owner |
|---|---|---|
| `kio/config.py` | `build_ml_pipeline()` | Student 3 |
| `kio/config.py` | `KIO_CLEF_MODEL`, Cloudflare settings, `KIO_MOCK` | Student 2 |
| `kio/config.py` | `EXPECTED_CONTENT_HASH`, `PROJECT_DIR` | Shared, nobody edits |
| `kio/validation.py` | `check_instructions_clean()` | Student 2 |
| `kio/validation.py` | `validate_output()`, `LABEL_TO_FLAG`, `ALLOWED_LABELS` | Shared, nobody edits |

Edit only your own symbols. Tell the team before changing anything else in these files.
