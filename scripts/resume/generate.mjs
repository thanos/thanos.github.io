#!/usr/bin/env node
/**
 * Generate cover.md / resume.md / provenance.md from a pack via an LLM.
 *
 * Prerequisites:
 *   npm run resume:pack -- --brief <slug>
 *
 * Env (see .env.example):
 *   RESUME_LLM_PROVIDER=openai|anthropic   (default: openai)
 *   RESUME_LLM_MODEL=...                  (provider default if unset)
 *   OPENAI_API_KEY=...                    (openai / OpenAI-compatible)
 *   OPENAI_BASE_URL=...                   (optional; OpenRouter, etc.)
 *   ANTHROPIC_API_KEY=...                 (anthropic)
 *
 * Usage:
 *   node scripts/resume/generate.mjs --brief principal-md-dev-manager
 *   npm run resume:generate -- --brief principal-md-dev-manager
 *   npm run resume:flavor -- --brief principal-md-dev-manager   # pack + generate
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseYaml } from 'yaml';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../..');
const resumeRoot = path.join(root, 'content/resume');

function loadDotEnv() {
  const envPath = path.join(root, '.env');
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, 'utf8').split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq < 0) continue;
    const key = trimmed.slice(0, eq).trim();
    let val = trimmed.slice(eq + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = val;
  }
}

function argValue(flag) {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : null;
}

function resolveSlug() {
  const briefArg = argValue('--brief');
  if (!briefArg) throw new Error('Pass --brief <slug>');
  if (briefArg.endsWith('.yaml') || briefArg.endsWith('.yml') || briefArg.includes('/')) {
    return path.basename(briefArg).replace(/\.ya?ml$/, '');
  }
  return briefArg;
}

function extractJson(text) {
  const trimmed = text.trim();
  try {
    return JSON.parse(trimmed);
  } catch {
    /* continue */
  }
  const fence = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fence) {
    return JSON.parse(fence[1].trim());
  }
  const start = trimmed.indexOf('{');
  const end = trimmed.lastIndexOf('}');
  if (start >= 0 && end > start) {
    return JSON.parse(trimmed.slice(start, end + 1));
  }
  throw new Error('Model response was not valid JSON');
}

function slimPack(pack) {
  return {
    brief: pack.brief,
    profile: pack.profile,
    jobs: pack.jobs,
    oss_selected: pack.oss_selected,
    selected: (pack.selected || []).map((row) => ({
      id: row.id,
      score: row.score,
      specializedMustHits: row.specializedMustHits,
      hits: row.hits,
      atom: row.atom,
    })),
  };
}

async function callOpenAI({ model, system, user }) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not set (see .env.example)');
  }
  const base = (process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1').replace(/\/$/, '');
  const res = await fetch(`${base}/chat/completions`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      temperature: 0.3,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: user },
      ],
    }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(`OpenAI API ${res.status}: ${JSON.stringify(body)}`);
  }
  const text = body.choices?.[0]?.message?.content;
  if (!text) throw new Error('OpenAI response missing content');
  return { text, model: body.model || model };
}

async function callAnthropic({ model, system, user }) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY is not set (see .env.example)');
  }
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      max_tokens: 8192,
      temperature: 0.3,
      system,
      messages: [{ role: 'user', content: user }],
    }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(`Anthropic API ${res.status}: ${JSON.stringify(body)}`);
  }
  const text = (body.content || [])
    .filter((b) => b.type === 'text')
    .map((b) => b.text)
    .join('\n');
  if (!text) throw new Error('Anthropic response missing text');
  return { text, model: body.model || model };
}

async function main() {
  loadDotEnv();
  const slug = resolveSlug();
  const outDir = path.join(resumeRoot, 'out', slug);
  const packPath = path.join(outDir, 'pack.json');
  if (!fs.existsSync(packPath)) {
    throw new Error(
      `Missing ${path.relative(root, packPath)}. Run: npm run resume:pack -- --brief ${slug}`
    );
  }

  const pack = JSON.parse(fs.readFileSync(packPath, 'utf8'));
  const system = fs.readFileSync(path.join(__dirname, 'system-prompt.md'), 'utf8');
  const provider = (process.env.RESUME_LLM_PROVIDER || 'openai').toLowerCase();
  const model =
    process.env.RESUME_LLM_MODEL ||
    (provider === 'anthropic' ? 'claude-sonnet-4-5-20250929' : 'gpt-4.1');

  const user = [
    `Generate cover_md, resume_md, and provenance_md for slug "${slug}".`,
    `Provider model id for provenance: ${model}`,
    '',
    'PACK JSON:',
    JSON.stringify(slimPack(pack), null, 2),
  ].join('\n');

  console.log(`Generating with ${provider} / ${model} …`);
  const { text, model: usedModel } =
    provider === 'anthropic'
      ? await callAnthropic({ model, system, user })
      : await callOpenAI({ model, system, user });

  const parsed = extractJson(text);
  for (const key of ['cover_md', 'resume_md', 'provenance_md']) {
    if (typeof parsed[key] !== 'string' || !parsed[key].trim()) {
      throw new Error(`Model JSON missing string field: ${key}`);
    }
  }

  let provenance = parsed.provenance_md.trim();
  if (!/model:/i.test(provenance)) {
    provenance += `\n\n- Model: ${usedModel} (${provider})\n`;
  }

  fs.writeFileSync(path.join(outDir, 'cover.md'), `${parsed.cover_md.trim()}\n`);
  fs.writeFileSync(path.join(outDir, 'resume.md'), `${parsed.resume_md.trim()}\n`);
  fs.writeFileSync(path.join(outDir, 'provenance.md'), `${provenance.trim()}\n`);
  fs.writeFileSync(
    path.join(outDir, 'generation.json'),
    JSON.stringify(
      {
        generated_at: new Date().toISOString(),
        provider,
        model: usedModel,
        slug,
      },
      null,
      2
    )
  );

  console.log(`Wrote:`);
  console.log(`  ${path.relative(root, path.join(outDir, 'cover.md'))}`);
  console.log(`  ${path.relative(root, path.join(outDir, 'resume.md'))}`);
  console.log(`  ${path.relative(root, path.join(outDir, 'provenance.md'))}`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
