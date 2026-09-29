# Build Plan

Everything we need to build, in order. Each item has an ID, an owner, what it produces, and how we know it's done. Track status in [`PROGRESS.md`](PROGRESS.md) with the same IDs. Rules and numbers are in [`PROJECT_SPEC.md`](PROJECT_SPEC.md).

## How the pieces connect

```
TACO + team photos
  → images.csv (John: first labels)
  → reviews.csv (Premajyoti: second review, resolved labels)
  → clean.csv + data/processed/ (Rickey: cleaned, deduped, resized)
  → splits.csv (Rickey: 70/15/15, group-aware)
      → baseline (Rickey) ─────────────┐
      → dataset + train → checkpoint ──┤→ predictions + metrics → error tables → error-pattern summary
        (Dakarai)                      │   (Rickey, Dakarai)      (Rickey)        (Premajyoti)
                                       └→ predict API → Streamlit demo (Amaka)
```

**Nobody waits on anyone's real work.** Rickey can write cleaning and split code against a few sample images. Dakarai can train on a small early split. Amaka can build the app with a fake predictor that follows `PROJECT_SPEC.md` §8.9.

## Code modules

| File | Owner | Does | Item |
|---|---|---|---|
| `src/recycle_coach/config.py` | Rickey (setup); changes need the team | Shared constants and paths | 0.1 |
| `src/recycle_coach/ingest.py` | John | TACO screening, crops, and the `images.csv` inventory | 1.3 |
| `src/recycle_coach/clean.py` | Rickey | Unreadable, duplicate, and label checks; resizing; `clean.csv` | 2.3 |
| `src/recycle_coach/splits.py` | Rickey | Group-aware stratified split; `splits.csv` | 2.4 |
| `src/recycle_coach/metrics.py` | Rickey | Metrics JSON, confusion matrix figure, prediction and error tables | 2.5 |
| `src/recycle_coach/baseline.py` | Rickey | Majority-class baseline | 2.6 |
| `src/recycle_coach/dataset.py` | Dakarai | PyTorch `Dataset` and transforms | 3.1 |
| `src/recycle_coach/train.py` | Dakarai | Two-stage fine-tuning, early stopping, checkpoint | 3.2 |
| `src/recycle_coach/predict.py` | Dakarai | `load_predictor()` and `predict()` | 3.4 |
| `notebooks/01_train_mobilenetv3.ipynb` | Dakarai | The reproducible training notebook | 3.3 |
| `app/app.py` | Amaka | The Streamlit demo | 2.8, 4.4 |

---

## Phase 0: Setup (by Thu 10-01)

**0.1 Repo boilerplate and docs.** *Rickey.* Folder structure, `AGENTS.md`, these docs, `config.py`, module stubs, `requirements.txt`, a smoke test.
Done when: merged to `main`, and `pytest` passes on a fresh clone.

**0.2 Everyone's environment works.** *All.* Clone, make a virtual environment, `pip install -r requirements.txt`, run `pytest` and `streamlit run app/app.py`.
Done when: all five members have run both.

**0.3 Shared data folder.** *John.* Create `SmartRecyclingCoach-data/` (with `raw/taco/`, `raw/team/`, `processed/`) on the team Google Drive and share it with everyone.
Done when: everyone can open it.

**0.4 Settle the open questions.** *All; Dakarai runs the meeting.* Decide Q1–Q6 in `PROJECT_SPEC.md` §15 and write the answers there.
Done when: §15 has an answer for each question.

## Phase 1: Data acquisition (Sun 10-04)

Pitch milestone: **source log, draft label guide, and the first 500 screened images.** Owners: John, Amaka, Premajyoti.

**1.1 Label guide draft.** *John; Amaka reviews.* Fill in `docs/LABEL_GUIDE.md`: the rules for each class, examples, edge cases, and the TACO category mapping table (§3).
Done when: every TACO category is mapped to a label or `exclude`, and Amaka has reviewed it.

**1.2 Source log.** *Premajyoti.* Fill in `docs/SOURCE_LOG.md` with TACO (URL, license, attribution), EPA, and team photos.
Done when: every source we use has a row with its license.

**1.3 TACO ingest.** *John.* `ingest.py`: download TACO, apply the category mapping, keep or crop single items (Q1), save to `data/raw/taco/`, and add rows to `images.csv`.
Done when: the script reruns from scratch and produces the same images and rows.

**1.4 Team photos.** *All; John coordinates.* Each member takes about 25 photos following `PROJECT_SPEC.md` §5.1 and uploads them to `raw/team/`.
Done when: about 125 photos are uploaded, EXIF stripped, and each person has at least 5 per class.

**1.5 First labels.** *John, Amaka.* Label screened images in `images.csv`, including the lighting and background columns.
Done when: **at least 500 images** are screened and labeled. ✅ Milestone 1.

## Phase 2: Data preparation and baseline (Sun 10-11)

Pitch milestone: **clean dataset, 70/15/15 split manifest, and majority-class baseline result.** Owners: Rickey, John.

**2.1 Second review.** *Premajyoti coordinates; reviewers label blind.* Fill `reviews.csv`, resolve disagreements against the label guide, and update the guide for new edge cases.
Done when: every image (or the agreed sample, Q5) has a second label, and every disagreement is resolved or marked excluded.

**2.2 Hit the dataset target.** *John.* Top up weak classes (from TACO or more team photos) until there are ≥ 900 usable images and ≥ 300 per class.
Done when: `clean.csv` shows the target counts. If it can't be reached, flag the fallback in `PROGRESS.md`.

**2.3 Cleaning.** *Rickey.* `clean.py` follows `PROJECT_SPEC.md` §6, writes `clean.csv`, and saves `data/processed/`. Includes the 20-per-class spot check.
Done when: tests cover the unreadable, duplicate, and label rules; the script reruns reproducibly; and the processed images are uploaded to Drive.

**2.4 Splits.** *Rickey.* `splits.py` follows §7 and writes `splits.csv`.
Done when: tests confirm 70/15/15 (± 2 points per class), no `group_id` in two splits, no image in two splits, and the same output with seed 365 on every run.

**2.5 Metrics and tables.** *Rickey.* `metrics.py`: compute §11 metrics from a predictions CSV, then write the metrics JSON (§8.6), the confusion matrix figure, and the error table (§8.7).
Done when: tests check the metric math on a tiny hand-made example.

**2.6 Baseline.** *Rickey.* `baseline.py`: majority class from train, predictions and metrics on val.
Done when: `results/predictions/baseline_val.csv` and `results/metrics/baseline_val.json` exist. ✅ Milestone 2.

**2.7 Data card draft.** *Premajyoti.* Fill in the `DATA_CARD.md` counts by class, source, lighting, and split.
Done when: the counts match `clean.csv` and `splits.csv`.

**2.8 Demo skeleton.** *Amaka.* `app/app.py` with upload, a fake predictor (same shape as §8.9), guidance cards, the low-confidence message, and the disclaimer.
Done when: `streamlit run app/app.py` works end to end with the fake.

## Phase 3: Modeling (Sun 10-25)

Pitch milestone: **MobileNetV3 training notebook, checkpoint, and validation metrics.** Owners: Dakarai, Rickey.

**3.1 Dataset and transforms.** *Dakarai.* `dataset.py` reads `splits.csv` and `data/processed/`, with the §10 transforms (augmentation on train only).
Done when: tests check tensor shape (3 × 224 × 224), label indices match `config.CLASSES`, and val and test aren't augmented.

**3.2 Training.** *Dakarai.* `train.py`: two-stage fine-tuning, early stopping on val macro F1, and the best checkpoint saved in the §8.8 format.
Done when: a short run on a small subset completes on a laptop, and a full run completes on Colab.

**3.3 Training notebook.** *Dakarai.* `notebooks/01_train_mobilenetv3.ipynb` calls `src/` code, logs settings, the device, and versions, and plots the training curves.
Done when: it runs top to bottom on a fresh Colab session.

**3.4 Prediction API.** *Dakarai.* `predict.py` with `load_predictor()` and `predict()`, exactly as in §8.9.
Done when: tests check the output keys, that probabilities sum to 1, and that the label is in `config.CLASSES`. Amaka confirms it drops into the app.

**3.5 Validation tables.** *Rickey.* Run the model on val and produce `mobilenetv3_val.csv`, the metrics JSON, the confusion figure, and the error table.
Done when: all four files exist in the §8 formats.

**3.6 Validation summary.** *Dakarai.* A short comparison of model vs baseline on val in `PROGRESS.md` (the numbers table) and the notebook.
Done when: val macro F1 for both models is recorded. ✅ Milestone 3.

## Phase 4: Evaluation and revision (Sun 11-08)

Pitch milestone: **held-out report, confusion matrix, error review, and revised labels or settings.** Owners: Dakarai, Amaka, Premajyoti.

**4.1 Held-out test run.** *Dakarai with Rickey.* Evaluate the baseline and the chosen checkpoint on test, **once**. Produce predictions, metrics, confusion matrices, and error tables for both.
Done when: all test files exist and the numbers are in `PROGRESS.md`.

**4.2 Error review.** *Premajyoti.* Using Rickey's error tables, summarize errors by class, lighting, background, and source, with 5–10 example mistakes.
Done when: the summary is in `docs/RESULTS.md` (create it).

**4.3 Revisions.** *John (labels), Dakarai (settings).* Fix label problems the review found, and retrain or tune if needed. Keep the first test result and report what changed.
Done when: changes are logged in `PROGRESS.md`, and any new split or checkpoint is documented.

**4.4 Real model in the app.** *Amaka.* Swap the fake predictor for `load_predictor(config.CHECKPOINT_PATH)`, and tune the low-confidence threshold on val with Dakarai.
Done when: the app runs with the real checkpoint on a laptop.

**4.5 Results write-up.** *Dakarai.* `docs/RESULTS.md`: the metrics table (baseline vs model, val and test), the confusion matrix, whether we hit the success criteria, and Premajyoti's error patterns.
Done when: a reader can see whether we hit macro F1 ≥ 0.70 and beat the baseline. ✅ Milestone 4.

## Phase 5: Final integration and presentation (Sun 11-22)

Pitch milestone: **Streamlit demo, final repository, presentation, and contribution summary.** Owners: all.

**5.1 Demo test.** *Amaka; everyone takes photos.* Ten new photos (at least 3 per class), run through the app and logged in `results/demo_test.csv`.
Done when: the result is recorded, with a pass at ≥ 9 of 10.

**5.2 Final data docs.** *Premajyoti (data card, source log), John (label guide).* Final counts, limitations, licenses, and the label guide change log.
Done when: the docs match the final dataset and splits.

**5.3 Reproducible repo.** *Dakarai and Rickey.* The README explains how to go from raw data to the demo; the final checkpoint is committed; `pytest` passes.
Done when: someone runs it from a fresh clone following only the README.

**5.4 Presentation.** *Amaka leads; all contribute.* Problem, data, method, results (baseline vs model, confusion matrix, errors), demo, limits and ethics, and who did what. Save it in `presentation/`.
Done when: rehearsed once as a team.

**5.5 Contribution summary.** *All.* `docs/CONTRIBUTIONS.md`: each member's specific work, pulled from the `PROGRESS.md` log.
Done when: every member has approved their own entry. ✅ Final.

---

## Fallback (if a class stays too small by Sun 10-11)

Switch to a clean TACO-only three-class subset. Still deliver the data card, the baseline, the trained model or error analysis, and a **static prediction demo** (saved predictions with images). Decide at the Oct 11 check-in and log it in `PROGRESS.md`.

## Stretch (only after milestone 4 is done)

- Grad-CAM heatmaps in the app ("what the model looked at")
- Compare MobileNetV3 Small vs Large
- Test-time augmentation
- Deploy the demo on Streamlit Community Cloud
