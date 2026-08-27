# app.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

import os
import json
import re
import sqlite3
import platform
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from analyzer import get_ats_analysis, extract_text_from_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

DATABASE = 'ats_database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                job_title TEXT,
                match_score INTEGER,
                interview_likelihood TEXT,
                likelihood_percentage INTEGER,
                analysis_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Initialize DB on start
init_db()

def extract_candidate_info(resume_text):
    """Extracts basic candidate info (name, email, phone) from resume text."""
    email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', resume_text)
    email = email_match.group(0) if email_match else "unknown@example.com"
    
    phone_match = re.search(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', resume_text)
    phone = phone_match.group(0) if phone_match else "N/A"
    
    # Name heuristic: First non-empty line (truncated to first few words)
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    name = "Unknown Candidate"
    if lines:
        for line in lines[:5]:  # Look in the first 5 lines for name
            if len(line) < 40 and not any(k in line.lower() for k in ["resume", "cv", "email", "phone", "http", "@", "+"]):
                name = line
                break
    
    return name, email, phone

def extract_text_from_file(file):
    """Extracts text from file (PDF or TXT)."""
    filename = secure_filename(file.filename)
    if not filename:
        return ""

    filename = filename.lower()
    file_bytes = file.read()
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith('.txt'):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_bytes.decode('latin-1')
            except Exception:
                return ""
    return ""

@app.route('/')
def index():
    sys_name = platform.system()
    if sys_name == 'Darwin':
        server_os = 'macOS'
    elif sys_name == 'Windows':
        server_os = 'Windows'
    elif sys_name == 'Linux':
        if os.path.exists('/proc/device-tree/model'):
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    server_os = f.read().strip()
            except Exception:
                server_os = 'Linux'
        else:
            server_os = 'Linux'
    else:
        server_os = sys_name

    return render_template('index.html', server_os=server_os)

@app.route('/api/config', methods=['GET'])
def get_config():
    gemini_enabled = bool(os.environ.get('GEMINI_API_KEY'))
    return jsonify({
        "gemini_enabled": gemini_enabled
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # 1. Check requirements
    if 'resume' not in request.files:
        return jsonify({"error": "Resume file is required"}), 400
        
    job_desc = request.form.get('job_description', '').strip()
    if not job_desc:
        return jsonify({"error": "Job description is required"}), 400
        
    resume_file = request.files['resume']
    cover_letter_file = request.files.get('cover_letter')
    
    job_title = request.form.get('job_title', '').strip()
    if not job_title:
        # Heuristic: Extract first line of job desc as title if not provided
        job_lines = [l.strip() for l in job_desc.split('\n') if l.strip()]
        job_title = job_lines[0][:50] if job_lines else "Target Job Position"

    parser_mode = request.form.get('parser_mode', 'local').strip().lower()

    # 2. Extract texts
    resume_text = extract_text_from_file(resume_file)
    if not resume_text:
        return jsonify({"error": "Failed to parse resume text. Please upload a valid PDF or TXT file."}), 400
        
    cover_letter_text = None
    if cover_letter_file and cover_letter_file.filename:
        cover_letter_text = extract_text_from_file(cover_letter_file)
        
    # 3. Analyze
    analysis = get_ats_analysis(resume_text, job_desc, cover_letter_text, parser_mode=parser_mode)
    if "error" in analysis:
        return jsonify(analysis), 400
        
    # 4. Extract Candidate details
    candidate_name, candidate_email, candidate_phone = extract_candidate_info(resume_text)
    
    # Allow overriding candidate name from the client request
    req_name = request.form.get('candidate_name', '').strip()
    if req_name:
        candidate_name = req_name
        
    # 5. Save candidate to database
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO candidates (
                    name, email, phone, job_title, match_score, 
                    interview_likelihood, likelihood_percentage, analysis_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate_name,
                candidate_email,
                candidate_phone,
                job_title,
                analysis["match_score"],
                analysis["interview_likelihood"],
                analysis["likelihood_percentage"],
                json.dumps(analysis)
            ))
            conn.commit()
            candidate_id = cursor.lastrowid
    except Exception as e:
        print(f"Error saving to DB: {e}")
        candidate_id = None
        
    # Add id to analysis response
    response_data = {
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "candidate_phone": candidate_phone,
        "job_title": job_title,
        "analysis": analysis
    }
    
    return jsonify(response_data)

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT id, name, email, phone, job_title, match_score, 
                       interview_likelihood, likelihood_percentage, created_at 
                FROM candidates 
                ORDER BY match_score DESC, created_at DESC
            ''')
            rows = cursor.fetchall()
            candidates = []
            for r in rows:
                candidates.append({
                    "id": r["id"],
                    "name": r["name"],
                    "email": r["email"],
                    "phone": r["phone"],
                    "job_title": r["job_title"],
                    "match_score": r["match_score"],
                    "interview_likelihood": r["interview_likelihood"],
                    "likelihood_percentage": r["likelihood_percentage"],
                    "created_at": r["created_at"]
                })
            return jsonify(candidates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/candidates/<int:candidate_id>', methods=['GET'])
def get_candidate_detail(candidate_id):
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT id, name, email, phone, job_title, match_score, 
                       interview_likelihood, likelihood_percentage, analysis_json, created_at 
                FROM candidates 
                WHERE id = ?
            ''', (candidate_id,))
            r = cursor.fetchone()
            if not r:
                return jsonify({"error": "Candidate not found"}), 404
                
            return jsonify({
                "id": r["id"],
                "name": r["name"],
                "email": r["email"],
                "phone": r["phone"],
                "job_title": r["job_title"],
                "match_score": r["match_score"],
                "interview_likelihood": r["interview_likelihood"],
                "likelihood_percentage": r["likelihood_percentage"],
                "analysis": json.loads(r["analysis_json"]),
                "created_at": r["created_at"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/candidates/<int:candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    try:
        with get_db() as conn:
            cursor = conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Candidate not found"}), 404
            return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/license', methods=['GET'])
def get_license():
    return render_template('license.html')

if __name__ == '__main__':
    # Run server on port 5000, visible on local network so they can access it on Pi
    # Debug mode is disabled by default for security and low resource usage
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't', 'y', 'yes']
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
