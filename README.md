# Smart Recycling Coach

**COMP 365 team project · Team Insert Team Name Here**
Dakarai Lanes · Rickey Johnson · John Sampson · Amaka Okoro · Premajyoti Gammon

Take a photo of one item and get a disposal suggestion: **recycling**, **trash**, or **special handling**. We fine-tune an ImageNet-pretrained MobileNetV3, compare it with a majority-class baseline on held-out images, and demo it in Streamlit.

**Goal:** test macro F1 ≥ 0.70 and better than the baseline, plus correct answers for ≥ 9 of 10 new demo photos. **Final due:** Sun 2026-11-22.

## Start here

| Read | For |
|---|---|
| [docs/PROGRESS.md](docs/PROGRESS.md) | Where everyone is right now (the progress tracker) |
| [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) | Everything we need to build, in order, with owners and dates |
| [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) | Rules, numbers, and file formats |
| [docs/LABEL_GUIDE.md](docs/LABEL_GUIDE.md) | How to label an image |
| [docs/DATA_CARD.md](docs/DATA_CARD.md) · [docs/SOURCE_LOG.md](docs/SOURCE_LOG.md) | Dataset documentation and sources |
| [docs/reference/](docs/reference/) | The submitted pitch (PDF + Markdown copy) |
| [AGENTS.md](AGENTS.md) | Context for AI agents (Claude Code, Codex, Gemini) |

## Setup

Use Python 3.11 or 3.12.

```bash
git clone https://github.com/rickeyjohnson/insert-team-name-here.git
cd insert-team-name-here
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app/app.py
```

**Images aren't in git.** Get them from the team Google Drive folder `SmartRecyclingCoach-data/` and copy `raw/` and `processed/` into `data/`. See [data/README.md](data/README.md).

**On Colab:** clone the repo, `pip install -r requirements.txt`, and mount Drive for the images.

## Layout

```
docs/                 spec, build plan, progress tracker, label guide, data card, source log
data/metadata/        CSV manifests (images, reviews, clean, splits)
data/raw, processed/  images (git-ignored)
src/recycle_coach/    all reusable code: config, ingest, clean, splits, metrics, baseline, dataset, train, predict
notebooks/            training and analysis notebooks
models/               final checkpoint
results/              predictions, metrics, error tables, figures
app/                  Streamlit demo
tests/                pytest
presentation/         slides and visuals
```

## Milestones

| Date | Milestone | Owners |
|---|---|---|
| Sun 10-04 | Source log, draft label guide, first 500 screened images | John, Amaka, Premajyoti |
| Sun 10-11 | Clean dataset, 70/15/15 split manifest, baseline result | Rickey, John |
| Sun 10-25 | Training notebook, checkpoint, validation metrics | Dakarai, Rickey |
| Sun 11-08 | Held-out report, confusion matrix, error review | Dakarai, Amaka, Premajyoti |
| Sun 11-22 | Streamlit demo, final repo, presentation, contribution summary | All |

## Working together

- Pull `main` before starting anything, and work on a branch.
- Update your row and the log in [docs/PROGRESS.md](docs/PROGRESS.md) at the end of every session.
- Keep code in `src/recycle_coach/`; notebooks and the app import it.
- Run `pytest` before you push.
