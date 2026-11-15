// pages/worker.js
// Copyright (c) 2026 Louie Bloomberg
// SPDX-License-Identifier: AGPL-3.0-only

// Runs Pyodide and the analyzer off the main thread so the UI never freezes.
// Pinned version, loaded from the jsDelivr CDN. Keep in sync with pages/package.json.
import { loadPyodide } from 'https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs';

const PY_FILES = ['analyzer.py', 'demo_core.py', 'bridge.py'];
let pyodide = null;
let analyzeJson = null;

async function init() {
    const base = new URL('../', self.location.href);

    pyodide = await loadPyodide();
    await pyodide.loadPackage(['micropip', 'lxml']);

    // pypdf and python-docx ship with the site, so PyPI is not needed at runtime.
    const manifest = await (await fetch(new URL('wheels/manifest.json', base))).json();
    const micropip = pyodide.pyimport('micropip');
    await micropip.install(manifest.wheels.map((w) => new URL(`wheels/${w}`, base).href));

    for (const name of PY_FILES) {
        const source = await (await fetch(new URL(`py/${name}`, base))).text();
        pyodide.FS.writeFile(`/home/pyodide/${name}`, source);
    }
    pyodide.runPython(`import sys; sys.path.insert(0, '/home/pyodide')`);
    analyzeJson = pyodide.pyimport('bridge').analyze_json;
}

const ready = init();

self.onmessage = async (event) => {
    const { id, type, payload } = event.data;
    try {
        await ready;
        if (type !== 'analyze') {
            throw new Error(`Unknown message type: ${type}`);
        }
        const result = analyzeJson(
            payload.filename,
            new Uint8Array(payload.bytes),
            payload.jobDesc,
            payload.jobTitle,
            payload.candidateName,
        );
        self.postMessage({ id, ok: true, result: JSON.parse(result) });
    } catch (error) {
        self.postMessage({ id, ok: false, error: String(error && error.message || error) });
    }
};

ready.then(
    () => self.postMessage({ type: 'ready' }),
    (error) => self.postMessage({ type: 'init-error', error: String(error && error.message || error) }),
);
