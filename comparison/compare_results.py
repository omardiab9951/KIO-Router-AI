# Project root is the parent of this file's folder.
# Add it so imports work when launched from the System folder.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from datetime import datetime, timezone

import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

from kio.config import PROJECT_DIR


def emit(text, dry):
    print(f"DRY RUN: NOT REAL RESULTS | {text}" if dry else text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run
    if dry:
        left = _made_up("ml")
        right = _made_up("clef")
        emit("made-up in-memory comparison only; no files read or written.", dry)
    else:
        left_path = PROJECT_DIR / "results" / "ml_results.csv"
        right_path = PROJECT_DIR / "results" / "decision_results.csv"
        if not left_path.exists():
            print(f"Missing results file: {left_path}")
            return 0
        if not right_path.exists():
            print(f"Missing results file: {right_path}")
            return 0
        left, right = pd.read_csv(left_path), pd.read_csv(right_path)
        if set(left.ID) != set(right.ID) or len(left) != 20 or len(right) != 20:
            print("Results files do not cover the same 20 test IDs.")
            return 1
        if left.dataset_content_hash.iloc[0] != right.dataset_content_hash.iloc[0]:
            print("Results files have different dataset content hashes.")
            return 1
    if not dry and len(left) != len(right):
        print("Results files have different row counts.")
        return 1
    summary = _summary(left, right)
    if dry:
        for line in summary.splitlines():
            emit(line, dry)
    else:
        (PROJECT_DIR / "results" / "comparison_summary.md").write_text(summary, encoding="utf-8")
        print(summary)
    return 0


def _made_up(name):
    now = datetime.now(timezone.utc).isoformat()
    return pd.DataFrame([
        {"ID": 9001, "Message": "invented alpha", "Type": "plain", "true flag": 0, "predicted flag": 0, "correct": True, "latency_ms": 1.0, "router/model id": name, "UTC date and time": now, "dataset_content_hash": "DRY"},
        {"ID": 9002, "Message": "invented beta", "Type": "negation", "true flag": 1, "predicted flag": 0, "correct": False, "latency_ms": 2.0, "router/model id": name, "UTC date and time": now, "dataset_content_hash": "DRY"},
    ])


def _metrics(frame):
    correct = int(frame.correct.sum())
    p, r, f, _ = precision_recall_fscore_support(frame["true flag"], frame["predicted flag"], labels=[1], average="binary", zero_division=0)
    return correct, len(frame) - correct, correct / len(frame), p, r, f


def _summary(left, right):
    lines = ["# Router comparison", "", "| Metric | ML classifier | Decision model |", "|---|---:|---:|"]
    lm, rm = _metrics(left), _metrics(right)
    for label, a, b in [("Correct", lm[0], rm[0]), ("Incorrect", lm[1], rm[1]), ("Accuracy", f"{lm[2]:.3f}", f"{rm[2]:.3f}"), ("Sales precision", f"{lm[3]:.3f}", f"{rm[3]:.3f}"), ("Sales recall", f"{lm[4]:.3f}", f"{rm[4]:.3f}"), ("Sales F1", f"{lm[5]:.3f}", f"{rm[5]:.3f}"), ("Average latency (ms)", f"{left.latency_ms.mean():.3f}", f"{right.latency_ms.mean():.3f}")]:
        lines.append(f"| {label} | {a} | {b} |")
    lines += ["", "Each test error = 5 percentage points.", "", "## Errors by Type", "", "| Type | ML classifier | Decision model |", "|---|---:|---:|"]
    for kind in ["plain", "paraphrase", "negation", "mixed"]:
        lines.append(f"| {kind} | {int(((left.Type == kind) & ~left.correct).sum())} | {int(((right.Type == kind) & ~right.correct).sum())} |")
    lines += ["", "## Disagreements", "", "| ID | Message | True label | ML label | Decision label |", "|---:|---|---:|---|---|"]
    merged = left.merge(right, on="ID", suffixes=("_ml", "_decision"))
    for row in merged[merged["predicted flag_ml"] != merged["predicted flag_decision"]].itertuples():
        lines.append(f"| {row.ID} | {row.Message_ml} | {row._asdict()['true flag_ml']} | {row._asdict()['predicted label_ml']} | {row._asdict()['predicted label_decision']} |")
    lines += ["", "## Non-numeric criteria", "", "| Criterion | ML classifier | Decision model |", "|---|---|---|", "| Needs training data | yes | no |", "| Setup and cost | local training; infrastructure dependent | API/account dependent |", "| Explainability | pipeline and top terms | typed decisions and probabilities |", "| License | TO VERIFY | TO VERIFY |"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

