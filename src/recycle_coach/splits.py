"""Group-aware, stratified 70/15/15 train/val/test split (seed 365).

Owner: Rickey Johnson · Build plan: 2.4 · Spec: docs/PROJECT_SPEC.md §7, §8.4
Reads: data/metadata/clean.csv
Writes: data/metadata/splits.csv
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from recycle_coach import config

logger = logging.getLogger(__name__)

SPLITS_CSV_COLUMNS = ["image_id", "group_id", "final_label", "split"]


def create_splits(
    clean_df: pd.DataFrame,
    seed: int = config.SEED,
    n_splits: int = 20,
    test_folds: int = 3,
    val_folds: int = 3,
) -> pd.DataFrame:
    """Perform group-aware stratified 70/15/15 split.

    Uses StratifiedGroupKFold with 20 folds (14 train, 3 val, 3 test)
    to ensure near-duplicates (group_id) never leak across splits while
    preserving class balance.
    """
    usable_df = clean_df[clean_df["usable"] == True].copy().reset_index(drop=True)
    if usable_df.empty:
        raise ValueError("Cannot split empty or all-unusable dataset.")

    y = usable_df["final_label"].values
    groups = usable_df["group_id"].values

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    fold_assignments = np.zeros(len(usable_df), dtype=int)

    for fold_idx, (_, test_indices) in enumerate(sgkf.split(usable_df, y, groups)):
        fold_assignments[test_indices] = fold_idx

    split_series = np.where(
        fold_assignments < test_folds,
        "test",
        np.where(
            fold_assignments < (test_folds + val_folds),
            "val",
            "train",
        ),
    )
    usable_df["split"] = split_series

    # Leakage check: no group_id can appear in more than one split
    leakage = usable_df.groupby("group_id")["split"].nunique().max()
    if leakage > 1:
        raise RuntimeError("Group leakage detected: images from the same group cross splits!")

    return usable_df[SPLITS_CSV_COLUMNS]


def run_splits(
    clean_csv: Path = config.CLEAN_CSV,
    output_splits_csv: Path = config.SPLITS_CSV,
    seed: int = config.SEED,
) -> pd.DataFrame:
    """Read clean.csv, compute 70/15/15 group-aware splits, and write splits.csv."""
    if not clean_csv.exists():
        raise FileNotFoundError(f"Missing clean manifest: {clean_csv}")

    df_clean = pd.read_csv(clean_csv)
    splits_df = create_splits(df_clean, seed=seed)

    output_splits_csv.parent.mkdir(parents=True, exist_ok=True)
    splits_df.to_csv(output_splits_csv, index=False)
    return splits_df
