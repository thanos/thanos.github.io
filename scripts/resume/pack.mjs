#!/usr/bin/env node
/**
 * Score & pack resume experiences for a job brief.
 *
 * Usage:
 *   node scripts/resume/pack.mjs --brief principal-md-dev-manager
 *   node scripts/resume/pack.mjs --brief path/to/brief.yaml
 *
 * Writes (gitignored):
 *   content/resume/out/<slug>/pack.json
 *   content/resume/out/<slug>/pack.md
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseYaml } from 'yaml';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../..');
const resumeRoot = path.join(root, 'content/resume');

function readYaml(file) {
  return parseYaml(fs.readFileSync(file, 'utf8'));
}

function listYaml(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.yaml') || f.endsWith('.yml'))
    .map((f) => path.join(dir, f));
}

/** Leadership-oriented musts — useful for jobs, noisy for OSS selection. */
const LEADERSHIP_MUST = new Set([
  'engineering-management',
  'mentoring',
  'principal',
  'development-manager',
  'managing-director',
  'md',
  'people-management',
  'budget',
  'hiring',
]);

/** Generic tech musts — true but weak discriminators for OSS lists. */
const GENERIC_TECH_MUST = new Set([
  'architecture',
  'platform',
  'distributed-systems',
]);

/** Expand brief signals into match tokens (and phrases to require). */
const SIGNAL_ALIASES = {
  'ai/ml': ['ai', 'ml', 'ai/ml', 'machine-learning', 'llm', 'zkml', 'bittensor', 'agents'],
  'big-data': ['big-data', 'bigdata', 'arrow', 'zarr', 'streaming', 'sketch', 'columnar', 'data-lake'],
  'quantum-computing': ['quantum-computing', 'systolic', 'spatial-dataflow', 'quantum-computing-adjacent'],
  'distributed-systems': ['distributed-systems', 'distributed'],
  architecture: ['architecture'],
  platform: ['platform', 'data-platform'],
};

/** Do not treat post-quantum crypto as quantum-computing. */
function atomTextBlob(atom) {
  const signals = atom.signals || {};
  return [
    atom.title,
    atom.summary,
    ...(atom.bullets || []),
    ...(signals.domains || []),
    ...(signals.skills || []),
    ...(signals.keywords || []),
    ...(signals.impact || []),
    signals.seniority,
    atom.kind,
    atom.org,
    atom.role,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
}

function tokenize(...parts) {
  return new Set(
    parts
      .flat()
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .split(/[^a-z0-9+#._/-]+/)
      .flatMap((t) => t.split('/'))
      .filter((t) => t.length > 1)
  );
}

function expandSignal(signal) {
  const key = String(signal).toLowerCase();
  return SIGNAL_ALIASES[key] || [key];
}

function matchesSignal(atomTokens, blob, signal) {
  const key = String(signal).toLowerCase();
  // post-quantum ≠ quantum computing
  if (key === 'quantum-computing' || key === 'quantum') {
    if (/\bpost[- ]?quantum\b/.test(blob) && !/\bquantum-computing\b|\bsystolic\b|\bzkml\b/.test(blob)) {
      return false;
    }
  }
  for (const alias of expandSignal(signal)) {
    if (atomTokens.has(alias)) return true;
    if (alias.length > 3 && blob.includes(alias)) return true;
  }
  return false;
}

function scoreAtom(atom, briefTokens, must, nice, avoid) {
  const blob = atomTextBlob(atom);
  const atomTokens = tokenize(blob);
  const isOssLike = atom.kind === 'oss' || atom.kind === 'article';

  let score = 0;
  const hits = [];
  let domainMustHits = 0;
  let specializedMustHits = 0;

  for (const t of briefTokens) {
    if (atomTokens.has(t)) {
      score += 1;
      hits.push(t);
    }
  }

  for (const t of must) {
    const key = String(t).toLowerCase();
    const leadership = LEADERSHIP_MUST.has(key);
    const genericTech = GENERIC_TECH_MUST.has(key);
    if (!matchesSignal(atomTokens, blob, t)) continue;

    if (isOssLike && leadership) {
      continue; // ignore leadership musts for OSS/articles
    }

    if (isOssLike) {
      domainMustHits += 1;
      if (genericTech) {
        score += 3;
        hits.push(`generic-must:${t}`);
      } else {
        specializedMustHits += 1;
        score += 14;
        hits.push(`domain-must:${t}`);
      }
    } else {
      score += leadership ? 4 : 5;
      hits.push(`must:${t}`);
    }
  }

  for (const t of nice) {
    if (!matchesSignal(atomTokens, blob, t)) continue;
    score += isOssLike ? 3 : 2;
    hits.push(`nice:${t}`);
  }

  for (const t of avoid) {
    if (matchesSignal(atomTokens, blob, t)) {
      score -= 3;
      hits.push(`avoid:${t}`);
    }
  }

  const kindBoost = {
    job_role: 3,
    ran: 2,
    built: 2,
    oss: 0,
    article: 0,
    interest: 0,
    talk: 1,
    publication: 1,
  };
  score += kindBoost[atom.kind] || 0;

  if (atom.job === 'rbc' || atom.org === 'RBC') score += 1;

  // OSS/articles: require specialized domain musts when the brief has any
  if (isOssLike) {
    const specializedMusts = must.filter((m) => {
      const k = String(m).toLowerCase();
      return !LEADERSHIP_MUST.has(k) && !GENERIC_TECH_MUST.has(k);
    });
    if (specializedMusts.length > 0 && specializedMustHits === 0) {
      score -= 25;
      hits.push('penalty:no-specialized-must');
    } else {
      score += specializedMustHits * 3;
    }
  }

  return {
    score,
    hits: [...new Set(hits)].slice(0, 16),
    domainMustHits,
    specializedMustHits,
  };
}

function resolveBriefPath(arg) {
  if (!arg) throw new Error('Pass --brief <slug-or-path>');
  if (arg.endsWith('.yaml') || arg.endsWith('.yml') || arg.includes('/')) {
    return path.isAbsolute(arg) ? arg : path.join(root, arg);
  }
  return path.join(resumeRoot, 'briefs', `${arg}.yaml`);
}

function main() {
  const args = process.argv.slice(2);
  const bi = args.indexOf('--brief');
  const briefPath = resolveBriefPath(bi >= 0 ? args[bi + 1] : null);
  if (!fs.existsSync(briefPath)) {
    console.error(`Brief not found: ${briefPath}`);
    process.exit(1);
  }

  const brief = readYaml(briefPath);
  const slug =
    brief.slug ||
    path.basename(briefPath).replace(/\.ya?ml$/, '');

  const profile = readYaml(path.join(resumeRoot, 'profile.yaml'));
  const jobs = Object.fromEntries(
    listYaml(path.join(resumeRoot, 'jobs')).map((f) => {
      const j = readYaml(f);
      return [j.id, j];
    })
  );
  const experiences = listYaml(path.join(resumeRoot, 'experiences')).map(readYaml);

  const must = (brief.emphasis?.must_signal || []).map(String);
  const nice = (brief.emphasis?.nice || []).map(String);
  const avoid = (brief.emphasis?.avoid || []).map(String);
  const briefTokens = tokenize(
    brief.target?.company,
    brief.target?.role,
    brief.target?.posting_text,
    must,
    nice,
    brief.emphasis?.keywords
  );

  const ranked = experiences
    .filter((a) => (a.visibility || 'public') !== 'private')
    .map((atom) => {
      const scored = scoreAtom(atom, briefTokens, must, nice, avoid);
      return { atom, ...scored };
    })
    .sort((a, b) => b.score - a.score);

  const limits = {
    max_total: brief.constraints?.max_atoms ?? 28,
    max_oss: brief.constraints?.max_oss ?? 5,
    max_articles: brief.constraints?.max_articles_as_proof ?? 3,
    max_interests: brief.constraints?.max_interests ?? 3,
    max_prior_roles: brief.constraints?.max_prior_roles ?? 4,
  };

  const hasSpecializedMusts = must.some((m) => {
    const k = String(m).toLowerCase();
    return !LEADERSHIP_MUST.has(k) && !GENERIC_TECH_MUST.has(k);
  });

  // OSS: cover specialized musts (AI/ML, big-data, …), then fill by score
  const specializedMustList = must.filter((m) => {
    const k = String(m).toLowerCase();
    return !LEADERSHIP_MUST.has(k) && !GENERIC_TECH_MUST.has(k);
  });

  const ossRanked = ranked
    .filter((r) => r.atom.kind === 'oss')
    .sort((a, b) => {
      if (b.specializedMustHits !== a.specializedMustHits) {
        return b.specializedMustHits - a.specializedMustHits;
      }
      return b.score - a.score;
    });

  const ossSelected = [];
  const coveredSpecialized = new Set();

  function specializedHitsFor(row) {
    const blob = atomTextBlob(row.atom);
    const tokens = tokenize(blob);
    return specializedMustList.filter((m) => matchesSignal(tokens, blob, m));
  }

  // Pass 1: cover each specialized must at least once when possible
  for (const need of specializedMustList) {
    if (ossSelected.length >= limits.max_oss) break;
    if (coveredSpecialized.has(need.toLowerCase())) continue;
    const candidate = ossRanked.find((row) => {
      if (ossSelected.includes(row)) return false;
      if (hasSpecializedMusts && row.specializedMustHits === 0) return false;
      return specializedHitsFor(row).some((m) => m.toLowerCase() === need.toLowerCase());
    });
    if (candidate) {
      ossSelected.push(candidate);
      for (const m of specializedHitsFor(candidate)) coveredSpecialized.add(m.toLowerCase());
    }
  }

  // Pass 2: fill remaining slots by score
  for (const row of ossRanked) {
    if (ossSelected.length >= limits.max_oss) break;
    if (ossSelected.includes(row)) continue;
    if (hasSpecializedMusts && row.specializedMustHits === 0) continue;
    ossSelected.push(row);
    for (const m of specializedHitsFor(row)) coveredSpecialized.add(m.toLowerCase());
  }

  const selected = [...ossSelected];
  let articles = 0;
  let interests = 0;
  const priorJobs = new Set();
  const selectedIds = new Set(ossSelected.map((r) => r.atom.id));

  for (const row of ranked) {
    if (selected.length >= limits.max_total) break;
    if (selectedIds.has(row.atom.id)) continue;
    const k = row.atom.kind;
    if (k === 'oss') continue; // already handled
    if (k === 'article') {
      if (articles >= limits.max_articles) continue;
      if (hasSpecializedMusts && row.specializedMustHits === 0) continue;
      articles++;
    }
    if (k === 'interest') {
      if (interests >= limits.max_interests) continue;
      interests++;
    }
    if (row.atom.job && jobs[row.atom.job] && !jobs[row.atom.job].current) {
      if (!priorJobs.has(row.atom.job) && priorJobs.size >= limits.max_prior_roles) {
        continue;
      }
      priorJobs.add(row.atom.job);
    }
    selected.push(row);
    selectedIds.add(row.atom.id);
  }

  // Always ensure current mandate / org-scale if present
  for (const id of ['rbc-mandate', 'rbc-org-scale']) {
    if (!selected.find((s) => s.atom.id === id)) {
      const row = ranked.find((r) => r.atom.id === id);
      if (row) selected.unshift(row);
    }
  }

  // Stable-ish output: non-OSS first by score, but keep OSS grouped at end of selection list for pack readability
  selected.sort((a, b) => {
    const ao = a.atom.kind === 'oss' ? 1 : 0;
    const bo = b.atom.kind === 'oss' ? 1 : 0;
    if (ao !== bo) return ao - bo;
    return b.score - a.score;
  });

  const outDir = path.join(resumeRoot, 'out', slug);
  fs.mkdirSync(outDir, { recursive: true });

  const pack = {
    generated_at: new Date().toISOString(),
    slug,
    brief,
    profile,
    jobs,
    selected: selected.map(({ atom, score, hits, domainMustHits, specializedMustHits }) => ({
      id: atom.id,
      score,
      domainMustHits,
      specializedMustHits,
      hits,
      atom,
    })),
    oss_selected: ossSelected.map(({ atom, score, domainMustHits, specializedMustHits, hits }) => ({
      id: atom.id,
      score,
      domainMustHits,
      specializedMustHits,
      hits,
    })),
    ranked_preview: ranked.slice(0, 40).map(({ atom, score, domainMustHits, specializedMustHits }) => ({
      id: atom.id,
      kind: atom.kind,
      score,
      domainMustHits,
      specializedMustHits,
    })),
  };

  fs.writeFileSync(path.join(outDir, 'pack.json'), JSON.stringify(pack, null, 2));

  const md = [];
  md.push(`# Resume pack: ${slug}`);
  md.push('');
  md.push(`Generated: ${pack.generated_at}`);
  md.push('');
  md.push('## Target');
  md.push(`- Company: ${brief.target?.company || '(generic)'}`);
  md.push(`- Role: ${brief.target?.role}`);
  md.push(`- Tone: ${brief.constraints?.tone || profile.defaults?.tone}`);
  md.push('');
  md.push('## Selected experiences (use ONLY these)');
  md.push('');
  for (const { atom, score, hits } of selected) {
    md.push(`### ${atom.id} (score ${score})`);
    md.push(`- kind: ${atom.kind}`);
    if (atom.org) md.push(`- org: ${atom.org}`);
    if (atom.role) md.push(`- role: ${atom.role}`);
    if (atom.when) md.push(`- when: ${JSON.stringify(atom.when)}`);
    md.push(`- title: ${atom.title}`);
    md.push(`- summary: ${atom.summary?.trim()}`);
    md.push('- bullets:');
    for (const b of atom.bullets || []) md.push(`  - ${b}`);
    if (atom.proof?.metrics?.length) {
      md.push(`- metrics: ${JSON.stringify(atom.proof.metrics)}`);
    }
    if (atom.proof?.links?.length) {
      md.push(`- links: ${JSON.stringify(atom.proof.links)}`);
    }
    md.push(`- score hits: ${hits.join(', ') || '(none)'}`);
    md.push('');
  }
  md.push('## Employer cards');
  md.push('```json');
  md.push(JSON.stringify(jobs, null, 2));
  md.push('```');
  md.push('');
  md.push('## Profile');
  md.push('```json');
  md.push(JSON.stringify(profile, null, 2));
  md.push('```');

  fs.writeFileSync(path.join(outDir, 'pack.md'), md.join('\n'));
  fs.writeFileSync(path.join(outDir, 'brief.copy.yaml'), fs.readFileSync(briefPath));

  console.log(`Packed ${selected.length} atoms → ${path.relative(root, outDir)}`);
  console.log('OSS:', ossSelected.map((s) => s.atom.id).join(', ') || '(none)');
  console.log(selected.map((s) => `${s.score}\t${s.atom.kind}\t${s.atom.id}`).join('\n'));
}

main();
