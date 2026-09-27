"""Safari implementation of the Jev browser contract using native WebDriver input."""

import hashlib
import json
import time
from pathlib import Path
from urllib.parse import quote

from .webdriver import ELEMENT, DriverError, WebDriver

READ_STATE = Path(__file__).with_name("snapshot.js").read_text()


class StalePage(ValueError):
    """Safe to observe again: this attempt has not performed any input."""


class ActionUncertain(RuntimeError):
    """An input command failed after dispatch; never retry automatically."""


def fingerprint(state):
    content = {k: state[k] for k in ("url", "text", "actions", "scroll")}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


RESOLVE_TARGET = """
const action=arguments[0], e=window.__jevFast?.nodes.get(action.node);
if (!e?.isConnected || e.matches(':disabled') || e.closest('[aria-disabled="true"],[inert]') ||
    !e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})) return null;
if (action.kind==='fill' && (e.readOnly || e.getAttribute('aria-readonly')==='true')) return null;
const r=e.getBoundingClientRect(), x=r.x+r.width/2, y=r.y+r.height/2;
if (!r.width || !r.height || x<0 || y<0 || x>=innerWidth || y>=innerHeight) return null;
if (!e.contains(document.elementFromPoint(x,y))) return null;
if (action.kind==='select') {
    if (e.tagName!=='SELECT') return null;
    return [...e.options].find(o=>o.value===action.value && !o.disabled &&
        !o.closest('optgroup[disabled]')) || null;
}
return e;
"""


class Browser:
    def __init__(self, url):
        self.driver = WebDriver()
        self.after_input = None
        try:
            self.driver.command("POST", "/window/rect", {"width": 1120, "height": 900})
            self.navigate(url)
        except BaseException:
            self.close()
            raise

    def navigate(self, url):
        return self.driver.command("POST", "/url", {"url": url})

    def evaluate(self, expression):
        # This convenience method accepts application-owned code, never model output.
        return self.driver.script("return eval(arguments[0]);", expression)

    def observe(self, screenshot=False):
        if self.after_input:
            # Allow input handlers and asynchronous autocomplete to publish their state.
            time.sleep(0.2 if self.after_input["kind"] == "fill" else 0.05)
            self.after_input = None
        state = self.driver.script("return " + READ_STATE)
        if state is None:
            raise StalePage("Document is navigating")
        state["fingerprint"] = fingerprint(state)
        if screenshot:
            state["screenshot"] = self.driver.command("GET", "/screenshot")
        return state

    def fresh(self, page, action=None):
        if action is not None and action["kind"] in {"click", "select"}:
            if type(action.get("node")) is not int:
                return False
            current = self.driver.script(
                "const c=window.__jevFast; return c ? [c.pageKey(),c.guard(c.nodes.get(arguments[0]))] : null;",
                action["node"],
            )
            return current == [page["page_key"], page["guards"].get(str(action["node"]))]
        state = self.driver.script("return " + READ_STATE)
        return state is not None and state["marker"] == page["marker"]

    def resolve(self, action):
        reference = self.driver.script(RESOLVE_TARGET, action)
        if not reference or ELEMENT not in reference:
            raise StalePage("Target changed or is covered. Observe again.")
        return quote(reference[ELEMENT], safe="")

    def act(self, action, page, text=None):
        if action not in page["actions"]:
            raise ValueError("Action was not offered by this observation")
        kind = action["kind"]
        if kind not in {"click", "fill", "select", "scroll", "wait"}:
            raise ValueError("Unsupported operation")
        if kind in {"click", "fill", "select"} and type(action.get("node")) is not int:
            raise ValueError("Invalid observed node")
        if kind == "fill" and (not isinstance(text, str) or not text.strip() or len(text) > 2000):
            raise ValueError("Invalid field text")
        if not self.fresh(page, action):
            raise StalePage("Page changed since this decision. Observe again.")
        if kind == "wait":
            time.sleep(0.1)
            return {"executed": action["id"]}
        target = self.resolve(action) if kind in {"click", "fill", "select"} else None
        # All errors after this point are uncertain; clearing a field may already have changed it.
        try:
            if kind in {"click", "select"}:
                self.driver.command("POST", f"/element/{target}/click", {})
            elif kind == "fill":
                self.driver.command("POST", f"/element/{target}/clear", {})
                self.driver.command("POST", f"/element/{target}/value", {"text": text})
            else:
                self.driver.script("window.scrollBy(0, arguments[0]);", action["delta"])
        except DriverError as exc:
            raise ActionUncertain("Safari input was not confirmed; inspect the result before retrying") from exc
        self.after_input = action
        return {"executed": action["id"]}

    def close(self):
        self.driver.close()
