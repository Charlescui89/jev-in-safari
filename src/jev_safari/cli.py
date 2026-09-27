"""Local Safari diagnostics, a disposable smoke test, and bounded Jev tasks."""

import argparse
import json
import os
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit

from dotenv import load_dotenv

from .agent import Agent
from .browser import ActionUncertain, Browser, StalePage
from .webdriver import DriverError

SMOKE_HTML = b'''<!doctype html><title>JEV in Safari test</title>
<style>body{font:22px sans-serif;margin:40px}input,button,select{font:22px sans-serif}
label{display:block;margin:20px 0}</style>
<h1>JEV in Safari test</h1>
<label>Test message <input id="message" autocomplete="off"></label>
<label>Category <select id="category"><option>General</option><option>Research</option></select></label>
<label><input id="enabled" type="checkbox">Enable test</label>
<button id="save" onclick="window.saveCount=(window.saveCount||0)+1;document.getElementById('result').textContent=
    'Saved: '+document.getElementById('message').value+' | '+document.getElementById('category').value+' | '+
    (document.getElementById('enabled').checked?'enabled':'disabled')">Save test</button>
<p id="result" role="status">No result saved.</p>'''


@contextmanager
def local_test_page():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(SMOKE_HTML)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()


def credentials():
    return {key: bool(os.environ.get(key, "").strip()) for key in ("TYPESAFE_API_KEY", "TEXT_MODEL_API_KEY")}


def require_keys():
    missing = [key for key, present in credentials().items() if not present]
    if missing:
        raise ValueError("Missing configuration: " + ", ".join(missing))


def safe_error(exc):
    value = str(exc)
    for name in ("TYPESAFE_API_KEY", "TEXT_MODEL_API_KEY"):
        if secret := os.environ.get(name):
            value = value.replace(secret, "[REDACTED]")
    return value


def run_agent(agent):
    for state in agent.run():
        print(json.dumps({"event": "progress", "status": state["status"],
                          "actions": len(state["history"]), "decisions": len(state["decisions"])}), flush=True)
    return state


def summary(state):
    return {"status": state["status"], "actions": len(state["history"]),
            "decisions": len(state["decisions"]), "text_calls": len(state["text_calls"]),
            "elapsed_ms": state["elapsed_ms"]}


def verify_smoke(browser):
    observed = browser.evaluate("({message:document.getElementById('message').value,"
                                "category:document.getElementById('category').value,"
                                "enabled:document.getElementById('enabled').checked,"
                                "result:document.getElementById('result').textContent,"
                                "save_count:window.saveCount||0})")
    expected = {"message": "Safari integration test", "category": "Research", "enabled": True,
                "result": "Saved: Safari integration test | Research | enabled", "save_count": 1}
    return {"verified": observed == expected, "observed": observed}


def smoke(live):
    with local_test_page() as url:
        if live:
            require_keys()
            goal = ("Enter Safari integration test in Test message, select Research as Category, "
                    "check Enable test, then click Save test exactly once. Finish when the saved result "
                    "shows Safari integration test, Research, and enabled.")
            with Agent(url, goal, max_steps=8) as agent:
                state = run_agent(agent)
                return {"mode": "live", **summary(state), **verify_smoke(agent.browser)}
        browser = Browser(url)
        try:
            # Deterministic adapter regression on a disposable local page; no model calls.
            for kind, label, value in [("fill", "Test message", "Safari integration test"),
                                       ("select", "Category", None), ("click", "Enable test", None),
                                       ("click", "Save test", None)]:
                page = browser.observe()
                action = next(a for a in page["actions"] if a["kind"] == kind and a["label"].startswith(label))
                browser.act(action, page, text=value)
            return {"mode": "browser-only", **verify_smoke(browser)}
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="JEV in Safari — isolated Safari automation")
    parser.add_argument("--env-file", type=Path, help="Local dotenv file; keys are never printed")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check Safari session creation and credential presence; no model calls")
    probe = commands.add_parser("smoke", help="Verify typing, selection, checkbox, and click on a local page")
    probe.add_argument("--live", action="store_true", help="Exercise the configured model APIs (paid requests)")
    run = commands.add_parser("run", help="Run a bounded user-authorized browser task")
    run.add_argument("--url", required=True)
    run.add_argument("--goal", required=True)
    run.add_argument("--max-steps", type=int, default=12)
    args = parser.parse_args()
    try:
        env_path = args.env_file or Path.cwd() / ".env"
        if args.env_file and not env_path.is_file():
            raise ValueError("The specified dotenv file does not exist")
        load_dotenv(env_path, override=False)
        if args.command == "doctor":
            browser = Browser("about:blank")
            try:
                result = {"browser_ready": browser.evaluate("document.readyState") == "complete",
                          "safari_version": browser.driver.capabilities.get("browserVersion"),
                          "credentials": credentials(), "isolated_session": True}
            finally:
                browser.close()
            print(json.dumps(result))
            return 0 if result["browser_ready"] else 1
        if args.command == "smoke":
            result = smoke(args.live)
            print(json.dumps(result))
            return 0 if result["verified"] else 1
        if urlsplit(args.url).scheme not in {"https", "http"}:
            raise ValueError("Starting URL must use http or https")
        require_keys()
        with Agent(args.url, args.goal, max_steps=args.max_steps) as agent:
            state = run_agent(agent)
            print(json.dumps({**summary(state), "independently_verified": False}))
        return 0 if state["status"] == "done" else 1
    except (DriverError, ActionUncertain, StalePage, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": safe_error(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
