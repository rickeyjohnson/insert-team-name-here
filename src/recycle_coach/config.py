"""Shared constants and paths for the whole project.

Import these; never retype them. Values come from docs/PROJECT_SPEC.md §14.
Changing one needs the team's OK: update PROJECT_SPEC.md in the same commit.
"""

from pathlib import Path

# Paths (relative to the repo root, so they work on every laptop and on Colab)
ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"

IMAGES_CSV = METADATA_DIR / "images.csv"
REVIEWS_CSV = METADATA_DIR / "reviews.csv"
CLEAN_CSV = METADATA_DIR / "clean.csv"
SPLITS_CSV = METADATA_DIR / "splits.csv"

MODELS_DIR = ROOT / "models"
CHECKPOINT_PATH = MODELS_DIR / "mobilenetv3_best.pt"

RESULTS_DIR = ROOT / "results"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
METRICS_DIR = RESULTS_DIR / "metrics"
ERRORS_DIR = RESULTS_DIR / "errors"
FIGURES_DIR = RESULTS_DIR / "figures"

# Labels (alphabetical, so the order matches torchvision's ImageFolder)
CLASSES = ("recycling", "special_handling", "trash")
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASSES)}
DISPLAY_NAMES = {
    "recycling": "Recycling",
    "special_handling": "Special handling",
    "trash": "Trash",
}

LIGHTING = ("bright", "dim", "glare")
BACKGROUNDS = ("plain", "cluttered")

# Reproducibility and splits
SEED = 365
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}

# Cleaning
MIN_SHORT_SIDE = 128
PHASH_MAX_DISTANCE = 6
PROCESSED_LONG_SIDE = 512
PROCESSED_JPEG_QUALITY = 90

# Model input
IMG_SIZE = 224
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# Evaluation and demo
TARGET_MACRO_F1 = 0.70
LOW_CONFIDENCE = 0.60
