import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import remarkGfm from 'remark-gfm';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { contentLastmodByPath } from './src/lib/sitemap-lastmod.mjs';

const lastmodByPath = contentLastmodByPath();

/** Copy sitemap-index.xml → sitemap.xml so the conventional URL works in Search Console. */
function sitemapXmlAlias() {
  return {
    name: 'sitemap-xml-alias',
    hooks: {
      'astro:build:done': ({ dir }) => {
        const out = fileURLToPath(dir);
        const src = path.join(out, 'sitemap-index.xml');
        const dest = path.join(out, 'sitemap.xml');
        if (fs.existsSync(src)) fs.copyFileSync(src, dest);
      },
    },
  };
}

function dateOnly(iso) {
  return String(iso).slice(0, 10);
}

// https://astro.build/config
// User site (`thanos.github.io` repo): https://thanos.github.io/
// If you only have `thanos/thanos`, GitHub serves at /thanos/ — use base: '/thanos/'.
export default defineConfig({
  site: 'https://thanos.github.io',
  base: '/',
  output: 'static',
  trailingSlash: 'always',
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap({
      // Paginated home listings duplicate `/`; keep canonical URLs only.
      filter: (page) => !/\/page\/\d+\/?$/.test(new URL(page).pathname),
      customPages: [
        'https://thanos.github.io/rss.xml',
        'https://thanos.github.io/llms.txt',
        'https://thanos.github.io/llms-full.txt',
      ],
      serialize(item) {
        const pathname = new URL(item.url).pathname;
        const lastmod = lastmodByPath.get(pathname);
        if (lastmod) item.lastmod = dateOnly(lastmod);

        if (pathname === '/') {
          item.changefreq = 'weekly';
          item.priority = 1.0;
        } else if (
          pathname === '/about/' ||
          pathname === '/articles/' ||
          pathname === '/notes/' ||
          pathname === '/series/' ||
          pathname === '/portfolio/' ||
          pathname === '/timeline/' ||
          pathname === '/llms.txt' ||
          pathname === '/llms-full.txt'
        ) {
          item.changefreq = 'weekly';
          item.priority = 0.8;
        } else if (
          pathname.startsWith('/articles/') ||
          pathname.startsWith('/notes/') ||
          pathname.startsWith('/series/') ||
          pathname.startsWith('/portfolio/')
        ) {
          item.changefreq = 'monthly';
          item.priority = 0.7;
        } else {
          item.changefreq = 'monthly';
          item.priority = 0.5;
        }

        return item;
      },
    }),
    sitemapXmlAlias(),
  ],
  markdown: {
    remarkPlugins: [remarkGfm],
  },
});
