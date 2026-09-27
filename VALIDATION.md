# Validation — 28 September 2026

## Completed

- Created a separate Git project on branch `main`.
- Installed the project in its own Python 3.14 virtual environment using the checked-in `uv.lock`.
- `python -m pytest -q`: **30 passed**. Includes reused Jev policy tests and new Safari adapter contracts.
- `ruff check .`: passed.
- `node --check src/jev_safari/snapshot.js`: passed.
- Built source and wheel distributions for `jev-safari 0.1.0`.
- Verified the wheel contains the DOM snapshot and CLI, without dotenv credentials or Browser Harness.
- Confirmed installed Safari WebDriver version: Safari 26.6.2 (21624.5.1.11.3).

## Live Safari tests pending

Initial session creation returned `session not created` because Safari remote automation was disabled.
Safari required local macOS authentication to change the setting. Live verification remains pending
completion of that authentication and the browser checks below.

After local authentication, run:

```sh
.venv/bin/jev-safari doctor
.venv/bin/jev-safari smoke
.venv/bin/python scripts/check_guards.py
.venv/bin/jev-safari --env-file '/absolute/path/to/credentials.env' smoke --live
```

Offline success does not confirm native Safari input, model-driven Safari operation, or Safari performance.
The earlier successful Chrome test is not a Safari result.

## Preserved

The installed Jev Ultrafast Chrome project, its API credentials, and its browser connection were not modified.
The new CLI reads the existing credential file only when explicitly supplied with `--env-file`.
