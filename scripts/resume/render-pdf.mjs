#!/usr/bin/env node
/**
 * Print cover.md + resume.md to letter-size PDFs via headless Chrome.
 *
 *   node scripts/resume/render-pdf.mjs --slug plexus-eng-manager-prediction-markets
 *   npm run resume:pdf -- --slug <slug>
 *   npm run resume:pdf -- --material   # content/material → public/material PDF
 *   npm run resume:pdf -- --private contracting
 *   npm run resume:pdf -- --private-all
 *
 * Markdown may include `<!-- pagebreak -->` (alone on a line) for an explicit
 * CSS page break. That marker is never shown as text.
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
const material = process.argv.includes('--material');
const privateName = argValue('--private');
const privateAll = process.argv.includes('--private-all');
if (!slug && !material && !privateName && !privateAll) {
  console.error('Pass --slug <flavor-slug>, --material, --private <name>, or --private-all');
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
    .replace(/\[([^\]]+)\]\((https?:[^)]+|mailto:[^)]+|\/[^)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}

const PAGEBREAK_RE = /^<!--\s*pagebreak\s*-->$/i;

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
    if (PAGEBREAK_RE.test(line.trim())) {
      flushPara();
      flushList();
      out.push('<div class="pagebreak" role="separator" aria-hidden="true"></div>');
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
    if (/^---+$/.test(line.trim())) {
      flushPara();
      flushList();
      out.push('<hr />');
      continue;
    }
    if (line.trim().startsWith('|')) {
      flushPara();
      flushList();
      const rows = [line.trim()];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        rows.push(lines[i].trim());
        i += 1;
      }
      const parsed = rows
        .filter((r) => !/^\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$/.test(r))
        .map((r) =>
          r
            .replace(/^\|/, '')
            .replace(/\|$/, '')
            .split('|')
            .map((c) => c.trim())
        );
      if (parsed.length) {
        const [header, ...body] = parsed;
        const thead = `<tr>${header.map((c) => `<th>${inline(c)}</th>`).join('')}</tr>`;
        const tbody = body
          .map((cols) => `<tr>${cols.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`)
          .join('');
        out.push(`<table><thead>${thead}</thead><tbody>${tbody}</tbody></table>`);
      }
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
    hr { border: 0; border-top: 0.7pt solid #ccc; margin: 10px 0; }
    table { width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 9pt; }
    th, td { border: 0.5pt solid #ccc; padding: 3px 6px; vertical-align: top; text-align: left; }
    th { font-weight: 700; background: #f5f5f5; }
    a { color: #1a365d; text-decoration: none; }
    code { font-size: 0.92em; }
    /* Prefer break-before so a trailing marker does not mint a blank last page. */
    .pagebreak {
      break-before: page;
      page-break-before: always;
      height: 0;
      margin: 0;
      padding: 0;
      border: 0;
    }
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

function renderDocx(htmlPath, docxPath) {
  const r = spawnSync(
    'textutil',
    ['-convert', 'docx', '-output', docxPath, htmlPath],
    { encoding: 'utf8' }
  );
  if (r.status === 0) {
    console.log(path.relative(root, docxPath));
  } else {
    console.warn('textutil docx conversion skipped:', r.stderr || r.stdout || 'failed');
  }
}

function renderPrivateVariant(name) {
  const outDir = path.join(root, 'content/resume/private', name);
  const mdPath = path.join(outDir, 'resume.md');
  if (!fs.existsSync(mdPath)) {
    console.error(`Missing ${path.relative(root, mdPath)}`);
    process.exit(1);
  }
  const resumeMd = fs.readFileSync(mdPath, 'utf8');
  const resumeHtml = path.join(outDir, 'resume.html');
  const resumePdf = path.join(outDir, 'Thanos-Vassilakis-resume.pdf');
  const resumeDocx = path.join(outDir, 'Thanos-Vassilakis-resume.docx');
  fs.writeFileSync(resumeHtml, page(`Thanos Vassilakis — ${name}`, mdToHtml(resumeMd)));
  printPdf(resumeHtml, resumePdf);
  renderDocx(resumeHtml, resumeDocx);
}

if (privateAll) {
  const base = path.join(root, 'content/resume/private');
  for (const name of fs.readdirSync(base)) {
    const md = path.join(base, name, 'resume.md');
    if (fs.existsSync(md)) renderPrivateVariant(name);
  }
  process.exit(0);
}

if (privateName) {
  renderPrivateVariant(privateName);
  process.exit(0);
}

if (material) {
  const mdPath = path.join(root, 'content/material/thanos-vassilakis-resume.md');
  const outDir = path.join(root, 'public/material');
  fs.mkdirSync(outDir, { recursive: true });
  let resumeMd = fs.readFileSync(mdPath, 'utf8');
  // Drop the self-referential PDF footer line from the printed PDF.
  resumeMd = resumeMd.replace(/\n\*Also available as \[PDF\][^\n]*\n?/g, '\n');
  const resumeHtml = path.join(outDir, 'thanos-vassilakis-resume.html');
  const resumePdf = path.join(outDir, 'thanos-vassilakis-resume.pdf');
  fs.writeFileSync(resumeHtml, page('Thanos Vassilakis — résumé', mdToHtml(resumeMd)));
  printPdf(resumeHtml, resumePdf);
  renderDocx(resumeHtml, path.join(outDir, 'thanos-vassilakis-resume.docx'));
  process.exit(0);
}

const outDir = path.join(root, 'content/resume/out', slug);
if (!fs.existsSync(outDir)) {
  console.error(`Missing ${path.relative(root, outDir)} — pack/generate first`);
  process.exit(1);
}

const resumeMd = fs.readFileSync(path.join(outDir, 'resume.md'), 'utf8');
const coverMd = fs.readFileSync(path.join(outDir, 'cover.md'), 'utf8');

const resumeHtml = path.join(outDir, 'resume.html');
const coverHtml = path.join(outDir, 'cover.html');
fs.writeFileSync(resumeHtml, page('Thanos Vassilakis — résumé', mdToHtml(resumeMd)));
fs.writeFileSync(coverHtml, page('Thanos Vassilakis — covering letter', mdToHtml(coverMd), 'letter'));

printPdf(resumeHtml, path.join(outDir, 'Thanos-Vassilakis-resume.pdf'));
printPdf(coverHtml, path.join(outDir, 'Thanos-Vassilakis-cover.pdf'));
