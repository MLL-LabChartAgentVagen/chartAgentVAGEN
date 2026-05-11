---
name: pytest-conda-env
description: Always run pytest in conda environment "chart" — user rejected bare pytest invocation
type: feedback
---

Always run pytest (and python commands for this project) using `conda run -n chart python -m pytest ...`.

**Why:** User explicitly rejected a bare `python -m pytest` invocation and instructed to always use the "chart" conda environment.

**How to apply:** Prefix all pytest and python commands with `conda run -n chart`.
