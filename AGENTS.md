# JEV in Safari

Build a Safari adapter for Jev without changing the installed Chrome project.
Read README.md and UPSTREAM.md before editing the agent loop or DOM snapshot.
Keep the original flow: observe indexed elements, ask Jev for an operation and compatible target, execute once.
Use Safari's isolated WebDriver automation window. Do not assume access to ordinary Safari tabs or saved logins.
Reject changed, hidden, disabled, replaced, or covered targets before input. Never automatically retry a browser mutation.
Keep API keys in local ignored files; do not print keys or provider request headers.
Offline tests must not call model APIs. Browser tests use local disposable pages.
For live tests, independently verify actual DOM results; DONE is not proof.
Run pytest, ruff check, JavaScript syntax checks, and a package build after implementation changes.
Record unavailable Safari permissions separately from test failures.
Do not commit, push, or publish unless requested.
