# Data Card: Smart Recycling Coach Dataset

**Owner:** Premajyoti · **Status:** Skeleton. Fill in during milestone 2 (draft) and milestone 5 (final). Counts must match `data/metadata/clean.csv` and `splits.csv`.

## 1. Summary

- **Purpose:** train and evaluate a three-class disposal classifier (recycling, special handling, trash) from photos of single items.
- **Size:** TBD usable images (target 900–1,200).
- **Format:** RGB JPG; long side 512 px after processing; one item per image.
- **Where it lives:** images in the team Google Drive folder `SmartRecyclingCoach-data/`; metadata in `data/metadata/` in this repo.

## 2. Sources

See [`SOURCE_LOG.md`](SOURCE_LOG.md) for URLs, licenses, and attribution.

| Source | Images (usable) | Share |
|---|---|---|
| TACO | TBD | TBD |
| Team photos | TBD | TBD |

## 3. Collection

- **TACO:** TBD (how images were screened or cropped; Q1 in `PROJECT_SPEC.md` §15).
- **Team photos:** five members, about 25 each, following `PROJECT_SPEC.md` §5.1. EXIF stripped; no people or personal information.

## 4. Labeling

- Guide: [`LABEL_GUIDE.md`](LABEL_GUIDE.md).
- Process: first label → blind second label → disagreements resolved against the guide (`PROJECT_SPEC.md` §5.3).
- Agreement rate between first and second labels: TBD.
- Images excluded for unresolved labels: TBD.

## 5. Cleaning

| Step | Images removed |
|---|---|
| Unreadable or too small | TBD |
| Exact duplicates | TBD |
| Label problems | TBD |
| Near-duplicate groups (kept, same split) | TBD groups |

## 6. Composition

| Class | Total | TACO | Team | Bright | Dim | Glare |
|---|---|---|---|---|---|---|
| recycling | | | | | | |
| special_handling | | | | | | |
| trash | | | | | | |
| **Total** | | | | | | |

## 7. Splits

Stratified, group-aware 70 / 15 / 15 with seed 365 (`PROJECT_SPEC.md` §7).

| Class | Train | Val | Test |
|---|---|---|---|
| recycling | | | |
| special_handling | | | |
| trash | | | |
| **Total** | | | |

## 8. Known limitations and biases

- TBD. For example: TACO is mostly outdoor litter while team photos are clean items indoors; certain items are over-represented; lighting imbalance.

## 9. Ethics and licenses

- No faces, people, personal records, or restricted locations. EXIF removed.
- TACO used under its stated license, with attribution (see the source log).
- Labels reflect general guidance; local rules vary.

## 10. Versions

| Date | Change | Who |
|---|---|---|
| 2026-09-29 | Skeleton created | Rickey |
