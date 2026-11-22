# JUDGEAI
### AI Response Intelligence & Quality Evaluation Platform

JUDGEAI is an AI-powered web application designed to evaluate, analyze and improve AI-generated responses. It provides a structured environment for assessing response quality, identifying weaknesses, monitoring evaluation performance and generating actionable improvement suggestions.

Built using Python, Streamlit, Groq and Supabase, JUDGEAI combines AI-powered response evaluation with interactive analytics, secure authentication and personalized user workspaces.

---

## Project Overview

Evaluating AI-generated responses involves more than checking whether an answer looks correct. Response quality also depends on accuracy, relevance, clarity and completeness.

JUDGEAI addresses this through a multi-dimensional evaluation platform where users can assess answers, analyze evaluation results and monitor quality trends through interactive dashboards.

## Key Features

### 1. AI Response Evaluation
- Evaluates responses across Accuracy, Relevance, Clarity and Completeness.
- Generates overall quality scores.
- Identifies response strengths and weaknesses.
- Provides suggestions for improving responses.
- Supports customizable weighted evaluation rubrics.

### 2. AI-Powered Answer Generation
- Generates answers using the Groq API.
- Uses the GPT-OSS 120B model by default.
- Provides clear and contextually relevant responses.
- Integrates answer generation with the evaluation workflow.

### 3. Judge Consistency
- Performs repeated evaluation tests.
- Calculates mean, score range and standard deviation.
- Analyzes consistency across repeated judgments.

### 4. Failure & Risk Detection
- Identifies potentially weak responses using score thresholds.
- Highlights low-performing evaluation dimensions.
- Helps identify areas requiring improvement.

### 5. Interactive Analytics
- Evaluation score distributions and quality trends.
- Rolling quality averages.
- Model-related evaluation analytics, where supported.
- Rubric radar diagnostics.
- Date-based evaluation analysis.
- Downloadable filtered analytics.

### 6. Insight Studio
- Personal quality fingerprint.
- Weekly evaluation goals.
- Recent evaluation momentum.
- Personalized improvement priorities.

### 7. Dataset & Benchmark Labs
- CSV-based answer dataset evaluation.
- Question-based benchmarking.
- Interactive result tables and analytics.

### 8. User Authentication & Personalization
- Account registration using username and email.
- Login using username or email.
- Supabase-powered authentication.
- Email verification.
- User-specific evaluation history.
- Personalized workspace settings.
- Custom profile information and accent colours.

---

## Technology Stack

| Technology | Application |
|---|---|
| Python | Core application development |
| Streamlit | Interactive web application |
| Supabase | Authentication and backend services |
| PostgreSQL | Persistent database storage |
| Groq API | Hosted AI inference |
| GPT-OSS 120B | Default AI evaluation and answer-generation model |
| Pandas | Data processing |
| Plotly | Interactive data visualization |
| Requests | HTTP communication |

---

## Application Structure

- `app.py` – Main application interface, navigation, authentication and dashboards.
- `database.py` – Supabase database operations, authentication and evaluation storage.
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

- Supabase Authentication manages user authentication.
- Email verification is part of the registration process.
- User profiles are linked to authenticated accounts.
- Evaluation records are associated with individual user accounts.
- Row Level Security (RLS) policies help restrict access to individual users' records.
- Sensitive configuration values are stored outside the public source code.

---

## AI Integration

JUDGEAI uses the Groq API to access hosted language models for answer generation and response evaluation.

**Default AI model:**
- `openai/gpt-oss-120b`

The application uses the Groq Chat Completions API to generate responses and evaluate them according to the configured evaluation rubric.

---

## Installation & Local Setup

### Prerequisites

- Python 3.10 or later
- Git
- A Supabase project
- A Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/meghana2615/JUDGEAI.git
cd JUDGEAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows:**

```powershell
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure application secrets

Create a file named `secrets.toml` inside the `.streamlit` folder.

Add the required configuration values:

```toml
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_service_role_key"
SUPABASE_PUBLISHABLE_KEY = "your_supabase_publishable_key"
GROQ_API_KEY = "your_groq_api_key"
```

**Important:** Never upload `secrets.toml`, API keys or service-role credentials to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## Deployment

JUDGEAI is designed for cloud deployment using:

- **Streamlit Community Cloud** – Application hosting.
- **Supabase** – Authentication and persistent database services.
- **Groq API** – Hosted AI inference.

This architecture allows the application to run without requiring users to install or host local language models.

---

## Project Objective

The objective of JUDGEAI is to provide an organized and interactive environment for understanding AI response quality, identifying weaknesses and analyzing evaluation consistency.

It brings AI response evaluation, quality analysis, failure detection and analytical insights together in a single platform.

---

## Future Enhancements

- Support for additional language models.
- Expanded model benchmarking capabilities.
- Advanced evaluation metrics.
- Improved explainability of AI judgments.
- Additional dataset analysis capabilities.

---

## Author

**Chereddy Meghana**

*AI Response Intelligence & Quality Evaluation Platform*