# KIO Router AI — System Branch

## 1. Project Overview

**KIO Router AI** is a customer-message routing system designed to classify incoming messages into two categories:

- **Support (Flag 0):** Messages about existing services, complaints, billing, account issues, and existing orders.
- **Sales (Flag 1):** Messages about new purchases, package upgrades, pricing, promotions, and sales inquiries.

The purpose of the system is to help route customer messages to the appropriate simulated agent based on their intent.

This repository branch focuses on the **Decision AI implementation and frontend**. The machine learning implementation is currently excluded and its folders are reserved for Student 3.

## 2. Branch Scope

The `System` branch contains the current Decision AI system, its web interface, supporting modules, dataset, evaluation utilities, and reserved directories for future machine learning work.

The branch includes:

- A Streamlit-based frontend.
- A Decision AI router powered by Cloudflare Clef.
- Routing instructions defining Support and Sales classification rules.
- Input validation and dataset integrity checks.
- Simulated Support and Sales agents.
- A frozen Excel dataset used for project data and evaluation.
- Decision-model testing and evaluation scripts.
- Empty directories reserved for future machine learning and comparison components.

**Important:** The current implementation does not include the trained ML classifier. Its future implementation is reserved for Student 3.

## 3. Frontend

The frontend is built with **Streamlit** and provides a web interface for interacting with the routing system.

Its main responsibilities include:

- Accepting customer messages as input.
- Sending messages to the Decision AI router.
- Displaying the predicted category and routing result.
- Supporting mock mode for simplified local testing.
- Displaying session history.
- Providing example messages for testing.
- Demonstrating routing through simulated Support and Sales agents.
- Handling invalid inputs and routing errors.

The frontend is an interface for testing and demonstrating the system. The simulated agents are not real telecom employees, and the application is not connected to a real customer-service platform.

### Mock Mode and Real Decision AI

- **Mock Mode:** Uses simplified, rule-based logic for testing. Its results may be less accurate for nuanced messages.
- **Real Clef Mode:** Uses the configured Cloudflare Clef decision-model API and the project's routing instructions.

Real Clef mode requires valid configuration and API access. It should not be assumed to work without the necessary credentials and connectivity.

## 4. Decision AI System

The Decision AI system determines whether a customer message should be routed to Support or Sales.

### Routing Rules

**Support — Flag 0**

Used for existing-service issues, complaints, billing questions, account assistance, and problems with existing orders or services.

**Sales — Flag 1**

Used for new purchases, package upgrades, prices, promotions, and requests for sales offers or quotations.

**Mixed Intent**

When a message combines an existing service problem with an interest in purchasing or upgrading, Support takes priority.

The system uses written routing instructions to guide the Clef model. This is separate from a locally trained machine learning classifier.

## 5. Repository Structure

```text
System/
├── README.md
├── STRUCTURE.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── data/
│   └── Agent_KIO_Dataset_FROZEN.xlsx
│
├── frontend/
│   ├── app.py
│   └── README.md
│
├── kio/
│   ├── __init__.py
│   ├── config.py
│   ├── data.py
│   ├── base.py
│   ├── validation.py
│   ├── agents.py
│   ├── router.py
│   ├── clef_router.py
│   └── routing_instructions.md
│
├── decision_model/
│   ├── README.md
│   ├── smoke_test_clef.py
│   └── evaluate_decision_model.py
│
├── ml_model/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── comparison/
│   └── .gitkeep
└── results/
    └── .gitkeep
```

## 6. Main Components

| Component | Purpose |
|---|---|
| `frontend/` | Contains the Streamlit user interface. |
| `kio/config.py` | Holds application configuration logic. |
| `kio/data.py` | Handles dataset loading and integrity validation. |
| `kio/base.py` | Provides shared routing-related functionality. |
| `kio/validation.py` | Validates inputs and related data. |
| `kio/agents.py` | Implements the simulated Support and Sales agents. |
| `kio/router.py` | Provides routing functionality. |
| `kio/clef_router.py` | Connects the routing workflow to the Clef decision model. |
| `kio/routing_instructions.md` | Defines the routing rules and decision instructions. |
| `decision_model/` | Contains Clef smoke-testing and decision-model evaluation scripts. |
| `data/` | Stores the frozen project dataset. |
| `ml_model/` | Reserved for Student 3's ML implementation. |
| `models/` | Reserved for future model artifacts. |
| `comparison/` | Reserved for future comparisons between routing approaches. |
| `results/` | Reserved for future generated results. |

The `.gitkeep` files preserve otherwise-empty directories in Git.

## 7. Dataset

The project dataset is:

`data/Agent_KIO_Dataset_FROZEN.xlsx`

It contains 60 records and 7 columns, with 30 Support examples and 30 Sales examples. The frozen evaluation arrangement contains 40 training records and 20 test records.

The dataset is intended to remain unchanged to preserve consistency and reproducibility. Any modifications must follow the project's agreed data-management rules.

Before distributing the repository publicly, confirm that the dataset's license and permissions allow redistribution.

## 8. Decision Model Testing and Evaluation

The `decision_model/` directory contains scripts for checking and evaluating the Decision AI implementation.

- `smoke_test_clef.py` is intended to check basic Clef routing behavior.
- `evaluate_decision_model.py` evaluates the decision model using the project's evaluation data and metrics.

Evaluation results should be interpreted in the context of the small frozen dataset. They do not guarantee the same performance on all real-world customer messages.

## 9. Machine Learning Work — Reserved for Student 3

The machine learning implementation is intentionally not included in the current branch.

The following directories are preserved for future development:

- `ml_model/` — ML source code and training/evaluation scripts.
- `models/` — saved model artifacts, if required.
- `comparison/` — comparison between the Decision AI and ML approaches.
- `results/` — generated evaluation results and outputs.

Student 3 can add the ML implementation to these locations later without requiring the current Decision AI structure to be removed.

## 10. Installation and Execution

### Requirements

- Python 3.12 is the recommended environment for the current setup.
- Dependencies listed in `requirements.txt`.
- Streamlit.
- Valid Clef configuration for real Decision AI mode.

### Setup with Anaconda

```bash
conda create -n kio python=3.12 -y
conda activate kio
python -m pip install -r requirements.txt
```

Configure the required environment variables using `.env.example` as a reference. Keep actual credentials in the local `.env` file and never commit that file.

### Run the Frontend

From the repository root:

```bash
python -m streamlit run frontend/app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

## 11. Security and Limitations

- Never commit API keys, tokens, or the local `.env` file.
- Confirm dataset redistribution permissions before making the repository public.
- Mock mode uses simplified logic and can misclassify nuanced messages.
- Clef mode depends on valid configuration, network access, and API availability.
- Simulated agents do not perform real customer-service operations.
- The current project does not provide a production telecom integration or guarantee real-world classification accuracy.

## 12. Current Status

The `System` branch is organized around the Decision AI router and Streamlit frontend. ML implementation, saved ML models, and comparison artifacts are excluded for now, while their directory structure is preserved for Student 3.

The immediate goal is to maintain a clean, understandable, testable Decision AI system while allowing the ML component to be developed separately and integrated later.
