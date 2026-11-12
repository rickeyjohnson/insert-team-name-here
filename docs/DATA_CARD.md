# Data Card: Smart Recycling Coach Dataset

**Owner:** Premajyoti Gammon · **Status:** Checkpoint 1 Draft (Updated). Counts match `split_manifest.csv` and Checkpoint 1 report.

## 1. Summary

- **Purpose:** Train and evaluate a three-class disposal classifier (recycling, special handling, trash) from single-item waste photos.
- **Size:** 1,030 crops from 662 photos (capped dataset for Checkpoint 1). Full collection target: 900–1,200 usable images including team photos.
- **Format:** RGB JPG; long side 512 px after processing; one item per image.
- **Storage:** Raw and processed images in shared team Google Drive folder `SmartRecyclingCoach-data/`; metadata CSVs in `data/metadata/` in git.

## 2. Sources

See [`SOURCE_LOG.md`](SOURCE_LOG.md) for URLs, licenses, and attribution.

| Source | Images (usable) | Share |
|---|---|---|
| TACO (Trash Annotations in Context) | 1,030 crops (from 662 photos) | 100% (Checkpoint 1) |
| Team photos | ~125 photos target | Phase 2–3 collection |

## 3. Collection

- **TACO:** 1,500 photos and 4,784 boxed annotations screened using `LABEL_MAP`. Bounding boxes cropped with 10% outer padding (`pad=0.10`). Bounding boxes smaller than 48 px excluded. Classes capped at 450 for recycling and trash to control class imbalance.
- **Team photos:** Five members shooting ~25 photos each following `PROJECT_SPEC.md` §5.1. Clean, centered, single items; EXIF stripped; no faces, tattoos, or personal data.

## 4. Labeling

- **Guide:** [`LABEL_GUIDE.md`](LABEL_GUIDE.md).
- **Process:** First label from TACO category mapping / initial screening $\rightarrow$ blind second label in `reviews.csv` $\rightarrow$ team resolution for disagreements.
- **Categories:** 41 TACO categories mapped to project labels; 19 ambiguous categories excluded.

## 5. Cleaning

| Step | Rule & Description |
|---|---|
| Unreadable / Too small | Exclude images corrupt or short side < 128 px |
| Orientation & EXIF | EXIF transposed to standard orientation; all EXIF metadata stripped |
| Exact duplicates | Deduplicated via pixel SHA-256 hash |
| Near-duplicates | Clustered via perceptual hash (`imagehash.phash`, Hamming distance $\le 6$) into shared `group_id` |
| Resizing | Resized to long side 512 px, JPEG quality 90 |

## 6. Composition (Checkpoint 1 Initial Dataset)

| Class | Total Crops | Share | Breakdown / Subcategories |
|---|---|---|---|
| `recycling` | 450 | 43.7% | Plastic bottles, drink cans, food cans, glass bottles/jars, paper cartons |
| `special_handling` | 130 | 12.6% | 63 plastic bags, 55 broken glass, 10 aerosols, 2 batteries |
| `trash` | 450 | 43.7% | Wrappers, film, snack packets, straws, foam containers, plastic cutlery |
| **Total** | **1,030** | **100%** | **662 unique source photos** |

## 7. Splits

Stratified, group-aware 70 / 15 / 15 with seed 365 (`PROJECT_SPEC.md` §7, `splits.py`). Near-duplicates sharing a `group_id` always reside in the same split.

| Class | Train (70%) | Val (15%) | Test (15%) | Total |
|---|---|---|---|---|
| `recycling` | 329 | 60 | 61 | 450 |
| `special_handling` | 91 | 13 | 26 | 130 |
| `trash` | 327 | 61 | 62 | 450 |
| **Total** | **747** | **134** | **149** | **1,030** |

## 8. Limitations & Known Bias

- Outdoor litter in TACO is weathered, sun-bleached, or partially crushed compared to indoor clean campus items.
- Special handling is currently imbalanced (130 samples) and dominated by plastic carrier bags and broken glass; batteries (2) and aerosols (10) need augmentation via team photos.
- Campus single-stream rules may vary from municipality to municipality.
