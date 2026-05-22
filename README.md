# TalentStream ATS

> [!IMPORTANT]
> This project is designed to be highly lightweight and resource-efficient. It is optimized to run on low-memory servers (such as a Raspberry Pi 2B) with a strict memory footprint target of **under 50MiB**.

## Overview

**TalentStream ATS** is an Applicant Tracking System (ATS) Recruiter Portal and Candidate Analyzer. It extracts details from candidate resumes and cover letters (PDF/TXT), analyzes them against a target job description using custom NLP algorithms, and ranks the candidates inside a streamlined recruiter dashboard.

Key capabilities include:
*   **Resume Parsing & Info Extraction:** Extracts candidate contact details (names, emails, phones) using regular expressions and heuristics.
*   **Custom Match Metric Engine:** Computes a normalized TF-IDF Cosine Similarity and keyword matching rate entirely in pure Python without heavy NLP libraries.
*   **Structural Resume Audit:** Scans for essential headers, quantified impact metrics, and action verbs.
*   **Cover Letter Evaluation:** Evaluates cover letters for greetings, sign-offs, keyword alignment, and formatting suggestions.
*   **Pipeline Persistence:** Uses an SQLite database to store candidate info and match analysis.

---

## 🛠️ Tech Stack & Skills

*   **Runtime:** Python 3.x
*   **Web Framework:** Flask 3.0.3
*   **Text Extraction:** `pypdf` 4.2.0 (lightweight PDF parsing)
*   **Database:** SQLite3
*   **Frontend:** HTML5, Vanilla CSS3 (Outfit & Inter fonts), Vanilla ES6 JavaScript
*   **IDE Support:** Fully compatible with the Google Antigravity agentic IDE environment

---

## Quick Start

To run the project locally, follow these steps:

### 1. Clone the GitHub Repository
```bash
git clone https://www.github.com/Bloomy52/talent-stream-ats-py.git
cd talent-stream-ats-py
```

### 1. Set Up Environment
Create and activate a virtual environment, then install the dependencies:
```bash
# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install lightweight dependencies
pip install -r requirements.txt
```

### 2. Run Tests
Verify the analyzer logic and custom calculations:
```bash
python -m unittest test_analyzer.py
```

### 3. Start the Web Server
Launch the Flask development server (runs by default on host `0.0.0.0` and port `5000` to be accessible on local networks):
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000` to access the Recruiter Dashboard.

---

## Agentic Workflow

This project is tailored for agent-assisted development using **Google Antigravity**:
*   **Tasks & Planning:** Track tasks via standard agent task files.
*   **Behavioral Rules:** Rely on minimal, optimized packages as defined in the rules below.
*   **Low-Memory Policy:** All algorithms must be implemented using vanilla Python standard libraries where possible. Do not import heavy libraries such as Pandas, NumPy, NLTK, or SpaCy to keep memory usage under 50MiB.

---

## Project Structure

```text
.
├── analyzer.py          # Custom NLP scoring, keyword extraction, and structural parser
├── app.py               # Flask backend controller, SQLite database manager, and server routes
├── ats_database.db      # Local SQLite database (automatically initialized)
├── FUTURE_PLANS.md      # Technical roadmap for low-memory environments (Pi 2B)
├── requirements.txt     # Python package requirements (Flask, pypdf)
├── test_analyzer.py     # Comprehensive unit tests for all parser/analyzer functions
├── static/
│   ├── app.js           # Client-side UI renderer, API interactions, and chart renderers
│   └── style.css        # Sleek, responsive stylesheet (dark-mode aesthetics)
└── templates/
    └── index.html       # Primary dashboard HTML page structure
```

---

## Contributing
Contributions are welcome! Please ensure any new features adhere to the low-memory guidelines. Avoid adding large package dependencies, and write unit tests inside `test_analyzer.py` for any new logic in `analyzer.py`.

## License
This project is licensed under the MIT License.
