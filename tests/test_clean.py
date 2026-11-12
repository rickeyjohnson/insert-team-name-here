"""Unit tests for clean.py (Rickey)."""

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from recycle_coach import clean, config


@pytest.fixture
def sample_image_dir(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()

    # Valid image: 200x200
    im_valid = Image.new("RGB", (200, 200), color=(100, 150, 200))
    im_valid.save(d / "valid_001.jpg")

    # Too small image: 100x100 (min side < 128)
    im_small = Image.new("RGB", (100, 100), color=(100, 150, 200))
    im_small.save(d / "small_001.jpg")

    # Large image: 800x600 (needs resize to 512)
    im_large = Image.new("RGB", (800, 600), color=(50, 60, 70))
    im_large.save(d / "large_001.jpg")

    # Exact duplicate of valid_001
    im_dup = Image.new("RGB", (200, 200), color=(100, 150, 200))
    im_dup.save(d / "dup_001.jpg")

    # Corrupt / unreadable file
    with open(d / "corrupt_001.jpg", "wb") as f:
        f.write(b"not an image file")

    return d


def test_too_small_exclusion(sample_image_dir, tmp_path):
    proc_dir = tmp_path / "proc"
    res = clean.clean_image(
        raw_path=sample_image_dir / "small_001.jpg",
        image_id="small_001",
        first_label="recycling",
        processed_dir=proc_dir,
    )
    assert res["usable"] is False
    assert "too_small" in res["exclusion_reason"]


def test_unreadable_exclusion(sample_image_dir, tmp_path):
    proc_dir = tmp_path / "proc"
    res = clean.clean_image(
        raw_path=sample_image_dir / "corrupt_001.jpg",
        image_id="corrupt_001",
        first_label="trash",
        processed_dir=proc_dir,
    )
    assert res["usable"] is False
    assert "unreadable" in res["exclusion_reason"]


def test_resize_long_side(sample_image_dir, tmp_path):
    proc_dir = tmp_path / "proc"
    res = clean.clean_image(
        raw_path=sample_image_dir / "large_001.jpg",
        image_id="large_001",
        first_label="special_handling",
        processed_dir=proc_dir,
        target_long_side=512,
    )
    assert res["usable"] is True
    out_img = Image.open(proc_dir / "large_001.jpg")
    assert max(out_img.size) == 512
    assert out_img.size == (512, 384)


def test_label_resolution():
    # Agreement
    rev_df = pd.DataFrame([
        {"image_id": "img1", "review_label": "trash", "resolution_label": ""},
    ])
    lbl, err = clean.resolve_label("trash", "img1", rev_df)
    assert lbl == "trash"
    assert err is None

    # Disagreement resolved
    rev_df2 = pd.DataFrame([
        {"image_id": "img2", "review_label": "recycling", "resolution_label": "special_handling"},
    ])
    lbl2, err2 = clean.resolve_label("trash", "img2", rev_df2)
    assert lbl2 == "special_handling"
    assert err2 is None

    # Disagreement unresolved
    rev_df3 = pd.DataFrame([
        {"image_id": "img3", "review_label": "recycling", "resolution_label": ""},
    ])
    lbl3, err3 = clean.resolve_label("trash", "img3", rev_df3)
    assert lbl3 is None
    assert err3 == "unresolved_disagreement"


def test_cluster_near_duplicates():
    # Create two nearly identical images and one different
    im1 = Image.new("RGB", (150, 150), color=(128, 128, 128))
    im2 = Image.new("RGB", (150, 150), color=(129, 128, 128))
    im3 = Image.fromarray(np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8))

    records = [
        {"image_id": "i1", "group_id": "i1", "phash": clean.compute_image_phash(im1), "usable": True},
        {"image_id": "i2", "group_id": "i2", "phash": clean.compute_image_phash(im2), "usable": True},
        {"image_id": "i3", "group_id": "i3", "phash": clean.compute_image_phash(im3), "usable": True},
    ]

    clustered = clean.cluster_near_duplicates(records, max_distance=6)
    # i1 and i2 should be in the same group
    assert clustered[0]["group_id"] == clustered[1]["group_id"]
    # i3 should be distinct
    assert clustered[2]["group_id"] != clustered[0]["group_id"]


def test_photo_group_id_from_taco_source_ref():
    assert clean.photo_group_id({"image_id": "taco_345", "source_ref": "taco:12:345"}) == "taco_img_12"
    assert clean.photo_group_id({"image_id": "team_rj_007", "source_ref": "rj"}) == "team_rj_007"
    assert clean.photo_group_id({"image_id": "x", "source_ref": "taco:9:1", "group_id": "custom"}) == "custom"


def test_run_cleaning_groups_crops_by_source_photo(tmp_path):
    # images.csv has no group_id column (ingest.py doesn't write one), so crops from the
    # same TACO photo must still share a group via source_ref, or splits leak by photo.
    raw = tmp_path / "raw"
    raw.mkdir()
    rng = np.random.default_rng(0)
    rows = []
    for crop_id, photo in [("taco_1", 7), ("taco_2", 7), ("taco_3", 8)]:
        Image.fromarray(rng.integers(0, 255, (160, 160, 3), dtype=np.uint8)).save(raw / f"{crop_id}.jpg")
        rows.append({"image_id": crop_id, "raw_path": str(raw / f"{crop_id}.jpg"), "source": "taco",
                     "source_ref": f"taco:{photo}:{crop_id[5:]}", "label": "trash"})
    images_csv = tmp_path / "images.csv"
    pd.DataFrame(rows).to_csv(images_csv, index=False)

    df = clean.run_cleaning(images_csv=images_csv, reviews_csv=tmp_path / "none.csv",
                            output_clean_csv=tmp_path / "clean.csv", processed_dir=tmp_path / "proc")
    groups = dict(zip(df["image_id"], df["group_id"]))
    assert groups["taco_1"] == groups["taco_2"] == "taco_img_7"
    assert groups["taco_3"] == "taco_img_8"


def test_near_duplicate_merge_keeps_photo_groups_whole():
    # a1 and a2 come from photo A; b1 (photo B) is a near-duplicate of a1.
    # All three must end up in one group, or a2 could land in a different split from a1.
    gray = Image.new("RGB", (150, 150), color=(128, 128, 128))
    gray2 = Image.new("RGB", (150, 150), color=(129, 128, 128))
    noise = Image.fromarray(np.random.default_rng(1).integers(0, 255, (150, 150, 3), dtype=np.uint8))
    records = [
        {"image_id": "b1", "group_id": "B", "phash": clean.compute_image_phash(gray2), "usable": True},
        {"image_id": "a1", "group_id": "A", "phash": clean.compute_image_phash(gray), "usable": True},
        {"image_id": "a2", "group_id": "A", "phash": clean.compute_image_phash(noise), "usable": True},
    ]
    clustered = clean.cluster_near_duplicates(records, max_distance=6)
    assert len({r["group_id"] for r in clustered}) == 1
