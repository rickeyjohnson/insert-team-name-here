"""PyTorch Dataset and transforms (augmentation on train only).

Owner: Dakarai Lanes · Build plan: 3.1 · Spec: docs/PROJECT_SPEC.md §10
Reads: data/metadata/splits.csv, data/processed/
Writes: (nothing; returns tensors)
"""

import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
import torch
from PIL import Image, ImageOps
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from recycle_coach import config

logger = logging.getLogger(__name__)


def get_transforms(split: str = "train") -> transforms.Compose:
    """Return torchvision transforms for split.

    Train split applies random resized crop, horizontal flip, rotation, and color jitter.
    Val and test splits apply resize 256 -> center crop 224 with zero augmentation.
    """
    normalize = transforms.Normalize(
        mean=config.IMAGENET_MEAN,
        std=config.IMAGENET_STD,
    )

    if split == "train":
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(config.IMG_SIZE, scale=(0.7, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.ToTensor(),
                normalize,
            ]
        )
    else:
        return transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(config.IMG_SIZE),
                transforms.ToTensor(),
                normalize,
            ]
        )


class RecycleDataset(Dataset):
    """PyTorch Dataset loading images from splits.csv and data/processed/."""

    def __init__(
        self,
        split: str,
        splits_df: Optional[pd.DataFrame] = None,
        splits_csv: Optional[Path] = config.SPLITS_CSV,
        processed_dir: Path = config.PROCESSED_DIR,
        transform: Optional[Callable] = None,
    ) -> None:
        self.split = split
        self.processed_dir = processed_dir

        if splits_df is not None:
            df = splits_df.copy()
        elif splits_csv and splits_csv.exists():
            df = pd.read_csv(splits_csv)
        else:
            df = pd.DataFrame(columns=["image_id", "final_label", "split"])

        if not df.empty and "split" in df.columns:
            df = df[df["split"] == split].reset_index(drop=True)

        self.df = df
        self.transform = transform or get_transforms(split)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        row = self.df.iloc[index]
        image_id = str(row["image_id"])
        label_str = str(row["final_label"])

        if label_str not in config.CLASS_TO_INDEX:
            raise KeyError(f"Label '{label_str}' not in config.CLASSES {config.CLASSES}")
        target = config.CLASS_TO_INDEX[label_str]

        # Check for image path
        if "processed_path" in row and pd.notna(row["processed_path"]):
            p = Path(str(row["processed_path"]))
            img_path = p if p.is_absolute() else config.ROOT / p
        else:
            img_path = self.processed_dir / f"{image_id}.jpg"

        if not img_path.exists():
            raise FileNotFoundError(f"Processed image missing for index {index}: {img_path}")

        with Image.open(img_path) as raw:
            img = ImageOps.exif_transpose(raw).convert("RGB")

        tensor = self.transform(img)
        return tensor, target


def create_dataloaders(
    splits_csv: Path = config.SPLITS_CSV,
    processed_dir: Path = config.PROCESSED_DIR,
    batch_size: int = 32,
    num_workers: int = 0,
) -> Dict[str, DataLoader]:
    """Create train, val, and test DataLoaders."""
    df_splits = pd.read_csv(splits_csv)
    loaders = {}

    for split in ("train", "val", "test"):
        ds = RecycleDataset(
            split=split,
            splits_df=df_splits,
            processed_dir=processed_dir,
            transform=get_transforms(split),
        )
        shuffle = split == "train"
        loaders[split] = DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
        )

    return loaders
