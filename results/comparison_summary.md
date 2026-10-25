# Router comparison

| Metric | ML classifier | Decision model |
|---|---:|---:|
| Correct | 18 | 20 |
| Incorrect | 2 | 0 |
| Accuracy | 0.900 | 1.000 |
| Sales precision | 1.000 | 1.000 |
| Sales recall | 0.800 | 1.000 |
| Sales F1 | 0.889 | 1.000 |
| Average latency (ms) | 6.630 | 1466.788 |

Each test error = 5 percentage points.

## Errors by Type

| Type | ML classifier | Decision model |
|---|---:|---:|
| plain | 0 | 0 |
| paraphrase | 0 | 0 |
| negation | 2 | 0 |
| mixed | 0 | 0 |

## Disagreements

| ID | Message | True label | ML label | Decision label |
|---:|---|---:|---|---|
| 59 | I am not interested in TV, just give me the internet prices. | 1 | support | sales |
| 60 | No TV channels, just pure fiber broadband, how much? | 1 | support | sales |

## Non-numeric criteria

| Criterion | ML classifier | Decision model |
|---|---|---|
| Needs training data | yes | no |
| Setup and cost | local training; infrastructure dependent | API/account dependent |
| Explainability | pipeline and top terms | typed decisions and probabilities |
| License | TO VERIFY | TO VERIFY |
