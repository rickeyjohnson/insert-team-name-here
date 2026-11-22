"""Checkpoint 3 model comparison: train every candidate on val, pick one, test it once.

Owner: Dakarai Lanes · Spec: docs/PROJECT_SPEC.md §10–§11 · Run: scripts/run_cp3_experiments.py
Reads: data/metadata/splits.csv, data/processed/
Writes: models/experiments/<id>.pt (git-ignored), models/mobilenetv3_best.pt (final pick),
        results/metrics/cp3_*.json|csv, results/predictions/cp3_*.csv, results/figures/cp3_*.png

Phase "val" trains every experiment with the same split and recipe, scores it on val,
times it on CPU, and records the pick (highest val macro F1). Phase "test" scores only
that pick on the test split, once. Nothing in phase "val" reads the test split.
"""

import json
import logging
import shutil
import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import torch

from recycle_coach import config
from recycle_coach.baseline import run_baseline
from recycle_coach.metrics import compute_metrics, evaluate_predictions
from recycle_coach.predict import Predictor
from recycle_coach.train import build_model, get_device, train_model

logger = logging.getLogger(__name__)

EXPERIMENTS_DIR = config.MODELS_DIR / "experiments"
VAL_SUMMARY_CSV = config.METRICS_DIR / "cp3_val_summary.csv"
SELECTION_JSON = config.METRICS_DIR / "cp3_selection.json"
TEST_JSON = config.METRICS_DIR / "cp3_test.json"

# The shared recipe (train.py defaults): head only at 1e-3 for 3 epochs, then all layers
# at 1e-4 with cosine decay for up to 15 epochs, early stop after 5 without val gain,
# class-weighted cross-entropy, batch 32, train-only augmentation, seed 365.
EXPERIMENTS: List[Dict[str, Any]] = [
    {"id": "E2", "arch": "mobilenet_v3_large", "oversample": False,
     "desc": "MobileNetV3-Large, two-stage, class-weighted loss (main model)"},
    {"id": "E4", "arch": "mobilenet_v3_large", "oversample": True,
     "desc": "E2 + oversample special handling (WeightedRandomSampler)"},
    {"id": "E5", "arch": "mobilenet_v3_small", "oversample": False,
     "desc": "MobileNetV3-Small, same recipe as E2"},
    {"id": "E6", "arch": "efficientnet_b0", "oversample": False,
     "desc": "EfficientNet-B0, same recipe as E2"},
]
OPTIONAL_EXPERIMENTS: List[Dict[str, Any]] = [
    {"id": "E6b", "arch": "resnet18", "oversample": False,
     "desc": "ResNet-18, same recipe as E2"},
]

# Committed and proposed targets (docs/PROJECT_SPEC.md, CP3 action plan)
TARGETS = {
    "macro_f1_committed": config.TARGET_MACRO_F1,
    "macro_f1_ideal": 0.80,
    "special_recall_ideal": 0.70,
    "every_class_recall_ideal": 0.70,
    "accuracy_ideal": 0.80,
}


def count_parameters(arch: str) -> int:
    model = build_model(pretrained=False, arch=arch)
    return sum(p.numel() for p in model.parameters())


def predict_split(predictor: Predictor, splits_df: pd.DataFrame, split: str) -> pd.DataFrame:
    """Run predictor over one split; return rows in the predictions CSV format."""
    df = splits_df[splits_df["split"] == split].reset_index(drop=True)
    rows = []
    for _, row in df.iterrows():
        res = predictor.predict(config.PROCESSED_DIR / f"{row['image_id']}.jpg")
        rows.append({
            "image_id": row["image_id"],
            "split": split,
            "true_label": row["final_label"],
            "pred_label": res["label"],
            "confidence": res["confidence"],
            **{f"p_{c}": res["probs"][c] for c in config.CLASSES},
        })
    return pd.DataFrame(rows)


def cpu_ms_per_image(checkpoint_path: Path, image_paths: List[Path], warmup: int = 5) -> float:
    """Median wall time of one predict() call on CPU, batch size 1, preprocessing included."""
    predictor = Predictor(checkpoint_path=checkpoint_path, device="cpu")
    for p in image_paths[:warmup]:
        predictor.predict(p)
    times = []
    for p in image_paths:
        t0 = time.perf_counter()
        predictor.predict(p)
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    return round(times[len(times) // 2], 1)


def run_val_phase(
    include_resnet: bool = False,
    only: Optional[List[str]] = None,
    stage2_epochs: int = 15,
    stage1_epochs: int = 3,
    timing_images: int = 50,
    pretrained: bool = True,
) -> pd.DataFrame:
    """Train and score every experiment on val; write the summary and the pick."""
    splits_df = pd.read_csv(config.SPLITS_CSV)
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    config.METRICS_DIR.mkdir(parents=True, exist_ok=True)
    config.PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)

    base_preds = run_baseline(split_name="val")
    base = compute_metrics(base_preds["true_label"].tolist(), base_preds["pred_label"].tolist())
    rows = [{
        "id": "E0", "model": "majority class (always recycling)", "arch": "baseline",
        "oversample": False, "params_m": 0.0, "best_epoch": None,
        "val_accuracy": base["accuracy"], "val_macro_f1": base["macro_f1"],
        **{f"val_recall_{c}": base["per_class"][c]["recall"] for c in config.CLASSES},
        "cpu_ms_per_image": 0.0, "train_minutes": 0.0,
    }]

    todo = EXPERIMENTS + (OPTIONAL_EXPERIMENTS if include_resnet else [])
    if only:
        todo = [e for e in todo if e["id"] in only]
    val_df = splits_df[splits_df["split"] == "val"]
    timing_paths = [config.PROCESSED_DIR / f"{i}.jpg" for i in val_df["image_id"].head(timing_images)]

    for exp in todo:
        ckpt = EXPERIMENTS_DIR / f"{exp['id']}_{exp['arch']}.pt"
        logger.info("=== %s: %s ===", exp["id"], exp["desc"])
        t0 = time.time()
        result = train_model(
            checkpoint_path=ckpt, arch=exp["arch"], oversample=exp["oversample"],
            stage1_epochs=stage1_epochs, stage2_epochs=stage2_epochs, pretrained=pretrained,
        )
        train_min = round((time.time() - t0) / 60, 1)
        pd.DataFrame(result["history"]).to_csv(
            config.METRICS_DIR / f"cp3_{exp['id']}_history.csv", index=False)

        predictor = Predictor(checkpoint_path=ckpt, device=str(get_device()))
        preds = predict_split(predictor, splits_df, "val")
        preds_csv = config.PREDICTIONS_DIR / f"cp3_{exp['id']}_val.csv"
        preds.to_csv(preds_csv, index=False)
        m = evaluate_predictions(
            predictions_csv=preds_csv, model_name=exp["id"], split_name="val",
            output_metrics_json=config.METRICS_DIR / f"cp3_{exp['id']}_val.json",
            output_figure_png=config.FIGURES_DIR / f"cp3_confusion_{exp['id']}_val.png",
        )
        rows.append({
            "id": exp["id"], "model": exp["desc"], "arch": exp["arch"],
            "oversample": exp["oversample"],
            "params_m": round(count_parameters(exp["arch"]) / 1e6, 2),
            "best_epoch": result["best_epoch"],
            "val_accuracy": m["accuracy"], "val_macro_f1": m["macro_f1"],
            **{f"val_recall_{c}": m["per_class"][c]["recall"] for c in config.CLASSES},
            "cpu_ms_per_image": cpu_ms_per_image(ckpt, timing_paths),
            "train_minutes": train_min,
        })
        pd.DataFrame(rows).to_csv(VAL_SUMMARY_CSV, index=False)  # save as we go

    summary = pd.DataFrame(rows)
    summary.to_csv(VAL_SUMMARY_CSV, index=False)

    models_only = summary[summary["id"] != "E0"]
    if not models_only.empty:
        # Highest val macro F1; ties go to the faster model.
        pick = models_only.sort_values(["val_macro_f1", "cpu_ms_per_image"],
                                       ascending=[False, True]).iloc[0]
        selection = {
            "id": pick["id"], "arch": pick["arch"], "oversample": bool(pick["oversample"]),
            "val_macro_f1": float(pick["val_macro_f1"]),
            "checkpoint": str((EXPERIMENTS_DIR / f"{pick['id']}_{pick['arch']}.pt").relative_to(config.ROOT)),
            "rule": "highest val macro F1; ties to lower CPU ms/image",
            "picked_on": str(date.today()),
        }
        with open(SELECTION_JSON, "w", encoding="utf-8") as f:
            json.dump(selection, f, indent=2)
    return summary


def run_test_phase(force: bool = False) -> Dict[str, Any]:
    """Score the val-phase pick on the test split, once. Copies it to the app checkpoint."""
    if not SELECTION_JSON.exists():
        raise FileNotFoundError("No val-phase pick found. Run --phase val first.")
    if TEST_JSON.exists() and not force:
        raise RuntimeError(
            f"The test split was already scored ({TEST_JSON.name}). It is used once. "
            "Pass --force only if that run crashed or was invalid, and say so in the report.")
    with open(SELECTION_JSON, encoding="utf-8") as f:
        selection = json.load(f)
    ckpt = config.ROOT / selection["checkpoint"]

    splits_df = pd.read_csv(config.SPLITS_CSV)
    predictor = Predictor(checkpoint_path=ckpt, device=str(get_device()))
    preds = predict_split(predictor, splits_df, "test")
    preds_csv = config.PREDICTIONS_DIR / f"cp3_{selection['id']}_test.csv"
    preds.to_csv(preds_csv, index=False)
    m = evaluate_predictions(
        predictions_csv=preds_csv, model_name=selection["id"], split_name="test",
        output_metrics_json=TEST_JSON,
        output_figure_png=config.FIGURES_DIR / f"cp3_confusion_{selection['id']}_test.png",
        output_error_csv=config.ERRORS_DIR / f"cp3_{selection['id']}_test_errors.csv",
    )
    m["selection"] = selection
    with open(TEST_JSON, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)

    shutil.copy2(ckpt, config.CHECKPOINT_PATH)  # the app loads this path
    return m


def target_lines(m: Dict[str, Any], baseline_macro_f1: float) -> List[str]:
    """Plain-language met/missed line for each target row."""
    recalls = {c: m["per_class"][c]["recall"] for c in config.CLASSES}
    checks = [
        (f"Macro F1 >= {TARGETS['macro_f1_committed']:.2f} and > baseline {baseline_macro_f1:.2f} (committed)",
         m["macro_f1"], m["macro_f1"] >= TARGETS["macro_f1_committed"] and m["macro_f1"] > baseline_macro_f1,
         TARGETS["macro_f1_committed"]),
        (f"Macro F1 >= {TARGETS['macro_f1_ideal']:.2f} (ideal)", m["macro_f1"],
         m["macro_f1"] >= TARGETS["macro_f1_ideal"], TARGETS["macro_f1_ideal"]),
        (f"Special-handling recall >= {TARGETS['special_recall_ideal']:.2f} (ideal)",
         recalls["special_handling"], recalls["special_handling"] >= TARGETS["special_recall_ideal"],
         TARGETS["special_recall_ideal"]),
        (f"Every class recall >= {TARGETS['every_class_recall_ideal']:.2f} (ideal)",
         min(recalls.values()), min(recalls.values()) >= TARGETS["every_class_recall_ideal"],
         TARGETS["every_class_recall_ideal"]),
        (f"Accuracy >= {TARGETS['accuracy_ideal']:.2f} (ideal)", m["accuracy"],
         m["accuracy"] >= TARGETS["accuracy_ideal"], TARGETS["accuracy_ideal"]),
    ]
    out = []
    for name, value, ok, bar in checks:
        verdict = "MET" if ok else f"MISSED by {bar - value:.2f}"
        out.append(f"  {name}: {value:.3f}  {verdict}")
    return out
