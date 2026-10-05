# A/B Testing Platform

Level: 2 — Data Science

Skills: Python, conversion lift, a z cutoff

Compare control and treatment success counts. A |z| above 1.96 names a winner; otherwise none.

```bash
pip install -r requirements.txt
pytest -q
```

This is a local laptop proof. It does not call a hosted model and it does not apply production changes.

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
