# data/

| Folder | In git? | What |
|---|---|---|
| `raw/` | No | Original images: `raw/taco/`, `raw/team/`. Sync from the team Drive folder `SmartRecyclingCoach-data/raw/`. |
| `processed/` | No | Cleaned, resized images named `<image_id>.jpg`, made by `clean.py`. Sync from Drive `processed/`, or rebuild them. |
| `metadata/` | Yes | `images.csv` (John), `reviews.csv` (Premajyoti), `clean.csv` and `splits.csv` (Rickey, generated). |

Column definitions: `docs/PROJECT_SPEC.md` §8. Never commit images: no faces, people, or personal info, and strip EXIF.
