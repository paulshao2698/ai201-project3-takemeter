# TakeMeter Project Plan: Hacker News Comment Classifier

## 1. Community

I will study discourse in **Hacker News**, a public online community focused on software, startups, AI, engineering, security, product decisions, and technology culture. Hacker News is a good fit for TakeMeter because discussion quality and function vary widely: some comments provide detailed technical or business reasoning, some give practical advice, and some mainly express frustration, humor, agreement, or surprise.

The original project idea used r/iRacing. During implementation, Reddit collection became too slow and unreliable for the available timeline, so I pivoted to Hacker News. This planning document reflects the final implemented project.

## 2. Label Taxonomy

I will classify each comment into exactly one of three labels.

### `technical_analysis`

A comment that explains a technical, business, economic, or social claim using reasoning, tradeoffs, evidence, comparison, or causal explanation.

Clear examples:
- "The main issue is not the language feature itself but the deployment model, because latency and operational cost scale differently once traffic increases."
- "ClickHouse and Postgres solve different workloads: OLAP favors columnar scans, while OLTP needs row-level transactional consistency."

### `practical_advice`

A comment that gives or asks for actionable guidance, such as what tool to use, how to debug something, how to approach a workflow/career decision, or how to implement a solution.

Clear examples:
- "Try SQLite first and only move to Postgres when you need concurrent writes or managed backups."
- "If you are replacing Elastic, test whether ClickHouse supports your search workload before migrating logs."

### `emotional_reaction`

A comment whose main purpose is to express approval, frustration, surprise, humor, disappointment, sarcasm, or another immediate reaction without much supporting reasoning.

Clear examples:
- "This is ridiculous. I cannot believe people still defend this."
- "The screenshots are awful; just draw the diagram by hand."

## 3. Hard Edge Cases and Decision Rules

### Edge case 1: Advice with technical reasoning

Example: "ClickHouse is great for analytics, but I would not replace Postgres with it for OLTP because transactions and row updates are not the same workload."

Possible labels: `technical_analysis` or `practical_advice`.

Decision rule: If the main purpose is explaining a concept or tradeoff, label it `technical_analysis`. If the main purpose is recommending what someone should do or avoid, label it `practical_advice`.

### Edge case 2: Emotional comment with technical vocabulary

Example: "This JVM memory-layout explanation is nonsense. The whole section sounds AI-written."

Possible labels: `technical_analysis` or `emotional_reaction`.

Decision rule: If the comment mainly reacts or complains without developing reasoning, label it `emotional_reaction`, even if it contains technical words. If it explains why the claim is wrong using specific evidence, label it `technical_analysis`.

### Edge case 3: Short question about a tool

Example: "Can ClickHouse search? If not, why replace Elastic with it?"

Possible labels: `practical_advice` or `emotional_reaction`.

Decision rule: If the question is about tool suitability, setup, implementation, migration, or debugging, label it `practical_advice`. If it is mainly rhetorical sarcasm or venting, label it `emotional_reaction`.

## 4. Data Collection Plan

I will collect at least 200 public Hacker News comments using the public Hacker News API. I will focus on text comments rather than story titles alone because the classifier is meant to evaluate discourse in comments.

Target distribution:
- `technical_analysis`: about 100-150 examples
- `practical_advice`: about 60-100 examples
- `emotional_reaction`: about 50-80 examples

The final dataset will be saved in one CSV file named `takemeter_dataset.csv` with columns:
- `text`
- `label`
- `notes`
- `source_type`
- `source_url`
- `parent_title`

The notebook will split this single file into train/validation/test using a 70/15/15 split.

## 5. Evaluation Metrics

I will report overall accuracy for both the fine-tuned DistilBERT model and the zero-shot Groq baseline. Accuracy is useful because no single class should dominate more than 70% of the dataset.

I will also examine per-class precision, recall, F1, and the confusion matrix because the most important question is whether the model can learn all three discourse functions. I expect the hardest boundary to be `technical_analysis` vs. `practical_advice`, because advice in Hacker News often contains technical explanation.

## 6. Definition of Success

A useful classifier should beat the zero-shot baseline and achieve at least about 70% accuracy or strong macro-F1. I would consider it good enough for a prototype if:
- overall accuracy is at least 70%;
- every class has non-trivial F1;
- the fine-tuned model improves over the Groq baseline or provides a clear cost/locality advantage.

If the fine-tuned model performs worse than the baseline, I will treat that as an important result and analyze why.

## 7. AI Tool Plan

### Label stress-testing

I will ask an AI tool to generate boundary cases between `technical_analysis`, `practical_advice`, and `emotional_reaction`. If I cannot classify the examples consistently, I will revise the decision rules before finalizing the dataset.

### Annotation assistance

I may use an LLM to pre-label examples, but I will review labels and focus especially on borderline cases. I will disclose this workflow in the README.

### Failure analysis

After fine-tuning, I will use an AI tool to summarize wrong-prediction patterns, then verify those patterns by rereading the examples and comparing them to the confusion matrix.
