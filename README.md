# Agent KIO Routing Dataset

## Purpose

Build and evaluate an intent router that directs customer messages to:

- **Support (0):** Existing-service problems, complaints, billing, account help, and existing requests.
- **Sales (1):** New purchases, packages, upgrades, prices, promotions, and quotes.

The project compares two approaches:

1. A traditional ML classifier trained on labeled examples.
2. A decision model/API (Jev or a suitable alternative) that follows written routing instructions without training on our dataset.

**System flow:** Customer Message → Intent Router → Flag (0 or 1) → Simulated Support or Sales Agent.

This is a routing experiment, not a complete chatbot or RAG pipeline.

## Dataset

- **Frozen file:** `Agent_KIO_Dataset_FROZEN.xlsx`
- **Total messages:** 60 synthetic English customer messages.
- **Classes:** 30 Support and 30 Sales.
- **Training set:** 40 messages (20 Support, 20 Sales).
- **Test set:** 20 messages (10 Support, 10 Sales).
- **Groups:** 41 `Group_ID` groups, consisting of 19 pairs and 22 single messages.

The dataset contains paraphrases, negation, and mixed-intent messages.

The dataset was reviewed, corrected, and independently verified. Three messages (IDs 17, 18, and 49) were replaced with Support messages containing negation about buying. All validation checks passed.

**Dataset status: FROZEN.** Do not modify messages, labels, types, or the predefined split.

### Columns

| Column | Description | Model input? |
|---|---|---|
| `ID` | Message identifier (1–60) | No |
| `Message` | Customer's message text | **Yes — the only input** |
| `Category` | Support or Sales | No — reference label |
| `Flag` | 0 = Support, 1 = Sales | No — target label |
| `Split` | Train or Test | No — identifies the split |
| `Group_ID` | Identifies messages grouped by similarity | No |
| `Type` | plain, paraphrase, negation, or mixed | No — used for error analysis |

## Labeling Rules

- **Support (0):** Existing-service problems, complaints, billing questions, account help, technician issues, refunds, and existing requests.
- **Sales (1):** New purchases, subscriptions, packages, upgrades, quotes, prices, promotions, and devices.
- **Mixed intent:** If a message contains both an existing problem and interest in buying, prioritize the existing problem and label it **Support (0)**.
- **Negation:** Determine the label from the message's meaning, not merely from the presence of negative words. For example, rejecting a purchase while requesting a repair is Support, whereas rejecting one product while asking for prices of another is Sales.
- **Label agreement:** The team agreed on the labeling rules before testing. Labels must not be changed to improve model results.

## Train/Test Split

| Split | Support | Sales | Total |
|---|---:|---:|---:|
| Train | 20 | 20 | 40 |
| Test | 10 | 10 | 20 |
| **Total** | **30** | **30** | **60** |

The predefined split must be used for both approaches.

Near-duplicate messages are kept in the same split. No `Group_ID` appears in both Train and Test, preventing leakage between grouped messages.

Both approaches must be evaluated on the **same 20 test messages**. Test messages must not be used to train or tune either approach.

## Message Types

The `Type` column supports error analysis. It helps explain which kinds of messages a model handles well or poorly.

| Type | Definition |
|---|---|
| `plain` | One clear intent, no negation or mixed intent, and no paraphrase partner in the same group. |
| `paraphrase` | Has a partner in the same group expressing the same intent using different wording. |
| `negation` | Contains negation rejecting a purchase, plan, contract, or customer status. Negation describing only a technical problem does not qualify. |
| `mixed` | Contains both an existing problem and interest in buying. Always labeled Support. |

If a message fits multiple types, the priority is: `mixed` > `negation` > `paraphrase` > `plain`.

### Verified Type Counts

| Split / Category | Plain | Paraphrase | Negation | Mixed | Total |
|---|---:|---:|---:|---:|---:|
| Train Support | 8 | 8 | 2 | 2 | 20 |
| Train Sales | 6 | 11 | 3 | 0 | 20 |
| Test Support | 0 | 6 | 1 | 3 | 10 |
| Test Sales | 0 | 8 | 2 | 0 | 10 |
| **Overall** | **14** | **33** | **8** | **5** | **60** |

The test set contains no plain messages. It includes 14 paraphrases, 3 negation messages, and 3 mixed-intent messages. These counts describe the dataset; they do not guarantee that either model will perform well on these cases.

## Examples

| Customer message | Category | Flag | Type |
|---|---|---:|---|
| My internet connection has been dropping constantly since yesterday. | Support | 0 | plain |
| What is the price of the premium fiber subscription? | Sales | 1 | paraphrase |
| My router is completely broken, and I also want to buy a new smart TV package. | Support | 0 | mixed |
| I'm not interested in any upgrade; I only need my phone line repaired. | Support | 0 | negation |
| I am not interested in TV, just give me the internet prices. | Sales | 1 | negation |

These are illustrative examples, not a replacement for the actual dataset rows.

## Validation Results

The frozen dataset passed the following checks:

- Exactly 60 rows with 30 Support and 30 Sales messages.
- Balanced Train split (20 Support, 20 Sales) and Test split (10 Support, 10 Sales).
- No `Group_ID` appears in both splits.
- No conflicting labels within a group.
- No duplicate messages.
- Every `Flag` matches its `Category`.
- All mixed-intent messages are labeled Support.
- Only messages with IDs 17, 18, and 49 differ from the original dataset.

**Frozen file:** `Agent_KIO_Dataset_FROZEN.xlsx`

**SHA-256:** `E606E3E8B1585D559E804901CD0F70869A51A4FD7AB2780FF03290A369A0162B`

The SHA-256 hash can be used to verify that a copy of the frozen file matches the verified version.

## How to Use the Dataset

```python
import pandas as pd

df = pd.read_excel(
    "Agent_KIO_Dataset_FROZEN.xlsx",
    sheet_name="Dataset"
)

train = df[df["Split"] == "Train"].copy()
test = df[df["Split"] == "Test"].copy()

# The only model input is Message.
X_train = train["Message"]
y_train = train["Flag"]

X_test = test["Message"]
y_test = test["Flag"]
```

Use only `Message` as the input feature. Never feed `ID`, `Category`, `Flag`, `Split`, `Group_ID`, or `Type` into the model.

The `Flag` is the target for training and the reference answer for evaluation. The `Type` column may be used after prediction to analyze errors.

## Model Comparison

### 1. Traditional ML Classifier

- Train on the 40 training messages.
- Choose an allowed classifier from the project brief: a linear classifier, Logistic Regression with degree-2 polynomial features, or an SVM with a linear or polynomial kernel.
- Convert text into numeric features. TF-IDF is a possible option, but the exact implementation should follow the instructor's requirements.
- Fit preprocessing and select settings using training data only.
- Evaluate on the 20 test messages.

### 2. Decision Model/API

- Choose Jev or a suitable open-source decision/classification alternative.
- Provide the customer message and written routing instructions.
- Validate the output against the allowed categories: `customer_service` and `sales`.
- Map the output to the common flag:
  - `customer_service` → `0`
  - `sales` → `1`
- Document the model, license, setup, instructions, output validation, and limitations.
- Write and freeze the routing instructions before evaluating the test set. Do not change them to fix specific test errors.

### 3. Evaluation

Both approaches must use the identical 20 test messages and the same reference labels.

Report:

- Correct and incorrect prediction counts.
- Accuracy and other appropriate classification metrics.
- Confusion matrices.
- Errors grouped by `Type`.
- A comparison table and evidence-based recommendation.

Each error changes test accuracy by **5 percentage points** because the test set contains only 20 messages.

## Known Limitations

- Only 20 test messages are available, so each error has a large effect on accuracy.
- The test set contains only 3 negation messages (2 groups) and 3 mixed-intent messages. Conclusions about these categories are indicative, not definitive.
- Mixed intent appears only with Support labels; there are no Sales-labeled messages that also mention a past problem.
- Some paraphrase groups share an intent but differ in topic details.
- Test topics such as smart-home cameras, unlimited data, laptops, and portable Wi-Fi do not appear in training, which may challenge a text-based ML model.
- The messages are synthetic and may not represent the diversity of real customer conversations.
- Results from this small experiment cannot establish real-world reliability or prove that one approach is universally better.

## Judgement Calls

The team agreed on the following interpretations:

- "Can I get a second line added to my account?" → **Sales (1)** — treated as a new purchase.
- "I am moving and need to transfer my service." → **Support (0)** — an existing service must be transferred.
- "I didn't receive the confirmation email for my renewal." → **Support (0)** — the missing email is the problem.
- "I don't want a contract, do you have monthly rolling plans?" → **Sales (1)** — the customer is exploring a purchase.

These decisions should remain consistent across both approaches.

## Current Project Status

**Completed:**
- Team plan and responsibilities.
- Dataset creation and exploration.
- Labeling rules and balanced split.
- Dataset corrections and independent validation.
- Frozen dataset file and checksum.

**Not yet completed according to the latest progress report:**
- Training and evaluating the ML classifier.
- Selecting, implementing, and evaluating the decision model.
- Comparing model results and analyzing errors.

## Next Steps

1. All three students review the 60 messages and approve the labels.
2. Student 2 selects and evaluates the decision model.
3. Student 3 builds and evaluates the traditional ML classifier.
4. Both approaches run on the same 20 test messages.
5. The team integrates the routing flags with simulated Support and Sales functions.
6. The team prepares the comparison, documents limitations and sources, and rehearses the eight-minute presentation.

**Project presentation:** Monday, 26 October 2026  
**Team size:** 3 students  
**Presentation limit:** 8 minutes

No full chatbot, real specialist agents, search tools, or RAG pipeline is required for this first-stage project.
