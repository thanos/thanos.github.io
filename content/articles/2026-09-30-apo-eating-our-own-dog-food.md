---
title: "Eating My Own Dog Food"
description: "What happened when I ran APO against APO: the first scores, the gaps I closed without inventing evidence, and the two findings I left Partial on purpose."
date: 2026-09-30
tags:
  - APO
  - Rust
  - engineering-evidence
  - CI
  - open-source
draft: false
authors:
  - Thanos Vassilakis
---

I built [APO](https://github.com/thanos/apo) to turn repository practice into evidence — and to say, without hand-waving, what is missing. I wrote the crate myself.

You point `apo` at a Git repository. It inventories what is already on disk and in sampled Git and CI text:

- **Hygiene controls** — docs, editor and setup, tests and coverage gates, dependency and secret-scanning signals, CI and release automation, CODEOWNERS, templates, commit conventions.
- **Knowledge artifacts** — README, ADRs, architecture and design notes, runbooks, API docs, glossaries, diagrams, onboarding, prompt libraries.
- **AI adoption signals** — prompts, agents, MCP configs, AI governance, hints that people actually use assistants in the workflow.

Then it turns that inventory into findings, scores, badges, and optional remediation prompts. It does not invent controls. It does not run your formatters, linters, or tests to decide a score.

The only test of that I trust is whether I would use the same reports on my own tree.

So I did.

## First look in the mirror

Every push and pull request to main already runs the usual Rust gates: rustfmt, clippy with warnings as errors, rustdoc with warnings as errors, tests on Linux, macOS, and Windows, line coverage that must stay at or above 80%, `cargo deny`, `cargo audit`, and gitleaks. After those pass, a job named **APO self-analysis** builds the release binary and runs it against the same checkout.

That last job is the dogfood. It calls `apo report` on `.`, writes markdown and JSON (and SARIF) into a self-analysis directory, and emits two SVG badges — hygiene and evidence. Those badges sit next to the docs and in the [README](https://github.com/thanos/apo/blob/main/README.md), so the scores show up next to CI and crates.io without an external badge CDN. Before I push, I run the same sequence locally: format, lint, docs, test, coverage, audits, then `apo report` on this repo.

On the first deliberate pass, the numbers were blunt:

| Metric | Score |
|--------|------:|
| Hygiene | 58.7 |
| Knowledge maturity | 43.8 |
| AI maturity | 0.0 |

Sixteen hygiene gaps. No ADRs. No architecture notes. No runbooks. No CODEOWNERS. No issue or pull-request templates. No secret scanning. No editor defaults. No setup automation. Knowledge kinds were empty for almost everything past a README. AI maturity was zero: no agents file, no governance, no versioned prompts.

That was the point of the tool. APO did not scold. It listed paths and remediations. With `--llm-prompt` it also wrote paste-ready prompts so an assistant could close gaps from the report, not from vibes.

## Closing gaps without inventing evidence

The rule I held myself to is the same one the tool asks of anyone using it: **do not invent controls**. Every artifact had to match how this repo actually works.

I wrote architecture and [design notes](https://github.com/thanos/apo/blob/main/docs/design.md) that describe the real pipeline: rules return statuses, a policy layer turns those into scores, language packs look at manifests and CI text instead of executing toolchains. I recorded the [single-crate, observational-packs decision](https://github.com/thanos/apo/blob/main/docs/adr/0001-single-crate-observational-evidence.md) as an ADR. I added a [release runbook](https://github.com/thanos/apo/blob/main/docs/runbooks/release.md) that tracks the publish flow I already had, plus a glossary and API notes.

I also added CODEOWNERS, pull-request and issue templates, and a checked-in GitHub settings file that *describes* branch protection and required checks (Format, Docs, Secret scanning, Clippy, and the rest). EditorConfig, pre-commit hooks, gitleaks in CI, and a Conventional Commits config. A Makefile and a setup script so onboarding is more than a paragraph: install rustfmt, clippy, and llvm-tools, optionally hook pre-commit, then run the same local checks CI runs.

For assistants I added `AGENTS.md`, an [AI governance](https://github.com/thanos/apo/blob/main/docs/ai-governance.md) note that forbids fabricating evidence, and a small versioned `prompts/` library for the remediation loop itself. The Rust language pack gained a needle that looks for `cargo doc` in CI and scripts, so documentation tooling scores when rustdoc is actually gated — which it is, both in GitHub Actions and in the local check script.

Then I ran the binary again.

## Second look

| Metric | Before | After |
|--------|-------:|------:|
| Hygiene | 58.7 | **84.8** |
| Knowledge maturity | 43.8 | **100** |
| AI maturity | 0.0 | **95.0** |

Two hygiene findings stayed intentionally imperfect.

Conventional Commits is still **Partial** because history is what it is. A config file does not rewrite old messages.

Branch protection is still **Partial** because a checked-in settings file is a signal that I *intend* required reviews and required checks on main. It is not proof that GitHub is enforcing them. APO cannot see the forge API from a local clone, and it refuses to pretend otherwise. That refusal is a feature. The ADR says the same thing: scores can lag true CI enforcement when policy lives only on the platform.

## What I learned

Reports beat checklists. The gap list was more useful than a generic “improve docs” aspiration. Remediations pointed at concrete files.

Prompts are accelerators, not oracles. The LLM prompts helped apply changes quickly. The scores only moved when the filesystem changed.

Dogfooding keeps the product honest. Living with `Unknown` and `Partial` where a local clone cannot see the platform stopped me from gaming the rubric.

Badges close the loop. The SVGs refresh when self-analysis runs and sit in the README next to the other shields. No extra service.

If you want the same loop on your repository, the split commands are:

```bash
apo analyze . --llm-prompt --badge-output docs/badges/apo-hygiene.svg
apo evidence . --llm-prompt --badge-output docs/badges/apo-evidence.svg
# apply remediations from the *-prompt.md files
# re-run until the badges tell the story you intend
```

`apo report` is the combined form CI uses: one pack, both badges, optional SARIF.

CI still runs that report on every push. The README badges are just the last scores — nothing I would not put in the report itself.
