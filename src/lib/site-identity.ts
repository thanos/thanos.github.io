import fs from 'node:fs';
import path from 'node:path';
import { parse as parseYaml } from 'yaml';

export interface SameAsLink {
  label: string;
  url: string;
}

export interface SiteProfile {
  name: string;
  email: string;
  phone?: string;
  github?: string;
  nationality?: string[];
  spoken_languages?: string[];
  default_titles: string[];
  languages?: string[];
  web: {
    url: string;
    tagline: string;
    headline: string;
    works_for: string;
    location: string;
    image: string;
    bio: string;
    sameAs: SameAsLink[];
    knowsAbout: string[];
  };
}

const SITE_ORIGIN = 'https://thanos.github.io';

let cached: SiteProfile | null = null;

export function loadSiteProfile(repoRoot = process.cwd()): SiteProfile {
  if (cached) return cached;
  const raw = parseYaml(
    fs.readFileSync(path.join(repoRoot, 'content/resume/profile.yaml'), 'utf8')
  ) as SiteProfile;
  cached = raw;
  return raw;
}

export function personId(site = SITE_ORIGIN): string {
  return `${stripSlash(site)}/#person`;
}

export function websiteId(site = SITE_ORIGIN): string {
  return `${stripSlash(site)}/#website`;
}

export function absoluteUrl(pathOrUrl: string, site = SITE_ORIGIN): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  return new URL(pathOrUrl.replace(/^\//, ''), `${stripSlash(site)}/`).href;
}

export function withSiteBase(pathOrUrl: string, base: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  const prefix = base.endsWith('/') ? base : `${base}/`;
  return `${prefix}${pathOrUrl.replace(/^\//, '')}`;
}

export function pageTitle(title: string, name: string): string {
  if (title === name || title.includes(name)) return title;
  return `${title} · ${name}`;
}

export function personJsonLd(site = SITE_ORIGIN) {
  const profile = loadSiteProfile();
  const { web } = profile;
  return {
    '@type': 'Person',
    '@id': personId(site),
    name: profile.name,
    url: stripSlash(site) + '/',
    image: absoluteUrl(web.image, site),
    email: `mailto:${profile.email}`,
    jobTitle: web.headline,
    worksFor: {
      '@type': 'Organization',
      name: web.works_for,
    },
    homeLocation: {
      '@type': 'Place',
      name: web.location,
    },
    nationality: profile.nationality,
    knowsLanguage: profile.spoken_languages,
    knowsAbout: web.knowsAbout,
    sameAs: web.sameAs.map((s) => s.url),
    description: collapse(web.bio),
  };
}

export function websiteJsonLd(site = SITE_ORIGIN) {
  const profile = loadSiteProfile();
  return {
    '@type': 'WebSite',
    '@id': websiteId(site),
    name: profile.name,
    url: stripSlash(site) + '/',
    description: collapse(profile.web.bio),
    inLanguage: 'en',
    publisher: { '@id': personId(site) },
    author: { '@id': personId(site) },
  };
}

export function graphJsonLd(pageNodes: unknown[], site = SITE_ORIGIN) {
  const extras = pageNodes.flatMap((node) => flattenJsonLd(node));
  return {
    '@context': 'https://schema.org',
    '@graph': [personJsonLd(site), websiteJsonLd(site), ...extras],
  };
}

export function flattenJsonLd(node: unknown): unknown[] {
  if (node == null) return [];
  if (Array.isArray(node)) return node.flatMap(flattenJsonLd);
  if (typeof node === 'object' && node !== null && '@graph' in node) {
    return flattenJsonLd((node as { '@graph': unknown })['@graph']);
  }
  if (typeof node === 'object' && node !== null && '@context' in node) {
    const { '@context': _c, ...rest } = node as Record<string, unknown>;
    return [rest];
  }
  return [node];
}

export function escapeXml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function collapse(text: string): string {
  return text.replace(/\s+/g, ' ').trim();
}

function stripSlash(url: string): string {
  return url.replace(/\/+$/, '');
}
