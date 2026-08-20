import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import remarkGfm from 'remark-gfm';
import { contentLastmodByPath } from './src/lib/sitemap-lastmod.mjs';

const lastmodByPath = contentLastmodByPath();

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
      serialize(item) {
        const pathname = new URL(item.url).pathname;
        const lastmod = lastmodByPath.get(pathname);
        if (lastmod) item.lastmod = lastmod;

        if (pathname === '/') {
          item.changefreq = 'weekly';
          item.priority = 1.0;
        } else if (
          pathname === '/articles/' ||
          pathname === '/notes/' ||
          pathname === '/series/'
        ) {
          item.changefreq = 'weekly';
          item.priority = 0.8;
        } else if (
          pathname.startsWith('/articles/') ||
          pathname.startsWith('/notes/') ||
          pathname.startsWith('/series/')
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
  ],
  markdown: {
    remarkPlugins: [remarkGfm],
  },
});
