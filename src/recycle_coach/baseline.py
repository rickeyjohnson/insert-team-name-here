"""Majority-class baseline: predict the most common train label for every image.

Owner: Rickey Johnson · Build plan: 2.6 · Spec: docs/PROJECT_SPEC.md §9
Reads: data/metadata/splits.csv
Writes: results/predictions/baseline_<split>.csv (then metrics.py for the rest)
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

from recycle_coach import config
from recycle_coach.metrics import evaluate_predictions

logger = logging.getLogger(__name__)

PREDICTIONS_CSV_COLUMNS = [
    "image_id",
    "split",
    "true_label",
    "pred_label",
    "confidence",
    "p_recycling",
    "p_special_handling",
    "p_trash",
]


def find_majority_class(splits_df: pd.DataFrame) -> Tuple[str, float]:
    """Find the most frequent class in the train split and its proportion."""
    train_df = splits_df[splits_df["split"] == "train"]
    if train_df.empty:
        raise ValueError("Train split is empty; cannot determine majority class.")

    counts = train_df["final_label"].value_counts()
    majority_label = counts.index[0]
    confidence = float(counts.iloc[0] / len(train_df))
    return majority_label, round(confidence, 4)


def predict_baseline(
    splits_df: pd.DataFrame,
    target_split: str = "val",
    majority_label: Optional[str] = None,
    confidence: Optional[float] = None,
) -> pd.DataFrame:
    """Generate baseline predictions for target split (val or test)."""
    if majority_label is None or confidence is None:
        majority_label, confidence = find_majority_class(splits_df)

    eval_df = splits_df[splits_df["split"] == target_split].copy().reset_index(drop=True)
    if eval_df.empty:
        raise ValueError(f"No samples found for split '{target_split}'")

    rows = []
    for _, row in eval_df.iterrows():
        rec = {
            "image_id": row["image_id"],
            "split": target_split,
            "true_label": row["final_label"],
            "pred_label": majority_label,
            "confidence": confidence,
            "p_recycling": confidence if majority_label == "recycling" else 0.0,
            "p_special_handling": confidence if majority_label == "special_handling" else 0.0,
            "p_trash": confidence if majority_label == "trash" else 0.0,
        }
        rows.append(rec)

    return pd.DataFrame(rows)[PREDICTIONS_CSV_COLUMNS]


def run_baseline(
    splits_csv: Path = config.SPLITS_CSV,
    split_name: str = "val",
    output_predictions_csv: Optional[Path] = None,
    output_metrics_json: Optional[Path] = None,
    output_figure_png: Optional[Path] = None,
    output_error_csv: Optional[Path] = None,
) -> pd.DataFrame:
    """Run baseline prediction and evaluation for a split."""
    if not splits_csv.exists():
        raise FileNotFoundError(f"Missing splits manifest: {splits_csv}")

    splits_df = pd.read_csv(splits_csv)
    pred_df = predict_baseline(splits_df, target_split=split_name)

    if output_predictions_csv is None:
        config.PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
        output_predictions_csv = config.PREDICTIONS_DIR / f"baseline_{split_name}.csv"

    output_predictions_csv.parent.mkdir(parents=True, exist_ok=True)
    pred_df.to_csv(output_predictions_csv, index=False)

    if output_metrics_json is None:
        config.METRICS_DIR.mkdir(parents=True, exist_ok=True)
        output_metrics_json = config.METRICS_DIR / f"baseline_{split_name}.json"

    if output_figure_png is None:
        config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        output_figure_png = config.FIGURES_DIR / f"confusion_baseline_{split_name}.png"

    if output_error_csv is None:
        config.ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        output_error_csv = config.ERRORS_DIR / f"baseline_{split_name}_errors.csv"

    evaluate_predictions(
        predictions_csv=output_predictions_csv,
        model_name="baseline",
        split_name=split_name,
        output_metrics_json=output_metrics_json,
        output_figure_png=output_figure_png,
        output_error_csv=output_error_csv,
    )

    return pred_df
