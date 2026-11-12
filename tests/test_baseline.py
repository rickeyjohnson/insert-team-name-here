"""Unit tests for baseline.py (Rickey)."""

import pandas as pd
import pytest

from recycle_coach import baseline, config


@pytest.fixture
def dummy_splits():
    rows = [
        # Train: 4 recycling, 2 trash, 1 special_handling
        {"image_id": f"tr_{i}", "group_id": f"g_tr_{i}", "final_label": "recycling", "split": "train"}
        for i in range(4)
    ] + [
        {"image_id": f"tr_{i+4}", "group_id": f"g_tr_{i+4}", "final_label": "trash", "split": "train"}
        for i in range(2)
    ] + [
        {"image_id": "tr_6", "group_id": "g_tr_6", "final_label": "special_handling", "split": "train"}
    ] + [
        # Val: 2 recycling, 1 trash
        {"image_id": "va_1", "group_id": "g_va_1", "final_label": "recycling", "split": "val"},
        {"image_id": "va_2", "group_id": "g_va_2", "final_label": "recycling", "split": "val"},
        {"image_id": "va_3", "group_id": "g_va_3", "final_label": "trash", "split": "val"},
    ]
    return pd.DataFrame(rows)


def test_find_majority_class(dummy_splits):
    lbl, conf = baseline.find_majority_class(dummy_splits)
    assert lbl == "recycling"
    # 4 out of 7 = 0.5714
    assert abs(conf - (4 / 7)) < 1e-3


def test_predict_baseline(dummy_splits):
    pred_df = baseline.predict_baseline(dummy_splits, target_split="val")
    assert len(pred_df) == 3
    assert list(pred_df["pred_label"]) == ["recycling", "recycling", "recycling"]
    assert pred_df.iloc[0]["confidence"] == pytest.approx(4 / 7, 0.001)
    assert "p_recycling" in pred_df.columns
    assert "p_special_handling" in pred_df.columns
    assert "p_trash" in pred_df.columns
