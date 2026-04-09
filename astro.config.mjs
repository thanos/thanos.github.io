import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import remarkGfm from 'remark-gfm';

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
  ],
  markdown: {
    remarkPlugins: [remarkGfm],
  },
});
