import { readFileSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { parse } from 'yaml';

// Pages disabled in site.config.yml still build as noindex redirect stubs
// pointing at /404, so keep them (and /404 itself) out of the sitemap.
const { pages } = parse(readFileSync('./site.config.yml', 'utf-8'));
const excluded = new Set(
  Object.entries(pages)
    .filter(([, enabled]) => !enabled)
    .map(([name]) => name)
    .concat('404')
);

export default defineConfig({
  site: 'https://yy-gx.github.io',
  integrations: [
    mdx(),
    sitemap({
      filter: (page) => !excluded.has(new URL(page).pathname.split('/')[1]),
    }),
  ],
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
  },
  markdown: {
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
    },
  },
});
