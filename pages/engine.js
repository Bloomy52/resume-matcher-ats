// pages/engine.js
// Copyright (c) 2026 Louie Bloomberg
// SPDX-License-Identifier: AGPL-3.0-only

// Replaces the Flask API for the static GitHub Pages demo. Resumes are analyzed
// by Python (Pyodide) in a Web Worker and never leave the user's browser.
(function () {
    const worker = new Worker(new URL('./worker.js', document.currentScript.src), { type: 'module' });
    const pending = new Map();
    let nextId = 1;

    const statusEl = () => document.getElementById('engine-status');
    const submitBtn = () => document.getElementById('btn-submit-scan');

    function setStatus(text, state) {
        const el = statusEl();
        if (el) {
            el.textContent = text;
            el.dataset.state = state;
        }
        const btn = submitBtn();
        if (btn && state === 'loading') btn.disabled = true;
    }

    let resolveReady, rejectReady;
    const ready = new Promise((resolve, reject) => { resolveReady = resolve; rejectReady = reject; });
    ready.catch(() => {});

    setStatus('Loading analysis engine…', 'loading');

    worker.onmessage = (event) => {
        const msg = event.data;
        if (msg.type === 'ready') {
            setStatus('Engine ready', 'ready');
            const btn = submitBtn();
            if (btn) btn.disabled = false;
            resolveReady();
        } else if (msg.type === 'init-error') {
            setStatus('Engine failed to load', 'error');
            rejectReady(new Error(`The analysis engine failed to load: ${msg.error}`));
        } else if (pending.has(msg.id)) {
            const { resolve, reject } = pending.get(msg.id);
            pending.delete(msg.id);
            if (msg.ok) resolve(msg.result);
            else reject(new Error(msg.error));
        }
    };

    worker.onerror = (event) => {
        setStatus('Engine failed to load', 'error');
        rejectReady(new Error(`The analysis engine failed to load: ${event.message || 'worker error'}`));
    };

    window.DEMO_BACKEND = {
        async analyze(formData) {
            await ready;
            const file = formData.get('resume');
            if (!file || !file.name) {
                throw new Error('Resume file is required');
            }
            const bytes = await file.arrayBuffer();
            const id = nextId++;
            const reply = new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
            worker.postMessage({
                id,
                type: 'analyze',
                payload: {
                    filename: file.name,
                    bytes,
                    jobDesc: formData.get('job_description') || '',
                    jobTitle: formData.get('job_title') || '',
                    candidateName: formData.get('candidate_name') || '',
                },
            }, [bytes]);
            const { status, body } = await reply;
            if (status !== 200) {
                throw new Error(body.error || 'An unknown error occurred during scanning');
            }
            return body;
        },
        async reset() {
            // Nothing is stored server-side in the static demo.
        },
    };
})();
