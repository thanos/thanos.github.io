# Resume experience corpus

Committed: `profile.yaml`, `jobs/`, `experiences/`, `taxonomy.yaml`, plus `scripts/resume/` and `.cursor/skills/resume-flavor/`.

Local only (**gitignored**): `briefs/`, `out/`, `.env`.

## Experience atom fields (portfolio filters)

```yaml
domain: [telecom]          # controlled list — see taxonomy.yaml
client: Ericsson           # who the work was for (null for personal OSS)
skills: [Erlang, C]        # languages / core tech shown in skill filters
```

Portfolio page filters: **Domain · Client · Skills** only.

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
