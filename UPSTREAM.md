# Upstream attribution

The Jev policy, text helper, agent loop, DOM snapshot, and policy/guard regressions derive from
[browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast), commit
`1231850a0bf1a0c0341fe408ef1668dbbfdfac46`, under the MIT license in LICENSE.

The Safari WebDriver transport, command-line interface, and Safari adapter are local additions.
The agent adds a configurable action budget and browser factory. Safari screenshots are PNG.
This project does not depend on the installed Chrome project's runtime or Browser Harness.
