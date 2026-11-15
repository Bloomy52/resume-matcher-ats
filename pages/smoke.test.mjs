// pages/smoke.test.mjs
// Copyright (c) 2026 Louie Bloomberg
// SPDX-License-Identifier: AGPL-3.0-only

// Loads the *built* site (_site/) into Pyodide the same way worker.js does and
// runs a real PDF and a real DOCX through the bridge. Run `python pages/build.py` first.
import { test, before } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadPyodide } from 'pyodide';

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '_site');
const RESUME_LINES = [
  'Jane Developer',
  'jane@example.com',
  '555-123-4567',
  'Experience',
  'Senior Python developer building REST APIs with Flask and PostgreSQL.',
  'Skills',
  'Python, Flask, SQL, Docker, Git',
];
const JOB_DESC = 'Python developer\nWe need Python, Flask, REST APIs, Docker and Kubernetes experience.';

// Minimal single-page PDF with a Helvetica text stream.
function buildPdf(lines) {
  const esc = (s) => s.replace(/[\\()]/g, '\\$&');
  const content = ['BT', '/F1 12 Tf', '14 TL', '72 720 Td',
    ...lines.map((l) => `(${esc(l)}) Tj T*`), 'ET'].join('\n');
  const objs = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>',
    `<< /Length ${content.length} >>\nstream\n${content}\nendstream`,
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
  ];
  let pdf = '%PDF-1.4\n';
  const offsets = [];
  objs.forEach((o, i) => { offsets.push(pdf.length); pdf += `${i + 1} 0 obj\n${o}\nendobj\n`; });
  const xref = pdf.length;
  pdf += `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n`;
  offsets.forEach((o) => { pdf += `${String(o).padStart(10, '0')} 00000 n \n`; });
  pdf += `trailer\n<< /Size ${objs.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
  return new Uint8Array(Buffer.from(pdf, 'latin1'));
}

let py;
let analyzeJson;

before(async () => {
  py = await loadPyodide();
  await py.loadPackage(['micropip', 'lxml']);

  const wheelDir = path.join(site, 'wheels');
  const { wheels } = JSON.parse(fs.readFileSync(path.join(wheelDir, 'manifest.json'), 'utf8'));
  py.FS.mkdirTree('/tmp/wheels');
  for (const w of wheels) py.FS.writeFile(`/tmp/wheels/${w}`, fs.readFileSync(path.join(wheelDir, w)));
  await py.pyimport('micropip').install(wheels.map((w) => `emfs:/tmp/wheels/${w}`));

  for (const f of fs.readdirSync(path.join(site, 'py'))) {
    py.FS.writeFile(`/home/pyodide/${f}`, fs.readFileSync(path.join(site, 'py', f), 'utf8'));
  }
  py.runPython(`import sys; sys.path.insert(0, '/home/pyodide')`);
  analyzeJson = py.pyimport('bridge').analyze_json;
});

function analyze(filename, bytes, jobDesc = JOB_DESC, jobTitle = '', name = '') {
  return JSON.parse(analyzeJson(filename, bytes, jobDesc, jobTitle, name));
}

async function buildDocx(lines) {
  py.globals.set('_lines', lines);
  const proxy = await py.runPythonAsync(`
import io
from docx import Document
doc = Document()
for line in _lines.to_py():
    doc.add_paragraph(line)
buf = io.BytesIO()
doc.save(buf)
buf.getvalue()
`);
  const bytes = proxy.toJs();
  proxy.destroy();
  return bytes;
}

function assertGoodResult(res) {
  assert.equal(res.status, 200, JSON.stringify(res.body));
  assert.equal(res.body.candidate_name, 'Jane Developer');
  assert.equal(res.body.candidate_email, 'jane@example.com');
  assert.equal(res.body.candidate_phone, '555-123-4567');
  assert.equal(res.body.job_title, 'Python developer');
  assert.ok(typeof res.body.analysis === 'object' && res.body.analysis !== null);
  assert.ok(JSON.stringify(res.body.analysis).toLowerCase().includes('python'));
}

test('analyzes a real PDF', () => {
  assertGoodResult(analyze('resume.pdf', buildPdf(RESUME_LINES)));
});

test('analyzes a real DOCX', async () => {
  assertGoodResult(analyze('resume.docx', await buildDocx(RESUME_LINES)));
});

test('rejects unsupported file types', () => {
  const res = analyze('resume.txt', new Uint8Array([104, 105]));
  assert.equal(res.status, 400);
  assert.match(res.body.error, /PDF and DOCX/);
});

test('requires a job description', () => {
  const res = analyze('resume.pdf', buildPdf(RESUME_LINES), '   ');
  assert.equal(res.status, 400);
  assert.match(res.body.error, /Job description/);
});

test('reports unparseable files', () => {
  const res = analyze('resume.pdf', new Uint8Array([1, 2, 3]));
  assert.equal(res.status, 400);
});
