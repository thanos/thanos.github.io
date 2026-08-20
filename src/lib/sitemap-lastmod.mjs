import fs from 'node:fs';
import path from 'node:path';

/**
 * Map published content URLs (pathname with trailing slash) to ISO lastmod
 * from frontmatter `date`. Used by `@astrojs/sitemap` serialize().
 */
export function contentLastmodByPath(root = process.cwd()) {
  const map = new Map();

  const collections = [
    { dir: path.join(root, 'content/articles'), prefix: '/articles/' },
    { dir: path.join(root, 'content/notes'), prefix: '/notes/' },
    { dir: path.join(root, 'content/series'), prefix: '/series/' },
  ];

  for (const { dir, prefix } of collections) {
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      if (!name.endsWith('.md') || name === 'README.md') continue;
      const text = fs.readFileSync(path.join(dir, name), 'utf8');
      const draft = /^draft:\s*true\s*$/m.test(text);
      const dateMatch = text.match(/^date:\s*(.+)$/m);
      if (draft || !dateMatch) continue;
      const lastmod = new Date(dateMatch[1].trim());
      if (Number.isNaN(lastmod.valueOf())) continue;
      const id = name.replace(/\.md$/i, '').toLowerCase();
      map.set(`${prefix}${id}/`, lastmod.toISOString());
    }
  }

  return map;
}
