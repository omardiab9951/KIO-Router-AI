# AGENT KIO PROJECT: PROGRESS SUMMARY

---

## 1. PROJECT GOAL
Build a small intent router for the customer chatbot **Agent KIO**. The router reads a customer message and returns a flag:
- `0` = Support
- `1` = Sales

We compare two approaches on the same test messages:
* **Approach A:** A traditional ML classifier trained on our examples.
* **Approach B:** A decision model (Jev or an open-source alternative) that follows written routing instructions with no training by us.

Both approaches map to the same flag. Two simulated agents (functions that print their names) receive the message. A full chatbot or RAG pipeline is out of scope.

> **Presentation Details:**  
> **Date:** Monday 26 October 2026  
> **Format:** Teams of 3, maximum 8 minutes, all three students speak.

---

## 2. LABELING RULE (Agreed Before Testing)
* **Support:** Existing problems, complaints, billing, account help, existing requests.
* **Sales:** New purchases, plans, upgrades, quotes, promotions.
* **Mixed Intent:** (A problem **AND** interest in buying): Label as **Support** (`0`), because the existing problem has priority.

---

## 3. WORK DONE SO FAR
* **Team Plan:** Written covering roles, shared tasks, and implementation order.
* **Dataset Creation:** Student 1 created the dataset and an exploration notebook that validates it.
* **Dataset Review:** Reviewed in detail. Weaknesses identified:
  * No negation messages in Support.
  * Only one negation group in the test set.
  * Inconsistent `Type` labels.
* **Fixes Applied via Codex:**
  1. Replaced 3 messages (IDs 17, 18, 49) with Support messages using negation about buying (e.g., *"I'm not looking to buy anything; I just need my bill explained."*).
  2. Audited the `Type` column against written definitions; no further changes needed.
  3. Saved a locked copy: `Agent_KIO_Dataset_FROZEN.xlsx`.
* **Verification:** The frozen file was verified independently. All checks passed. *(Note: Codex's text reports contained two typos regarding a wrong Train Support total and wrong negation IDs, but the data file itself is correct).*
* **Current Status:** No model has been trained or tested yet.

---

## 4. DATASET SPECIFICATIONS

* **File Name:** `Agent_KIO_Dataset_FROZEN.xlsx`
* **SHA-256 Checksum:** `E606E3E8B1585D559E804901CD0F70869A51A4FD7AB2780FF03290A369A0162B`
* **Volume:** 60 synthetic English messages regarding telecom customer service (30 Support / 30 Sales).

### Schema (Columns)
1. **ID:** Row number (1 to 60)
2. **Message:** The customer text input
3. **Category:** `Support` or `Sales`
4. **Flag:** `0` (Support) or `1` (Sales)
5. **Split:** `Train` or `Test`
6. **Group_ID:** Groups paraphrases together (41 total groups: 19 pairs, 22 single messages)
7. **Type:** `plain`, `paraphrase`, `negation`, or `mixed`

### Type Definitions
* **`plain`:** One clear intent, alone in its group, no negation, not mixed.
* **`paraphrase`:** Has a partner in the same group expressing the same intent using different phrasing.
* **`negation`:** Contains a negation that rejects a purchase, plan, contract, or customer status. *(Negative words describing a problem like "isn't working" do not count).*
* **`mixed`:** Contains both an existing problem and interest in buying; always categorized as **Support**.

### Train / Test Split
*Balanced by class; groups never split across Train and Test sets.*
* **Train Set:** 40 messages (20 Support, 20 Sales)
* **Test Set:** 20 messages (10 Support, 10 Sales)

### Type Distribution Breakdown
* **Train Support:** 8 plain, 8 paraphrase, 2 mixed, 2 negation
* **Train Sales:** 6 plain, 11 paraphrase, 3 negation
* **Test Support:** 6 paraphrase, 3 mixed, 1 negation
* **Test Sales:** 8 paraphrase, 2 negation
* **Overall Totals:** 14 plain, 33 paraphrase, 8 negation, 5 mixed

### Representative Examples
* **Support:** *"My internet connection has been dropping constantly since yesterday."*
* **Sales:** *"What is the price of the premium fiber subscription?"*
* **Mixed (Support):** *"My router is completely broken, and I also want to buy a new smart TV package."*
* **Negation (Support):** *"I'm not interested in any upgrade; I only need my phone line repaired."*
* **Negation (Sales):** *"I am not interested in TV, just give me the internet prices."*

---

## 5. DATASET USAGE
* **Training Phase:** The 40 training messages are used exclusively by the ML classifier to learn intent patterns.
* **Evaluation Phase:** The 20 test messages evaluate **both** approaches. The decision model is not trained, so it is evaluated directly on these 20 messages.
* **Error Analysis:** The `Type` column allows tracking specific failure modes (e.g., *"The ML model struggles with negation structures"*).
* **Test Complexity:** The test set intentionally contains zero `plain` messages—only `paraphrases`, `mixed-intent`, and `negation` cases to rigorously evaluate model performance on complex inputs.

---

## 6. VALIDATION CHECKS PASSED
- [x] Total 60 rows, exact 30/30 class balance (Train: 20/20, Test: 10/10).
- [x] Zero data leakage: No `Group_ID` spans both Train and Test splits.
- [x] Consistency: No group contains conflicting labels.
- [x] Uniqueness: No duplicate text messages.
- [x] Integrity: `Flag` strictly matches `Category` on every row.
- [x] Rule Enforcement: All `mixed` messages are correctly assigned to `Support`.
- [x] Audit Trace: Exactly 3 messages modified from the original draft (IDs 17, 18, 49).

---

## 7. KNOWN LIMITATIONS
*(To be transparently communicated during the presentation)*

1. **Small Sample Size:** With only 20 test messages, a single error shifts model accuracy by $5\%$.
2. **Limited Edge Cases:** Only 3 negation messages (2 groups) and 3 mixed messages exist in the test set. Findings on these sub-types are indicative rather than statistically conclusive.
3. **Asymmetric Mixed Intent:** Mixed intent is represented exclusively in Support. There are no Sales messages that reference a resolved past problem.
4. **Subtle Group Variations:** Some paraphrase pairs share intent but vary slightly in domain details (e.g., G37 and G39).
5. **Out-of-Vocabulary (OOV) Risk:** Specific test topics (smart-home cameras, unlimited data, laptops, portable Wi-Fi) do not appear in the training split. This may disadvantage traditional ML models reliant on exact word occurrences.
6. **Synthetic Bias:** Synthetic data with $N=60$ does not guarantee real-world user performance.

---

## 8. EXPERIMENTAL GOVERNANCE RULES
1. **Data Freeze:** `Agent_KIO_Dataset_FROZEN.xlsx` is locked. No edits to text, labels, types, or splits are permitted.
2. **Prompt/Instruction Integrity:** Routing instructions for the decision model must be authored prior to testing and frozen (no post-test tweaking based on test failures).
3. **Hyperparameter Isolation:** ML model choices and feature extraction techniques must rely strictly on training data.
4. **Standardized Benchmarking:** Both models will be evaluated on the exact same 20 test messages.

---

## 9. NEXT STEPS & DIVISION OF LABOR

* **Student 2:** 
  * Select the decision model engine.
  * Author clear routing instructions.
  * Validate output integrity.
  * Run benchmark against the 20 test messages.
  * Document setup steps and licensing.

* **Student 3:** 
  * Construct the ML classification pipeline (e.g., TF-IDF + Logistic Regression or SVM).
  * Visualize decision boundary / feature importances where applicable.
  * Evaluate on the identical 20 test messages.
  * Conduct comparative error analysis and formulate final recommendations.

* **All Team Members:**
  * Review all 60 dataset instances for final sign-off.
  * Build the head-to-head comparison metrics table.
  * Design presentation slides.
  * Conduct at least two timed presentation dry runs (8-minute strict limit).