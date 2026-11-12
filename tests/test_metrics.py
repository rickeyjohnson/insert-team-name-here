"""Unit tests for metrics.py (Rickey)."""

import pandas as pd
import pytest

from recycle_coach import config, metrics


def test_compute_metrics_perfect_score():
    y_true = ["recycling", "special_handling", "trash"]
    y_pred = ["recycling", "special_handling", "trash"]

    res = metrics.compute_metrics(y_true, y_pred)

    assert res["accuracy"] == 1.0
    assert res["macro_f1"] == 1.0
    assert res["confusion_matrix"] == [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]


def test_compute_metrics_imperfect_score():
    y_true = ["recycling", "recycling", "trash", "special_handling"]
    y_pred = ["recycling", "trash", "trash", "special_handling"]

    res = metrics.compute_metrics(y_true, y_pred)

    assert res["n"] == 4
    assert res["accuracy"] == 0.75
    # Class order is recycling (0), special_handling (1), trash (2)
    # True recycling: 1 pred recycling, 1 pred trash
    assert res["confusion_matrix"][0] == [1, 0, 1]
    # True special_handling: 1 pred special_handling
    assert res["confusion_matrix"][1] == [0, 1, 0]
    # True trash: 1 pred trash
    assert res["confusion_matrix"][2] == [0, 0, 1]


def test_generate_error_table(tmp_path):
    preds_df = pd.DataFrame([
        {
            "image_id": "img1",
            "split": "val",
            "true_label": "recycling",
            "pred_label": "trash",
            "confidence": 0.85,
        },
        {
            "image_id": "img2",
            "split": "val",
            "true_label": "trash",
            "pred_label": "trash",
            "confidence": 0.95,
        },
    ])

    images_csv = tmp_path / "images.csv"
    images_csv.write_text(
        "image_id,raw_path,source,source_ref,license,item,label,labeler,lighting,background,notes\n"
        "img1,path1,taco,ref1,CC,plastic wrapper,recycling,js,bright,cluttered,\n"
        "img2,path2,taco,ref2,CC,can,trash,js,dim,plain,\n"
    )

    err_df = metrics.generate_error_table(preds_df, images_csv=images_csv)

    assert len(err_df) == 1
    assert err_df.iloc[0]["image_id"] == "img1"
    assert err_df.iloc[0]["item"] == "plastic wrapper"
    assert err_df.iloc[0]["lighting"] == "bright"
