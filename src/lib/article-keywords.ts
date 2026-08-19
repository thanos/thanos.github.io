const TOP_KEYWORD_COUNT = 20;

export type ArticleKeyword = {
  key: string;
  label: string;
  count: number;
};

type Tagged = { data: { tags?: string[] } };

export function normalizeKeyword(tag: string): string {
  return tag.trim().toLowerCase();
}

/** Most-used article tags, capped at 20. Ties break alphabetically. */
export function topArticleKeywords(
  articles: Tagged[],
  limit = TOP_KEYWORD_COUNT
): ArticleKeyword[] {
  const counts = new Map<string, { label: string; count: number }>();

  for (const article of articles) {
    for (const tag of article.data.tags ?? []) {
      const key = normalizeKeyword(tag);
      if (!key) continue;
      const existing = counts.get(key);
      if (existing) {
        existing.count += 1;
      } else {
        counts.set(key, { label: tag.trim(), count: 1 });
      }
    }
  }

  return [...counts.values()]
    .map((entry) => ({
      key: normalizeKeyword(entry.label),
      label: entry.label,
      count: entry.count,
    }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, undefined, { sensitivity: 'base' }))
    .slice(0, limit);
}

export function articleKeywordKeys(tags: string[] | undefined): string[] {
  return [...new Set((tags ?? []).map(normalizeKeyword).filter(Boolean))];
}
