# TakeMeter Project Plan

## 1. Community

I will study discourse in **r/iRacing**, the Reddit community for the iRacing racing simulator. This community is a good fit for TakeMeter because discussion quality varies widely: members ask practical setup questions, analyze racing incidents, give racecraft advice, celebrate wins, and sometimes post emotional rants after crashes. The distinction matters because a useful community tool should recognize the difference between advice that helps drivers improve and posts that are mainly venting.

## 2. Label Taxonomy

I will classify each post/comment into exactly one of three labels.

### `racecraft_analysis`
A post that explains driving behavior, incident responsibility, race strategy, or technique using specific reasoning about what happened on track.

Clear examples:
- "You turned in as if the inside car wasn't there. Once he had overlap before turn-in, you needed to leave a lane."
- "Your braking point is okay, but you release the brake too quickly, which unloads the front tires and causes understeer."

### `practical_help`
A post that asks for or gives concrete help about equipment, settings, cars, tracks, rules, licenses, software, or troubleshooting.

Clear examples:
- "Is the Porsche Cup worth buying for C class if I already own a GT4?"
- "Lower your force feedback clipping first; if the wheel still oscillates on straights, add a small amount of damping."

### `emotional_reaction`
A post that mainly expresses frustration, excitement, humor, blame, celebration, or venting without enough specific reasoning to be useful as advice or analysis.

Clear examples:
- "I got punted again in rookies. This game is impossible."
- "Finally won my first race! I am never financially recovering from this subscription."

## 3. Hard Edge Cases and Decision Rules

### Edge case 1: Complaint with some evidence
Example: "The guy divebombed from a mile back and ruined my race. He was never making the corner."

Possible labels: `racecraft_analysis` or `emotional_reaction`.

Decision rule: If the post explains the incident with specific observable details, such as overlap, braking point, corner phase, racing line, or replay evidence, label it `racecraft_analysis`. If the post mainly blames another driver with only vague evidence, label it `emotional_reaction`.

### Edge case 2: Question that includes analysis
Example: "I keep losing the rear when trail braking into T1 at Spa. Am I braking too late or releasing too fast?"

Possible labels: `practical_help` or `racecraft_analysis`.

Decision rule: If the post's main purpose is asking for a solution, label it `practical_help`. If the post's main purpose is explaining why something happened or judging responsibility, label it `racecraft_analysis`.

### Edge case 3: Gear/racing recommendation with opinion
Example: "GT3 is way better than Porsche Cup for learning because the ABS lets you focus on racecraft first."

Possible labels: `practical_help` or `racecraft_analysis`.

Decision rule: If the post gives a recommendation about what to buy/use/do, label it `practical_help`, even if it includes a short reason. Only label `racecraft_analysis` when the reasoning is mainly about driving behavior or on-track decisions.

## 4. Data Collection Plan

I will collect at least 200 public posts or comments from r/iRacing. I will prioritize text-heavy discussion, question/help, and incident/racecraft threads rather than image-only memes because the classifier uses text.

Target distribution:
- `racecraft_analysis`: about 70 examples
- `practical_help`: about 70 examples
- `emotional_reaction`: about 70 examples

If one label is underrepresented after the first 200 examples, I will search within the subreddit for terms likely to surface that label:
- `racecraft_analysis`: "fault", "incident", "braking", "line", "overlap", "replay"
- `practical_help`: "setup", "buy", "wheel", "force feedback", "license", "track", "car"
- `emotional_reaction`: "rant", "frustrated", "finally won", "rookies", "crashed"

I will save all examples in one CSV file named `takemeter_dataset.csv` with columns:
- `text`
- `label`
- `notes`

The notebook will split this single file into train/validation/test using a 70/15/15 split.

## 5. Evaluation Metrics

I will report overall accuracy for both the fine-tuned DistilBERT model and the zero-shot Groq baseline. Accuracy is useful because the label distribution should be reasonably balanced, but it is not enough by itself.

I will also report per-class precision, recall, and F1 because the most important question is whether the model can learn all three discourse types, not just the most common one. I will use the confusion matrix to identify which label boundary is hardest, especially whether `racecraft_analysis` is confused with `emotional_reaction`.

## 6. Definition of Success

A useful classifier should beat the zero-shot baseline and achieve at least **0.70 macro F1** on the test set. I would consider it good enough for a prototype if:
- overall accuracy is at least 70%;
- every class has F1 above 0.60;
- the fine-tuned model improves over the Groq baseline by at least 5 percentage points, or performs similarly while being cheaper and local.

For real deployment in a community tool, I would want a larger dataset, stronger inter-annotator agreement, and more testing on new posts outside the original collection period.

## 7. AI Tool Plan

### Label stress-testing
I will ask an AI tool to generate boundary cases between `racecraft_analysis`, `practical_help`, and `emotional_reaction`. If I cannot label those examples consistently using the decision rules above, I will revise the definitions before annotating the full dataset.

### Annotation assistance
I may use an LLM to pre-label examples in batches, but I will manually review every label. I will track AI-assisted labels in the `notes` column using notes such as `AI prelabel reviewed` so I can disclose the workflow in the README.

### Failure analysis
After fine-tuning, I will paste the wrong predictions into an AI tool and ask it to identify recurring error patterns. I will verify those patterns myself by rereading the examples before including them in the README.
