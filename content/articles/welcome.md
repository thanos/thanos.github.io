---
title: "Welcome to the site"
description: "A short example article demonstrating the articles collection and front matter."
date: 2026-04-01
tags:
  - meta
  - astro
draft: true
---

![Abstract header image (sourced from your Pictures/t.webp; copy lives beside this .md for the content pipeline)](./welcome-hero.webp)

This is an example **article** stored under `content/articles/`. It uses the shared schema: title, description, date, tags, and draft. The hero above is `welcome-hero.webp` next to this file (same trick Astro uses for portable posts).[^source]

Use Markdown for long-form technical writing. Code blocks are styled at build time via Shiki (Astro default):

```elixir
defmodule Example do
  def hello, do: :ok
end
```

### Example table

| Artifact | Role |
| -------- | ---- |
| `content/articles/*.md` | Long-form posts |
| `src/content.config.ts` | Zod + collection loaders |
| `public/` | Static assets (images, `robots.txt`, …) |

When you add real posts, keep filenames URL-friendly; the file stem becomes the entry id unless you set a custom `slug` in front matter.

[^source]: A copy of `~/Pictures/t.webp` lives beside this Markdown so the build resolves it; `public/images/` keeps another copy if you want non-post static URLs.
