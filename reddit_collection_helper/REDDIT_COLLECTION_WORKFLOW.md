# Reddit Data Collection Workflow for TakeMeter

## Goal

Collect 200+ public r/iRacing posts/comments and manually label them for:

- `racecraft_analysis`
- `practical_help`
- `emotional_reaction`

The script creates candidates, not final labels. You must review every row yourself.

## Step 1: Install requests

```bash
pip install requests
```

## Step 2: Run the collector

From your repo root:

```bash
python tools/collect_reddit_candidates.py
```

It will create:

```text
data/iracing_reddit_candidates.csv
```

## Step 3: Review the CSV

Open the CSV in Excel or Google Sheets.

Important columns:

| Column | How to use |
|---|---|
| `text` | The post/comment to classify |
| `suggested_label` | Rough keyword suggestion only |
| `label` | Your final human-reviewed label |
| `notes` | Use this for hard edge cases |

Do not blindly trust `suggested_label`.

## Step 4: Build the final dataset

Keep only the rows you reviewed. Aim for about:

| Label | Target |
|---|---:|
| `racecraft_analysis` | 65–75 |
| `practical_help` | 65–75 |
| `emotional_reaction` | 65–75 |

Save as:

```text
takemeter_dataset.csv
```

The starter notebook expects at least:

```csv
text,label,notes
```

You can keep the extra metadata columns if the notebook only selects `text` and `label`. If the notebook errors, export a simplified CSV with only those three columns.

## Label rules

### `racecraft_analysis`

Use this when the post explains driving behavior, incident responsibility, line choice, braking, defending, overtaking, safety, or strategy with specific reasoning.

Example pattern:

```text
The inside car had overlap before turn-in, so the outside car needed to leave space.
```

### `practical_help`

Use this when the post asks for or gives concrete help about settings, hardware, software, cars, tracks, purchases, licenses, training, or troubleshooting.

Example pattern:

```text
What GT4 should I buy for C class if I already own Watkins Glen and Spa?
```

### `emotional_reaction`

Use this when the post mainly vents, celebrates, complains, jokes, or reacts emotionally without much reasoning.

Example pattern:

```text
I got punted again on lap one. Rookies are impossible.
```

## Hard edge-case rule

When a post is emotional but contains specific, useful reasoning, label it by the useful reasoning.

- Emotional + actual incident reasoning → `racecraft_analysis`
- Emotional + concrete help request → `practical_help`
- Emotional only → `emotional_reaction`
