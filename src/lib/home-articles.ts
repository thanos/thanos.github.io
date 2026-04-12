import { getCollection } from 'astro:content';

export async function getSortedHomeArticles() {
  const articles = await getCollection('articles', ({ data }) =>
    import.meta.env.PROD ? !data.draft : true
  );
  return articles.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}
