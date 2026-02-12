import fs from 'node:fs';
import path from 'node:path';
import yaml from 'yaml';

export interface SiteConfig {
  site: { title: string; description: string; url: string; language: string };
  profile: { name: string; position: string; affiliation: string; university: string; email: string; avatar: string; bio: string; bio_short: string };
  social: Record<string, string>;
  pages: Record<string, boolean>;
  theme: { cursor_spotlight: boolean; style: string; palette: string; random_theme: boolean; avatars: string[]; };
  cv?: { hide_pdf_download?: boolean };
  publications: { author_name: string; bibtex_file: string; group_by_year: boolean; show_badges: boolean };
  blog: { posts_per_page: number; show_reading_time: boolean; show_table_of_contents: boolean; comments: { enabled: boolean; repo: string; repo_id: string; category: string; category_id: string } };
}

let _config: SiteConfig | null = null;

export function getConfig(): SiteConfig {
  if (_config) return _config;
  const configPath = path.resolve(process.cwd(), 'site.config.yml');
  const configFile = fs.readFileSync(configPath, 'utf-8');
  _config = yaml.parse(configFile) as SiteConfig;
  return _config;
}

export function getEnabledPages(): { name: string; path: string; label: string }[] {
  const config = getConfig();
  const pageMap: Record<string, { path: string; label: string }> = {
    about: { path: '/', label: 'About' },
    publications: { path: '/publications', label: 'Publications' },
    cv: { path: '/cv', label: 'CV' },
    projects: { path: '/projects', label: 'Projects' },
    news: { path: '/news', label: 'News' },
    teaching: { path: '/teaching', label: 'Teaching' },
    talks: { path: '/talks', label: 'Talks' },
    awards: { path: '/awards', label: 'Awards' },
    team: { path: '/team', label: 'Team' },
    positions: { path: '/positions', label: 'Positions' },
    collaborators: { path: '/collaborators', label: 'Collaborators' },
    service: { path: '/service', label: 'Service' },
    repositories: { path: '/repositories', label: 'Repos' },
    blog: { path: '/blog', label: 'Blog' },
    gallery: { path: '/gallery', label: 'Gallery' },
    books: { path: '/books', label: 'Books' },
    media: { path: '/media', label: 'Media' },
    travel: { path: '/travel', label: 'Travel' },
  };
  return Object.entries(config.pages)
    .filter(([_, enabled]) => enabled)
    .map(([name]) => ({ name, ...pageMap[name] }))
    .filter(page => page.path);
}
