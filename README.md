# Agent KIO Routing Dataset

## Purpose

Route customer messages to **Support (0)** or **Sales (1)**, and compare a trained ML classifier with Jev or a similar decision model.

**Flow:** Customer Message → Router → Support / Sales

## Dataset

- **File:** `Agent_KIO_Dataset_FINAL.xlsx`
- **Sheets:**
  - `Dataset`: the 60 messages
  - `Checks`: formulas that verify the dataset is valid
  - `Label_Rules`: the written labeling rules
- 60 synthetic English messages: 30 Support and 30 Sales.
- Includes paraphrases, negation, and mixed intent.

### Columns

| Column | What it is | Used as model input? |
|---|---|---|
| `ID` | Row number (1–60), for referring to a message | No |
| `Message` | The customer text | **Yes, the only input** |
| `Category` | Support or Sales (words) | No, reference answer |
| `Flag` | 0 = Support, 1 = Sales | No, reference answer |
| `Split` | Train or Test | No, used to separate the data |
| `Group_ID` | Messages that are near-duplicates share the same ID | No |
| `Type` | `plain`, `paraphrase`, `negation` or `mixed` | No, used only for error analysis |

## Labeling Rules

- **Support (0):** existing-service problems, complaints, billing questions, account help, technician issues, refunds.
- **Sales (1):** new purchases, subscriptions, packages, quotes, prices, promotions, devices.
- **Mixed intent:** an existing problem takes priority → **Support**.
- **Negation:** a negation word does not decide the label, the meaning does.
- Labels were agreed **before** testing and must not change after seeing results.

## Split

| Split | Support | Sales | Total |
|---|---|---|---|
| Train | 20 | 20 | 40 |
| Test | 10 | 10 | 20 |

- Use the predefined split.
- Near-duplicates are kept together: every `Group_ID` is entirely in Train or entirely in Test, so no test message has a twin in training. The `Checks` sheet confirms **0** groups cross the split.
- Evaluate both approaches on the **same 20 test messages**.

## Message Types

`Type` shows what kind of message each row is, so you can explain *which* messages a router gets wrong, not just how many.

| Type | Meaning | Example |
|---|---|---|
| `plain` | Ordinary message | My cable box is blinking red. |
| `paraphrase` | Has a near-duplicate twin with different wording | I hear static on my phone line. |
| `negation` | A negation word is central to the intent | I am not interested in TV, just give me the internet prices. |
| `mixed` | Problem and purchase together → Support | My router is completely broken, and I also want to buy a new smart TV package. |

If a message fits several types, the priority is: mixed > negation > paraphrase > plain.

| Split | plain | paraphrase | negation | mixed |
|---|---|---|---|---|
| Train | 16 | 19 | 3 | 2 |
| Test | 1 | 14 | 2 | 3 |

The test set is deliberately harder than the training set (only 1 plain message, 3 mixed-intent).

## Examples

| Message | Label | Type |
|---|---|---|
| I can't log into my account. | Support (0) | plain |
| What is the price of the premium fiber subscription? | Sales (1) | paraphrase |
| I want to add the sports channels, but my receiver isn't working at all. | Support (0) | mixed |
| I am not interested in TV, just give me the internet prices. | Sales (1) | negation |

## How to Use

```python
import pandas as pd

df = pd.read_excel("Agent_KIO_Dataset_FINAL.xlsx", sheet_name="Dataset")
train = df[df["Split"] == "Train"]
test  = df[df["Split"] == "Test"]

X_train, y_train = train["Message"], train["Flag"]   # input, answer
X_test,  y_test  = test["Message"],  test["Flag"]
```

Only `Message` is given to a model. `Flag`, `Category`, `Group_ID`, `Type` and `ID` are never inputs.

## Model Comparison

- **ML classifier:** learns from the 40 labeled training messages. Choose settings using the training data only (for example cross-validation), never the test set.
- **Decision model:** receives each message plus routing instructions, returns `customer_service` or `sales`. Validate that the output is one of the two allowed labels, then map it: `customer_service` → 0, `sales` → 1.
- Write the routing instructions from the labeling rules and training messages, not by adjusting them to fix a specific test message.

## Reporting Results

- Report actual correct/incorrect counts, not only accuracy.
- Each test error changes accuracy by **5 percentage points**.
- Break errors down by `Type` to explain where each approach fails.
- This small synthetic dataset does not establish real-world reliability. Treat it as a small comparative experiment.

## Judgement Calls

These labels are debatable and were fixed by team agreement:

- "Can I get a second line added to my account?" → Sales (new purchase)
- "I am moving and need to transfer my service." → Support (existing service)
- "I didn't receive the confirmation email for my renewal." → Support (missing email is the problem)
- "I don't want a contract, do you have monthly rolling plans?" → Sales (wants to buy)
