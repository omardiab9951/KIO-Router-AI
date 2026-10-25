# Project root is the parent of this file's folder.
# Add it so imports work when launched from the System folder.
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import contextlib
import hashlib
import io
import json
import os
from datetime import datetime, timezone

import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from kio import clef_router as clef_module
from kio.clef_router import ClefRouter
from kio.config import PROJECT_DIR
from kio.data import _canonical_content_hash, _read_frozen, get_test
from kio.router import dispatch
from kio.validation import check_instructions_clean


def emit(text, dry):
    print(f"DRY RUN: NOT REAL RESULTS | {text}" if dry else text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run
    if not dry and os.getenv("KIO_MOCK", "0") == "1":
        emit("Refusing to run: KIO_MOCK=1. Use --dry-run for mock evaluation.", dry)
        return 1
    output = PROJECT_DIR / "results" / "decision_results.csv"
    if output.exists() and not args.allow_overwrite and not dry:
        emit(f"Refusing to overwrite {output}; pass --allow-overwrite.", dry)
        return 1
    if dry:
        with contextlib.redirect_stdout(io.StringIO()):
            check_instructions_clean()
            frame = _read_frozen()
    else:
        check_instructions_clean()
        frame = _read_frozen()
    content_hash = _canonical_content_hash(frame)
    instruction_hash = hashlib.sha256((PROJECT_DIR / "kio" / "routing_instructions.md").read_bytes()).hexdigest()
    emit(f"dataset content hash: {content_hash}", dry)
    emit(f"instructions SHA-256: {instruction_hash}", dry)
    clef_module.KIO_MOCK = True if dry else clef_module.KIO_MOCK
    router = ClefRouter()
    if dry:
        with contextlib.redirect_stdout(io.StringIO()):
            test = get_test(i_am_the_final_evaluation=True)
        for row in test.itertuples(index=False):
            with contextlib.redirect_stdout(io.StringIO()):
                dispatch(row.Message, router)
        emit("20 mock router calls completed; no results written.", dry)
        return 0
    test = get_test(i_am_the_final_evaluation=True)
    rows = _run_rows(test, router, content_hash, instruction_hash)
    result = pd.DataFrame(rows)
    output.parent.mkdir(exist_ok=True)
    result.to_csv(output, index=False)
    _print_report(result, emit, dry)
    return 0


def _run_rows(test, router, content_hash, instruction_hash):
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for row in test.itertuples(index=False):
        output, _ = dispatch(row.Message, router)
        rows.append({"ID": row.ID, "Message": row.Message, "Type": row.Type, "Group_ID": row.Group_ID,
                     "true flag": row.Flag, "predicted label": output.label, "predicted flag": output.flag,
                     "correct": output.flag == row.Flag, "confidence": output.confidence,
                     "latency_ms": output.latency_ms, "status": output.status, "raw output": output.raw,
                     "router/model id": output.router_name, "UTC date and time": now,
                     "dataset_content_hash": content_hash, "instructions_sha256": instruction_hash})
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


if __name__ == "__main__":
    raise SystemExit(main())

