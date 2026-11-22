"""Campus photo test: run the app's predict() on new photos and score them against targets.

Owner: Amaka Okoro (demo test) · Code: Dakarai Lanes · Run: scripts/run_demo_test.py
Reads: a folder of photos named with their true class, e.g. test_js_special_handling_battery.jpg
Writes: results/demo_test.csv

Targets (pitch + CP3 action plan): >= 90% correct overall (9 of 10) and >= 80% in each
class (8 of 10). With fewer than 5 photos in a class the per-class rate is reported but
flagged as too few to judge.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from recycle_coach import config
from recycle_coach.predict import load_predictor

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # convert iPhone HEIC to JPG first
OVERALL_TARGET = 0.90
PER_CLASS_TARGET = 0.80
MIN_PER_CLASS = 5


def label_from_filename(name: str) -> Optional[str]:
    """Return the class named in a filename, or None. Longest class name wins."""
    stem = Path(name).stem.lower().replace("-", "_").replace(" ", "_")
    for cls in sorted(config.CLASSES, key=len, reverse=True):
        if re.search(rf"(^|_){cls}(_|$)", stem):
            return cls
    return None


def run_demo_test(
    folder: Path,
    checkpoint_path: Path = config.CHECKPOINT_PATH,
    output_csv: Path = config.RESULTS_DIR / "demo_test.csv",
) -> pd.DataFrame:
    photos = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
    predictor = load_predictor(checkpoint_path=checkpoint_path)
    if type(predictor).__name__ == "FakePredictor":
        raise FileNotFoundError(f"No checkpoint at {checkpoint_path}; the demo test needs the real model.")

    rows: List[Dict[str, Any]] = []
    skipped = []
    for p in photos:
        true = label_from_filename(p.name)
        if true is None:
            skipped.append(p.name)
            continue
        res = predictor.predict(p)
        rows.append({
            "file": p.name, "true_label": true, "pred_label": res["label"],
            "correct": res["label"] == true, "confidence": res["confidence"],
            "low_confidence": res["low_confidence"],
            **{f"p_{c}": res["probs"][c] for c in config.CLASSES},
        })
    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    df.attrs["skipped"] = skipped
    return df


def summarize(df: pd.DataFrame) -> List[str]:
    if df.empty:
        return ["No photos with a class in the filename were found."]
    lines = []
    n, k = len(df), int(df["correct"].sum())
    overall = k / n
    verdict = "MET" if overall >= OVERALL_TARGET else f"MISSED by {OVERALL_TARGET - overall:.0%}"
    lines.append(f"Overall: {k} of {n} correct ({overall:.0%}); target >= 90%: {verdict}")
    for cls in config.CLASSES:
        sub = df[df["true_label"] == cls]
        if sub.empty:
            lines.append(f"  {cls}: no photos")
            continue
        kc, nc = int(sub["correct"].sum()), len(sub)
        rate = kc / nc
        if nc < MIN_PER_CLASS:
            verdict = f"too few photos to judge (need {MIN_PER_CLASS})"
        else:
            verdict = "MET" if rate >= PER_CLASS_TARGET else f"MISSED by {PER_CLASS_TARGET - rate:.0%}"
        lines.append(f"  {cls}: {kc} of {nc} ({rate:.0%}); target >= 80%: {verdict}")
    lines.append(f"Low-confidence answers ('Not sure'): {int(df['low_confidence'].sum())} of {n}")
    wrong = df[~df["correct"]]
    for _, r in wrong.iterrows():
        lines.append(f"  wrong: {r['file']} -> {r['pred_label']} ({r['confidence']:.2f})")
    if n < 15:
        lines.append(f"Note: {n} photos. About 15 (5 per class) are needed to judge the targets.")
    return lines
