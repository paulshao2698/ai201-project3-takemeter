# TakeMeter: r/iRacing Discourse Quality Classifier

TakeMeter is a fine-tuned text classifier that evaluates discourse style in the r/iRacing community. The project classifies public posts/comments into three labels: `racecraft_analysis`, `practical_help`, and `emotional_reaction`.

## Project Summary

Online sim-racing communities contain many different kinds of discussion. Some posts help drivers understand racecraft or improve technique, some ask for practical help, and some mainly express frustration or excitement. This project tests whether a small fine-tuned DistilBERT model can learn those distinctions from a 200+ example labeled dataset.

## Community

I chose r/iRacing because it has active, text-heavy discussion around race incidents, driving technique, hardware/software setup, car and track purchases, and emotional reactions after races. These distinctions matter because regular community members value useful advice and analysis, but the subreddit also contains many heat-of-the-moment reactions.

## Labels

| Label | Definition |
|---|---|
| `racecraft_analysis` | Explains driving behavior, incident responsibility, race strategy, or technique using specific reasoning about what happened on track. |
| `practical_help` | Asks for or gives concrete help about equipment, settings, cars, tracks, rules, licenses, software, or troubleshooting. |
| `emotional_reaction` | Mainly expresses frustration, excitement, humor, blame, celebration, or venting without enough specific reasoning to be useful as advice or analysis. |

## Dataset

Dataset file: `takemeter_dataset.csv`

Minimum columns:
- `text`
- `label`
- `notes`

Data source: public r/iRacing posts/comments.

Labeling process:
1. Read each post/comment.
2. Assign exactly one label using the definitions in `planning.md`.
3. Add notes for ambiguous examples.
4. Check label distribution before training.

### Label Distribution

Replace this table after labeling:

| Label | Count |
|---|---:|
| `racecraft_analysis` | TODO |
| `practical_help` | TODO |
| `emotional_reaction` | TODO |
| **Total** | TODO |

## Difficult Labeling Examples

Replace with three real examples from the dataset.

| Text excerpt | Possible labels | Final label | Why |
|---|---|---|---|
| TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO |

## Model and Training

Base model: `distilbert-base-uncased`

Training approach:
- Tokenize post/comment text with a maximum length of 256 tokens.
- Fine-tune DistilBERT as a sequence classifier.
- Use the starter notebook's 70/15/15 train/validation/test split.
- Evaluate on the locked test set.

Hyperparameters:
- Epochs: 3
- Learning rate: 2e-5
- Batch size: 16
- Weight decay: 0.01
- Warmup steps: 50

I kept the default hyperparameters because the dataset is small, and increasing epochs too much could overfit the training examples.

## Zero-Shot Baseline

The baseline uses Groq `llama-3.3-70b-versatile` with no task-specific training. It classifies the same test examples as the fine-tuned model.

Prompt used in notebook:

```text
You are classifying posts from the r/iRacing Reddit community.
Assign each post to exactly one of the following categories.

racecraft_analysis: A post that explains driving behavior, incident responsibility, race strategy, or technique using specific reasoning about what happened on track.
Example: "You turned in as if the inside car wasn't there. Once he had overlap before turn-in, you needed to leave a lane."

practical_help: A post that asks for or gives concrete help about equipment, settings, cars, tracks, rules, licenses, software, or troubleshooting.
Example: "Is the Porsche Cup worth buying for C class if I already own a GT4?"

emotional_reaction: A post that mainly expresses frustration, excitement, humor, blame, celebration, or venting without enough specific reasoning to be useful as advice or analysis.
Example: "I got punted again in rookies. This game is impossible."

Respond with ONLY the label name.
Do not explain your reasoning.

Valid labels:
racecraft_analysis
practical_help
emotional_reaction
```

## Evaluation Results

Replace after running the notebook.

| Model | Accuracy |
|---|---:|
| Zero-shot Groq baseline | TODO |
| Fine-tuned DistilBERT | TODO |

### Per-Class Metrics: Fine-Tuned DistilBERT

| Label | Precision | Recall | F1 |
|---|---:|---:|---:|
| `racecraft_analysis` | TODO | TODO | TODO |
| `practical_help` | TODO | TODO | TODO |
| `emotional_reaction` | TODO | TODO | TODO |

### Per-Class Metrics: Groq Baseline

| Label | Precision | Recall | F1 |
|---|---:|---:|---:|
| `racecraft_analysis` | TODO | TODO | TODO |
| `practical_help` | TODO | TODO | TODO |
| `emotional_reaction` | TODO | TODO | TODO |

### Confusion Matrix: Fine-Tuned DistilBERT

Rows are true labels; columns are predicted labels.

| True \ Predicted | `racecraft_analysis` | `practical_help` | `emotional_reaction` |
|---|---:|---:|---:|
| `racecraft_analysis` | TODO | TODO | TODO |
| `practical_help` | TODO | TODO | TODO |
| `emotional_reaction` | TODO | TODO | TODO |

## Wrong Prediction Analysis

Replace after reviewing notebook output.

### Error 1
- Text:
- True label:
- Predicted label:
- Confidence:
- Analysis:

### Error 2
- Text:
- True label:
- Predicted label:
- Confidence:
- Analysis:

### Error 3
- Text:
- True label:
- Predicted label:
- Confidence:
- Analysis:

## Sample Classifications

Replace with 3–5 outputs from the fine-tuned model.

| Text excerpt | Predicted label | Confidence | Comment |
|---|---|---:|---|
| TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO |

## Reflection: Intended vs. Learned Behavior

The intended classifier should distinguish post function: analysis, help, or reaction. After evaluation, I will compare that intention with the model's actual error patterns. I expect the hardest boundary to be between `racecraft_analysis` and `emotional_reaction` because many incident posts contain both blame and some description of what happened.

## Spec Reflection

The planning spec helped by forcing label definitions and edge-case rules before annotation. This reduced the chance that I would change the label meaning halfway through the dataset.

One expected divergence is that the final label distribution may not exactly match the original target distribution. If one class is harder to collect, I will collect additional examples from targeted search terms instead of accepting a strongly imbalanced dataset.

## AI Usage

I used AI assistance in the following ways:

1. **Label design stress test:** I asked AI to generate boundary cases between my labels. I used this to revise the decision rules in `planning.md`.
2. **Documentation drafting:** I used AI to draft the initial README and planning document, then revised the content to match my actual dataset and results.
3. **Failure analysis:** After training, I will use AI to look for patterns in wrong predictions, then verify the patterns manually before reporting them.

If AI was used for pre-labeling examples, I will disclose that here and explain that every label was manually reviewed.

## How to Run

1. Open the starter Colab notebook.
2. Set runtime to T4 GPU.
3. Upload `takemeter_dataset.csv`.
4. Set the label map:

```python
LABEL_MAP = {
    "racecraft_analysis": 0,
    "practical_help": 1,
    "emotional_reaction": 2,
}
```

5. Run Sections 1 and 2.
6. Run Section 5 for the Groq baseline.
7. Run Sections 3 and 4 for fine-tuning and evaluation.
8. Run Section 6 to export `evaluation_results.json` and `confusion_matrix.png`.
9. Commit all project files to GitHub.

## Repository Contents

| File | Purpose |
|---|---|
| `planning.md` | Project design, label definitions, data plan, success criteria |
| `takemeter_dataset.csv` | Labeled examples |
| `README.md` | Final project report |
| `evaluation_results.json` | Exported evaluation summary |
| `confusion_matrix.png` | Confusion matrix image |
| `Copy_of_ai201_project3_takemeter_starter_clean.ipynb` | Colab training/evaluation notebook |
