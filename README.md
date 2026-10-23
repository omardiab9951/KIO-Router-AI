# Agent KIO intent router

This project routes a customer message to Support (`0`) or Sales (`1`). It has two interchangeable router slots: the implemented scikit-learn router (`kio/ml_router.py`) and the implemented Cloudflare Clef router (`kio/clef_router.py`). Only `frontend/app.py`, `ml_model/evaluate_ml_model.py`, `decision_model/evaluate_decision_model.py`, and `comparison/compare_results.py` are still placeholders. The project does not generate chatbot answers, use RAG, or train a model in this initial setup.

## Windows setup

Open PowerShell in this `System` folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Run all commands from the `System` folder.

The moved entry points are:

```powershell
python ml_model/train_ml_model.py
python ml_model/evaluate_ml_model.py
python decision_model/evaluate_decision_model.py
python comparison/compare_results.py
streamlit run frontend/app.py
```

Leave the Cloudflare values empty until credentials are provided. Never commit `.env` or real secrets.

The frozen dataset is hash-checked before loading. The test split is intentionally available only to final evaluation scripts.
