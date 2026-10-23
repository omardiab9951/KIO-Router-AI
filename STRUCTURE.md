# Agent KIO repository structure

| Path | Purpose | Owner |
|---|---|---|
| `data/` | Frozen input data | Shared |
| `data/Agent_KIO_Dataset_FROZEN.xlsx` | Integrity-checked dataset | Shared |
| `frontend/` | Streamlit frontend | Student 3 |
| `frontend/app.py` | Clef-only user interface | Student 3 |
| `frontend/README.md` | Frontend guide | Student 3 |
| `kio/` | Shared routing package | Shared |
| `kio/__init__.py` | Package marker | Shared |
| `kio/config.py` | Environment and integrity configuration | Shared |
| `kio/data.py` | Dataset loading and integrity validation | Student 1 |
| `kio/base.py` | Router interface and output record | Shared |
| `kio/validation.py` | Output and instruction validation | Shared |
| `kio/agents.py` | Simulated Support/Sales agents | Shared |
| `kio/router.py` | Router dispatch | Shared |
| `kio/clef_router.py` | Cloudflare Clef router | Student 3 |
| `kio/routing_instructions.md` | Decision rules | Shared |
| `decision_model/` | Clef scripts | Student 3 |
| `decision_model/README.md` | Decision-model guide | Student 3 |
| `decision_model/smoke_test_clef.py` | Single invented-message smoke test | Student 2 |
| `decision_model/evaluate_decision_model.py` | Clef evaluation script | Student 3 |
| `ml_model/` | Reserved for Student 3 | Student 3 |
| `ml_model/.gitkeep` | Reserved-folder placeholder | Student 3 |
| `models/` | Reserved for Student 3 | Student 3 |
| `models/.gitkeep` | Reserved-folder placeholder | Student 3 |
| `comparison/` | Reserved for Student 3 | Student 3 |
| `comparison/.gitkeep` | Reserved-folder placeholder | Student 3 |
| `results/` | Reserved for generated Clef results | Shared |
| `results/.gitkeep` | Reserved-folder placeholder | Shared |
| `requirements.txt` | Runtime and evaluation dependencies | Shared |
| `.env.example` | Safe environment template | Shared |
| `.gitignore` | Git exclusion rules | Shared |
| `README.md` | Project guide | Shared |
| `STRUCTURE.md` | Repository map and ownership | Shared |

## Team rules

1. Do not edit another student's files.
2. Tell the team before changing a shared file.
3. Every router follows `kio/base.py`: message in, flag `0` or `1` out.

The ML implementation, comparison implementation, notebook, generated ML artifacts, and historical ML archive are intentionally absent from this branch. The reserved folders contain only `.gitkeep` placeholders.
