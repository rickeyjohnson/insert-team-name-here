# Label Guide

**Owner:** John · **Reviewer:** Amaka · **Status:** Draft skeleton. The examples below are starting points; check each one against the EPA page and campus rules before labeling.

Everyone labels with this guide. When two labelers disagree and the guide doesn't settle it, fix the guide (and add a line to the change log) so the next person gets it right.

EPA reference: https://www.epa.gov/recycle/how-do-i-recycle-common-recyclables

## 1. Before you label

- **One item per image.** If the photo clearly shows more than one item, label it `exclude` and say why in `notes`.
- **Label the item, not the background.**
- **Judge it as shown.** A greasy pizza box is labeled as it looks in the photo, not as it would be when clean.
- **Not sure?** Label your best guess and write `unsure` in `notes`. The second review will catch it.
- Also fill in `lighting` (`bright`, `dim`, `glare`) and `background` (`plain`, `cluttered`).

## 2. Classes

### `recycling`

Goes in a standard campus recycling bin. It must be empty and clean enough.

| Include | Examples |
|---|---|
| Plastic bottles and jugs | Water and soda bottles, milk jugs |
| Metal cans | Aluminum soda cans, steel food cans |
| Glass bottles and jars | Clean beverage bottles, food jars |
| Paper | Office paper, newspaper, magazines |
| Cardboard | Flattened, clean boxes |

### `special_handling`

Doesn't belong in either bin; it needs a drop-off or facilities. **The app never gives hazardous-waste instructions**, only "check with campus facilities."

| Include | Examples |
|---|---|
| Batteries | AA, AAA, phone batteries |
| Small electronics | Cables, chargers, earbuds, old phones |
| Light bulbs | CFLs, fluorescent tubes |
| Plastic bags and film | Grocery bags, shrink wrap (store drop-off, not curbside) |
| Other drop-off items | TBD (John) |

### `trash`

Everything else that isn't recyclable in the campus stream.

| Include | Examples |
|---|---|
| Food-soiled paper | Greasy boxes, used napkins |
| Wrappers and chip bags | Multilayer film packaging |
| Foam | Styrofoam cups and containers |
| Mixed-material items | TBD (John) |

## 3. TACO category mapping

Map every TACO category (from the annotations file) to a label or `exclude`. `ingest.py` reads this table.

| TACO category | Our label | Notes |
|---|---|---|
| _fill in_ | | |

## 4. Edge cases

| Item or situation | Label | Why |
|---|---|---|
| Pizza box, partly greasy | TBD | |
| Bottle with liquid still inside | TBD | |
| Paper cup (plastic-lined) | TBD | |
| Crushed can | TBD | |
| Item too blurry to identify | `exclude` | Can't be labeled reliably |

## 5. What the app says

One short card per class. Amaka's app shows these; keep them in sync with `app/`.

- **Recycling:** TBD
- **Special handling:** TBD. Must say to check with campus facilities; no hazardous-waste instructions.
- **Trash:** TBD
- **Not sure (low confidence):** "Not sure. Check the label guide or ask facilities."
- **Always shown:** "General guidance only. Recycling rules vary by location, and this doesn't replace campus policy."

## 6. Change log

| Date | Who | Change |
|---|---|---|
| 2026-09-29 | Rickey | Skeleton created |
