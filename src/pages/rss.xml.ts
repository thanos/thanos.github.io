import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { loadSiteProfile, escapeXml, collapse } from '../lib/site-identity';

export const GET: APIRoute = async ({ site }) => {
  const profile = loadSiteProfile();
  const origin = site ?? new URL(profile.web.url);
  const articles = (
    await getCollection('articles', ({ data }) => (import.meta.env.PROD ? !data.draft : true))
  ).sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  const items = articles
    .map((post) => {
      const url = new URL(`articles/${post.id}/`, origin).href;
      return `    <item>
      <title>${escapeXml(post.data.title)}</title>
      <link>${escapeXml(url)}</link>
      <guid isPermaLink="true">${escapeXml(url)}</guid>
      <pubDate>${post.data.date.toUTCString()}</pubDate>
      <description>${escapeXml(post.data.description)}</description>
      <author>${escapeXml(profile.email)} (${escapeXml(profile.name)})</author>
    </item>`;
    })
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(profile.name)}</title>
    <link>${escapeXml(new URL('/', origin).href)}</link>
    <description>${escapeXml(collapse(profile.web.bio))}</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
