# demo.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

import os
import re
import json
import secrets
import shutil
import platform
import tomllib
from pathlib import Path
from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

from analyzer import get_ats_analysis, extract_text_from_pdf, extract_text_from_docx

app = Flask(__name__)


app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_EXTRACTED_TEXT_CHARS = 50000

DEMO_STORAGE_DIR = Path('/tmp/resume-matcher-demo')
DEMO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def get_app_version():
    """Reads the version string from pyproject.toml."""
    try:
        pyproject_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyproject.toml')
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
        return data.get('project', {}).get('version', 'unknown')
    except Exception as e:
        print(f"Error reading version from pyproject.toml: {e}")
        return 'unknown'


APP_VERSION = get_app_version()

def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_demo_session_dir(demo_id):
    """Returns the Path for a given demo_id's storage dir."""
    safe_id = secure_filename(demo_id) if demo_id else None
    if not safe_id or safe_id != demo_id:
        return None
    return DEMO_STORAGE_DIR / safe_id


def delete_demo_session(demo_id):
    """Deletes a demo session's temporary storage directory, if it exists."""
    session_dir = get_demo_session_dir(demo_id)
    if session_dir and session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
        print("Demo session expired")


def save_demo_results(analysis, candidate_name, candidate_email, candidate_phone, job_title):
    """Creates a new demo session and stores analysis results temporarily on disk."""
    demo_id = secrets.token_urlsafe(32)
    session_dir = DEMO_STORAGE_DIR / demo_id
    session_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "name": candidate_name,
        "email": candidate_email,
        "phone": candidate_phone,
        "job_title": job_title,
        "analysis": analysis
    }

    with open(session_dir / 'results.json', 'w') as f:
        json.dump(payload, f)

    session['demo_id'] = demo_id
    print("Processing demo resume")
    return demo_id


def extract_candidate_info(resume_text):
    """Extracts basic candidate info (name, email, phone) from resume text."""
    email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', resume_text)
    email = email_match.group(0) if email_match else "unknown@example.com"

    phone_match = re.search(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', resume_text)
    phone = phone_match.group(0) if phone_match else "N/A"

    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    name = "Unknown Candidate"
    if lines:
        for line in lines[:5]:
            if len(line) < 40 and not any(k in line.lower() for k in ["resume", "cv", "email", "phone", "http", "@", "+"]):
                name = line
                break

    return name, email, phone


def extract_text_from_upload(file):
    """Extracts text from an uploaded PDF or DOCX file."""
    filename = file.filename.lower()
    file_bytes = file.read()

    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(file_bytes)
    else:
        return ""

    if text and len(text) > MAX_EXTRACTED_TEXT_CHARS:
        text = text[:MAX_EXTRACTED_TEXT_CHARS]

    return text


@app.route('/')
def index():
    sys_name = platform.system()
    server_os = sys_name if sys_name else 'Unknown'
    return render_template('demo_index.html', server_os=server_os, app_version=APP_VERSION)


@app.route('/api/config', methods=['GET'])
def demo_config():
    return jsonify({
        "gemini_enabled": False,
        "demo_mode": True
    })


@app.route('/api/analyze', methods=['POST'])
def demo_analyze():
    if 'resume' not in request.files:
        return jsonify({"error": "Resume file is required"}), 400

    resume_file = request.files['resume']
    if not allowed_file(resume_file.filename):
        return jsonify({"error": "Only PDF and DOCX files are supported in the demo."}), 400

    job_desc = request.form.get('job_description', '').strip()
    if not job_desc:
        return jsonify({"error": "Job description is required"}), 400

    job_title = request.form.get('job_title', '').strip()
    if not job_title:
        job_lines = [l.strip() for l in job_desc.split('\n') if l.strip()]
        job_title = job_lines[0][:50] if job_lines else "Target Job Position"

    resume_text = extract_text_from_upload(resume_file)
    if not resume_text:
        return jsonify({"error": "Failed to parse resume text. Please upload a valid PDF or DOCX file."}), 400

    analysis = get_ats_analysis(resume_text, job_desc, cover_letter_text=None, parser_mode='local')
    if "error" in analysis:
        return jsonify(analysis), 400

    candidate_name, candidate_email, candidate_phone = extract_candidate_info(resume_text)

    req_name = request.form.get('candidate_name', '').strip()
    if req_name:
        candidate_name = req_name

    # Clean up any previous demo session tied to this browser session
    # before starting a new one.
    old_demo_id = session.get('demo_id')
    if old_demo_id:
        delete_demo_session(old_demo_id)

    save_demo_results(analysis, candidate_name, candidate_email, candidate_phone, job_title)

    response_data = {
        "candidate_id": None,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "candidate_phone": candidate_phone,
        "job_title": job_title,
        "analysis": analysis
    }

    return jsonify(response_data)

@app.route('/api/reset', methods=['POST'])
def demo_reset():
    demo_id = session.pop('demo_id', None)
    if demo_id:
        delete_demo_session(demo_id)
    return jsonify({"success": True})

@app.route('/license', methods=['GET'])
def get_license():
    return render_template('license.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)