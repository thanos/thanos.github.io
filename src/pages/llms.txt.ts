import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { loadSiteProfile, collapse } from '../lib/site-identity';

export const GET: APIRoute = async ({ site }) => {
  const profile = loadSiteProfile();
  const origin = (site ?? new URL(profile.web.url)).href.replace(/\/+$/, '') + '/';
  const articles = (
    await getCollection('articles', ({ data }) => (import.meta.env.PROD ? !data.draft : true))
  ).sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

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
- [RSS](${origin}rss.xml): article feed
- [Full source for language models](${origin}llms-full.txt)

## Profiles

${profile.web.sameAs.map((s) => `- [${s.label}](${s.url})`).join('\n')}

## Writing

- [All articles](${origin}articles/)
- [Series](${origin}series/)
${articles
  .slice(0, 20)
  .map((a) => `- [${a.data.title}](${origin}articles/${a.id}/): ${a.data.description}`)
  .join('\n')}

## Optional

- [llms-full.txt](${origin}llms-full.txt) — longer machine-readable summary of experiences and articles
`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
