import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Explicit content collection definitions (Astro 5 Content Layer).
 *
 * Declaring this file opts the site out of Astro's deprecated implicit
 * `src/content/*` collection detection, which is slated for removal in the
 * next Astro major. It also silences the `[glob-loader] No files found`
 * warnings the implicit behaviour emitted for `src/content/books`, `/cv`,
 * `/teaching` and `/publications` — none of those hold Markdown, so no
 * collection is declared for them here.
 *
 * IMPORTANT: nothing in this project imports `astro:content`. Every page reads
 * its content straight off disk with `node:fs` (see src/pages/**,
 * src/components/home/**, src/lib/bibtex.ts), including the blog `draft: true`
 * filtering in src/pages/blog/index.astro and src/pages/blog/[slug].astro.
 * These declarations therefore only register which directories are
 * collections; they do not feed any rendered page.
 *
 * No `schema` is attached on purpose. A zod schema here would validate data
 * that no page consumes while duplicating the interfaces in src/lib/types.ts,
 * and Astro emits a `collections/<name>.schema.json` artifact per schema into
 * the build output, changing the published file set for no benefit. Add a
 * schema at the same time as the first real `getCollection()` consumer.
 *
 * Deliberately NOT declared:
 *   - src/content/*.yml (books, collaborators, media, positions, repositories,
 *     talks, team, travel) plus cv/cv.yml and teaching/courses.yml — parsed
 *     directly by the pages that render them; src/lib/types.ts holds their
 *     shapes.
 *   - src/content/publications/papers.bib — parsed by src/lib/bibtex.ts, not a
 *     content collection.
 *   - src/content/about.md — a single loose file, read by home/Hero.astro.
 *   - src/content/books/ — empty; books.astro reads src/content/books.yml.
 */

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
});

const news = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/news' }),
});

const projects = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/projects' }),
});

export const collections = { blog, news, projects };
