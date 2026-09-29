# Project Spec: Smart Recycling Coach

The rules, numbers, and file formats for the whole project. The pitch ([`reference/PITCH.md`](reference/PITCH.md)) says *what* we promised; this file says *exactly how*. Values marked **(default)** are starting points the owner can change. If you change one, update it here and in `src/recycle_coach/config.py` in the same commit, and note it in the `PROGRESS.md` log.

---

## 1. Overview

- **User:** students and campus facilities staff.
- **Problem:** people aren't sure whether an item goes in recycling, trash, or special handling, and guidance isn't consistent.
- **What we build:** a three-class image classifier (fine-tuned MobileNetV3) plus a Streamlit app. The user uploads or takes a photo of one item and gets a disposal suggestion, a confidence, and a short guidance note.
- **What we prove:** on held-out test images, the model beats a majority-class baseline and reaches macro F1 ≥ 0.70. The demo answers correctly for at least 9 of 10 new photos taken after training.

## 2. Scope

**In:** the dataset and its documentation (label guide, data card, source log), cleaning and split scripts, the baseline, the MobileNetV3 training notebook and final checkpoint, evaluation outputs (metrics, confusion matrix, error analysis), the Streamlit demo, and presentation materials.

**Out:** object detection or multiple items per photo, location-specific rules, hazardous-waste decisions, mobile apps, user accounts, and deploying beyond a simple demo.

**Fallback (from the pitch):** if one class stays too small or inconsistent, use a clean TACO-only three-class subset and still deliver the data card, baseline, trained model or error analysis, and a static prediction demo (a page of saved predictions instead of live upload).

## 3. Classes

| Index | Label (code) | Label (display) | Examples (full rules in [`LABEL_GUIDE.md`](LABEL_GUIDE.md)) |
|---|---|---|---|
| 0 | `recycling` | Recycling | Clean plastic bottles, aluminum cans, glass bottles and jars, clean paper and cardboard |
| 1 | `special_handling` | Special handling | Batteries, small electronics, light bulbs, plastic bags and film, other items that need a drop-off |
| 2 | `trash` | Trash | Food-soiled paper, chip bags and wrappers, styrofoam, mixed-material items |

- Code always uses the lowercase labels and this index order (alphabetical). Import them from `recycle_coach.config.CLASSES`.
- The label guide is the authority on edge cases. Base it on the EPA guidance: https://www.epa.gov/recycle/how-do-i-recycle-common-recyclables
- Special handling means "don't put this in either bin; take it to a drop-off or ask facilities." The app never tells anyone how to dispose of hazardous waste.

## 4. Data sources and storage

| Source | What we take | Owner | Target count |
|---|---|---|---|
| **TACO** (https://github.com/pedropro/TACO) | Images whose items map clearly to one of the three labels (see §5.2) | John | ~800–1,000 screened |
| **Team photos** | About 25 photos of clean, common items per member (5 × 25 ≈ 125) | John coordinates, everyone shoots | ~125 |
| **EPA guidance** | Label rules only, no images | John | — |

**Target:** 900–1,200 usable images, **at least 300 per class** (default), and no class above 40% of the total.

**Storage (default, see §15):** images live in a shared team Google Drive folder, `SmartRecyclingCoach-data/`, with `raw/` and `processed/` inside. Each person syncs it into their local `data/raw/` and `data/processed/`, which git ignores. Colab mounts the same folder. Only the CSVs in `data/metadata/` go in git.

## 5. Collecting images

### 5.1 Team photos

- **One item per photo**, centered, filling most of the frame. The item is clean (rinsed, empty).
- Mix it up across your 25: at least two backgrounds (a plain surface and a busy one), and at least two lighting conditions (bright, dim, or glare).
- Cover all three classes, with at least 5 photos per class per person (default).
- **No faces, hands with rings or tattoos, people, screens showing personal info, mail with names, or restricted places.**
- Strip EXIF before uploading (phones store GPS location). The cleaning script also re-saves images without EXIF.
- Filename: `team_<initials>_<NNN>.jpg`, for example `team_rj_007.jpg`. Initials: `dl`, `rj`, `js`, `ao`, `pg`.

### 5.2 TACO

- TACO images show litter in real scenes and come with COCO-format annotations (bounding boxes and a category per object).
- Map every TACO category to one of our three labels or to `exclude`, in a table in `LABEL_GUIDE.md` §3.
- **Unit is one item per image.** Two ways to get there (decide in §15, Q1): keep only images with one clearly dominant annotated object, or crop each annotation's bounding box (with some padding) into its own image.
- Keep TACO's license and attribution; record them in `SOURCE_LOG.md`.
- `image_id` format: `taco_<taco image id>` (or `taco_<image id>_<annotation id>` for crops).

### 5.3 Labeling and review

1. **First label:** John and Amaka label with `LABEL_GUIDE.md`, filling `images.csv`.
2. **Second label:** a different person labels each image without seeing the first label, filling `reviews.csv` (default: every image).
3. **Disagreements:** Premajyoti collects them and the team resolves each one against the label guide. Record the result in `reviews.csv` (`resolution_label`). If the guide didn't cover the case, update the guide.
4. **Final label** = the first label when both labels agree, otherwise `resolution_label`. Images still unresolved are excluded.

## 6. Cleaning (Rickey)

Run in this order and write the result to `data/metadata/clean.csv`:

1. **Unreadable:** can't be opened by Pillow, or smaller than 128 px on the short side → exclude.
2. **Convert:** to RGB, fix EXIF rotation, then drop all EXIF.
3. **Exact duplicates:** same SHA-256 of the pixels → keep one.
4. **Near-duplicates:** perceptual hash (`imagehash.phash`) with a Hamming distance ≤ **6** (default) → same `group_id`. They stay in the dataset but always go to the same split.
5. **Label problems:** missing, unresolved, or conflicting labels → exclude.
6. **Resize:** save to `data/processed/<image_id>.jpg` with the long side at **512 px** (default), JPEG quality 90. The model resizes to 224 at load time.
7. **Spot check:** look at **20 random images per class** (default) and log problems in `PROGRESS.md`.

## 7. Splits (Rickey)

- **70 / 15 / 15** train / val / test, stratified by final label, **seed 365**.
- Split by `group_id` (group-aware), so near-duplicates never cross splits. Class proportions in each split should be within about 2 percentage points of the whole dataset.
- Write `data/metadata/splits.csv` (§8.4). Once published, **don't regenerate it** unless the team agrees (for example, after label revisions in milestone 4), and log it when you do.
- **The test split is locked** until the held-out evaluation. Nobody looks at its predictions before then.

## 8. File formats

These are the hand-off points between people. Keep columns and names exactly as listed. All paths are relative to the repo root.

### 8.1 `data/metadata/images.csv` (John)

| Column | Example | Notes |
|---|---|---|
| `image_id` | `team_rj_007` | Unique. Also the processed filename. |
| `raw_path` | `data/raw/team/team_rj_007.jpg` | |
| `source` | `team` | `taco` or `team` |
| `source_ref` | `rj` / `taco:1234:5678` | Photographer initials, or TACO image and annotation IDs |
| `license` | `CC BY 4.0` | As stated by the source |
| `item` | `aluminum can` | Short description |
| `label` | `recycling` | First label |
| `labeler` | `js` | Initials |
| `lighting` | `bright` | `bright`, `dim`, or `glare` |
| `background` | `plain` | `plain` or `cluttered` |
| `notes` | | Optional |

### 8.2 `data/metadata/reviews.csv` (Premajyoti)

`image_id, reviewer, review_label, resolution_label, notes`. Leave `resolution_label` empty when the two labels agree.

### 8.3 `data/metadata/clean.csv` (Rickey, generated)

`image_id, processed_path, final_label, sha256, phash, group_id, width, height, usable, exclusion_reason`. `usable` is `true` or `false`.

### 8.4 `data/metadata/splits.csv` (Rickey, generated)

`image_id, group_id, final_label, split`. `split` is `train`, `val`, or `test`. Usable images only.

### 8.5 Predictions: `results/predictions/<model>_<split>.csv`

`image_id, split, true_label, pred_label, confidence, p_recycling, p_special_handling, p_trash`. `<model>` is `baseline` or `mobilenetv3`. `confidence` is the top probability.

### 8.6 Metrics: `results/metrics/<model>_<split>.json`

```json
{
  "model": "mobilenetv3",
  "split": "val",
  "n": 180,
  "classes": ["recycling", "special_handling", "trash"],
  "accuracy": 0.0,
  "macro_f1": 0.0,
  "per_class": {"recycling": {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0}},
  "confusion_matrix": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
  "created": "2026-10-25"
}
```

The confusion matrix has rows = true labels and columns = predicted, in class order. Figures go in `results/figures/confusion_<model>_<split>.png`.

### 8.7 Error table: `results/errors/<model>_<split>_errors.csv` (Rickey)

The wrong rows from §8.5, joined with `item`, `source`, `lighting`, and `background` from `images.csv`. Premajyoti summarizes patterns from it.

### 8.8 Checkpoint: `models/mobilenetv3_best.pt` (Dakarai)

Saved with `torch.save` as a dict: `arch` (for example `mobilenet_v3_large`), `classes`, `img_size`, `mean`, `std`, `state_dict`, `val_macro_f1`, `split_seed`, `trained_at`. Only the final checkpoint is committed (it's small, about 10–20 MB). Experiment checkpoints stay local or on Drive.

### 8.9 Prediction API: `recycle_coach.predict` (Dakarai; used by Amaka)

The app only talks to the model through this:

```python
predictor = load_predictor("models/mobilenetv3_best.pt")
result = predictor.predict(pil_image)
# result == {"label": "recycling", "confidence": 0.91,
#            "probs": {"recycling": 0.91, "special_handling": 0.04, "trash": 0.05}}
```

Amaka can build the app against a fake predictor with the same shape before the real model exists.

## 9. Baseline (Rickey)

- **Majority class:** find the most common label in the **train** split and predict it for every image.
- Report it on val (milestone 2) and on test (milestone 4), with the same metrics and file formats as the model.
- Its confidence is that class's share of the train split.

## 10. Model and training (Dakarai)

| Setting | Value |
|---|---|
| Architecture | torchvision MobileNetV3 with ImageNet weights; replace the last classifier layer with 3 outputs. Small vs Large: §15, Q2 (default Large) |
| Input | 224 × 224 RGB, ImageNet mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]` |
| Train augmentation | Random resized crop (scale 0.7–1.0), horizontal flip, color jitter (brightness and contrast 0.2), rotation ±15° (defaults) |
| Val and test transforms | Resize 256 → center crop 224. No augmentation. |
| Loss | Cross-entropy; use class weights if the train split is imbalanced |
| Optimizer | AdamW. Stage 1: train the head only, lr 1e-3, 3 epochs. Stage 2: unfreeze all, lr 1e-4, up to 20 epochs (defaults) |
| Batch size | 32 (default) |
| Model selection | Best **val macro F1**; early stopping with patience 5 |
| Reproducibility | Seed 365 for Python, NumPy, and torch; log the device and library versions in the notebook |
| Device | CUDA, then MPS (Apple Silicon), then CPU, chosen automatically |

The notebook (`notebooks/01_train_mobilenetv3.ipynb`) must run top to bottom on a fresh Colab session and on a laptop, with the logic imported from `src/recycle_coach/`.

## 11. Evaluation

- **Metrics:** accuracy, macro F1, per-class recall, and the confusion matrix (scikit-learn).
- **Validation (milestone 3):** used for tuning and choosing the checkpoint.
- **Held-out test (milestone 4):** run **once**, for both the baseline and the chosen model. If labels or settings are revised afterward, report the first test result too, and say what changed.
- **Success:** test macro F1 ≥ **0.70**, and higher than the baseline on macro F1.
- **Error analysis:** errors by class, by lighting (`bright`, `dim`, `glare`), by background, and by source (TACO vs team). List the most-confused class pair and 5–10 example mistakes with a likely reason.

## 12. Demo app (Amaka)

**Flow:** open app → upload a photo (or use the camera) → see the photo, the predicted label, the confidence, and a guidance card → option to try another.

- **Guidance cards:** one short card per class, written from `LABEL_GUIDE.md`. The special-handling card says to check with campus facilities and never gives hazardous-waste instructions.
- **Low confidence:** if the confidence is below **0.60** (default; tune on val), show "Not sure. Check the label guide or ask facilities" alongside the top two guesses.
- **Always visible:** a note that rules vary by location and the app gives general guidance, not campus policy.
- **Demo test:** after training, the team takes **10 new photos** that aren't in the dataset (at least 3 per class). Log each one in `results/demo_test.csv` (`photo, true_label, shown_label, confidence, correct, notes`). **Pass = at least 9 correct** (definition in §15, Q4).
- **Fallback:** a static page of saved predictions with images, if the live model can't run.

## 13. Ethics and limits

- No identifiable people or personal information in any image; EXIF stripped.
- Respect source licenses; attribute TACO.
- Rules vary by location, and the app says so.
- No hazardous-waste decisions.
- Report where the model fails (class, lighting, source), not just the headline score.

## 14. Key numbers

| What | Value | Where it's used |
|---|---|---|
| Classes | `recycling`, `special_handling`, `trash` | Everywhere (`config.CLASSES`) |
| Dataset size | 900–1,200 usable, ≥ 300 per class, no class > 40% | §4 |
| Photos per member | ~25, ≥ 5 per class | §5.1 |
| Min image size | 128 px short side | §6 |
| Near-duplicate threshold | pHash Hamming ≤ 6 | §6 |
| Processed long side | 512 px, JPEG 90 | §6 |
| Split | 70 / 15 / 15, seed 365, group-aware | §7 |
| Model input | 224 × 224, ImageNet normalization | §10 |
| Batch size, lr | 32; 1e-3 head, 1e-4 full | §10 |
| Early stopping | patience 5 on val macro F1 | §10 |
| Success | test macro F1 ≥ 0.70 and > baseline | §11 |
| Low-confidence threshold | 0.60 | §12 |
| Demo test | ≥ 9 of 10 new photos | §12 |

## 15. Open questions

Settle these at the next team meeting, then replace the question with the answer here.

| # | Question | Default until decided | Who decides |
|---|---|---|---|
| Q1 | TACO: keep single-object images only, or crop every bounding box? | Crop boxes with 10% padding, skip crops under 128 px | John |
| Q2 | MobileNetV3 Small or Large? | Large | Dakarai |
| Q3 | Where do images live? | Shared Google Drive folder (§4) | Team |
| Q4 | What counts as a "correct response" in the demo test? | Right label and guidance card, no errors | Amaka |
| Q5 | Is every image second-reviewed, or a sample? | Every image | Premajyoti |
| Q6 | Where does training run? | Colab GPU; laptop for quick checks | Dakarai |
