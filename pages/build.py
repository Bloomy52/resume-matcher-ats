# pages/build.py
# Copyright (c) 2026 Louie Bloomberg
# SPDX-License-Identifier: AGPL-3.0-only

"""Builds the static GitHub Pages demo into _site/.

Renders the Flask demo templates into plain HTML, copies the Python sources
Pyodide runs, and downloads the pure-Python wheels (versions pinned by uv.lock).
Usage: python pages/build.py [--out _site]
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLED_PACKAGES = ['pypdf', 'python-docx']  # lxml and typing-extensions come from Pyodide
PY_SOURCES = [ROOT / 'analyzer.py', ROOT / 'demo_core.py', ROOT / 'pages' / 'bridge.py']


def replace_once(text, old, new):
    if old not in text:
        raise SystemExit(f"build: expected text not found: {old[:60]!r}")
    return text.replace(old, new)


def static_url(match):
    return f"static/{match.group(1)}"


def render_index(version):
    html = (ROOT / 'templates' / 'demo_index.html').read_text()

    html = replace_once(
        html,
        '<span class="status-label">Server Status: Online</span>',
        '<span class="status-label" id="engine-status">Loading analysis engine…</span>',
    )
    html = replace_once(html, "{{ server_os|default('Cloud Demo') }}", 'Your browser')
    html = replace_once(html, "{{ server_os|default('Cloud Instance') }}", 'your browser')
    html = replace_once(html, 'Running on', 'Running in')
    html = html.replace('{{ app_version }}', version)
    html = replace_once(html, "{{ url_for('get_license') }}", 'license.html')
    html = replace_once(
        html,
        'Uploaded resumes and job descriptions are processed temporarily and automatically deleted.',
        'Your resume and job description are analyzed entirely in your browser and are never uploaded to a server.',
    )
    html = replace_once(
        html,
        "Avoid uploading resumes containing sensitive personal information you wouldn't want processed by a public demo.",
        'The analysis engine downloads once from a CDN when the page loads; your files stay on your device.',
    )

    # Swap the Flask route block for the in-browser engine.
    html = re.sub(
        r'    <!-- Inline static templates or variables for JS -->.*?</script>\n',
        '',
        html,
        flags=re.S,
    )
    html = replace_once(
        html,
        "<script src=\"{{ url_for('static', filename='demo.js') }}?v=2\"></script>",
        '<script src="pages/engine.js"></script>\n    <script src="static/demo.js"></script>',
    )
    html = re.sub(r"\{\{ url_for\('static', filename='([^']+)'\) \}\}", static_url, html)

    leftover = re.findall(r'\{\{.*?\}\}|\{%.*?%\}', html)
    if leftover:
        raise SystemExit(f"build: unrendered template tags in index: {leftover}")
    return html


def render_license():
    html = (ROOT / 'templates' / 'license.html').read_text()
    html = re.sub(r"\{\{ url_for\('static', filename='([^']+)'\) \}\}", static_url, html)
    leftover = re.findall(r'\{\{.*?\}\}|\{%.*?%\}', html)
    if leftover:
        raise SystemExit(f"build: unrendered template tags in license: {leftover}")
    return html


def locked_versions():
    lock = tomllib.loads((ROOT / 'uv.lock').read_text())
    return {p['name']: p['version'] for p in lock['package']}


def download_wheels(dest):
    versions = locked_versions()
    dest.mkdir(parents=True)
    specs = [f"{name}=={versions[name]}" for name in BUNDLED_PACKAGES]
    subprocess.run(
        [sys.executable, '-m', 'pip', 'download', '--no-deps', '--only-binary=:all:',
         '--dest', str(dest), *specs],
        check=True,
    )
    wheels = sorted(p.name for p in dest.glob('*.whl'))
    if len(wheels) != len(BUNDLED_PACKAGES):
        raise SystemExit(f"build: expected {len(BUNDLED_PACKAGES)} wheels, got {wheels}")
    (dest / 'manifest.json').write_text(json.dumps({'wheels': wheels}, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=str(ROOT / '_site'))
    out = Path(parser.parse_args().out).resolve()

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    version = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']

    (out / 'index.html').write_text(render_index(version))
    (out / 'license.html').write_text(render_license())
    (out / '.nojekyll').write_text('')

    (out / 'static').mkdir()
    shutil.copy(ROOT / 'static' / 'style.css', out / 'static' / 'style.css')
    shutil.copy(ROOT / 'static' / 'demo.js', out / 'static' / 'demo.js')

    (out / 'pages').mkdir()
    for name in ('engine.js', 'worker.js'):
        shutil.copy(ROOT / 'pages' / name, out / 'pages' / name)

    (out / 'py').mkdir()
    for src in PY_SOURCES:
        shutil.copy(src, out / 'py' / src.name)

    download_wheels(out / 'wheels')
    print(f"Built {out}")


if __name__ == '__main__':
    main()
