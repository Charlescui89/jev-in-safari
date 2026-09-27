# Contributing

This project is preparing an experimental alpha. The most useful early contributions are
installation reports, reproducible Safari issues, and small adapter fixes with regression tests.
Read [VALIDATION.md](VALIDATION.md) for the current verification boundary.

## Report a result

Use the repository's bug or alpha tester issue template. Include macOS, Safari, Python, commit,
the command, and sanitized output. A successful browser-only smoke test is useful feedback too.
Use synthetic pages when possible. Never attach credentials, `.env`, cookies, or private page content.

## Development

Fork and clone the repository, then run `uv sync --locked`.

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
node --check src/jev_safari/snapshot.js
uv build
```

CI runs these offline checks on Python 3.12 and 3.14 on Linux, and Python 3.14 on macOS.
It does not start Safari or call paid model APIs.
For adapter changes, run `doctor`, `smoke`, and `scripts/check_guards.py` locally on macOS.
Run `smoke --live` only with your own configured service access; model calls may incur charges.
Record unavailable checks honestly in the pull request.

Keep changes focused. Describe the failing behavior, the fix, and the validation performed.
Preserve upstream attribution and the existing MIT license. See [UPSTREAM.md](UPSTREAM.md).

## Adapter rules

- Act only on elements and operations from the current observation.
- Reject stale or unusable targets before input.
- Stop if input may have occurred; never automatically retry a mutation.
- Verify actual page state; the model reporting DONE is insufficient.
- Keep credentials and provider request headers out of logs.
