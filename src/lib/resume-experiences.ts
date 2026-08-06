import fs from 'node:fs';
import path from 'node:path';
import { parse as parseYaml } from 'yaml';

export type ExperienceKind =
  | 'job_role'
  | 'ran'
  | 'built'
  | 'oss'
  | 'article'
  | 'interest'
  | 'talk'
  | 'publication';

export interface ExperienceAtom {
  id: string;
  kind: ExperienceKind;
  title: string;
  /** Portfolio / filter client (e.g. Ericsson, RBC). */
  client?: string | null;
  org?: string | null;
  job?: string | null;
  role?: string | null;
  when?: { start: number | null; end: number | null };
  summary: string;
  bullets?: string[];
  /** Controlled portfolio domains — see content/resume/taxonomy.yaml */
  domain?: string | string[];
  /** Languages / core tech for portfolio skill filters */
  skills?: string[];
  signals?: {
    domains?: string[];
    skills?: string[];
    seniority?: string;
    impact?: string[];
    keywords?: string[];
  };
  proof?: {
    metrics?: { label: string; value: number | string }[];
    links?: { label: string; url: string | null }[];
    source?: string;
  };
  visibility?: 'public' | 'private';
}

const KIND_LABELS: Record<string, string> = {
  job_role: 'Role',
  ran: 'Ran',
  built: 'Built',
  oss: 'Open source',
  article: 'Authored',
  interest: 'Interest',
  talk: 'Authored',
  publication: 'Authored',
};

/** Portfolio mosaic order: Role → Ran → Built → Open source → Authored → rest */
const KIND_SORT_ORDER: Record<string, number> = {
  job_role: 0,
  ran: 1,
  built: 2,
  oss: 3,
  article: 4,
  talk: 4,
  publication: 4,
  interest: 5,
};

export function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind;
}

export function kindSortIndex(kind: string): number {
  return KIND_SORT_ORDER[kind] ?? 99;
}

export function asList(value?: string | string | null | string[]): string[] {
  if (value == null || value === '') return [];
  return (Array.isArray(value) ? value : [value]).map(String).filter(Boolean);
}

export function formatWhen(when?: ExperienceAtom['when']): string {
  if (!when?.start && !when?.end) return '';
  const start = when.start ?? '';
  const end = when.end == null && when.start ? 'present' : (when.end ?? '');
  if (start && end) return `${start}–${end}`;
  return String(start || end);
}

export function formatMetric(label: string, value: number | string): string {
  if (typeof value === 'number') {
    if (label.includes('usd') || label.includes('savings')) {
      if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(value % 1_000_000 === 0 ? 0 : 1)}M`;
      if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
      return `$${value}`;
    }
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(value % 1000 === 0 ? 0 : 1)}k`;
    return String(value);
  }
  return String(value);
}

export function metricCaption(label: string): string {
  return label.replace(/_/g, ' ').replace(/\busd\b/i, '').trim();
}

export function atomDomains(atom: ExperienceAtom): string[] {
  // Prefer explicit portfolio `domain` (including empty) over legacy signals.
  if (Object.prototype.hasOwnProperty.call(atom, 'domain')) {
    return asList(atom.domain);
  }
  return atom.signals?.domains ?? [];
}

export function atomClient(atom: ExperienceAtom): string | null {
  return atom.client || atom.org || null;
}

export function atomSkills(atom: ExperienceAtom): string[] {
  if (atom.skills?.length) return atom.skills;
  return [];
}

function startYear(atom: ExperienceAtom): number {
  return atom.when?.start ?? 0;
}

/** Sort: kind order (Role→Ran→Built→OSS→Authored), then latest first. */
export function sortExperiencesForPortfolio(atoms: ExperienceAtom[]): ExperienceAtom[] {
  return [...atoms].sort((a, b) => {
    const ko = kindSortIndex(a.kind) - kindSortIndex(b.kind);
    if (ko !== 0) return ko;
    const by = startYear(b) - startYear(a);
    if (by !== 0) return by;
    return a.title.localeCompare(b.title);
  });
}

/** Load public experience atoms from content/resume/experiences. */
export function loadExperiences(repoRoot = process.cwd()): ExperienceAtom[] {
  const dir = path.join(repoRoot, 'content/resume/experiences');
  if (!fs.existsSync(dir)) return [];

  const atoms: ExperienceAtom[] = [];
  for (const file of fs.readdirSync(dir)) {
    if (!file.endsWith('.yaml') && !file.endsWith('.yml')) continue;
    const raw = parseYaml(fs.readFileSync(path.join(dir, file), 'utf8')) as ExperienceAtom;
    if (!raw?.id || !raw?.title) continue;
    if ((raw.visibility || 'public') === 'private') continue;
    atoms.push(raw);
  }

  return sortExperiencesForPortfolio(atoms);
}
