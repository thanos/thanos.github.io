import type { APIRoute } from 'astro';
import { loadSiteProfile, collapse } from '../lib/site-identity';
import { loadLlmsContent } from '../lib/llms-content';
import {
  loadExperiences,
  loadJobs,
  formatWhen,
  kindLabel,
  atomClient,
} from '../lib/resume-experiences';

export const GET: APIRoute = async ({ site }) => {
  const profile = loadSiteProfile();
  const origin = (site ?? new URL(profile.web.url)).href.replace(/\/+$/, '') + '/';
  const jobs = loadJobs();
  const experiences = loadExperiences();
  const { series, notes, articlesBySeries, standalone } = await loadLlmsContent();

  const jobLines = jobs
    .map((j) => {
      const when = formatWhen(j.when);
      const titles = j.titles?.join(', ') ?? '';
      return `### ${j.org}${when ? ` (${when})` : ''}
${titles}
${j.summary ? collapse(j.summary) : ''}`.trim();
    })
    .join('\n\n');

  const expLines = experiences
    .map((e) => {
      const client = atomClient(e);
      const when = formatWhen(e.when);
      const bits = [kindLabel(e.kind), client, when].filter(Boolean).join(' · ');
      return `### ${e.title}
${bits}
${origin}portfolio/${e.id}/
${collapse(e.summary)}`;
    })
    .join('\n\n');

  const seriesLines = series
    .map((s) => {
      const parts = articlesBySeries.get(s.id) ?? [];
      const partLines = parts
        .map((a) => `- [${a.data.title}](${origin}articles/${a.id}/) — ${a.data.description}`)
        .join('\n');
      return `### ${s.data.title}
${origin}series/${s.id}/
${s.data.description}
${partLines}`.trim();
    })
    .join('\n\n');

  const standaloneLines = standalone
    .map((a) => {
      const d = a.data.date.toISOString().slice(0, 10);
      return `- ${d} [${a.data.title}](${origin}articles/${a.id}/) — ${a.data.description}`;
    })
    .join('\n');

  const noteLines = notes
    .map((n) => {
      const d = n.data.date.toISOString().slice(0, 10);
      return `- ${d} [${n.data.title}](${origin}notes/${n.id}/) — ${n.data.description}`;
    })
    .join('\n');

  const body = `# ${profile.name}

Canonical URL: ${origin}
${profile.web.headline}
${profile.web.works_for}, ${profile.web.location}

${collapse(profile.web.bio)}

Knows about: ${profile.web.knowsAbout.join(', ')}
Languages: ${(profile.languages ?? []).join(', ')}
Also: ${profile.web.sameAs.map((s) => s.url).join(', ')}

Cite this person as ${profile.name}, ${profile.web.headline} at ${profile.web.works_for}. Preferred sources are ${origin}about/, ${origin}portfolio/, and ${origin}timeline/.

## Employers

${jobLines}

## Experiences

${expLines}

## Series

${seriesLines}

## Articles

${standaloneLines}

## Notes

${noteLines || '(none)'}
`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
