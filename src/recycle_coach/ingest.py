"""TACO download, screening, and single-item crops; builds the images.csv inventory.

Owner: John Sampson · Build plan: 1.3 · Spec: docs/PROJECT_SPEC.md §5, §8.1
Reads: TACO annotations (COCO JSON) and images, the TACO mapping in docs/LABEL_GUIDE.md §3
Writes: data/raw/taco/, rows in data/metadata/images.csv
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from PIL import Image, ImageOps

from recycle_coach import config

logger = logging.getLogger(__name__)

TACO_ANNOTATIONS_URL = (
    "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
)

# 41 TACO categories mapped to 3 project labels (EPA guidance compliant)
TACO_LABEL_MAP: Dict[str, str] = {
    # recycling
    "Clear plastic bottle": "recycling",
    "Other plastic bottle": "recycling",
    "Glass bottle": "recycling",
    "Glass jar": "recycling",
    "Drink can": "recycling",
    "Food Can": "recycling",
    "Metal lid": "recycling",
    "Corrugated carton": "recycling",
    "Other carton": "recycling",
    "Drink carton": "recycling",
    "Egg carton": "recycling",
    "Toilet tube": "recycling",
    "Normal paper": "recycling",
    "Magazine paper": "recycling",
    "Paper bag": "recycling",
    # special_handling
    "Battery": "special_handling",
    "Aerosol": "special_handling",
    "Broken glass": "special_handling",
    "Single-use carrier bag": "special_handling",
    "Polypropylene bag": "special_handling",
    # trash
    "Cigarette": "trash",
    "Plastic film": "trash",
    "Other plastic wrapper": "trash",
    "Crisp packet": "trash",
    "Plastic straw": "trash",
    "Paper straw": "trash",
    "Styrofoam piece": "trash",
    "Foam cup": "trash",
    "Foam food container": "trash",
    "Tissues": "trash",
    "Paper cup": "trash",
    "Disposable plastic cup": "trash",
    "Plastic utensils": "trash",
    "Food waste": "trash",
    "Rope & strings": "trash",
    "Plastic glooves": "trash",
    "Squeezable tube": "trash",
    "Six pack rings": "trash",
    "Garbage bag": "trash",
    "Aluminium blister pack": "trash",
    "Carded blister pack": "trash",
}

IMAGES_CSV_COLUMNS = [
    "image_id",
    "raw_path",
    "source",
    "source_ref",
    "license",
    "item",
    "label",
    "labeler",
    "lighting",
    "background",
    "notes",
]


def download_annotations(
    url: str = TACO_ANNOTATIONS_URL,
    save_path: Optional[Path] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """Download TACO annotations COCO JSON."""
    if save_path and save_path.exists():
        with open(save_path, "r", encoding="utf-8") as f:
            return json.load(f)

    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    return data


def parse_taco_records(
    annotations_data: Dict[str, Any],
    min_side: int = 48,
    cap_per_class: Optional[int] = None,
    seed: int = config.SEED,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Filter and map TACO annotations to project format."""
    cats = {c["id"]: c["name"] for c in annotations_data.get("categories", [])}
    imgs = {i["id"]: i for i in annotations_data.get("images", [])}

    records: List[Dict[str, Any]] = []
    excluded: Dict[str, int] = {}

    for ann in annotations_data.get("annotations", []):
        cat_name = cats.get(ann["category_id"])
        if not cat_name or cat_name not in TACO_LABEL_MAP:
            if cat_name:
                excluded[cat_name] = excluded.get(cat_name, 0) + 1
            continue

        x, y, w, h = ann["bbox"]
        if min(w, h) < min_side:
            continue

        image_info = imgs.get(ann["image_id"])
        if not image_info:
            continue

        crop_id = f"taco_{ann['id']}"
        raw_file = image_info["file_name"].replace("/", "_")
        label = TACO_LABEL_MAP[cat_name]

        records.append(
            {
                "crop_id": crop_id,
                "image_id": crop_id,
                "source": "taco",
                "source_ref": f"taco:{ann['image_id']}:{ann['id']}",
                "group_id": f"taco_img_{ann['image_id']}",
                "taco_category": cat_name,
                "item": cat_name.lower(),
                "label": label,
                "url": image_info.get("flickr_url", ""),
                "raw_file": raw_file,
                "bbox": [x, y, w, h],
                "license": "CC BY 4.0",
                "labeler": "js",
                "lighting": "bright",
                "background": "cluttered",
                "notes": f"TACO category: {cat_name}",
            }
        )

    if cap_per_class and records:
        df = pd.DataFrame(records)
        sampled = []
        for label, group in df.groupby("label"):
            if len(group) > cap_per_class:
                sampled.append(
                    group.sample(cap_per_class, random_state=seed)
                )
            else:
                sampled.append(group)
        df_sampled = pd.concat(sampled).reset_index(drop=True)
        records = df_sampled.to_dict("records")

    return records, excluded


def crop_image_bbox(
    image: Image.Image,
    bbox: List[float],
    pad: float = 0.10,
    expected_size: Optional[Tuple[int, int]] = None,
) -> Image.Image:
    """Crop bounding box with padding, respecting image bounds."""
    im = ImageOps.exif_transpose(image).convert("RGB")
    if expected_size and (im.width, im.height) != expected_size:
        im = image.convert("RGB")

    x, y, w, h = bbox
    px = w * pad
    py = h * pad

    x1 = max(0, int(x - px))
    y1 = max(0, int(y - py))
    x2 = min(im.width, int(x + w + px))
    y2 = min(im.height, int(y + h + py))

    return im.crop((x1, y1, x2, y2))


def scan_team_photos(
    team_dir: Path = config.RAW_DIR / "team",
) -> List[Dict[str, Any]]:
    """Scan local team photos directory for manually added photos."""
    team_records: List[Dict[str, Any]] = []
    if not team_dir.exists():
        return team_records

    for ext in ("*.jpg", "*.jpeg", "*.png"):
        for p in team_dir.rglob(ext):
            parts = p.stem.split("_")
            label = "trash"
            if p.parent.name in config.CLASSES:
                label = p.parent.name
            elif len(parts) >= 3 and parts[1] in config.CLASSES:
                label = parts[1]

            initials = parts[1] if len(parts) >= 2 else "team"
            team_records.append(
                {
                    "crop_id": f"team_{p.stem}",
                    "image_id": f"team_{p.stem}",
                    "raw_path": str(p.relative_to(config.ROOT)),
                    "source": "team",
                    "source_ref": initials,
                    "group_id": f"team_{p.stem}",
                    "license": "team-owned",
                    "item": p.stem,
                    "label": label,
                    "labeler": initials,
                    "lighting": "bright",
                    "background": "plain",
                    "notes": "Team collection photo",
                }
            )

    return team_records


def build_images_manifest(
    records: List[Dict[str, Any]],
    output_csv: Path = config.IMAGES_CSV,
) -> pd.DataFrame:
    """Build and save data/metadata/images.csv."""
    df = pd.DataFrame(records)
    for col in IMAGES_CSV_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[IMAGES_CSV_COLUMNS]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


def ingest_taco_dataset(
    output_raw_dir: Path = config.RAW_DIR / "taco",
    annotations_json_path: Optional[Path] = config.DATA_DIR / "taco_annotations.json",
    cap_per_class: Optional[int] = 450,
    min_side: int = 48,
    max_workers: int = 16,
    output_csv: Path = config.IMAGES_CSV,
) -> pd.DataFrame:
    """Download TACO annotations, fetch photos, cut single-item crops, and write images.csv."""
    logger.info("Downloading TACO annotations...")
    ann = download_annotations(save_path=annotations_json_path)

    records, excluded = parse_taco_records(
        ann,
        min_side=min_side,
        cap_per_class=cap_per_class,
        seed=config.SEED,
    )
    logger.info("Parsed %d usable crops (excluded %d ambiguous items)", len(records), sum(excluded.values()))

    df_records = pd.DataFrame(records)
    if df_records.empty:
        raise ValueError("No TACO records found matching the criteria.")

    output_raw_dir.mkdir(parents=True, exist_ok=True)
    full_photos_dir = output_raw_dir / "full_photos"
    full_photos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Download unique full photos
    unique_photos = df_records.drop_duplicates("raw_file").to_dict("records")
    logger.info("Downloading %d unique full photos...", len(unique_photos))

    def _fetch_photo(row: Dict[str, Any]) -> bool:
        dest = full_photos_dir / row["raw_file"]
        if dest.exists() and dest.stat().st_size > 1000:
            return True
        for _ in range(3):
            try:
                resp = requests.get(row["url"], timeout=30)
                if resp.ok and len(resp.content) > 1000:
                    dest.write_bytes(resp.content)
                    return True
            except requests.RequestException:
                time.sleep(1)
        return False

    with ThreadPoolExecutor(max_workers) as executor:
        results = list(executor.map(_fetch_photo, unique_photos))
    logger.info("Successfully downloaded %d/%d photos", sum(results), len(unique_photos))

    # 2. Extract crops
    crops_dir = output_raw_dir / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    imgs_by_file = {i["file_name"].replace("/", "_"): i for i in ann.get("images", [])}

    valid_records = []
    for rec in records:
        raw_photo_path = full_photos_dir / rec["raw_file"]
        if not raw_photo_path.exists():
            continue

        crop_dest = crops_dir / f"{rec['crop_id']}.jpg"
        if not crop_dest.exists():
            try:
                with Image.open(raw_photo_path) as im:
                    exp_size = None
                    file_info = imgs_by_file.get(rec["raw_file"])
                    if file_info:
                        exp_size = (file_info["width"], file_info["height"])
                    cropped = crop_image_bbox(im, rec["bbox"], pad=0.10, expected_size=exp_size)
                    cropped.thumbnail((512, 512))
                    cropped.save(crop_dest, "JPEG", quality=92)
            except Exception as e:
                logger.warning("Failed to crop %s: %s", rec["crop_id"], e)
                continue

        rec_copy = dict(rec)
        try:
            rec_copy["raw_path"] = str(crop_dest.relative_to(config.ROOT))
        except ValueError:
            rec_copy["raw_path"] = str(crop_dest)
        valid_records.append(rec_copy)

    # 3. Add team photos if present
    team_records = scan_team_photos()
    valid_records.extend(team_records)

    # 4. Save images.csv
    df_manifest = build_images_manifest(valid_records, output_csv=output_csv)
    logger.info("Saved %d items to %s", len(df_manifest), output_csv)
    return df_manifest
