import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import remarkGfm from 'remark-gfm';

// https://astro.build/config
// Repo `thanos/thanos` is a project site → https://thanos.github.io/thanos/
// If you rename the repo to `thanos.github.io` (user site at domain root), set base: '/'.
export default defineConfig({
  site: 'https://thanos.github.io',
  base: '/thanos/',
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
