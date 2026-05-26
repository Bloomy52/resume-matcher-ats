# TalentStream: Future Implementation Plans (Low-Memory Edition)

This document outlines potential future features, extensions, and architectural upgrades for the TalentStream ATS Recruiter Portal & Candidate Analyzer. 

Because the target deployment platform is a **Raspberry Pi 2B** (which has strict resource constraints and must run with a memory footprint **under 50MiB**), all proposed features are specifically architected to offload processing to the client (browser) or the cloud, and optimize Python memory usage.

---

## 1. [ ] Cloud-Offloaded AI Semantic Analysis
* **Description:** 
  Transition from simple rule-based keyword matching to semantic understanding (e.g., recognizing that "GCP" matches a requirement for "cloud experience") without running heavy NLP libraries (like SpaCy or NLTK) which would instantly crash a Pi 2B's memory.
* **Low-Memory Plan:**
  1. Use the **Google Gemini API** or **Claude API** for semantic analysis. The heavy LLM processing happens in the cloud; the Pi 2B only handles standard JSON payloads.
  2. Implement an optional API integration in [analyzer.py](file:///home/louie/antigravity_ats/analyzer.py).
  3. Keep the request payload minimal (strip unnecessary whitespace from raw text before sending to save network buffer memory).
  4. Ensure the API calls are asynchronous or run on a separate thread to prevent blocking the main Flask thread.

---

## 2. [ ] Browser-Side (Client) Rendering & Computation
* **Description:** 
  Keep server CPU and RAM usage to a absolute minimum by offloading data formatting, markdown parsing, and visualization to the user's browser.
* **Low-Memory Plan:**
  1. **Do not** compile reports or generate charts on the Pi.
  2. For historical charts and trends, load [Chart.js](https://www.chartjs.org/) via a client-side CDN. The Pi will only serve a tiny JSON array of raw scores (a few bytes), and the user's browser will compute and render the canvas.
  3. Use a lightweight client-side markdown parser (like `marked.js` loaded via CDN) so the Pi sends raw markdown suggestions and the browser converts them to HTML.

---

## 3. [ ] Streaming and Memory-Bounded File Uploads
* **Description:** 
  Currently, the app reads the entire uploaded PDF file into RAM as bytes (`file.read()`) and passes it to `pypdf.PdfReader` ([app.py:L59-75](file:///home/louie/antigravity_ats/app.py#L59-75)). If a user uploads a large PDF, it can cause memory spikes that trigger the Linux Out-Of-Memory (OOM) killer.
* **Low-Memory Plan:**
  1. Enforce a strict file upload limit in Flask (e.g., `app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024` to cap uploads at 2MB).
  2. Modify [app.py](file:///home/louie/antigravity_ats/app.py) to stream the file to a temporary file on the Pi's disk (in `/tmp` or a local scratch folder) instead of holding all bytes in RAM.
  3. Initialize `PdfReader` directly from the disk file stream, extract the text page-by-page, and clear each page object from memory immediately after text extraction.

---

## 4. [ ] SQLite Memory Tuning & Connection Lifecycle
* **Description:** 
  SQLite is fast, but open connections and large caches can consume valuable RAM. We must tune SQLite to run in "micro-memory" mode.
* **Low-Memory Plan:**
  1. Implement SQLite connection reuse using Flask's `g` context object ([flask.g](https://flask.palletsprojects.com/en/3.0.x/api/#flask.g)) to open one connection per request and close it cleanly at the end of the request.
  2. Execute memory-tuning PRAGMAs on every connection:
     * `PRAGMA cache_size = -500;` (restricts the database cache to roughly 500KB of RAM).
     * `PRAGMA temp_store = MEMORY;` (keeps temp tables in memory only if they are tiny, or set to `FILE` to save RAM).
     * `PRAGMA journal_mode = WAL;` (enables Write-Ahead Logging for concurrency without database locks).

---

## 5. [ ] Single-Threaded, Low-Footprint WSGI Runner
* **Description:** 
  Standard development servers are inefficient, but running multi-worker Gunicorn servers creates several child processes, each consuming ~25-30MiB of RAM, easily exceeding the 50MiB budget.
* **Low-Memory Plan:**
  1. Avoid heavy containers (like Docker) which introduce container engine memory overhead. Run directly in a virtual environment (`ats-env`).
  2. Deploy using a lightweight, single-process WSGI server like **Waitress** or **uWSGI** configured with exactly `1` worker and a small thread pool (e.g., 2-4 threads).
  3. Waitress runs natively on a single process and consumes less than 15MiB of baseline memory, keeping the entire application (Flask + Waitress) well under the 50MiB target.

---

## 6. [x] Strict "Vanilla Python" Rule (No Heavy Analytical Packages)
* **Description:** 
  Avoid importing heavy data science libraries like `pandas`, `numpy`, `scikit-learn`, `nltk`, or `spacy`, which can push memory usage over 150-500MiB.
* **Low-Memory Plan:**
  1. Keep [requirements.txt](file:///home/louie/antigravity_ats/requirements.txt) restricted to only standard Flask and parsing packages.
  2. Implement all similarity logic (like Cosine Similarity) using Python's built-in `math` and `collections` libraries (as currently done in [analyzer.py:L161-209](file:///home/louie/antigravity_ats/analyzer.py#L161-209)).

---

## 7. [ ] CSS Print Stylesheet PDF Export
* **Description:** 
  Enable recruiters to export candidate analysis reports as a PDF without running heavy PDF generation engines (like WeasyPrint, ReportLab, or wkhtmltopdf) on the Raspberry Pi, which would consume too much CPU and RAM.
* **Low-Memory Plan:**
  1. Add a print-specific CSS block using `@media print` in [style.css](file:///home/louie/talentstream_ats/static/style.css) to hide navigation, forms, and interactive buttons, while formatting the report layout nicely for standard paper (A4/Letter).
  2. Implement an "Export to PDF" trigger in [index.html](file:///home/louie/talentstream_ats/templates/index.html) (e.g., via `window.print()`) that prompts the browser's built-in print dialog, shifting all PDF generation work entirely to the user's browser.

