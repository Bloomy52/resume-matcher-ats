# Contributing to Resume Matcher ATS

Thank you for your interest in contributing to Resume Matcher ATS!

Resume Matcher ATS is a lightweight Flask application that compares resumes and cover letters with job descriptions. Contributions that improve accuracy, usability, accessibility, reliability, documentation, or resource efficiency are welcome.

Please read this guide before opening an issue or pull request.

## Code of Conduct

Be respectful, constructive, and considerate when communicating with other contributors.

Technical disagreements are welcome, but discussions should focus on the problem and proposed solution rather than individuals.

## Before You Start

Before making a change:

1. Check the existing issues and pull requests to avoid duplicating work.
2. For significant changes, open an issue first to discuss the proposed approach.
3. Keep pull requests focused on one feature, bug fix, or documentation improvement.
4. Do not include private resumes, cover letters, personal information, API keys, or database files in commits.

## Development Requirements

The project currently supports:

- Python 3.11 or later
- Flask
- SQLite
- Vanilla JavaScript, HTML, and CSS
- `unittest` for automated tests

The application is designed to remain lightweight and suitable for low-memory devices. New contributions should avoid unnecessarily increasing memory usage, startup time, or dependency size.

## Setting Up a Development Environment

### 1. Fork and clone the repository

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/<your-username>/resume-matcher-ats.git
cd resume-matcher-ats
```

Add the original repository as an `upstream` remote if desired:

```bash
git remote add upstream https://github.com/Bloomy52/resume-matcher-ats.git
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Using `pip`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you are using the project’s `uv` workflow:

```bash
uv sync
```

### 4. Configure optional environment variables

Create a local `.env` file if needed:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
FLASK_DEBUG=true
```

Do not commit `.env` files, API keys, or other credentials.

## Running the Application Locally

Start the Flask development server with:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

Do not use Flask debug mode in a production deployment.

## Running Tests

Run the analyzer test suite from the repository root:

```bash
python -m unittest test_analyzer.py
```

Before submitting a pull request, make sure that:

- All existing tests pass.
- New behavior has appropriate tests.
- Tests cover normal cases and relevant edge cases.
- Changes to matching or parsing behavior do not unintentionally break existing behavior.

When modifying `analyzer.py`, add or update tests in `test_analyzer.py`.

## What to Test

Depending on the change, consider testing:

- Empty or malformed input.
- PDF, DOCX, and TXT processing behavior.
- Keyword matching and missing-keyword detection.
- Fuzzy matching behavior.
- Resume structure detection.
- Cover letter scoring.
- Special cases involving dates, seasons, technologies, or framework names.
- API validation and error responses.
- File upload size and file type handling.
- SQLite persistence and deletion behavior.
- Frontend behavior for loading, error, and empty states.

Avoid tests that depend on external services, live network requests, or real personal documents.

## Coding Guidelines

### Python

- Follow the existing project structure and coding style.
- Prefer clear, small functions with focused responsibilities.
- Use descriptive names for functions, variables, and test cases.
- Handle invalid input explicitly.
- Avoid introducing a large NLP or machine-learning dependency when a lightweight solution is sufficient.
- Keep parsing and matching behavior deterministic where possible.
- Do not log sensitive resume or cover-letter contents.
- Preserve compatibility with Python 3.11 and later.

### JavaScript

- Use modern, browser-compatible JavaScript.
- Keep API interactions and UI rendering understandable and separated where practical.
- Handle loading, success, empty, and error states.
- Avoid adding a frontend framework unless there is a clear, documented reason.
- Do not expose API keys or sensitive user data in client-side code.

### HTML and CSS

- Preserve semantic HTML and accessible labels.
- Ensure interactive controls are keyboard accessible.
- Maintain the existing responsive layout.
- Keep styles organized and avoid unnecessary duplication.
- Check both light and dark mode behavior when changing shared styles.

### Dependencies

Before adding a dependency, consider:

- Whether the functionality can be implemented with the standard library or existing dependencies.
- The dependency’s effect on installation size and memory usage.
- Its compatibility with Python 3.11 and supported deployment environments.
- Its license and maintenance status.
- Whether the dependency is necessary for the project’s intended use on low-memory devices.

Explain new dependencies in the pull request description.

## Database and Generated Files

The application creates a local SQLite database named `ats_database.db`.

Do not commit:

- `ats_database.db`
- Local virtual environments
- `.env` files
- API keys or credentials
- Uploaded resumes or cover letters
- Personal test data
- Generated caches or build artifacts

Use synthetic or anonymized data when testing file uploads.

## Commit Guidelines

Use concise commit messages that describe the change.

Examples:

```text
Fix keyword extraction for seasonal terms
Add tests for DOCX text extraction
Improve candidate list error handling
Update contributing documentation
```

Keep unrelated changes in separate commits when practical.

## Pull Request Process

Before opening a pull request:

1. Rebase or update your branch with the latest changes from the default branch when appropriate.
2. Run the test suite.
3. Review the complete diff for unintended changes.
4. Confirm that no credentials, personal documents, databases, or generated files are included.
5. Update documentation when behavior, configuration, or setup instructions change.
6. Add tests for new or changed behavior.

Your pull request description should include:

- A concise summary of the change.
- The problem it solves.
- The approach taken.
- Testing performed.
- Any new dependencies or configuration changes.
- Known limitations or follow-up work.

A useful pull request structure is:

```markdown
## Summary

Describe what changed.

## Motivation

Explain why the change was needed.

## Testing

- `python -m unittest test_analyzer.py`

## Additional Notes

Mention compatibility concerns, trade-offs, or follow-up work.
```

Pull requests may be asked to make changes before they are merged. Please respond to review feedback and keep the branch updated if requested.

## Reporting Bugs

When reporting a bug, include:

- A clear and descriptive title.
- Steps to reproduce the problem.
- The expected behavior.
- The actual behavior.
- Relevant error messages or logs.
- Your Python version and operating system.
- Whether the issue occurs with PDF, DOCX, TXT, or plain text input.
- A minimal synthetic example that reproduces the issue.

Do not attach real resumes, cover letters, API keys, or other personal information.

## Suggesting Features

Feature requests should explain:

- The problem or use case.
- The proposed behavior.
- Why the change fits the project’s lightweight design goals.
- Any impact on compatibility, memory usage, dependencies, or privacy.

Small, focused proposals are easier to review and implement.

## Security Issues

Please do not publicly report security vulnerabilities with sensitive details.

If a contribution involves credentials, file uploads, personal information, database access, or external API integration, take extra care to avoid exposing sensitive data in issues, pull requests, logs, screenshots, or test fixtures.

## Documentation Changes

Documentation improvements are welcome. Keep documentation:

- Accurate and consistent with the current application.
- Clear for new contributors.
- Free of secrets and personal information.
- Explicit about required configuration and supported workflows.

Update the relevant documentation whenever a code change affects setup, configuration, API behavior, or deployment.

## Contribution License

By submitting a contribution, including a pull request, commit, patch, comment containing code, or other contribution, you confirm that:

1. You have the legal right to submit the contribution.
2. You understand that the contribution will be distributed as part of this project.
3. You agree that the contribution may be made available under the project’s license, the GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).

Unless otherwise stated, copyright in your contribution remains with you.

Thank you for helping improve Resume Matcher ATS!
