# Progress Tracker

**Read this at the start of every session. Update it at the end.** Tick items in the same commit as the work. Item IDs match [`BUILD_PLAN.md`](BUILD_PLAN.md).

Status key: ⚪ not started · 🟢 on track · 🟡 at risk · 🔴 blocked · ✅ done

---

## Milestones

| # | Date | Milestone | Owners | Status |
|---|---|---|---|---|
| 0 | Thu 10-01 | Setup: repo, environments, data folder, open questions | All | ✅ |
| 1 | Sun 10-04 | Source log, draft label guide, first 500 screened images | John, Amaka, Premajyoti | ✅ |
| 2 | Sun 10-11 | Clean dataset, 70/15/15 split manifest, majority-class baseline | Rickey, John | ✅ |
| 3 | Sun 10-25 | Training notebook, checkpoint, validation metrics | Dakarai, Rickey | ✅ |
| 4 | Sun 11-08 | Held-out report, confusion matrix, error review, revisions | Dakarai, Amaka, Premajyoti | 🟢 |
| 5 | Sun 11-22 | Streamlit demo, final repo, presentation, contribution summary | All | 🟢 |

## Key numbers

| Metric | Target | Current | Updated |
|---|---|---|---|
| Images screened | ≥ 500 by 10-04 | 4,784 annotations (2,611 usable) | 2026-10-25 |
| Usable images (total) | 900–1,200 | 815 of 1,030 crops after `clean.py` (215 under 128 px); 681 source photos | 2026-11-12 |
| Usable: recycling / special handling / trash | ≥ 300 each | 392 / 89 / 334 after `clean.py` (450 / 130 / 450 before) | 2026-11-12 |
| Team photos uploaded | ~125 (25 each) | In progress | — |
| Label disagreements resolved | all | 19 ambiguous excluded | 2026-10-25 |
| Baseline val macro F1 | (reference) | 0.21 (seed-365 split, 124 crops; CP1 seed-42 split: 0.19) | 2026-11-12 |
| MobileNetV3 val macro F1 | > baseline | 0.70 | 2026-10-25 |
| Baseline test macro F1 | (reference) | 0.21 (seed-365 split, 127 crops; CP1 seed-42 split: 0.19) | 2026-11-12 |
| MobileNetV3 test macro F1 | ≥ 0.70 and > baseline | 0.65 (Checkpoint 1 initial run) | 2026-10-25 |
| Demo test | ≥ 9 / 10 | Streamlit app built | 2026-11-12 |

## Experiments (Checkpoint 3)

Same split (seed 365, 564 / 124 / 127) and recipe for every model unless noted. Pick on val macro F1 only; test runs once (E7). Run with `notebooks/02_cp3_experiments.ipynb` or `scripts/run_cp3_experiments.py`.

| ID | Experiment | Split | Status | Val macro F1 | Test macro F1 | CPU ms/img |
|---|---|---|---|---|---|---|
| E0 | Majority class (always recycling) | seed 365 | ✅ Completed | 0.21 | 0.21 | — |
| E1 | MobileNetV3-Large, single stage (CP1 notebook) | seed 42 (leaky) | ✅ Completed | 0.77 | 0.65 | — |
| E2 | MobileNetV3-Large, two stage, class-weighted loss | seed 365 | ⚪ Code ready, run pending | ___ | — | ___ |
| E3 | E2 + team photos | new split | ⚪ Planned (needs team photos) | — | — | — |
| E4 | E2 + oversample (`WeightedRandomSampler`) | seed 365 | ⚪ Code ready, run pending | ___ | — | ___ |
| E5 | MobileNetV3-Small, same recipe | seed 365 | ⚪ Code ready, run pending | ___ | — | ___ |
| E6 | EfficientNet-B0, same recipe | seed 365 | ⚪ Code ready, run pending | ___ | — | ___ |
| E7 | Final: best by val, test once | seed 365 | ⚪ After E2–E6 | ___ | ___ | ___ |

The checkpoint committed on 2026-11-12 (val 0.69, best epoch 1) was trained on the earlier leaky split and is replaced by E7's pick.

## Team status

| Member | Working on | Next | Blocked by | Updated |
|---|---|---|---|---|
| Dakarai | Modular package fine-tuning (`train.py`, `predict.py`) | Hyperparameter tuning to push test macro F1 ≥ 0.70 | — | 2026-11-12 |
| Rickey | Fixed photo grouping in `clean.py`; committed `clean.csv`, `splits.csv` (564 / 124 / 127) and baseline results | Model val and test tables once Dakarai retrains on the new split | Dakarai's retrain | 2026-11-12 |
| John | Modular ingest (`ingest.py`), label guide (`LABEL_GUIDE.md`) | Ingest team photos when collected | — | 2026-11-12 |
| Amaka | Streamlit interactive demo (`app/app.py`) | 10 new test photos user flow testing | — | 2026-11-12 |
| Premajyoti | Dataset documentation (`DATA_CARD.md`, `SOURCE_LOG.md`) | Detailed error pattern report from test predictions | — | 2026-11-12 |

## Checklist

### Phase 0: Setup (Thu 10-01)
- [x] 0.1 Repo boilerplate and docs (Rickey)
- [x] 0.2 Everyone's environment works: Dakarai · Rickey · John · Amaka · Premajyoti (All)
- [x] 0.3 Shared data folder (John)
- [x] 0.4 Open questions Q1–Q6 settled (All)

### Phase 1: Data acquisition (Sun 10-04)
- [x] 1.1 Label guide draft + TACO mapping (John; Amaka reviews)
- [x] 1.2 Source log (Premajyoti)
- [x] 1.3 TACO ingest (John)
- [ ] 1.4 Team photos: Dakarai · Rickey · John · Amaka · Premajyoti (All)
- [x] 1.5 First labels, ≥ 500 screened (John, Amaka)

### Phase 2: Data preparation and baseline (Sun 10-11)
- [x] 2.1 Second review and disagreements resolved (Premajyoti)
- [x] 2.2 Dataset target reached, or fallback flagged (John)
- [x] 2.3 Cleaning: `clean.py`, `clean.csv`, processed images (Rickey)
- [x] 2.4 Splits: `splits.py`, `splits.csv` (Rickey)
- [x] 2.5 Metrics and tables: `metrics.py` (Rickey)
- [x] 2.6 Baseline on val (Rickey)
- [x] 2.7 Data card draft (Premajyoti)
- [x] 2.8 Demo skeleton with a fake predictor (Amaka)

### Phase 3: Modeling (Sun 10-25)
- [x] 3.1 Dataset and transforms (Dakarai)
- [x] 3.2 Training script and checkpoint (Dakarai)
- [x] 3.3 Training notebook runs on fresh Colab (Dakarai)
- [x] 3.4 Prediction API (Dakarai)
- [x] 3.5 Validation tables (Rickey)
- [x] 3.6 Validation summary, model vs baseline (Dakarai)

### Phase 4: Evaluation and revision (Sun 11-08)
- [x] 4.1 Held-out test run, once (Dakarai, Rickey)
- [ ] 4.2 Error review (Premajyoti)
- [ ] 4.3 Label and settings revisions (John, Dakarai)
- [x] 4.4 Real model in the app (Amaka)
- [ ] 4.5 Results write-up (Dakarai)

### Phase 5: Final integration and presentation (Sun 11-22)
- [ ] 5.1 Demo test, 10 new photos (Amaka)
- [x] 5.2 Final data docs (Premajyoti, John)
- [x] 5.3 Reproducible repo from a fresh clone (Dakarai, Rickey)
- [ ] 5.4 Presentation (Amaka + all)
- [ ] 5.5 Contribution summary (All)

## Blockers and risks

| Date | Issue | Owner | Status |
|---|---|---|---|
| 2026-10-25 | Special handling class is small (130 crops); model achieves 0.56 F1 on this class | John / Dakarai | Add team photos for batteries/aerosols, keep class-weighted loss |
| 2026-10-25 | Test macro F1 currently 0.65, shy of 0.70 target | Dakarai | Plan longer fine-tuning run with adjusted learning rate and cosine scheduler |
| 2026-11-12 | `models/mobilenetv3_best.pt` was trained on a split grouped by crop, not photo (37 of 123 test crops shared a photo with train). 91 of 127 crops in the new test split were in its training set, so it can't be scored on the new split. | Dakarai | Retrain on the committed `splits.csv` before any new val/test numbers. Notebook 01 skips ingest when `splits.csv` exists, so on fresh Colab check for `data/processed/*.jpg` instead. |
| 2026-11-12 | `clean.py`'s 128 px minimum drops 215 crops (`ingest.py` keeps boxes down to 48 px); special handling falls from 130 to 89 | Team | Decide: keep 128 px, or lower `MIN_SHORT_SIDE` to match ingest |

## Log

- **2026-11-22 (Dakarai, Claude Code):** CP3 comparison code. `train.py` builds MobileNetV3-Large/Small, EfficientNet-B0 or ResNet-18 (`arch=`), optional class oversampling (`oversample=`), seeded runs; `predict.py` reads the architecture from the checkpoint (old checkpoints load as Large). New `experiments.py` + `scripts/run_cp3_experiments.py` (`--phase val` trains E2, E4, E5, E6 and picks on val; `--phase test` scores the pick once and refuses a second run), `demo_eval.py` + `scripts/run_demo_test.py` (campus photos vs 9/10 and 8/10-per-class targets), `notebooks/02_cp3_experiments.ipynb` for Colab. 16 new tests (41 passing). Smoke-tested both phases end to end on synthetic images (no real results yet: needs a Colab GPU run).
- **2026-11-12 (Rickey, Claude Code):** `clean.py` now groups crops by source photo (`images.csv` has no `group_id`, so every crop was its own group and splits leaked by photo); near-duplicate merges keep whole photo groups. 3 new tests (25 passing). Ran ingest → clean → splits → baseline: 815 usable of 1,030, seed-365 split 564 / 124 / 127 with no photo in two splits, baseline (always recycling) val 47.6% / 0.21 macro F1, test 46.5% / 0.21. Committed `clean.csv`, `splits.csv`, `images.csv` (unchanged `ingest.py` output) and the baseline predictions, metrics, confusion figures and error tables.
- **2026-11-12 (John / Team):** Modularized all core logic from `Smart_Recycling_Coach_Checkpoint.ipynb` into `src/recycle_coach/` (`ingest.py`, `clean.py`, `splits.py`, `baseline.py`, `metrics.py`, `dataset.py`, `train.py`, `predict.py`).
- **2026-11-12 (Amaka):** Built interactive Streamlit demo (`app/app.py`) with photo upload, camera support, class probability charts, guidance cards, and mock fallback.
- **2026-11-12 (Rickey / Dakarai):** Built comprehensive unit test suite covering clean, splits, metrics, baseline, dataset, and predictor (22 tests passing).
- **2026-11-12 (John / Premajyoti):** Updated `LABEL_GUIDE.md`, `SOURCE_LOG.md`, and `DATA_CARD.md`.
