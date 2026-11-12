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
| Usable images (total) | 900–1,200 | 1,030 crops (662 source photos) | 2026-10-25 |
| Usable: recycling / special handling / trash | ≥ 300 each | 450 / 130 / 450 | 2026-10-25 |
| Team photos uploaded | ~125 (25 each) | In progress | — |
| Label disagreements resolved | all | 19 ambiguous excluded | 2026-10-25 |
| Baseline val macro F1 | (reference) | 0.19 | 2026-10-25 |
| MobileNetV3 val macro F1 | > baseline | 0.70 | 2026-10-25 |
| Baseline test macro F1 | (reference) | 0.19 | 2026-10-25 |
| MobileNetV3 test macro F1 | ≥ 0.70 and > baseline | 0.65 (Checkpoint 1 initial run) | 2026-10-25 |
| Demo test | ≥ 9 / 10 | Streamlit app built | 2026-11-12 |

## Team status

| Member | Working on | Next | Blocked by | Updated |
|---|---|---|---|---|
| Dakarai | Modular package fine-tuning (`train.py`, `predict.py`) | Hyperparameter tuning to push test macro F1 ≥ 0.70 | — | 2026-11-12 |
| Rickey | Pipeline modules (`clean.py`, `splits.py`, `baseline.py`, `metrics.py`) | Error tables analysis on test set | — | 2026-11-12 |
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

## Log

- **2026-11-12 (John / Team):** Modularized all core logic from `Smart_Recycling_Coach_Checkpoint.ipynb` into `src/recycle_coach/` (`ingest.py`, `clean.py`, `splits.py`, `baseline.py`, `metrics.py`, `dataset.py`, `train.py`, `predict.py`).
- **2026-11-12 (Amaka):** Built interactive Streamlit demo (`app/app.py`) with photo upload, camera support, class probability charts, guidance cards, and mock fallback.
- **2026-11-12 (Rickey / Dakarai):** Built comprehensive unit test suite covering clean, splits, metrics, baseline, dataset, and predictor (22 tests passing).
- **2026-11-12 (John / Premajyoti):** Updated `LABEL_GUIDE.md`, `SOURCE_LOG.md`, and `DATA_CARD.md`.
