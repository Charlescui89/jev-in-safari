# JEV in Safari

A custom Safari adapter for Jev Ultrafast. Jev chooses an operation and observed target;
the configured text model writes field values; Safari WebDriver performs the input.

## First milestone

- Native Safari WebDriver session lifecycle, independent of Chrome and Browser Harness.
- Indexed DOM observations with document, field, and target freshness checks.
- Native click, clear/type, dropdown selection, page scrolling, and waiting.
- No automatic retry after input may have occurred.
- Bounded model/action budgets, offline tests, local browser checks, and a live smoke test.

This is an initial prototype. See VALIDATION.md for checks actually completed on this machine.

## Setup

Requires macOS, Safari with `/usr/bin/safaridriver`, and Python 3.12 or newer.
Enable Safari's **Allow remote automation** setting in its Developer settings.
If Developer settings are hidden, enable **Show features for web developers** under Advanced.
Safari may require a one-time `safaridriver --enable` authorization.

Install the project and run the local checks:

```sh
uv sync --locked
.venv/bin/jev-safari doctor
.venv/bin/jev-safari smoke
```

Alternatively, create a virtual environment and install the project with
`python -m pip install -e .`.

## Credentials and live use

Supply an existing local dotenv file with `--env-file`, or copy `.env.example` to `.env`
and fill the keys locally. `.env` is ignored by Git. Never paste real keys into a chat.
Existing environment variables take precedence over the file. No Chrome configuration is modified.

```sh
.venv/bin/jev-safari --env-file '/absolute/path/to/credentials.env' smoke --live
.venv/bin/jev-safari --env-file '/absolute/path/to/credentials.env' run \
  --url 'https://en.wikipedia.org/wiki/Main_Page' \
  --goal 'Find and open the Wikipedia article about Safari, the web browser.' \
  --max-steps 12
```

Live runs send observed page text to TypeSafe and selected field context to the configured text provider.
They incur provider usage. The smoke test uses only synthetic local content and verifies the resulting DOM,
including that Save was clicked exactly once. Generic `run` reports the model's status and
`independently_verified: false`; callers must verify the requested outcome themselves.

The library exposes `jev_safari.Agent`. Use it as a context manager and verify the final browser state
inside the context, before its owned Safari session closes.

## Current limitations

Safari WebDriver opens an isolated automation window. Existing Safari tabs, cookies, saved logins,
and extensions are not reused. Safari normally permits one active WebDriver session.
This version does not support pop-up tabs, nested frames, shadow roots, uploads, canvas controls,
or arbitrary keyboard widgets. Password fields are excluded from Jev's action table.
It stops on unexpected dialogs. It does not include a transaction-approval interface; keep goals
within the user's explicit authorization and use it first on test pages.

The adapter uses native WebDriver element commands. Its behavior and speed differ from Chrome's CDP.
No Chrome benchmark is claimed for Safari. Browser-only tests make no model calls.

## Development

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
node --check src/jev_safari/snapshot.js
.venv/bin/python scripts/check_guards.py
uv build
```

`src/jev_safari/webdriver.py` manages the local driver and protocol.
`browser.py` translates observed actions to Safari input. `agent.py`, `model.py`,
`questions.py`, and `snapshot.js` contain the adapted upstream loop and policy.
`cli.py` provides diagnostics, smoke tests, and the command line.

See UPSTREAM.md and LICENSE for attribution.
