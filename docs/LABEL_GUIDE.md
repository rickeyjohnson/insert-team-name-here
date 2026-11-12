# Label Guide

**Owner:** John Sampson · **Reviewer:** Amaka Okoro · **Status:** Complete (Milestone 1 Deliverable).

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
| Plastic bottles and jugs | Water and soda bottles, milk jugs, detergent jugs |
| Metal cans | Aluminum soda cans, steel food/soup cans |
| Glass bottles and jars | Clean beverage bottles, food jars |
| Paper | Office paper, newspaper, magazines, paper bags |
| Cardboard | Flattened, clean corrugated and egg cartons |

### `special_handling`

Doesn't belong in either bin; it needs a designated drop-off or campus facilities attention. **The app never gives hazardous-waste instructions**, only "take to drop-off or check with campus facilities."

| Include | Examples |
|---|---|
| Batteries | AA, AAA, 9V, laptop and phone batteries |
| Small electronics | Cables, chargers, earbuds, electronic peripherals |
| Light bulbs | CFLs, fluorescent tubes, LEDs |
| Plastic bags and film | Single-use grocery bags, shrink wrap (store drop-off only, never curbside) |
| Broken glass | Wrapped broken glass to prevent handler injury |

### `trash`

Everything else that isn't recyclable in standard single-stream bins.

| Include | Examples |
|---|---|
| Food-soiled paper | Greasy pizza boxes, used paper towels, soiled napkins |
| Wrappers and snack bags | Multilayer chip bags, candy wrappers, foil film |
| Foam | Styrofoam cups, clamshell containers, packing peanuts |
| Straws and utensils | Disposable plastic and paper straws, cutlery |
| Plastic cups & lined cups | To-go coffee cups (poly-coated), disposable plastic drink cups |
| PPE & sanitary | Plastic gloves, tissues, wipes, cigarettes |

## 3. TACO Category Mapping

41 categories from TACO are mapped to project classes based on EPA rules; 19 ambiguous or context-dependent categories are excluded.

| TACO Category | Project Label | Rationale |
|---|---|---|
| Clear plastic bottle | `recycling` | Standard PET bottle (#1), curbside recyclable |
| Other plastic bottle | `recycling` | HDPE/PP bottles (#2, #5), curbside recyclable |
| Glass bottle | `recycling` | Container glass, universally recyclable |
| Glass jar | `recycling` | Clean container glass |
| Drink can | `recycling` | Aluminum beverage cans |
| Food Can | `recycling` | Steel/tin food cans |
| Metal lid | `recycling` | Ferrous/aluminum container lids |
| Corrugated carton | `recycling` | Cardboard shipping boxes |
| Other carton | `recycling` | Non-corrugated paperboard packaging |
| Drink carton | `recycling` | Gable-top / aseptic beverage cartons |
| Egg carton | `recycling` | Molded pulp paper cartons |
| Toilet tube | `recycling` | Cardboard roll cores |
| Normal paper | `recycling` | Office paper, loose leaf |
| Magazine paper | `recycling` | Glossy printed paper |
| Paper bag | `recycling` | Kraft shopping and grocery bags |
| Battery | `special_handling` | Hazardous, fire risk in collection trucks |
| Aerosol | `special_handling` | Pressurized cans; requires hazardous drop-off |
| Broken glass | `special_handling` | Physical safety hazard for collection workers |
| Single-use carrier bag | `special_handling` | Plastic film jams sorting machinery; retail drop-off only |
| Polypropylene bag | `special_handling` | Woven/film bag; store collection stream |
| Cigarette | `trash` | Non-recyclable toxic litter |
| Plastic film | `trash` | Thin wrap, film wrap |
| Other plastic wrapper | `trash` | Multi-layer barrier wrappers |
| Crisp packet | `trash` | Metalized multi-layer film packaging |
| Plastic straw | `trash` | Too small for sorting screens |
| Paper straw | `trash` | Soiled, fiber degrades too fast |
| Styrofoam piece | `trash` | Expanded polystyrene (EPS) not recyclable curbside |
| Foam cup | `trash` | EPS beverage cup |
| Foam food container | `trash` | EPS clamshell packaging |
| Tissues | `trash` | Short fibers, contaminated with bodily fluids |
| Paper cup | `trash` | Polyethylene-lined hot drink cups |
| Disposable plastic cup | `trash` | Low-grade brittle thermoformed cups |
| Plastic utensils | `trash` | Polypropylene/polystyrene single-use cutlery |
| Food waste | `trash` | Organic matter (unless compost stream present) |
| Rope & strings | `trash` | Tanglers that damage sorting machinery |
| Plastic glooves | `trash` | Nitrile/vinyl/latex PPE |
| Squeezable tube | `trash` | Multilayer toothpaste and lotion tubes |
| Six pack rings | `trash` | Plastic photodegradable rings |
| Garbage bag | `trash` | Large soiled refuse bags |
| Aluminium blister pack | `trash` | Mixed foil and plastic backing |
| Carded blister pack | `trash` | Mixed cardboard and plastic thermoform |
| Bottle cap | `exclude` | Ambiguous: often separated and too small |
| Plastic bottle cap | `exclude` | Ambiguous: depends on whether screwed on or loose |
| Metal bottle cap | `exclude` | Ambiguous: loose metal caps fall through screens |
| Food container | `exclude` | Ambiguous: cleanliness and resin varies |
| Disposable food container | `exclude` | Ambiguous: varies between clear PET and dirty paper |
| Other plastic | `exclude` | Ambiguous catch-all category |
| Plastic lid | `exclude` | Ambiguous: varies by plastic resin |
| Pop tab | `exclude` | Ambiguous: too small |
| Scrap metal | `exclude` | Non-container metal; belongs in scrap stream |
| Unlabeled litter | `exclude` | Unidentified |

## 4. Edge Cases

| Item or situation | Label | Why |
|---|---|---|
| Pizza box, greasy bottom | `trash` | Food grease contaminates paper recycling batches |
| Pizza box, clean lid only | `recycling` | Clean cardboard portion can be torn off and recycled |
| Bottle with liquid inside | `trash` (or empty first) | Liquids contaminate paper bales and add dead weight |
| Coffee cup with plastic lid | `trash` | Lined paper cup is trash; lid alone is ambiguous |
| Crushed aluminum can | `recycling` | Metal is sorted magnetically/eddy current and retained |
| Item too blurry to identify | `exclude` | Fails short-side resolution or visual quality criteria |

## 5. What the App Says

- **Recycling:** "Recycling bin: empty and rinse; flatten cardboard."
- **Special handling:** "Special handling: do not bin. Take to designated drop-off or check with campus facilities."
- **Trash:** "Trash bin: not accepted in standard campus recycling."
- **Not sure (low confidence < 0.60):** "Not sure. Check the label guide or ask campus facilities."
- **Always shown:** "General guidance only. Recycling rules vary by municipal and campus location. This coach does not replace campus facilities policy or make hazardous waste decisions."

## 6. Change Log

| Date | Who | Change |
|---|---|---|
| 2026-09-29 | Rickey Johnson | Initial skeleton created |
| 2026-10-04 | John Sampson | Completed 41-category TACO mapping, EPA edge cases, and app guidance cards |
