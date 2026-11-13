# JUDGEAI
### AI Response Intelligence & Quality Evaluation Platform

JUDGEAI is an AI-powered web application designed to evaluate, analyze and compare AI-generated responses. It provides a structured environment for assessing response quality, identifying potential weaknesses, benchmarking language models and visualizing evaluation performance.

Built using Python, Streamlit, SQLite and Ollama, JUDGEAI combines AI-powered evaluation with interactive analytics and personalized workspaces.

---

## Project Overview

Evaluating AI-generated responses involves more than checking whether an answer looks correct. Response quality also depends on relevance, clarity, completeness and consistency.

JUDGEAI addresses this by providing a multi-dimensional evaluation platform where users can assess answers, compare language models and monitor quality trends through interactive dashboards.

## Key Features

### AI Response Evaluation
- Evaluates responses across Accuracy, Relevance, Clarity and Completeness.
- Generates overall quality scores.
- Identifies strengths and weaknesses.
- Provides suggestions for improving responses.
- Supports customizable weighted evaluation rubrics.

### Model Arena
- Integrates locally hosted language models through Ollama.
- Generates answers using different AI models.
- Supports two-to-four-model comparisons.
- Helps analyze differences in response quality.

### Judge Consistency
- Performs repeated evaluation tests.
- Calculates mean, score range and standard deviation.
- Analyzes consistency across repeated judgments.

### Failure & Risk Detection
- Identifies potentially weak responses using score thresholds.
- Highlights low-performing evaluation dimensions.
- Helps identify areas requiring improvement.

### Interactive Analytics
- Evaluation score distributions and quality trends.
- Rolling quality averages.
- Filterable model comparisons.
- Rubric radar diagnostics.
- Date-based model behaviour replay.
- Downloadable filtered analytics.

### Insight Studio
- Personal quality fingerprint.
- Weekly evaluation goals.
- Recent evaluation momentum.
- Personalized improvement priorities.

### Dataset & Benchmark Labs
- CSV-based answer dataset evaluation.
- Question-based model benchmarking.
- Interactive result tables and analytics.

### User Authentication & Personalization
- Account registration and login using username or email.
- Salted PBKDF2-HMAC-SHA256 password hashing.
- User-specific evaluation history.
- Personalized workspace settings.
- Custom profile information and accent colours.

---

## Technology Stack

| Technology | Application |
|---|---|
| Python | Core application development |
| Streamlit | Web application interface |
| SQLite | User and evaluation data storage |
| Ollama | Local AI model integration |
| Llama 3.2 | Default evaluation model |
| Gemma 3 | Optional answer-generation model |
| Pandas | Data processing |
| Plotly | Interactive data visualization |

---

## Application Structure

- `app.py` – Main application interface, navigation, authentication and dashboards.
- `database.py` – Database operations, user authentication and evaluation storage.
- `judge.py` – AI evaluation, answer generation, consistency testing and failure detection.
- `requirements.txt` – Python dependencies.
- `sample_dataset.csv` – Sample dataset for testing.

---

## Evaluation Dimensions

JUDGEAI evaluates responses using four primary dimensions:

1. **Accuracy** – Assesses the correctness of the response.
2. **Relevance** – Measures how well the response addresses the question.
3. **Clarity** – Evaluates readability and clarity of expression.
4. **Completeness** – Examines whether the response adequately covers the question.

Users can customize the importance of these dimensions through weighted evaluation settings. Custom weights are normalized automatically when calculating overall scores.

---

## Authentication & Data Security

- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes.
- Usernames and email addresses are unique.
- Evaluation records are associated with authenticated user accounts.
- Users can access and manage their own evaluation history.

Email verification and password-reset emails are not currently implemented.

---

## Local AI Integration

JUDGEAI uses Ollama to run language models locally.

Supported example models:
- `llama3.2:3b`
- `gemma3:1b`

The default evaluation model is `llama3.2:3b`. Additional answer-generation models can be configured for comparison.

---

## Deployment Note

The current application is designed for local execution using Ollama. Public cloud deployment requires a securely accessible hosted inference service or model API, along with persistent database storage and appropriate security configuration.

---

## Project Objective

The objective of JUDGEAI is to provide an organized and interactive environment for understanding AI response quality, comparing language models and analyzing evaluation consistency.

It brings response evaluation, model benchmarking, failure detection and analytical insights together in a single platform.

---

## Author

**Chereddy Meghana**

AI Response Intelligence & Quality Evaluation Platform