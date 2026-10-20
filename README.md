Agent KIO Routing Dataset
Purpose
Route customer messages to Support (0) or Sales (1) and compare a trained ML classifier with Jev or a similar decision model.

Flow: Customer Message ... Router ... Support / Sales
Dataset
- File: Agent_KIO_Dataset_v3(4).xlsx
- Sheet: Dataset
- 60 synthetic English messages: 30 Support and 30 Sales.
- Includes paraphrases, negation, and mixed intent.
- Columns: Message, Category, Flag, Split.
Labeling Rules
- Support (0): Existing-service problems, complaints, billing questions, and account assistance.
- Sales (1): New purchases, subscriptions, packages, and quotes.
- Mixed intent: Existing problems take priority → Support.
- Agree on labels before testing.
Split
Split	Support	Sales	Total
Train	20	20	40
Test	10	10	20


Use the predefined split and keep near-duplicates together. Evaluate both approaches on the same test messages. Only Message is the input; labels are reference answers.
Examples
Message	Label
I can't log into my account.	Support (0)
What is the price of the premium fiber subscription?	Sales (1)
I want to add the sports channels, but my receiver isn't working at all.	Support (0)


Model Comparison
The ML classifier learns from the 40 labeled training messages. The decision model receives messages and routing instructions; validate its output and map it to 0 or 1.

Report actual test results. Each test error changes accuracy by 5 percentage points. This small synthetic dataset does not establish real-world reliability.

