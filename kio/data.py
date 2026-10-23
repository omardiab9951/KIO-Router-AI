"""Load and validate the frozen KIO dataset."""

import hashlib
from pathlib import Path

import pandas as pd

from .config import EXPECTED_CONTENT_HASH

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Agent_KIO_Dataset_FROZEN.xlsx"
REQUIRED_COLUMNS = ["ID", "Message", "Category", "Flag", "Split", "Group_ID", "Type"]


def _canonical_content_hash(frame: pd.DataFrame) -> str:
    """Hash sorted, stable CSV content rather than Excel container bytes."""
    canonical = frame[REQUIRED_COLUMNS].sort_values("ID", kind="stable").to_csv(
        index=False, lineterminator="\n"
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _read_frozen() -> pd.DataFrame:
    """Read the workbook, report both hashes, then enforce its content hash."""
    try:
        file_hash = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    except Exception as exc:
        raise RuntimeError(f"Could not read frozen dataset {DATA_PATH}: {exc}") from exc
    try:
        frame = pd.read_excel(DATA_PATH, engine="openpyxl")
    except Exception as exc:
        raise RuntimeError(f"Could not load frozen dataset {DATA_PATH}: {exc}") from exc
    content_hash = _canonical_content_hash(frame)
    print(f"content_hash={content_hash} file_hash={file_hash}")
    if content_hash.lower() != EXPECTED_CONTENT_HASH.lower():
        raise RuntimeError(
            "Frozen dataset content hash mismatch: "
            f"expected {EXPECTED_CONTENT_HASH}, got {content_hash}"
        )
    _validate(frame)
    return frame


def _validate(frame: pd.DataFrame) -> None:
    if list(frame.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Unexpected columns: {list(frame.columns)}")
    if len(frame) != 60:
        raise ValueError("Dataset must contain exactly 60 rows")
    if frame["Category"].value_counts().to_dict() != {"Support": 30, "Sales": 30}:
        raise ValueError("Dataset must contain 30 Support and 30 Sales rows")
    for split, expected in {"Train": {"Support": 20, "Sales": 20}, "Test": {"Support": 10, "Sales": 10}}.items():
        actual = frame.loc[frame["Split"] == split, "Category"].value_counts().to_dict()
        if actual != expected:
            raise ValueError(f"Unexpected {split} distribution: {actual}")
    split_count = frame.groupby("Group_ID")["Split"].nunique()
    if (split_count > 1).any():
        raise ValueError("A Group_ID appears in both Train and Test")
    expected_flags = frame["Category"].map({"Support": 0, "Sales": 1})
    if not frame["Flag"].eq(expected_flags).all():
        raise ValueError("Flag does not match Category")


def get_train() -> pd.DataFrame:
    return _read_frozen().query("Split == 'Train'").copy()


def get_test(i_am_the_final_evaluation: bool = False) -> pd.DataFrame:
    # Test data is restricted to the final evaluation scripts only.
    if not i_am_the_final_evaluation:
        raise PermissionError("get_test() is restricted to final evaluation scripts")
    return _read_frozen().query("Split == 'Test'").copy()


def get_all_messages() -> pd.DataFrame:
    return _read_frozen()[["ID", "Message"]].copy()

