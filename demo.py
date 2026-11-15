# demo.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

import os
import json
import secrets
import shutil
import platform
import tomllib
from pathlib import Path
from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

from demo_core import run_demo_analysis

app = Flask(__name__)


app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

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
    response_data, status = run_demo_analysis(
        resume_file.filename,
        resume_file.read(),
        request.form.get('job_description', ''),
        request.form.get('job_title', ''),
        request.form.get('candidate_name', ''),
    )
    if status != 200:
        return jsonify(response_data), status

    # Clean up any previous demo session tied to this browser session
    # before starting a new one.
    old_demo_id = session.get('demo_id')
    if old_demo_id:
        delete_demo_session(old_demo_id)

    save_demo_results(
        response_data["analysis"],
        response_data["candidate_name"],
        response_data["candidate_email"],
        response_data["candidate_phone"],
        response_data["job_title"],
    )

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