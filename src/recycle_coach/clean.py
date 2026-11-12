"""Cleaning: unreadable and duplicate checks, near-duplicate groups, final labels, EXIF strip, resize.

Owner: Rickey Johnson · Build plan: 2.3 · Spec: docs/PROJECT_SPEC.md §6, §8.3
Reads: data/metadata/images.csv, data/metadata/reviews.csv, data/raw/
Writes: data/processed/<image_id>.jpg, data/metadata/clean.csv
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import imagehash
except ImportError:
    imagehash = None
import pandas as pd
from PIL import Image, ImageOps

from recycle_coach import config

logger = logging.getLogger(__name__)

CLEAN_CSV_COLUMNS = [
    "image_id",
    "processed_path",
    "final_label",
    "sha256",
    "phash",
    "group_id",
    "width",
    "height",
    "usable",
    "exclusion_reason",
]


def compute_image_sha256(im: Image.Image) -> str:
    """Compute SHA-256 hash of RGB pixel bytes."""
    return hashlib.sha256(im.tobytes()).hexdigest()


def compute_image_phash(im: Image.Image) -> str:
    """Compute perceptual hash using imagehash.phash."""
    if imagehash is None:
        raise ImportError(
            "The 'imagehash' package is required for perceptual hashing. "
            "Please install it with: pip install imagehash"
        )
    return str(imagehash.phash(im))


def resolve_label(
    first_label: str,
    image_id: str,
    reviews_df: Optional[pd.DataFrame] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Determine final label using first label and reviews.csv.

    Returns:
        (final_label, exclusion_reason)
    """
    if not first_label or str(first_label).strip() == "" or first_label == "exclude":
        return None, "unlabeled_or_excluded"

    first_label = str(first_label).strip().lower()
    if first_label not in config.CLASSES:
        return None, f"invalid_class_{first_label}"

    if reviews_df is not None and not reviews_df.empty and "image_id" in reviews_df.columns:
        matching = reviews_df[reviews_df["image_id"] == image_id]
        if not matching.empty:
            rev_row = matching.iloc[0]
            review_label = str(rev_row.get("review_label", "")).strip().lower()
            resolution_label = str(rev_row.get("resolution_label", "")).strip().lower()

            if review_label and review_label != first_label:
                if resolution_label in config.CLASSES:
                    return resolution_label, None
                elif resolution_label == "exclude":
                    return None, "resolved_to_exclude"
                else:
                    return None, "unresolved_disagreement"

    return first_label, None


def resize_image_long_side(
    im: Image.Image,
    target_long_side: int = config.PROCESSED_LONG_SIDE,
) -> Image.Image:
    """Resize image so its longest side equals target_long_side while keeping aspect ratio."""
    w, h = im.size
    long_side = max(w, h)
    if long_side <= target_long_side:
        return im

    scale = target_long_side / float(long_side)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return im.resize((new_w, new_h), Image.Resampling.LANCZOS)


def clean_image(
    raw_path: Path,
    image_id: str,
    first_label: str,
    processed_dir: Path = config.PROCESSED_DIR,
    min_short_side: int = config.MIN_SHORT_SIDE,
    target_long_side: int = config.PROCESSED_LONG_SIDE,
    jpeg_quality: int = config.PROCESSED_JPEG_QUALITY,
    reviews_df: Optional[pd.DataFrame] = None,
    save_processed: bool = True,
) -> Dict[str, any]:
    """Inspect, validate, hash, resize, and save a single image."""
    result = {
        "image_id": image_id,
        "processed_path": "",
        "final_label": "",
        "sha256": "",
        "phash": "",
        "group_id": image_id,
        "width": 0,
        "height": 0,
        "usable": False,
        "exclusion_reason": "",
    }

    if not raw_path.exists():
        result["exclusion_reason"] = "file_not_found"
        return result

    try:
        with Image.open(raw_path) as raw_img:
            im = ImageOps.exif_transpose(raw_img).convert("RGB")
    except Exception as e:
        result["exclusion_reason"] = f"unreadable_{type(e).__name__}"
        return result

    w, h = im.size
    result["width"] = w
    result["height"] = h

    if min(w, h) < min_short_side:
        result["exclusion_reason"] = f"too_small_{min(w, h)}px"
        return result

    final_label, label_exclusion = resolve_label(first_label, image_id, reviews_df)
    if label_exclusion:
        result["exclusion_reason"] = label_exclusion
        return result

    result["final_label"] = final_label
    result["sha256"] = compute_image_sha256(im)
    result["phash"] = compute_image_phash(im)
    result["usable"] = True

    if save_processed:
        processed_dir.mkdir(parents=True, exist_ok=True)
        dest_path = processed_dir / f"{image_id}.jpg"
        resized_im = resize_image_long_side(im, target_long_side=target_long_side)
        resized_im.save(dest_path, "JPEG", quality=jpeg_quality)
        try:
            result["processed_path"] = str(dest_path.relative_to(config.ROOT))
        except ValueError:
            result["processed_path"] = str(dest_path)

    return result


def cluster_near_duplicates(
    records: List[Dict[str, any]],
    max_distance: int = config.PHASH_MAX_DISTANCE,
) -> List[Dict[str, any]]:
    """Group near-duplicates having pHash Hamming distance <= max_distance into shared group_id."""
    if imagehash is None:
        raise ImportError(
            "The 'imagehash' package is required for near-duplicate grouping. "
            "Please install it with: pip install imagehash"
        )
    hashes = []
    for r in records:
        ph = r.get("phash")
        if ph:
            hashes.append(imagehash.hex_to_hash(ph))
        else:
            hashes.append(None)

    n = len(records)
    parent = list(range(n))

    def find(i: int) -> int:
        path = []
        while parent[i] != i:
            path.append(i)
            i = parent[i]
        for node in path:
            parent[node] = i
        return i

    def union(i: int, j: int) -> None:
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_j] = root_i

    for i in range(n):
        if not records[i].get("usable") or hashes[i] is None:
            continue
        for j in range(i + 1, n):
            if not records[j].get("usable") or hashes[j] is None:
                continue
            dist = hashes[i] - hashes[j]
            if dist <= max_distance:
                union(i, j)

    groups: Dict[int, str] = {}
    for i in range(n):
        root = find(i)
        if root not in groups:
            groups[root] = records[root]["group_id"]
        records[i]["group_id"] = groups[root]

    return records


def run_cleaning(
    images_csv: Path = config.IMAGES_CSV,
    reviews_csv: Path = config.REVIEWS_CSV,
    output_clean_csv: Path = config.CLEAN_CSV,
    processed_dir: Path = config.PROCESSED_DIR,
    max_phash_distance: int = config.PHASH_MAX_DISTANCE,
    min_short_side: int = config.MIN_SHORT_SIDE,
) -> pd.DataFrame:
    """Run full cleaning pipeline on images.csv and write clean.csv."""
    if not images_csv.exists():
        raise FileNotFoundError(f"Missing images inventory: {images_csv}")

    df_images = pd.read_csv(images_csv)
    df_reviews = pd.read_csv(reviews_csv) if reviews_csv.exists() else None

    records = []
    seen_sha: Dict[str, str] = {}

    for _, row in df_images.iterrows():
        image_id = str(row["image_id"])
        p = Path(str(row["raw_path"]))
        raw_path = p if p.is_absolute() else config.ROOT / p
        first_label = str(row.get("label", ""))

        clean_rec = clean_image(
            raw_path=raw_path,
            image_id=image_id,
            first_label=first_label,
            processed_dir=processed_dir,
            min_short_side=min_short_side,
            reviews_df=df_reviews,
        )

        if "group_id" in row and pd.notna(row["group_id"]) and str(row["group_id"]).strip():
            clean_rec["group_id"] = str(row["group_id"])

        if clean_rec["usable"]:
            sha = clean_rec["sha256"]
            if sha in seen_sha:
                clean_rec["usable"] = False
                clean_rec["exclusion_reason"] = f"exact_duplicate_of_{seen_sha[sha]}"
            else:
                seen_sha[sha] = image_id

        records.append(clean_rec)

    records = cluster_near_duplicates(records, max_distance=max_phash_distance)

    df_clean = pd.DataFrame(records)[CLEAN_CSV_COLUMNS]
    output_clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_clean_csv, index=False)
    return df_clean
