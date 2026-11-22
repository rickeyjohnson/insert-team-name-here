"""Checkpoint 3 model comparison. Run --phase val first, then --phase test once.

    python scripts/run_cp3_experiments.py --phase val            # E0, E2, E4, E5, E6
    python scripts/run_cp3_experiments.py --phase val --resnet   # also ResNet-18
    python scripts/run_cp3_experiments.py --phase test           # the val pick, on test, once

Needs data/processed/*.jpg (from Drive, or rebuilt by notebooks/02_cp3_experiments.ipynb).
Logic lives in src/recycle_coach/experiments.py.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recycle_coach import config, experiments  # noqa: E402

# CP1 notebook run (seed-42 split, single stage), for the "what changed" comparison
E1 = {"split": "seed 42 (leaky)", "val_macro_f1": 0.766, "test_macro_f1": 0.6486, "test_accuracy": 0.678}


def check_images() -> None:
    df = pd.read_csv(config.SPLITS_CSV)
    missing = [i for i in df["image_id"] if not (config.PROCESSED_DIR / f"{i}.jpg").exists()]
    if missing:
        sys.exit(f"{len(missing)} of {len(df)} images in splits.csv are missing from "
                 f"{config.PROCESSED_DIR} (e.g. {missing[:3]}). Copy data/processed/ from Drive first.")


def print_val(summary: pd.DataFrame) -> None:
    cols = ["id", "arch", "oversample", "params_m", "best_epoch", "val_accuracy", "val_macro_f1",
            "val_recall_recycling", "val_recall_special_handling", "val_recall_trash",
            "cpu_ms_per_image", "train_minutes"]
    print("\n===== CP3 VALIDATION RESULTS (seed-365 split, val n=%d) =====" %
          int((pd.read_csv(config.SPLITS_CSV)["split"] == "val").sum()))
    print(summary[cols].to_string(index=False))
    if experiments.SELECTION_JSON.exists():
        sel = json.loads(experiments.SELECTION_JSON.read_text())
        print(f"\nPICK (val only): {sel['id']} {sel['arch']} oversample={sel['oversample']} "
              f"val macro F1 {sel['val_macro_f1']:.3f}. Rule: {sel['rule']}.")
    print("CPU time = median single-image predict() on this machine's CPU, preprocessing included.")
    print("Test split not touched. Next: python scripts/run_cp3_experiments.py --phase test")


def print_test(m: dict) -> None:
    base = json.loads((config.METRICS_DIR / "baseline_test.json").read_text())
    sel = m["selection"]
    print(f"\n===== CP3 TEST RESULT (run once; model {sel['id']} {sel['arch']}, test n={m['n']}) =====")
    print(f"  Accuracy {m['accuracy']:.3f} | Macro F1 {m['macro_f1']:.3f}")
    for c in config.CLASSES:
        pc = m["per_class"][c]
        print(f"  {c:17s} recall {pc['recall']:.3f}  precision {pc['precision']:.3f}  "
              f"F1 {pc['f1']:.3f}  (n={pc['support']})")
    print(f"  Confusion matrix (rows true, cols predicted, {', '.join(config.CLASSES)}): "
          f"{m['confusion_matrix']}")
    print(f"  Baseline E0 on test: accuracy {base['accuracy']:.3f} | macro F1 {base['macro_f1']:.3f}")
    print(f"  E1 (CP1, {E1['split']}): test macro F1 {E1['test_macro_f1']:.3f}, accuracy {E1['test_accuracy']:.3f}")
    print("\n  Targets:")
    print("\n".join(experiments.target_lines(m, base["macro_f1"])))
    print(f"\n  Copied the pick to {config.CHECKPOINT_PATH.relative_to(config.ROOT)} (the app's checkpoint).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=["val", "test"], required=True)
    ap.add_argument("--resnet", action="store_true", help="also train ResNet-18 (E6b)")
    ap.add_argument("--only", nargs="+", help="run only these experiment ids, e.g. E2 E5")
    ap.add_argument("--stage2-epochs", type=int, default=15)
    ap.add_argument("--force", action="store_true", help="re-run test (only if the first run was invalid)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    check_images()
    if args.phase == "val":
        print_val(experiments.run_val_phase(include_resnet=args.resnet, only=args.only,
                                            stage2_epochs=args.stage2_epochs))
    else:
        print_test(experiments.run_test_phase(force=args.force))


if __name__ == "__main__":
    main()
