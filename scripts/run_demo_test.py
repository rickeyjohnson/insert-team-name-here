"""Score the app's predictions on new campus photos against the 9/10 and 8/10-per-class targets.

    python scripts/run_demo_test.py campus_test/

Name each photo with its true class: test_<initials>_<class>_<item>.jpg, where <class> is
recycling, special_handling or trash. Writes results/demo_test.csv.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recycle_coach import config, demo_eval  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--checkpoint", type=Path, default=config.CHECKPOINT_PATH)
    args = ap.parse_args()

    df = demo_eval.run_demo_test(args.folder, checkpoint_path=args.checkpoint)
    print(f"\n===== CAMPUS PHOTO TEST ({args.folder}) =====")
    print(df[["file", "true_label", "pred_label", "confidence", "correct"]].to_string(index=False))
    print()
    print("\n".join(demo_eval.summarize(df)))
    if df.attrs.get("skipped"):
        print(f"Skipped (no class in filename): {', '.join(df.attrs['skipped'])}")
    print("Saved results/demo_test.csv")


if __name__ == "__main__":
    main()
