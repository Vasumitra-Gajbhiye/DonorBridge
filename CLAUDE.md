ASK QUESTIONS IF REQUIRED BEFORE CODING
Do not write "co-author: claude" in any commits
Do not write "generated with claude code" or anything like that in PRs or anywhere
This is a uv project (Python 3.11). Run everything with `uv run` (e.g. `uv run pytest`, `uv run python -m donorbridge`). Never `pip install` into the project; dependencies change only via `uv add`, then re-export requirements.txt (see team/01_lead.md, L1.0).
