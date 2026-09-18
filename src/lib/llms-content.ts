import { getCollection, type CollectionEntry } from 'astro:content';

type Article = CollectionEntry<'articles'>;
type Series = CollectionEntry<'series'>;
type Note = CollectionEntry<'notes'>;

function published<C extends 'articles' | 'series' | 'notes'>(name: C) {
  return getCollection(name, ({ data }) => (import.meta.env.PROD ? !data.draft : true));
}

function byDateDesc<T extends { data: { date: Date }; id: string }>(a: T, b: T) {
  const delta = b.data.date.valueOf() - a.data.date.valueOf();
  return delta !== 0 ? delta : a.id.localeCompare(b.id);
}

function byDateAsc<T extends { data: { date: Date }; id: string }>(a: T, b: T) {
  const delta = a.data.date.valueOf() - b.data.date.valueOf();
  return delta !== 0 ? delta : a.id.localeCompare(b.id);
}

export async function loadLlmsContent() {
  const [articles, series, notes] = await Promise.all([
    published('articles'),
    published('series'),
    published('notes'),
  ]);

  articles.sort(byDateDesc);
  series.sort(byDateDesc);
  notes.sort(byDateDesc);

  const seriesIds = new Set(series.map((s) => s.id));
  const articlesBySeries = new Map<string, Article[]>();
  const standalone: Article[] = [];

  for (const article of articles) {
    const seriesId = article.data.series;
    if (seriesId && seriesIds.has(seriesId)) {
      const list = articlesBySeries.get(seriesId) ?? [];
      list.push(article);
      articlesBySeries.set(seriesId, list);
    } else {
      standalone.push(article);
    }
  }

  for (const list of articlesBySeries.values()) {
    list.sort(byDateAsc);
  }

  return { articles, series, notes, articlesBySeries, standalone };
}

export type { Article, Series, Note };
