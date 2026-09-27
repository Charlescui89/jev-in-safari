# JEV in Safari

[![Offline checks](https://github.com/Charlescui89/jev-in-safari/actions/workflows/ci.yml/badge.svg)](https://github.com/Charlescui89/jev-in-safari/actions/workflows/ci.yml)

**An experimental, open-source Safari adapter for Jev Ultrafast.**
Use natural-language goals to drive an isolated Safari automation window on macOS.
Jev chooses an operation and observed target;
the configured text model writes field values; Safari WebDriver performs the input.

**Status: alpha preparation.** Offline tests pass; native Safari and model-driven Safari validation
are still pending local remote-automation authorization. A green CI badge covers offline checks only.
See [validation results](VALIDATION.md) before trying it. No Safari speed benchmark is available.

## What is implemented

- Native Safari WebDriver session lifecycle, independent of Chrome and Browser Harness.
- Indexed DOM observations with document, field, and target freshness checks.
- Native click, clear/type, dropdown selection, page scrolling, and waiting.
- No automatic retry after input may have occurred.
- Bounded model/action budgets, offline tests, local browser checks, and a live smoke test.

Built for macOS developers exploring Jev on Safari. Adapted from
[Jev Ultrafast](https://github.com/browser-use/jev-ultrafast); this is an independent community project.

## Quick start — no API keys needed

Requires macOS, Safari with `/usr/bin/safaridriver`, Python 3.12 or newer, Git, and
[uv](https://docs.astral.sh/uv/getting-started/installation/).
Enable Safari's **Allow remote automation** setting in its Developer settings.
If Developer settings are hidden, enable **Show features for web developers** under Advanced.
Complete any Mac authentication prompt locally. See
[Apple's WebDriver setup guide](https://developer.apple.com/documentation/safari-developer-tools/macos-enabling-webdriver).

Clone, install, and test the browser adapter on a disposable local page:

```sh
git clone https://github.com/Charlescui89/jev-in-safari.git
cd jev-in-safari
uv sync --locked
.venv/bin/jev-safari doctor
.venv/bin/jev-safari smoke
```

`doctor` should report `browser_ready: true`. Missing credential flags are expected at this stage.
`smoke` should report `verified: true` after checking the field, dropdown, checkbox, and exactly one Save.
These commands make no model calls. This is the expected result, not a claim of completed Safari validation.

Without uv, run `python3 -m venv .venv` and `.venv/bin/python -m pip install -e .` after cloning.

### If setup fails

- **Session not created:** enable remote automation, complete local authentication, and close other
  WebDriver sessions. Retry `doctor`.
- **Missing configuration:** browser-only `smoke` needs no keys; live commands need the two keys below.
- **Input outcome uncertain:** inspect the result before starting another run; an input may already have occurred.
- **Other failures:** [file a bug report](https://github.com/Charlescui89/jev-in-safari/issues/new/choose)
  with macOS/Safari/Python versions and sanitized output.

## Credentials and live use

You need a [TypeSafe](https://docs.typesafe.ai/introduction) API key for Jev and a key for
the configured text model provider. The example configuration uses DeepSeek.
Model calls require provider service access and may incur charges.

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

## Help test the alpha

Start with `doctor` and browser-only `smoke`, then try `smoke --live` if you have provider access.
Report your versions, the command, and whether the verified result passed using the
[tester report template](https://github.com/Charlescui89/jev-in-safari/issues/new/choose).
Do not include `.env` files, credentials, or private page content.
See [CONTRIBUTING.md](CONTRIBUTING.md) for development and feedback guidelines.
