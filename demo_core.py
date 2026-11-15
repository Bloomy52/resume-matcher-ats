# demo_core.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

"""Framework-free demo logic shared by the Flask demo (demo.py) and the
in-browser Pyodide demo (pages/). Nothing here may import Flask."""

import re

from analyzer import get_ats_analysis, extract_text_from_pdf, extract_text_from_docx

ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_EXTRACTED_TEXT_CHARS = 50000


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


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


def extract_text_from_bytes(filename, file_bytes):
    """Extracts text from PDF or DOCX bytes, capped at MAX_EXTRACTED_TEXT_CHARS."""
    filename = (filename or '').lower()

    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(file_bytes)
    else:
        return ""

    if text and len(text) > MAX_EXTRACTED_TEXT_CHARS:
        text = text[:MAX_EXTRACTED_TEXT_CHARS]

    return text


def run_demo_analysis(filename, file_bytes, job_desc, job_title='', candidate_name=''):
    """Runs the full demo scan. Returns (response_dict, http_status)."""
    if not allowed_file(filename):
        return {"error": "Only PDF and DOCX files are supported in the demo."}, 400

    job_desc = (job_desc or '').strip()
    if not job_desc:
        return {"error": "Job description is required"}, 400

    job_title = (job_title or '').strip()
    if not job_title:
        job_lines = [l.strip() for l in job_desc.split('\n') if l.strip()]
        job_title = job_lines[0][:50] if job_lines else "Target Job Position"

    resume_text = extract_text_from_bytes(filename, file_bytes)
    if not resume_text:
        return {"error": "Failed to parse resume text. Please upload a valid PDF or DOCX file."}, 400

    analysis = get_ats_analysis(resume_text, job_desc, cover_letter_text=None, parser_mode='local')
    if "error" in analysis:
        return analysis, 400

    name, email, phone = extract_candidate_info(resume_text)
    candidate_name = (candidate_name or '').strip()
    if candidate_name:
        name = candidate_name

    return {
        "candidate_id": None,
        "candidate_name": name,
        "candidate_email": email,
        "candidate_phone": phone,
        "job_title": job_title,
        "analysis": analysis,
    }, 200
