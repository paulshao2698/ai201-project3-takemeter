# TakeMeter: Hacker News Comment Classifier

TakeMeter is a fine-tuned text classifier that evaluates discourse function in public Hacker News comments. The final project classifies each comment into one of three labels: `technical_analysis`, `practical_advice`, or `emotional_reaction`.

This README intentionally reflects the final implemented version of the project. The original plan used r/iRacing, but Reddit collection became impractical during implementation, so the project pivoted to Hacker News. The dataset, label map, notebook prompt, and evaluation results all use the Hacker News label taxonomy.

## Project Summary

Online technical communities contain a mix of deep analysis, practical guidance, and quick reactions. Hacker News is a useful test case because comments are text-heavy and often sit near the boundary between technical reasoning, advice, and opinion. This project tests whether a small fine-tuned DistilBERT model can learn those discourse functions from a 300-example labeled dataset, and compares it against a zero-shot Groq LLM baseline.

## Community

The community studied is **Hacker News**, a public discussion community focused on software, startups, AI, engineering, security, product decisions, and technology culture. I chose Hacker News because comments are text-heavy and varied: some comments make structured arguments about technology or business, some offer practical implementation or career advice, and some mainly express frustration, humor, agreement, or surprise.

## Labels

| Label | Definition |
|---|---|
| `technical_analysis` | The comment explains a technical, business, economic, or social claim using reasoning, tradeoffs, evidence, comparison, or causal explanation. |
| `practical_advice` | The comment gives or asks for actionable guidance, such as tools, debugging steps, career/workflow advice, implementation suggestions, or recommendations. |
| `emotional_reaction` | The comment mainly expresses approval, frustration, surprise, humor, complaint, excitement, or another immediate reaction without much supporting reasoning. |

### Label Boundary Rules

The hardest boundary is between `technical_analysis` and `practical_advice`, because Hacker News users often give advice using technical reasoning. I used this decision rule: if the main purpose is to explain why something is true, I label it `technical_analysis`; if the main purpose is to tell someone what to do, use, try, avoid, or choose, I label it `practical_advice`.

The second hard boundary is between `technical_analysis` and `emotional_reaction`. If a comment contains technical words but mainly expresses irritation, sarcasm, or approval without a developed argument, I label it `emotional_reaction`.

## Dataset

Dataset file: `takemeter_dataset.csv`

Source: public Hacker News comments collected using the public Hacker News API and labeled for this classroom classification task. The final training file stores the comment text, label, optional notes, source type, source URL, and parent story title. Usernames are not included.

### Label Distribution

| Label | Count | Share |
|---|---:|---:|
| `technical_analysis` | 146 | 48.7% |
| `practical_advice` | 84 | 28.0% |
| `emotional_reaction` | 70 | 23.3% |
| **Total** | **300** | **100.0%** |

The dataset is not perfectly balanced, but no class exceeds 70% of the data, and each class has enough examples to be represented in train/validation/test splits.

## Difficult Labeling Examples

| Text excerpt | Possible labels | Final label | Why |
|---|---|---|---|
| "18446744073709551616 possible values and you can't spare 1 for null? :) TIL that Rust has NonZeroU64..." | `technical_analysis`, `practical_advice` | `practical_advice` | The comment includes a technical observation but points to a concrete Rust mechanism that solves the issue. |
| "Also, the images were ruinously far off from what they intended to convey. Dude, just draw a picture by hand..." | `emotional_reaction`, `practical_advice` | `emotional_reaction` | It includes a suggestion, but the main function is criticism/frustration about the article quality. |
| "Value types kind of definitively don't have null, right? You can have a zero int but not a null int..." | `technical_analysis`, `practical_advice` | `technical_analysis` | The main purpose is conceptual explanation about value types and nullability rather than advice. |

## Model and Training

Base model: `distilbert-base-uncased`

Training approach:
- Tokenized Hacker News comment text.
- Used the starter notebook's 70/15/15 train/validation/test split.
- Fine-tuned DistilBERT as a sequence classifier.
- Evaluated on the same locked test set used by the Groq baseline.

Hyperparameters:
- Epochs: 3
- Learning rate: 2e-5
- Batch size: 16
- Base model: `distilbert-base-uncased`

I kept the default hyperparameters because the dataset is small. With only 300 examples, increasing epochs too much could lead to overfitting.

## Zero-Shot Baseline

The baseline uses Groq `llama-3.3-70b-versatile` with no task-specific training. It classifies the same test examples as the fine-tuned model.

The baseline prompt used the same three Hacker News labels and instructed the model to output only one exact label name.

## Evaluation Results

The committed `evaluation_results.json` reports the following results:

| Model | Accuracy |
|---|---:|
| Zero-shot Groq baseline | 0.5333 |
| Fine-tuned DistilBERT | 0.4889 |
| Difference | -0.0444 |

The fine-tuned model performed worse than the zero-shot baseline by 4.44 percentage points. This is an important project finding, not just a bad score. It suggests that the small training set and noisy label boundaries were not enough for DistilBERT to learn the intended discourse-function distinction better than a large instruction-tuned LLM.

### What the Accuracy Result Means

The fine-tuned model did not meet the original success criteria. My planned success threshold was for the fine-tuned model to beat the baseline and reach at least roughly 70% accuracy or strong macro-F1. Instead, the zero-shot baseline did better. The most likely reasons are:

1. **Small dataset size:** 300 comments is enough to run a fine-tuning pipeline, but not enough for a subtle subjective discourse task.
2. **Label ambiguity:** Many Hacker News comments combine explanation, advice, and emotional tone in the same text.
3. **Surface vocabulary bias:** The fine-tuned model appeared to rely heavily on technical vocabulary. Comments mentioning Java, ClickHouse, Rust, SQL, or databases were often treated as `technical_analysis`, even when the comment's function was advice or reaction.
4. **AI-assisted annotation noise:** The labels were AI-assisted and reviewed, but some borderline rows may still be inconsistent. This can hurt a small fine-tuned model more than a zero-shot LLM.

## Fine-Tuned Confusion Matrix

The committed `confusion_matrix.png` is the visual confusion matrix from the notebook. The main qualitative pattern was over-prediction of `technical_analysis`, especially for comments that contained software/tool vocabulary.

A representative markdown version of the fine-tuned error pattern is:

| True \ Predicted | `technical_analysis` | `practical_advice` | `emotional_reaction` |
|---|---:|---:|---:|
| `technical_analysis` | high | low | low |
| `practical_advice` | high | low | low |
| `emotional_reaction` | medium/high | low | low/medium |

The most important takeaway is that the model did not learn `practical_advice` as a stable class. It often treated advice-like comments as analysis because they contained technical terminology.

## Wrong Prediction Analysis

### Error 1

- **Text excerpt:** "Same we are also stuck with ES wish could migrate to clickhouse but not able to do so because of the legacy load."
- **True label:** `practical_advice`
- **Predicted label:** `technical_analysis`
- **Analysis:** The model likely focused on technical terms such as ES, ClickHouse, and legacy load. However, the comment is closer to practical discussion about migration constraints than a structured technical argument.

### Error 2

- **Text excerpt:** "And here I thought engineers were mostly logical and objective. This thread is very entertaining."
- **True label:** `emotional_reaction`
- **Predicted label:** `technical_analysis`
- **Analysis:** This is mainly sarcastic emotional commentary. The model may have been misled by words such as "engineers," "logical," and "objective," which sound analytical even though the comment does not actually develop an argument.

### Error 3

- **Text excerpt:** "Can ClickHouse to search? If not why did you seek to replace Elastic with it"
- **True label:** `practical_advice`
- **Predicted label:** `emotional_reaction`
- **Analysis:** The short phrasing is informal and slightly confrontational, which may have pushed the model toward reaction. But the comment is asking a practical architecture/tool-choice question.

### Error 4

- **Text excerpt:** "I wonder if this could be practical for controlled environment devices like game consoles."
- **True label:** `emotional_reaction`
- **Predicted label:** `technical_analysis`
- **Analysis:** This row is also a labeling ambiguity. It could arguably be `technical_analysis` because it proposes an application context. This shows that some model errors may partly reflect noisy labels rather than model behavior alone.

## Sample Classifications

| Text excerpt | Predicted label | Confidence | Comment |
|---|---|---:|---|
| "The JVM can now store the values themselves in the array..." | `technical_analysis` | medium | Reasonable because the comment discusses memory layout and representation details. |
| "Try using SQLite first and only move to Postgres when you need concurrent writes..." | `practical_advice` | medium | Reasonable because the comment gives actionable guidance. |
| "This is ridiculous. I cannot believe people still defend this." | `emotional_reaction` | medium | Reasonable because the text expresses frustration without supporting reasoning. |
| "Can ClickHouse search? If not why replace Elastic with it?" | `emotional_reaction` | low | Incorrect or debatable; this should probably be `practical_advice` because it asks about tool suitability. |

## Reflection: Intended vs. Learned Behavior

I intended the classifier to distinguish the function of a comment: analysis, advice, or reaction. The fine-tuned model instead appeared to learn a shallower shortcut: comments with technical vocabulary are likely `technical_analysis`. This shortcut works for many Hacker News comments but fails on practical advice because advice often also contains technical words.

The underperformance compared with the Groq baseline is meaningful. A large instruction-tuned model can use the label definitions directly and reason about the function of a comment. DistilBERT, fine-tuned on only 300 examples, had to infer those boundaries from limited examples. The result suggests that fine-tuning a small model is not automatically better than prompting a strong zero-shot model, especially when labels are subjective and overlap.

To improve this project, I would collect a larger and more balanced dataset, manually review all borderline examples more carefully, and create more examples where `practical_advice` contains technical vocabulary. I would also add inter-annotator agreement to measure whether the labels are clear to humans before expecting a model to learn them.

## Spec Reflection

The original spec helped by forcing me to define labels, data sources, evaluation metrics, and success criteria before training. The biggest implementation divergence was the pivot from r/iRacing to Hacker News after Reddit API/browser collection became too slow and unreliable for the project timeline.

The mistake in the first submission was that I pivoted the dataset and notebook labels but did not update `README.md` and `planning.md`. That created a serious mismatch between documentation and implementation. This resubmission fixes that by making the community, labels, dataset, notebook label map, and evaluation discussion all refer to Hacker News.

## AI Usage

I used AI assistance in the following ways:

1. **Project pivot planning:** I used AI to identify Hacker News as a practical replacement community after Reddit collection became blocked or too slow.
2. **Notebook debugging:** I used AI to fix the Groq baseline parsing issue so the baseline output matched the expected label names.
3. **Failure analysis:** I used AI to help identify patterns in wrong predictions, then connected those patterns to the confusion matrix and example errors.

## How to Run

1. Open the starter Colab notebook.
2. Set runtime to T4 GPU.
3. Upload `takemeter_dataset.csv`.
4. Set the label map:

```python
LABEL_MAP = {
    "technical_analysis": 0,
    "practical_advice": 1,
    "emotional_reaction": 2,
}
```

5. Run Sections 1 and 2.
6. Run Section 5 for the Groq baseline.
7. Run Sections 3 and 4 for fine-tuning and evaluation.
8. Run Section 6 to export `evaluation_results.json` and `confusion_matrix.png`.

## Repository Contents

| File | Purpose |
|---|---|
| `planning.md` | Updated Hacker News project design, label definitions, and evaluation plan |
| `takemeter_dataset.csv` | Final labeled Hacker News dataset |
| `hn_candidates_labeled_full.csv` | Full labeled candidate file with metadata |
| `evaluation_results.json` | Exported evaluation summary |
| `confusion_matrix.png` | Fine-tuned model confusion matrix |
| `README.md` | Final project report |
| `Copy_of_ai201_project3_takemeter_starter_clean.ipynb` | Colab training/evaluation notebook |
