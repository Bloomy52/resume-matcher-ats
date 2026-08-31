# Resume Matching & Analysis System (ATS)

> [!IMPORTANT]
> This project is designed to be highly lightweight and resource-efficient. It is optimized to run on low-memory devices (such as a Raspberry Pi 2B) with a memory footprint target of **under 50MiB**.
When I tested it on my Raspberry Pi 2B, the usage seemed to be around 32MiB with one `gunicorn` worker running.

## Overview

**Resume Matcher ATS** is a Resume Matching Applicant Tracking System (ATS) Portal and Candidate Analyzer. It extracts details from candidate resumes and cover letters (PDF, DOCX, TXT), analyzes them against a target job description using custom NLP algorithms, and ranks the candidates inside a streamlined dashboard.

Key capabilities include:
*   **Resume Parsing & Info Extraction:** Extracts candidate contact details (names, emails, phones) using regular expressions and heuristics.
*   **Custom Match Metric Engine:** Computes a normalized TF-IDF Cosine Similarity and keyword matching rate entirely in pure Python without heavy NLP libraries.
*   **Structural Resume Audit:** Scans for essential headers, quantified impact metrics, and action verbs.
*   **Cover Letter Evaluation:** Evaluates cover letters for greetings, sign-offs, keyword alignment, and formatting suggestions.
*   **Pipeline Persistence:** Uses an SQLite database to store candidate info and match analysis.

---

## Tech Stack & Skills

*   **Runtime:** Python 3.11 or later
*   **Web Framework:** Flask 3.1.3 or later
*   **Text Extraction:** `pypdf` 6.16.1 or later (lightweight PDF parsing)  and `python-docx` 1.2.0 or later (lightweight Word parsing)
*   **WSGI Server:** Gunicorn 26.1.0 or later (for production deployment)
*   **Database:** SQLite3
*   **Frontend:** HTML5, Vanilla CSS3 (Outfit & Inter fonts), Vanilla ES6 JavaScript

---

## Demo Mode
Don't want to set this up? Look no further than the live Demo Mode! You can check it out at the following link: [https://resume-matcher-ats-hxg7.onrender.com](https://resume-matcher-ats-hxg7.onrender.com)

But... There are some limitations that you should be aware of:
1. **No Cover Letters.** You can only upload resumes in the Demo Mode.
2. **The Demo Mode is non-persistent.** That means the candidate data does not get saved after presenting it to you. Once you reload the page or ask for a new scan, your scan is gone.
3. **The Demo Mode only accepts DOCX and PDFs.** For simplicity, the TXT files are not accepted as a valid upload.
4. **No Gemini API.** Gemini isn't available in the demo mode. You can only use the Local NPL engine.

If you don't want to deal with those limitations, follow the instructions below to host the app locally on your Raspberry Pi (or computer, idgaf what device you choose).

---

## Configuration
The app is configured entirely through environment variables. You can set these variables in a `.env` file using the format below.

| Variable         | Required | Default | Description |
|------------------|----------|---------|-------------|
| `GEMINI_API_KEY` | No       | unset   | Enables the Google Gemini AI parser option in the UI. Without it, the app uses the local NLP engine only, and the Gemini toggle is disabled client-side. |
| `FLASK_DEBUG`    | No       | `false` | Enables Flask debug mode. Leave unset in production. |

```dotenv
GEMINI_API_KEY=your-gemini-api-key
FLASK_DEBUG=false
```

## Quick Start

To run the project locally, follow these steps:

### 1. Clone the GitHub Repository
```bash
git clone https://www.github.com/Bloomy52/resume-matcher-ats.git
cd resume-matcher-ats
```

### 2. Set Up Environment
Create and activate a virtual environment, then install the dependencies:
```bash
# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install lightweight dependencies
pip install --no-cache-dir -r requirements.txt
```

### 3. Run Tests
Verify the analyzer logic and custom calculations:
```bash
python -m unittest test_analyzer.py
```

### 4. Start the Web Server

#### Development Mode (Built-in Server)
Launch the Flask development server (runs by default on host `0.0.0.0` and port `5000` to be accessible on local networks):
```bash
python app.py
```
> [!WARNING]
> **macOS Users:**
> By default, Flask defaults to Port `5000` which is already in use by macOS's AirPlay Reciever. To avoid any issues resulting from this, you will need to set the port in `app.py` to a different value, such as `5001`:

#### Production Mode (WSGI Server - Recommended)
To run the application in a production environment, use a WSGI server like **Gunicorn**. This handles multiple concurrent connections, manages worker processes, and is highly resource-efficient (perfect for a Raspberry Pi):
```bash
gunicorn --workers 2 --bind 0.0.0.0:5000 app:app
```
For extremely low-memory systems (like a Raspberry Pi 2B target of `<50MiB`), you can run with 1 worker to minimize the memory footprint:
```bash
gunicorn --workers 1 --bind 0.0.0.0:5000 app:app
```

Once started, open your browser and navigate to `http://localhost:5000` to access the Recruiter Dashboard.


Alternatively, you can set up the WSGI server using `systemd`. You can find the instructions for setting up the systemd service in the `systemd_setup.md` document.

#### `uv`
Don't want to use the "old-fashioned" way of installing the app? Well, you're in luck! You can use `uv` to install the dependencies!

```bash
uv sync
uv run app.py
```

If you are running this on a low-memory device, such as the Raspberry Pi 2B, I do not recommend using `uv` or `pyproject.toml` to install and use this app. Just do it the "old-fashioned" way. If you insist on using `uv` on a low-memory device, you can use the following command:
```bash
uv venv
source .venv/bin/activate
uv pip install --no-cache-dir -r requirements.txt
```

### Docker
If you somehow decided to use Docker instead of the above methods, we have conveniently provided you with a [Dockerfile](./Dockerfile). The install commands are below:
```bash
docker build -t resume-matcher-ats .
docker run --rm -it resume-matcher-ats
```
If you have a `.env` file, replace `docker run --rm -it resume-matcher-ats` with `docker run --rm -it --env-file .env resume-matcher-ats`.


---

## How Matching Works

This project uses a custom NLP algorithm to analyze your resumes and cover letters against the job description. A high-level overview is detailed below.

- **Do the right skills show up?** This accounts for 60% of the score. Key skills from the job description are checked against the resume, with some wiggle room for typos or slight wording differences.
- **Does the resume "sound like" the job?** This accounts for 40% of the score. The overall language and phrasing of the resume is compared against the job description to see how closely they align.
- **Bonus points** for quantified wins (numbers, percentages), clean section headers, and a solid cover letter if you upload one.

---

## Project Structure

```text
.
├── .gitignore              # gitignore file for the repository. Includes Python Template and SQLite database
├── analyzer.py             # Custom NLP scoring, keyword extraction, and structural parser
├── app.py                  # Flask backend controller, SQLite database manager, and server routes
├── ats_database.db         # Local SQLite database (automatically initialized) - not included in git repository
├── THIRD-PARTY-NOTICES.txt # Third-party notices for the project
├── LICENSE                 # AGPL-3.0-only license file
├── README.md               # Overview for the repository
├── requirements.txt        # Python package requirements
├── systemd_setup.md        # Instructions for how to set up a systemd service for the WSGI server
├── test_analyzer.py        # Comprehensive unit tests for all parser/analyzer functions
├── pyproject.toml          # Python packaging configuration
├── uv.lock                 # Lock file for uv server
├── static/
│   ├── app.js              # Client-side UI renderer, API interactions, and chart renderers
│   ├── demo.js             # Demo version of app.js
│   └── style.css           # Sleek, responsive stylesheet with Dark Mode support
└── templates/
    ├── demo_index.html     # Demo version of index.html
    ├── index.html          # Primary dashboard HTML page structure
    └── license.html        # AGPL-3.0 license text page
```

---

## API Endpoints

| Method | Path                    | Description |
|--------|-------------------------|-------------|
| GET    | `/`                     | Renders the main dashboard |
| GET    | `/api/config`           | Returns `{"gemini_enabled": bool}` |
| POST   | `/api/analyze`          | Accepts a resume file (and optional cover letter) plus a job description; returns the full match analysis |
| GET    | `/api/candidates`       | Lists all scanned candidates, ranked by match score |
| GET    | `/api/candidates/<id>`  | Returns full analysis detail for one candidate |
| DELETE | `/api/candidates/<id>`  | Deletes a candidate record |
| GET    | `/license`              | Renders the full AGPL-3.0 license text |

---

## Known Limitations

- **Upload size is capped at 5MB.** 5MB is larger than a resume and a cover letter combined. Why would you have a 5MB resume anyways?
- **Concurrent writes are not supported.** We aren't using PostgreSQL here, so concurrent writes are not supported. Deal with it.
- **PDF/DOCX Parsing.** Due to this being super lightweight, the text extraction algorithms don't do well with graphics, columns, tables, pictures, and fancy formatting. Keep it to boring paragraphs and bullet points. 

Contributions addressing any of the above are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Contributing
Contributions are welcome! Please ensure any new features adhere to the low-memory guidelines. Avoid adding large package dependencies and write unit tests inside `test_analyzer.py` for any new logic in `analyzer.py`.
By submitting a contribution, you agree that your contribution is licensed under AGPL-3.0-only.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details on contributing to the project.

## License
Copyright (c) 2026 Louie Bloomberg.

This project is licensed under the GNU Affero General Public License v3.0 only (AGPL-3.0-only).
