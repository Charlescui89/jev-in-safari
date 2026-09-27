# Alpha launch kit

## Current gate

The repository is public. Keep the alpha release as a draft until native Safari smoke tests,
guard checks, and the live model smoke test pass. Publish their actual results in VALIDATION.md.
No verified Safari demo has been recorded yet.

## Release checklist

- [ ] Fresh-clone setup succeeds on macOS.
- [ ] `doctor` reports browser ready.
- [ ] Browser-only `smoke` reports verified true.
- [ ] `scripts/check_guards.py` passes.
- [ ] `smoke --live` reports verified true, including Save count one.
- [ ] Offline CI passes for the release commit.
- [ ] Record a 30–60 second demo on the synthetic smoke page with no credentials visible.
- [ ] Add demo and tested macOS/Safari versions to README and release notes.
- [ ] Publish the draft alpha release.

## First audience

Recruit five macOS developers already interested in Jev, Browser Use, or browser automation.
Start with communities you participate in and follow each community's posting rules.
Ask each tester to install from a fresh clone, run the smoke test, and submit a tester report.
Track setup success, setup time, verified test results, and repeated blockers. Fix repeated blockers
before broadening the launch. Do not use stars as a substitute for successful installs.

## Early tester invitation — draft

I’m building JEV in Safari, an experimental open-source Safari adapter for Jev Ultrafast.
It uses native Safari WebDriver and isolated automation windows on macOS.

The repository includes a local smoke test that requires no API keys. Natural-language runs
use TypeSafe for Jev plus a configured text model provider and may incur provider charges.
Native Safari validation is still pending; I’m looking for macOS developers to help test setup
and report issues. This is an independent community project adapted from Browser Use’s Jev Ultrafast.

Repo: https://github.com/Charlescui89/jev-in-safari
Feedback: https://github.com/Charlescui89/jev-in-safari/issues/new/choose

## After verified launch — draft outline

Replace the pending-validation sentence above with actual tested versions and a link to the
verified demo. Describe exactly which smoke-test operations passed. Include known limitations:
isolated sessions, one WebDriver session, and no existing logins, frames, or pop-up workflow support.
Avoid speed or compatibility claims until measured.

For a later Show HN post, use a concrete title such as “Show HN: JEV in Safari — a Safari adapter
for Jev browser agents” and explain the implementation, setup, and limitations in a first comment.
Post only once the project is ready to try. Follow the
[Show HN guidelines](https://news.ycombinator.com/showhn.html); do not solicit votes.

## Demo sequence

1. Show the project name, tested Safari version, and synthetic test page.
2. Run the live smoke command without displaying the credential file.
3. Show the field, dropdown, checkbox, and Save result.
4. Show `verified: true` and `save_count: 1` from the independent DOM check.
5. End with the repository link and an invitation to report test results.

Use a real run. If it fails, fix or document the failure before recording a successful demo.
