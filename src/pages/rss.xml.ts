import rss from '@astrojs/rss';
import { getConfig } from '@lib/config';
import fs from 'node:fs';
import path from 'node:path';
import { calculateReadingTime } from '@lib/utils';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const config = getConfig();
  const blogDir = path.resolve(process.cwd(), 'src/content/blog');

  let posts: any[] = [];
  try {
    const files = fs.readdirSync(blogDir).filter(f => f.endsWith('.mdx') || f.endsWith('.md'));
    for (const file of files) {
      const raw = fs.readFileSync(path.join(blogDir, file), 'utf-8');
      const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
      if (!fmMatch) continue;
      const fm = fmMatch[1];
      const content = fmMatch[2];
      const title = fm.match(/title:\s*"(.+?)"/)?.[1] || '';
      const dateStr = fm.match(/date:\s*(.+)/)?.[1]?.trim() || '';
      const description = fm.match(/description:\s*"(.+?)"/)?.[1] || '';
      const draft = fm.includes('draft: true');
      const slug = file.replace(/\.(mdx?|md)$/, '');
      if (!draft) posts.push({ title, date: new Date(dateStr), description, slug });
    }
  } catch {}

  posts.sort((a, b) => b.date.getTime() - a.date.getTime());

  return rss({
    title: config.site.title,
    description: config.site.description,
    site: context.site || config.site.url,
    items: posts.map(post => ({
      title: post.title,
      pubDate: post.date,
      description: post.description,
      link: `/blog/${post.slug}/`,
    })),
  });
}
