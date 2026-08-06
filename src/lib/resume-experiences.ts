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
  org?: string | null;
  job?: string | null;
  role?: string | null;
  when?: { start: number | null; end: number | null };
  summary: string;
  bullets?: string[];
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
  article: 'Writing',
  interest: 'Interest',
  talk: 'Talk',
  publication: 'Publication',
};

export function kindLabel(kind: string): string {
  return KIND_LABELS[kind] ?? kind;
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

  return atoms.sort((a, b) => {
    const ay = a.when?.start ?? 0;
    const by = b.when?.start ?? 0;
    if (by !== ay) return by - ay;
    return a.title.localeCompare(b.title);
  });
}
