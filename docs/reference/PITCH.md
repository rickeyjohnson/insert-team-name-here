# Team Project Pitch and Roles (as submitted)

A Markdown copy of [`COMP365_TP_Pitch_and_Roles.pdf`](COMP365_TP_Pitch_and_Roles.pdf), submitted **2026-09-27**, so agents can read and search it. **Don't edit this file.** It records what we committed to. The working spec is [`../PROJECT_SPEC.md`](../PROJECT_SPEC.md). If the two disagree, the pitch wins until the team agrees on a change and records it in `PROJECT_SPEC.md`.

## 1. Final team confirmation

| Team name | Members | Submitted |
|---|---|---|
| Insert Team Name Here | Dakarai Lanes, Rickey Johnson, John Sampson, Amaka Okoro, Premajyoti Gammon | 2026-09-27 |

## 2. Project pitch

| Field | Team response |
|---|---|
| Working title | Smart Recycling Coach |
| Problem and user | Students and campus facilities staff need quick, consistent disposal guidance for common items. The project helps a user decide whether an item belongs in recycling, trash, or special handling. |
| Project objective | Train and test a three-class image classifier that gives a disposal suggestion from a photo. Compare a fine-tuned model with a majority-class baseline on held-out images and demonstrate the result in a small web app. |
| AI or ML role | Fine-tune a MobileNetV3 image classifier pretrained on ImageNet for recycling, trash, and special-handling labels. Image classification fits because material and item appearance vary too much for a fixed keyword or rule system. |
| Final deliverables | A documented image dataset, label guide, training notebook and saved model, baseline and model results with a confusion matrix, Streamlit demo, and presentation materials. |

## 3. Specific aims

| Aim | Goal | Measurable result | Owners |
|---|---|---|---|
| 1 | Create a balanced three-class image dataset and label guide | At least 900 usable images, class counts, source metadata, and a reviewed labeling guide | John, Amaka, Premajyoti |
| 2 | Build a baseline and fine-tune a MobileNetV3 classifier | Reproducible training notebook, saved checkpoint, and held-out predictions for both comparisons | Dakarai, Rickey |
| 3 | Evaluate errors and integrate the model into a usable demo | Accuracy, macro F1, per-class recall, confusion matrix, and a demo tested on at least 10 new images | Dakarai, Rickey, Amaka, Premajyoti |

## 4. Data plan

| Question | Team response |
|---|---|
| Dataset or source | TACO: Trash Annotations in Context (https://github.com/pedropro/TACO); team-taken photos of common clean items; EPA recycling guidance (https://www.epa.gov/recycle/how-do-i-recycle-common-recyclables). |
| Access or creation | John downloads TACO and keeps images that fit the three labels. Each member contributes about 25 photos of clean items. The team labels with one guide, and Premajyoti coordinates a second review of disagreements. No faces, people, personal records, or restricted locations. TACO attribution and license terms are kept. |
| Expected structure | 900–1,200 RGB JPG images. Unit: one photo of one item. Labels: recycling, trash, or special handling. Inputs are resized images; metadata records source, label, and reviewer. |
| Preparation and splits | Remove duplicates, unreadable images, and inconsistent labels; resize; review a sample of each class. Keep near-duplicate items in the same split, then use stratified 70/15/15 train/validation/test splits. Augment training images only. |
| Limits and ethics | Recycling rules vary by location, so the demo gives general guidance and doesn't replace campus policy. Avoid identifiable images, respect data licenses, avoid hazardous-waste decisions, and report errors by class and lighting condition. |

## 5. Methodology and evaluation

| Method | Team response |
|---|---|
| Workflow | Load and document images with Python, pandas, Pillow, and PyTorch. Establish a majority-class baseline, then fine-tune MobileNetV3 with the same train/validation split. Export predictions and model confidence, then connect the saved model to a simple Streamlit upload interface. |
| Evaluation | Held-out accuracy, macro F1, per-class recall, and a confusion matrix. Compare MobileNetV3 with the majority-class baseline. **Success:** macro F1 ≥ 0.70, improvement over baseline, and correct response flow for at least 9 of 10 demo images selected after training. |
| Feasibility and risk | Biggest risk: too few or inconsistent images for a difficult class. **Fallback:** a clean TACO-only three-class subset, delivering the dataset card, baseline, trained model or error analysis, and a static prediction demo. |

## 6. Timeline

| Date | Phase | Milestone | Owners |
|---|---|---|---|
| Oct 4 | Data acquisition or creation | Source log, draft label guide, first 500 screened images | John, Amaka, Premajyoti |
| Oct 11 | Data preparation and baseline | Clean dataset, 70/15/15 split manifest, majority-class baseline result | Rickey, John |
| Oct 25 | Modeling or system build | MobileNetV3 training notebook, checkpoint, validation metrics | Dakarai, Rickey |
| Nov 8 | Evaluation and revision | Held-out report, confusion matrix, error review, revised labels or settings | Dakarai, Amaka, Premajyoti |
| Nov 22 | Final integration and presentation | Streamlit demo, final repository, presentation, contribution summary | All |

## 7. Roles

| Member | Role | Contribution | Depends on |
|---|---|---|---|
| Dakarai Lanes | Project lead and model developer | Training pipeline, baseline comparison, model checkpoint, metrics summary | Rickey (split files, validation data); Amaka (demo integration) |
| Rickey Johnson | Data engineer and validation analyst | Clean images, maintain split manifests, check duplicates, produce prediction and error tables | John (source and label records); Dakarai (model outputs) |
| John Sampson | Data acquisition and labeling lead | Download and screen source data, coordinate team photos, maintain the label guide and data documentation | Amaka (label review); Rickey (quality checks) |
| Amaka Okoro | Demo and evaluation lead | Streamlit interface, user-flow testing, label review, presentation visuals | Dakarai (saved model); John (label guidance) |
| Premajyoti Gammon | Quality review and documentation | Second label review, data card and source log, error-pattern summary for the final report | John (initial labels); Rickey and Dakarai (prediction results) |
