# pages/bridge.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

"""Entry point called from JavaScript (worker and smoke test) inside Pyodide."""

import json

from demo_core import run_demo_analysis


def analyze_json(filename, file_bytes, job_desc, job_title, candidate_name):
    """Runs a demo scan and returns a JSON string: {"status": int, "body": dict}."""
    body, status = run_demo_analysis(
        filename, bytes(file_bytes), job_desc, job_title, candidate_name
    )
    return json.dumps({"status": status, "body": body})
