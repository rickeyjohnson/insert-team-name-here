"""Unit tests for dataset.py (Dakarai)."""

import pandas as pd
import pytest
import torch
from PIL import Image

from recycle_coach import config, dataset


@pytest.fixture
def mock_dataset_env(tmp_path):
    proc_dir = tmp_path / "processed"
    proc_dir.mkdir()

    # Generate 6 dummy images for 3 classes
    rows = []
    for i in range(6):
        cls = config.CLASSES[i % 3]
        img_id = f"test_img_{i:03d}"
        im = Image.new("RGB", (300, 300), color=(i * 30, i * 20, i * 40))
        im_path = proc_dir / f"{img_id}.jpg"
        im.save(im_path)

        rows.append({
            "image_id": img_id,
            "processed_path": str(im_path),
            "group_id": f"grp_{i}",
            "final_label": cls,
            "split": "train" if i < 4 else "val",
        })

    df = pd.DataFrame(rows)
    splits_csv = tmp_path / "splits.csv"
    df.to_csv(splits_csv, index=False)
    return splits_csv, proc_dir, df


def test_recycle_dataset_output_shape(mock_dataset_env):
    splits_csv, proc_dir, df = mock_dataset_env

    ds = dataset.RecycleDataset(
        split="train",
        splits_df=df,
        processed_dir=proc_dir,
    )

    assert len(ds) == 4
    tensor, target = ds[0]
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (3, config.IMG_SIZE, config.IMG_SIZE)
    assert target in (0, 1, 2)


def test_val_transforms_deterministic():
    val_tf = dataset.get_transforms("val")
    im = Image.new("RGB", (300, 300), color=(120, 150, 180))

    t1 = val_tf(im)
    t2 = val_tf(im)

    # In val/test, transforms must be deterministic
    assert torch.allclose(t1, t2)
