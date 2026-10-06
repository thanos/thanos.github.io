#!/usr/bin/env node
/**
 * Print cover.md + resume.md to letter-size PDFs via headless Chrome.
 *
 *   node scripts/resume/render-pdf.mjs --slug plexus-eng-manager-prediction-markets
 *   npm run resume:pdf -- --slug <slug>
 */
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../..');

function argValue(flag) {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : null;
}

const slug = argValue('--slug');
if (!slug) {
  console.error('Pass --slug <flavor-slug>');
  process.exit(1);
}

const outDir = path.join(root, 'content/resume/out', slug);
if (!fs.existsSync(outDir)) {
  console.error(`Missing ${path.relative(root, outDir)} — pack/generate first`);
  process.exit(1);
}

const chrome =
  process.env.RESUME_CHROME ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function inline(s) {
  return escapeHtml(s)
    .replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}

function mdToHtml(md) {
  const lines = md.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  let i = 0;
  let para = [];
  let list = null;

  const flushPara = () => {
    if (!para.length) return;
    out.push(`<p>${inline(para.join(' '))}</p>`);
    para = [];
  };
  const flushList = () => {
    if (!list) return;
    out.push(`<ul>${list.map((t) => `<li>${inline(t)}</li>`).join('')}</ul>`);
    list = null;
  };

  while (i < lines.length) {
    const line = lines[i].trimEnd();
    i += 1;
    if (!line.trim()) {
      flushPara();
      flushList();
      continue;
    }
    if (line.startsWith('# ')) {
      flushPara();
      flushList();
      out.push(`<h1>${inline(line.slice(2))}</h1>`);
      continue;
    }
    if (line.startsWith('## ')) {
      flushPara();
      flushList();
      out.push(`<h2>${inline(line.slice(3))}</h2>`);
      continue;
    }
    if (line.startsWith('### ')) {
      flushPara();
      flushList();
      out.push(`<h3>${inline(line.slice(4))}</h3>`);
      continue;
    }
    if (/^[-*] /.test(line.trim())) {
      flushPara();
      list = list || [];
      list.push(line.trim().replace(/^[-*] /, ''));
      continue;
    }
    flushList();
    para.push(line.trim());
  }
  flushPara();
  flushList();
  return out.join('\n');
}

const css = `    @page { size: letter; margin: 0.5in 0.58in 0.48in; }
    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0; color: #1a1a1a;
      font: 9.6pt/1.32 "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
      -webkit-print-color-adjust: exact; print-color-adjust: exact;
    }
    h1 {
      font: 700 18.5pt/1.1 "Helvetica Neue", Helvetica, Arial, sans-serif;
      letter-spacing: 0.02em; margin: 0 0 6px; text-align: center;
    }
    h2 {
      font: 700 9pt/1.2 "Helvetica Neue", Helvetica, Arial, sans-serif;
      text-transform: uppercase; letter-spacing: 0.12em;
      border-bottom: 0.7pt solid #222; margin: 11px 0 6px; padding: 0 0 2px;
    }
    h3 {
      font: 700 10pt/1.25 "Helvetica Neue", Helvetica, Arial, sans-serif;
      margin: 7px 0 2px;
    }
    p { margin: 0 0 5px; }
    ul { margin: 2px 0 6px; padding: 0 0 0 1.05em; }
    li { margin: 0 0 2px; }
    a { color: #1a365d; text-decoration: none; }
    code { font-size: 0.92em; }
    .letter { font-size: 10.4pt; line-height: 1.38; }
    .letter h1 { font-size: 14pt; text-align: left; }
    @page letter { size: letter; margin: 0.75in 0.9in 0.7in; }
    .letter { page: letter; }
`;

function page(title, body, extraClass = '') {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>${escapeHtml(title)}</title>
  <style>${css}</style>
</head>
<body class="${extraClass}">
${body}
</body>
</html>
`;
}

function printPdf(htmlPath, pdfPath) {
  if (!fs.existsSync(chrome)) {
    console.error(`Chrome not found at ${chrome}. Set RESUME_CHROME. HTML left at ${htmlPath}`);
    return false;
  }
  const r = spawnSync(
    chrome,
    [
      '--headless=new',
      '--disable-gpu',
      '--no-pdf-header-footer',
      `--print-to-pdf=${pdfPath}`,
      `file://${htmlPath}`,
    ],
    { encoding: 'utf8' }
  );
  if (r.status !== 0) {
    console.error(r.stderr || r.stdout || 'Chrome print failed');
    process.exit(r.status ?? 1);
  }
  console.log(path.relative(root, pdfPath));
  return true;
}

const resumeMd = fs.readFileSync(path.join(outDir, 'resume.md'), 'utf8');
const coverMd = fs.readFileSync(path.join(outDir, 'cover.md'), 'utf8');

const resumeHtml = path.join(outDir, 'resume.html');
const coverHtml = path.join(outDir, 'cover.html');
fs.writeFileSync(resumeHtml, page('Thanos Vassilakis — résumé', mdToHtml(resumeMd)));
fs.writeFileSync(coverHtml, page('Thanos Vassilakis — covering letter', mdToHtml(coverMd), 'letter'));

printPdf(resumeHtml, path.join(outDir, 'Thanos-Vassilakis-resume.pdf'));
printPdf(coverHtml, path.join(outDir, 'Thanos-Vassilakis-cover.pdf'));
