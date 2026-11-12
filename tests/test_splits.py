"""Unit tests for splits.py (Rickey)."""

import pandas as pd
import pytest

from recycle_coach import config, splits


@pytest.fixture
def dummy_clean_df():
    rows = []
    # 300 samples across 3 classes and groups of size 1-3
    for i in range(300):
        cls = config.CLASSES[i % 3]
        group = f"group_{i // 2}"  # 2 crops per photo/group
        rows.append(
            {
                "image_id": f"img_{i:04d}",
                "processed_path": f"data/processed/img_{i:04d}.jpg",
                "final_label": cls,
                "sha256": f"sha_{i}",
                "phash": f"phash_{i}",
                "group_id": group,
                "width": 200,
                "height": 200,
                "usable": True,
                "exclusion_reason": "",
            }
        )
    return pd.DataFrame(rows)


def test_split_no_group_leakage(dummy_clean_df):
    splits_df = splits.create_splits(dummy_clean_df, seed=365)

    assert set(splits_df["split"].unique()) == {"train", "val", "test"}
    # Verify no group appears in more than one split
    leakage = splits_df.groupby("group_id")["split"].nunique().max()
    assert leakage == 1


def test_split_reproducibility(dummy_clean_df):
    splits_df1 = splits.create_splits(dummy_clean_df, seed=365)
    splits_df2 = splits.create_splits(dummy_clean_df, seed=365)

    pd.testing.assert_frame_equal(splits_df1, splits_df2)


def test_split_proportions(dummy_clean_df):
    splits_df = splits.create_splits(dummy_clean_df, seed=365)
    n_total = len(splits_df)

    proportions = splits_df["split"].value_counts(normalize=True)

    # 70 / 15 / 15 target (within 3 percentage points for small datasets)
    assert abs(proportions["train"] - 0.70) < 0.05
    assert abs(proportions["val"] - 0.15) < 0.05
    assert abs(proportions["test"] - 0.15) < 0.05
