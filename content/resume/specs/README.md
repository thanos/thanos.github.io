# Job specs (local)

Drop one folder per role. These files stay gitignored (recruiter email, compensation).

```
content/resume/specs/<slug>/spec.md    # required
content/resume/specs/<slug>/notes.md   # optional
```

Then: *flavor the spec in content/resume/specs/&lt;slug&gt;*

The agent follows `.cursor/skills/resume-flavor/SKILL.md`. Output lands in `content/resume/out/<slug>/` (also gitignored).
