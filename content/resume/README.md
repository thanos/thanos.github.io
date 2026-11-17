# Resume experience corpus

Committed: `profile.yaml`, `jobs/`, `experiences/`, `taxonomy.yaml`, `work-timeline.yaml` (static employment titles/dates), plus `scripts/resume/` and `.cursor/skills/resume-flavor/`.

Employment titles and dates on flavored résumés come only from `work-timeline.yaml` — do not invent or go earlier than NYSE/SIAC.

Local only (**gitignored**): `briefs/`, `out/`, `specs/<slug>/`, `.env`.

Job specs: drop a posting in `content/resume/specs/<slug>/spec.md` and ask the agent to flavor it (see `.cursor/skills/resume-flavor/`).

## Experience atom fields (portfolio filters)

```yaml
domain: [telecom]          # controlled list — see taxonomy.yaml
client: Ericsson           # who the work was for (null for personal OSS)
skills: [Erlang, C]        # languages / core tech shown in skill filters
responsible:               # optional, multi-valued — see taxonomy.yaml
  - built                  # you implemented / delivered
  - run                    # you operated / owned the running service or org
  - architected            # you set the design / architecture
```

`kind:` remains the atom type (`built` | `ran` | `oss` | `job_role` | …).  
`responsible:` is who-did-what on that work and may list several values.

Portfolio page filters: **Domain · Client · Skills** only (not yet `responsible`).

## Pipeline

| Step | Command | Who writes prose |
|------|---------|------------------|
| 1. Brief | edit `briefs/<slug>.yaml` | you |
| 2. Pack | `npm run resume:pack -- --brief <slug>` | nobody (deterministic scores) |
| 3. Generate | `npm run resume:generate -- --brief <slug>` | **LLM API** (`.env` model) |

```bash
cp .env.example .env
npm run resume:flavor -- --brief principal-md-dev-manager
```
