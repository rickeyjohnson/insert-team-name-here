# Data Card: Smart Recycling Coach Dataset

**Owner:** Premajyoti Gammon · **Status:** Checkpoint 3 (updated 2026-11-22). Counts match `data/metadata/clean.csv` and `data/metadata/splits.csv`, the data behind the Checkpoint 3 results.

## 1. Summary

- **Purpose:** Train and evaluate a three-class disposal classifier (recycling, special handling, trash) from single-item waste photos.
- **Size:** 815 usable crops from 589 TACO source photos, after 215 of 1,030 screened crops were dropped for a short side under 128 px. Full collection target: 900–1,200 usable images including team photos.
- **Format:** RGB JPG; long side 512 px after processing; one item per image.
- **Storage:** Raw and processed images in shared team Google Drive folder `SmartRecyclingCoach-data/`; metadata CSVs in `data/metadata/` in git.

## 2. Sources

See [`SOURCE_LOG.md`](SOURCE_LOG.md) for URLs, licenses, and attribution.

| Source | Images (usable) | Share |
|---|---|---|
| TACO (Trash Annotations in Context) | 815 crops (from 589 photos) | 100% (Checkpoint 3) |
| Team photos | ~125 photos target | Phase 2–3 collection |

## 3. Collection

- **TACO:** 1,500 photos and 4,784 boxed annotations screened using `LABEL_MAP`. Bounding boxes cropped with 10% outer padding (`pad=0.10`). Bounding boxes smaller than 48 px skipped at crop time. Recycling and trash capped at 450 crops each before cleaning. 1,030 crops went into cleaning.
- **Team photos:** Five members shooting ~25 photos each following `PROJECT_SPEC.md` §5.1. Clean, centered, single items; EXIF stripped; no faces, tattoos, or personal data.

## 4. Labeling

- **Guide:** [`LABEL_GUIDE.md`](LABEL_GUIDE.md).
- **Process:** First label from TACO category mapping / initial screening $\rightarrow$ blind second label in `reviews.csv` $\rightarrow$ team resolution for disagreements.
- **Categories:** 41 TACO categories mapped to project labels; 19 ambiguous categories excluded.

## 5. Cleaning

| Step | Rule & Description |
|---|---|
| Unreadable / Too small | Exclude images corrupt or short side < 128 px (`MIN_SHORT_SIDE`); this removed 215 of 1,030 crops |
| Orientation & EXIF | EXIF transposed to standard orientation; all EXIF metadata stripped |
| Exact duplicates | Deduplicated via pixel SHA-256 hash |
| Near-duplicates | Clustered via perceptual hash (`imagehash.phash`, Hamming distance $\le 6$) into shared `group_id` |
| Resizing | Resized to long side 512 px, JPEG quality 90 |

## 6. Composition (usable dataset, Checkpoint 3)

| Class | Total Crops | Share | Breakdown / Subcategories |
|---|---|---|---|
| `recycling` | 392 | 48.1% | 115 plastic bottles, 89 drink cans, 44 glass bottles/jars, 84 cartons, 43 paper, 17 food cans/lids |
| `special_handling` | 89 | 10.9% | 59 plastic bags, 20 broken glass, 8 aerosols, 2 batteries |
| `trash` | 334 | 41.0% | 127 plastic film, 77 wrappers and packets, 35 cups, 26 foam, 23 straws, 46 other |
| **Total** | **815** | **100%** | **589 unique source photos** |

## 7. Splits

Stratified, group-aware 70 / 15 / 15 with seed 365 (`PROJECT_SPEC.md` §7, `splits.py`). Every crop from the same source photo, and every near-duplicate, shares a `group_id` and stays in one split, so no photo appears in both train and test.

| Class | Train (70%) | Val (15%) | Test (15%) | Total |
|---|---|---|---|---|
| `recycling` | 274 | 59 | 59 | 392 |
| `special_handling` | 56 | 15 | 18 | 89 |
| `trash` | 234 | 50 | 50 | 334 |
| **Total** | **564** | **124** | **127** | **815** |

## 8. Limitations & Known Bias

- Outdoor litter in TACO is weathered, sun-bleached, or partially crushed compared to indoor clean campus items.
- Special handling is small (89 crops) and dominated by plastic bags; batteries (2) and aerosols (8) need team photos.
- Because splits are grouped by photo, one photo can dominate a split: 9 of the 18 special-handling test crops come from a single broken-glass photo.
- Plastic film (trash) and plastic bags (special handling) look alike; all 7 trash crops the CP3 model called special handling were plastic film.
- Campus single-stream rules may vary from municipality to municipality.
