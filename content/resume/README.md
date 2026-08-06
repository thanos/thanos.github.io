# Resume experience corpus

Committed: `profile.yaml`, `jobs/`, `experiences/`, plus `scripts/resume/` and `.cursor/skills/resume-flavor/`.

Local only (**gitignored**): `briefs/`, `out/`, `.env`.

## Pipeline

| Step | Command | Who writes prose |
|------|---------|------------------|
| 1. Brief | edit `briefs/<slug>.yaml` | you |
| 2. Pack | `npm run resume:pack -- --brief <slug>` | nobody (deterministic scores) |
| 3. Generate | `npm run resume:generate -- --brief <slug>` | **LLM API** (`.env` model) |

One shot:

```bash
cp .env.example .env   # set OPENAI_API_KEY or ANTHROPIC_API_KEY
npm run resume:flavor -- --brief principal-md-dev-manager
```

Outputs land in `content/resume/out/<slug>/`:

- `pack.json` / `pack.md` — selected atoms
- `cover.md`, `resume.md`, `provenance.md` — model-written
- `generation.json` — provider + model id used

### Model config

See `.env.example`:

- `RESUME_LLM_PROVIDER=openai|anthropic`
- `RESUME_LLM_MODEL=...` (optional override)
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` (OpenAI-compatible)
- `ANTHROPIC_API_KEY`

Changing the **Cursor chat model** does not change pack or `resume:generate`. Only `RESUME_LLM_*` / API keys do.
