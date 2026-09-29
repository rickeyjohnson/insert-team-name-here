# Progress Tracker

**Read this at the start of every session. Update it at the end.** Tick items in the same commit as the work. Item IDs match [`BUILD_PLAN.md`](BUILD_PLAN.md).

Status key: ⚪ not started · 🟢 on track · 🟡 at risk · 🔴 blocked · ✅ done

---

## Milestones

| # | Date | Milestone | Owners | Status |
|---|---|---|---|---|
| 0 | Thu 10-01 | Setup: repo, environments, data folder, open questions | All | 🟢 |
| 1 | Sun 10-04 | Source log, draft label guide, first 500 screened images | John, Amaka, Premajyoti | ⚪ |
| 2 | Sun 10-11 | Clean dataset, 70/15/15 split manifest, majority-class baseline | Rickey, John | ⚪ |
| 3 | Sun 10-25 | Training notebook, checkpoint, validation metrics | Dakarai, Rickey | ⚪ |
| 4 | Sun 11-08 | Held-out report, confusion matrix, error review, revisions | Dakarai, Amaka, Premajyoti | ⚪ |
| 5 | Sun 11-22 | Streamlit demo, final repo, presentation, contribution summary | All | ⚪ |

## Key numbers

| Metric | Target | Current | Updated |
|---|---|---|---|
| Images screened | ≥ 500 by 10-04 | 0 | — |
| Usable images (total) | 900–1,200 | 0 | — |
| Usable: recycling / special handling / trash | ≥ 300 each | 0 / 0 / 0 | — |
| Team photos uploaded | ~125 (25 each) | 0 | — |
| Label disagreements resolved | all | — | — |
| Baseline val macro F1 | (reference) | — | — |
| MobileNetV3 val macro F1 | > baseline | — | — |
| Baseline test macro F1 | (reference) | — | — |
| MobileNetV3 test macro F1 | ≥ 0.70 and > baseline | — | — |
| Demo test | ≥ 9 / 10 | — | — |

## Team status

Each person updates only their own row.

| Member | Working on | Next | Blocked by | Updated |
|---|---|---|---|---|
| Dakarai | — | 0.4 run the open-questions meeting | — | — |
| Rickey | 0.1 repo boilerplate | 2.3 cleaning (against sample images) | — | 2026-09-29 |
| John | — | 0.3 data folder, 1.1 label guide | — | — |
| Amaka | — | 1.1 review the label guide, 1.5 labels | — | — |
| Premajyoti | — | 1.2 source log | — | — |

## Checklist

### Phase 0: Setup (Thu 10-01)
- [ ] 0.1 Repo boilerplate and docs (Rickey)
- [ ] 0.2 Everyone's environment works: Dakarai · Rickey · John · Amaka · Premajyoti (All)
- [ ] 0.3 Shared data folder (John)
- [ ] 0.4 Open questions Q1–Q6 settled (All)

### Phase 1: Data acquisition (Sun 10-04)
- [ ] 1.1 Label guide draft + TACO mapping (John; Amaka reviews)
- [ ] 1.2 Source log (Premajyoti)
- [ ] 1.3 TACO ingest (John)
- [ ] 1.4 Team photos: Dakarai · Rickey · John · Amaka · Premajyoti (All)
- [ ] 1.5 First labels, ≥ 500 screened (John, Amaka)

### Phase 2: Data preparation and baseline (Sun 10-11)
- [ ] 2.1 Second review and disagreements resolved (Premajyoti)
- [ ] 2.2 Dataset target reached, or fallback flagged (John)
- [ ] 2.3 Cleaning: `clean.py`, `clean.csv`, processed images (Rickey)
- [ ] 2.4 Splits: `splits.py`, `splits.csv` (Rickey)
- [ ] 2.5 Metrics and tables: `metrics.py` (Rickey)
- [ ] 2.6 Baseline on val (Rickey)
- [ ] 2.7 Data card draft (Premajyoti)
- [ ] 2.8 Demo skeleton with a fake predictor (Amaka)

### Phase 3: Modeling (Sun 10-25)
- [ ] 3.1 Dataset and transforms (Dakarai)
- [ ] 3.2 Training script and checkpoint (Dakarai)
- [ ] 3.3 Training notebook runs on fresh Colab (Dakarai)
- [ ] 3.4 Prediction API (Dakarai)
- [ ] 3.5 Validation tables (Rickey)
- [ ] 3.6 Validation summary, model vs baseline (Dakarai)

### Phase 4: Evaluation and revision (Sun 11-08)
- [ ] 4.1 Held-out test run, once (Dakarai, Rickey)
- [ ] 4.2 Error review (Premajyoti)
- [ ] 4.3 Label and settings revisions (John, Dakarai)
- [ ] 4.4 Real model in the app (Amaka)
- [ ] 4.5 Results write-up (Dakarai)

### Phase 5: Final integration and presentation (Sun 11-22)
- [ ] 5.1 Demo test, 10 new photos (Amaka)
- [ ] 5.2 Final data docs (Premajyoti, John)
- [ ] 5.3 Reproducible repo from a fresh clone (Dakarai, Rickey)
- [ ] 5.4 Presentation (Amaka + all)
- [ ] 5.5 Contribution summary (All)

## Blockers and risks

| Date | Issue | Owner | Status |
|---|---|---|---|
| — | — | — | — |

## Log

Newest first. One line per session: date, who, what changed. This is the raw material for the contribution summary (5.5).

- **2026-09-29 · Rickey (Claude Code):** added the pitch PDF, repo boilerplate (folders, `config.py`, module stubs, requirements, smoke test), `AGENTS.md`, and the docs (`PROJECT_SPEC`, `BUILD_PLAN`, `PROGRESS`, `LABEL_GUIDE`, `DATA_CARD`, `SOURCE_LOG`).
