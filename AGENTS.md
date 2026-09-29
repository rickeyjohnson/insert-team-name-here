# AGENTS.md: Smart Recycling Coach

Context for any AI agent (Claude Code, Codex, Gemini) working in this repo. `CLAUDE.md` imports this file, so edit this one.

## The project

**Smart Recycling Coach** is the COMP 365 (AI & Machine Learning) team project for team **Insert Team Name Here**. It's a three-class image classifier that tells a student or campus facilities worker whether an item goes in **recycling**, **trash**, or **special handling**, from one photo.

We fine-tune an ImageNet-pretrained **MobileNetV3** (PyTorch), compare it against a **majority-class baseline** on held-out images, and demo it in a **Streamlit** app.

**Success means:** held-out macro F1 of at least **0.70**, better than the baseline, and a correct response for at least **9 of 10** new demo photos taken after training.

**Final due:** Sun 2026-11-22. Milestones are in [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md).

## Read first (every session)

1. [`docs/PROGRESS.md`](docs/PROGRESS.md): what's done, what's in progress, who's blocked.
2. [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md): everything we need to build, in order, with owners and "done when" checks.
3. [`docs/PROJECT_SPEC.md`](docs/PROJECT_SPEC.md): the rules, numbers, and file formats. Check the section for your task.
4. [`docs/reference/PITCH.md`](docs/reference/PITCH.md): what we promised the instructor (the source of truth for scope).

## Team and ownership

| Member | Role | Owns |
|---|---|---|
| Dakarai Lanes | Project lead, model developer | Training pipeline, baseline comparison, checkpoint, metrics summary. `src/recycle_coach/{dataset,train,predict}.py`, `notebooks/`, `models/` |
| Rickey Johnson | Data engineer, validation analyst | Cleaning, dedupe, split manifests, baseline, metrics, prediction and error tables. `src/recycle_coach/{clean,splits,baseline,metrics}.py`, `data/metadata/clean.csv`, `data/metadata/splits.csv` |
| John Sampson | Data acquisition and labeling lead | TACO download and screening, team photo drive, label guide. `src/recycle_coach/ingest.py`, `data/metadata/images.csv`, `docs/LABEL_GUIDE.md` |
| Amaka Okoro | Demo and evaluation lead | Streamlit app, user-flow testing, label review, presentation visuals. `app/`, `presentation/` |
| Premajyoti Gammon | Quality review and documentation | Second label review, data card, source log, error-pattern summary. `data/metadata/reviews.csv`, `docs/DATA_CARD.md`, `docs/SOURCE_LOG.md` |

If it isn't clear which teammate you're working for, ask before editing. Stick to that person's files; if a task needs a change in someone else's file, say so instead of making it.

## Repo map

```
AGENTS.md, CLAUDE.md     agent context (this file)
README.md                human overview and setup
docs/
  PROJECT_SPEC.md        rules, numbers, file formats
  BUILD_PLAN.md          ordered list of everything to build
  PROGRESS.md            progress tracker (update every session)
  LABEL_GUIDE.md         how to label an item (deliverable)
  DATA_CARD.md           dataset documentation (deliverable)
  SOURCE_LOG.md          where every image came from (deliverable)
  reference/             the submitted pitch (PDF + Markdown copy)
data/
  raw/                   original images (NOT in git)
  processed/             cleaned, resized images (NOT in git)
  metadata/              CSV manifests (in git)
src/recycle_coach/       all reusable Python code (importable package)
notebooks/               training and analysis notebooks (thin; call src/)
models/                  saved checkpoints (only the final one goes in git)
results/                 metrics JSON, prediction CSVs, confusion matrices, figures
app/                     Streamlit demo
tests/                   pytest tests
presentation/            slides and visuals
```

## Stack and commands

Python 3.11+, pandas, Pillow, PyTorch + torchvision, scikit-learn (metrics), matplotlib, imagehash, Streamlit, pytest, Jupyter.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # also installs src/recycle_coach in editable mode
pytest                              # run all tests
streamlit run app/app.py            # run the demo
```

Training can run on Google Colab (GPU), Apple Silicon (`mps`), or CPU. Code picks the device automatically.

## Facts that must not drift

These live in `src/recycle_coach/config.py`. Import them; never retype them.

- **Classes, in this order:** `recycling` (0), `special_handling` (1), `trash` (2). The order is alphabetical, so it matches torchvision's `ImageFolder` too.
- **Unit:** one photo of one item. RGB JPG.
- **Splits:** stratified 70 / 15 / 15 train / val / test, seed `365`. Near-duplicates share a `group_id` and always land in the same split.
- **The test split is locked.** Never train, tune, pick thresholds, or choose a checkpoint on it. It's used once, for the held-out report (milestone 4).
- **Augmentation** is for training images only.
- **Metrics:** accuracy, macro F1, per-class recall, confusion matrix (rows = true, columns = predicted, class order above).
- **Model input:** 224 × 224, ImageNet mean and std normalization.

## Rules

- **No images in git.** `data/raw/` and `data/processed/` are git-ignored. The shared copy lives in the team data folder (see `PROJECT_SPEC.md` §4). Metadata CSVs *are* committed.
- **Privacy:** no faces, people, personal records, or restricted locations in any image. Strip EXIF (phone photos carry GPS).
- **Licenses:** keep TACO attribution and license terms. Log every source in `docs/SOURCE_LOG.md`.
- **Logic goes in `src/recycle_coach/`, not notebooks.** Notebooks import and call it, so tests can cover it and the app can reuse it.
- **Reproducible:** set seeds, read paths from `config.py` (no hard-coded personal paths), and write outputs to `results/` in the formats in `PROJECT_SPEC.md` §8.
- **Test what has a rule or a number** (split ratios, no group leakage, class order, metric math, prediction output shape). Run `pytest` before saying something works, and report the real result.
- **The demo gives general guidance.** It never claims to replace campus policy and never makes hazardous-waste calls; special handling tells the user to check with campus facilities.
- **Update `docs/PROGRESS.md`** at the end of every session: your row, the checklist, and a line in the log.
- **Don't add scope** that isn't in the pitch. Put ideas under "Stretch" in `BUILD_PLAN.md`.

## Ask first

- Deleting or renaming files
- Adding a dependency to `requirements.txt`
- Changing anything in "Facts that must not drift"
- `git push`, opening or merging PRs

## Never

- Commit images, datasets, `.venv/`, secrets, or experiment checkpoints
- Touch the test split before the held-out evaluation
- Claim a test passed or a metric was reached without seeing the output
