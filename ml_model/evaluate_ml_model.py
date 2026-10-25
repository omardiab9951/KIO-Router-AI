# Project root is the parent of this file's folder.
# Add it so imports work when launched from the System folder.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import hashlib
import json
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from kio.config import PROJECT_DIR
from kio.data import _canonical_content_hash, _read_frozen, get_test, get_train
from kio.ml_router import MLRouter
from kio.router import dispatch


def emit(text, dry):
    print(f"DRY RUN: NOT REAL RESULTS | {text}" if dry else text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run
    results = PROJECT_DIR / "results"
    output = results / "ml_results.csv"
    if output.exists() and not args.allow_overwrite and not dry:
        emit(f"Refusing to overwrite {output}; pass --allow-overwrite.", dry)
        return 1
    model_path = PROJECT_DIR / "models" / "ml_model.joblib"
    settings_path = results / "ml_settings.json"
    if not model_path.exists():
        emit("ML model missing: run python ml_model/train_ml_model.py", dry)
        return 0
    frame = _read_frozen()
    content_hash = _canonical_content_hash(frame)
    instruction_hash = hashlib.sha256((PROJECT_DIR / "kio" / "routing_instructions.md").read_bytes()).hexdigest()
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    settings_hash = hashlib.sha256(settings_path.read_bytes()).hexdigest()
    for name, value in [("dataset content hash", content_hash), ("instructions SHA-256", instruction_hash),
                        ("model SHA-256", model_hash), ("settings SHA-256", settings_hash)]:
        emit(f"{name}: {value}", dry)
    if dry:
        emit("Dry-run metadata and router setup validated; no results written.", dry)
        return 0
    test = get_test(i_am_the_final_evaluation=True)
    router = MLRouter(model_path)
    rows = _run_rows(test, router, content_hash, instruction_hash, model_hash, settings_hash)
    result = pd.DataFrame(rows)
    results.mkdir(exist_ok=True)
    result.to_csv(output, index=False)
    _print_report(result, emit, dry)
    _save_boundary(get_train(), test, router, result, results / "ml_boundary_with_test.png")
    return 0


def _run_rows(test, router, content_hash, instruction_hash, model_hash, settings_hash):
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for row in test.itertuples(index=False):
        output, _ = dispatch(row.Message, router)
        rows.append({"ID": row.ID, "Message": row.Message, "Type": row.Type, "Group_ID": row.Group_ID,
                     "true flag": row.Flag, "predicted label": output.label, "predicted flag": output.flag,
                     "correct": output.flag == row.Flag, "confidence": output.confidence,
                     "latency_ms": output.latency_ms, "status": output.status, "raw output": output.raw,
                     "router/model id": output.router_name, "UTC date and time": now,
                     "dataset_content_hash": content_hash, "instructions_sha256": instruction_hash,
                     "model_sha256": model_hash, "settings_sha256": settings_hash})
    return rows


def _print_report(result, emit, dry):
    correct = int(result["correct"].sum())
    emit(f"correct/incorrect: {correct}/{len(result)-correct}; accuracy: {correct/len(result):.3f}", dry)
    matrix = confusion_matrix(result["true flag"], result["predicted flag"], labels=[0, 1])
    emit(f"confusion matrix [[{matrix[0,0]}, {matrix[0,1]}], [{matrix[1,0]}, {matrix[1,1]}]]", dry)
    valid = result["predicted flag"].notna()
    p, r, f, _ = precision_recall_fscore_support(result.loc[valid, "true flag"], result.loc[valid, "predicted flag"], labels=[1], average="binary", zero_division=0)
    emit(f"Sales precision: {p:.3f}; recall: {r:.3f}; F1: {f:.3f}", dry)
    emit("errors by Type: " + json.dumps(result.loc[~result.correct].groupby("Type").size().to_dict()), dry)


def _save_boundary(train, test, router, result, path):
    from sklearn.decomposition import TruncatedSVD
    model = router._model
    tfidf = model.named_steps["tfidf"]
    svd = TruncatedSVD(n_components=2, random_state=42)
    train_z = svd.fit_transform(tfidf.transform(train["Message"]))
    test_z = svd.transform(tfidf.transform(test["Message"]))
    plt.figure(figsize=(8, 6))
    plt.scatter(train_z[:, 0], train_z[:, 1], c=train["Flag"], cmap="coolwarm", label="training", alpha=0.6)
    correct = result["correct"].to_numpy()
    plt.scatter(test_z[correct, 0], test_z[correct, 1], marker="^", facecolors="none", edgecolors="green", label="test correct", s=80)
    plt.scatter(test_z[~correct, 0], test_z[~correct, 1], marker="X", color="black", label="test wrong", s=80)
    plt.xlabel("SVD component 1"); plt.ylabel("SVD component 2")
    plt.title("ML boundary with test points — training data and test overlay")
    plt.legend(); plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()


if __name__ == "__main__":
    raise SystemExit(main())

