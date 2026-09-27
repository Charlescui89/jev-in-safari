# v0.1.0-alpha.1 — draft

JEV in Safari is an experimental community adapter for running Jev Ultrafast through native
Safari WebDriver on macOS. Package version: `0.1.0a1`.

## Included

- Isolated Safari session lifecycle and indexed DOM observations.
- Native click, fill, select, scrolling, and wait operations.
- Freshness checks and a stop when a browser input may have occurred.
- Bounded agent runs, credential-presence diagnostics, and a synthetic local smoke test.
- Offline regression tests, CI, setup instructions, and tester feedback templates.

## Validation and limitations

The initial 30 offline tests passed locally. See [VALIDATION.md](VALIDATION.md) for current results.
Native Safari and model-driven Safari tests remain pending local remote-automation authorization.
Keep this release as a draft until those checks pass and the results are recorded.

Requires macOS, Safari remote automation, and Python 3.12+. Browser-only smoke needs no API keys.
Natural-language tasks require TypeSafe/Jev and text model service access and may incur charges.
Existing Safari tabs and saved logins are not reused. Frames, pop-up workflows, shadow roots,
uploads, and arbitrary keyboard widgets are unsupported. No Safari performance claim is made.

Start with [README.md](README.md). Report results using the repository's issue templates.
Based on Browser Use's MIT-licensed Jev Ultrafast; see [UPSTREAM.md](UPSTREAM.md).
