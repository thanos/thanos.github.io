import type { APIRoute } from 'astro';
import { loadSiteProfile, collapse } from '../lib/site-identity';
import { loadLlmsContent } from '../lib/llms-content';

export const GET: APIRoute = async ({ site }) => {
  const profile = loadSiteProfile();
  const origin = (site ?? new URL(profile.web.url)).href.replace(/\/+$/, '') + '/';
  const { articles, series } = await loadLlmsContent();

  const body = `# ${profile.name}

> ${collapse(profile.web.bio)}

- Canonical site: ${origin}
- ${profile.web.headline}
- ${profile.web.works_for}, ${profile.web.location}

## Identity

- [About](${origin}about/): who I am and how to cite this site
- [Résumé](${origin}resume/): full curriculum vitae
- [Portfolio](${origin}portfolio/): roles, systems, open source, and writing
- [Timeline](${origin}timeline/): chronological career view
- [Notes](${origin}notes/): short notes
- [RSS](${origin}rss.xml): article feed
- [Full source for language models](${origin}llms-full.txt)

## Profiles

${profile.web.sameAs.map((s) => `- [${s.label}](${s.url})`).join('\n')}

## Series

- [All series](${origin}series/)
${series
  .map((s) => `- [${s.data.title}](${origin}series/${s.id}/): ${s.data.description}`)
  .join('\n')}

## Writing

- [All articles](${origin}articles/)
${articles
  .map((a) => `- [${a.data.title}](${origin}articles/${a.id}/): ${a.data.description}`)
  .join('\n')}

## Optional

- [llms-full.txt](${origin}llms-full.txt) — longer machine-readable summary of experiences, series, and articles
`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
