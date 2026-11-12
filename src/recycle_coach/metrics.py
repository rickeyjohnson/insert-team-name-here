"""Accuracy, macro F1, per-class recall, confusion matrix, and error tables.

Owner: Rickey Johnson · Build plan: 2.5 · Spec: docs/PROJECT_SPEC.md §8.5–§8.7, §11
Reads: results/predictions/<model>_<split>.csv, data/metadata/images.csv
Writes: results/metrics/*.json, results/figures/confusion_*.png, results/errors/*_errors.csv
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from recycle_coach import config

logger = logging.getLogger(__name__)


def compute_metrics(
    y_true: List[str],
    y_pred: List[str],
    classes: List[str] = list(config.CLASSES),
) -> Dict[str, Any]:
    """Compute accuracy, macro F1, per-class metrics, and confusion matrix."""
    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", labels=classes, zero_division=0))

    report = classification_report(
        y_true,
        y_pred,
        labels=classes,
        target_names=classes,
        output_dict=True,
        zero_division=0,
    )

    per_class = {}
    for cls in classes:
        cls_rep = report.get(cls, {})
        per_class[cls] = {
            "precision": round(float(cls_rep.get("precision", 0.0)), 4),
            "recall": round(float(cls_rep.get("recall", 0.0)), 4),
            "f1": round(float(cls_rep.get("f1-score", 0.0)), 4),
            "support": int(cls_rep.get("support", 0)),
        }

    cm = confusion_matrix(y_true, y_pred, labels=classes)

    return {
        "n": len(y_true),
        "classes": list(classes),
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
    }


def save_confusion_matrix_figure(
    cm_matrix: List[List[int]],
    classes: List[str] = list(config.CLASSES),
    title: str = "Confusion Matrix",
    output_path: Optional[Path] = None,
) -> Path:
    """Plot and save confusion matrix figure."""
    fig, ax = plt.subplots(figsize=(5, 4.2))
    display_labels = [config.DISPLAY_NAMES.get(c, c) for c in classes]
    disp = ConfusionMatrixDisplay(
        confusion_matrix=np.array(cm_matrix),
        display_labels=display_labels,
    )
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title, fontsize=10)
    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def generate_error_table(
    predictions_df: pd.DataFrame,
    images_csv: Optional[Path] = config.IMAGES_CSV,
    output_error_csv: Optional[Path] = None,
) -> pd.DataFrame:
    """Filter incorrect predictions and join with image metadata."""
    wrong_df = predictions_df[
        predictions_df["true_label"] != predictions_df["pred_label"]
    ].copy()

    metadata_cols = ["item", "source", "lighting", "background"]
    if images_csv and images_csv.exists():
        df_images = pd.read_csv(images_csv)
        avail_cols = ["image_id"] + [c for c in metadata_cols if c in df_images.columns]
        merged = wrong_df.merge(
            df_images[avail_cols],
            on="image_id",
            how="left",
        )
    else:
        merged = wrong_df
        for col in metadata_cols:
            if col not in merged.columns:
                merged[col] = ""

    if output_error_csv:
        output_error_csv.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(output_error_csv, index=False)

    return merged


def evaluate_predictions(
    predictions_csv: Path,
    model_name: str,
    split_name: str,
    output_metrics_json: Optional[Path] = None,
    output_figure_png: Optional[Path] = None,
    output_error_csv: Optional[Path] = None,
    images_csv: Optional[Path] = config.IMAGES_CSV,
) -> Dict[str, Any]:
    """Run full evaluation from predictions CSV and save metrics, figure, and errors."""
    df_pred = pd.read_csv(predictions_csv)
    y_true = df_pred["true_label"].astype(str).tolist()
    y_pred = df_pred["pred_label"].astype(str).tolist()

    metrics = compute_metrics(y_true, y_pred)
    metrics["model"] = model_name
    metrics["split"] = split_name
    metrics["created"] = str(date.today())

    if output_metrics_json:
        output_metrics_json.parent.mkdir(parents=True, exist_ok=True)
        with open(output_metrics_json, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

    if output_figure_png:
        title = f"{model_name.capitalize()} ({split_name} set, n={metrics['n']})"
        save_confusion_matrix_figure(
            cm_matrix=metrics["confusion_matrix"],
            classes=metrics["classes"],
            title=title,
            output_path=output_figure_png,
        )

    if output_error_csv:
        generate_error_table(
            predictions_df=df_pred,
            images_csv=images_csv,
            output_error_csv=output_error_csv,
        )

    return metrics
