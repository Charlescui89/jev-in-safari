"""Small local W3C WebDriver client; each command is sent at most once."""

import os
import socket
import subprocess
import time
from urllib.parse import quote

import httpx

ELEMENT = "element-6066-11e4-a52e-4f735466cecf"


class DriverError(RuntimeError):
    pass


class WebDriver:
    def __init__(self):
        self.session = None
        self.process = None
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        self.client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=35, trust_env=False)
        try:
            self.process = subprocess.Popen(
                ["/usr/bin/safaridriver", "--port", str(port)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                env={k: v for k, v in os.environ.items() if k not in {"TYPESAFE_API_KEY", "TEXT_MODEL_API_KEY"}},
            )
            deadline = time.monotonic() + 8
            while True:
                if self.process.poll() is not None:
                    raise DriverError("Safari driver exited during startup")
                try:
                    response = self.client.get("/status", timeout=0.5)
                    if response.is_success:
                        break
                except httpx.HTTPError:
                    pass
                if time.monotonic() >= deadline:
                    raise DriverError("Safari driver did not start within eight seconds")
                time.sleep(0.1)
            value = self.request("POST", "/session", {"capabilities": {"alwaysMatch": {
                "browserName": "safari", "pageLoadStrategy": "normal", "unhandledPromptBehavior": "ignore",
            }}})
            self.session = value["sessionId"]
            self.capabilities = value.get("capabilities", {})
            self.command("POST", "/timeouts", {"script": 10000, "pageLoad": 25000, "implicit": 0})
        except BaseException:
            self.close()
            raise

    def request(self, method, path, body=None):
        try:
            response = self.client.request(method, path, json=body)
        except httpx.HTTPError:
            raise DriverError("Safari WebDriver connection failed; command was not retried") from None
        try:
            value = response.json()["value"]
        except (ValueError, KeyError, TypeError):
            raise DriverError("Safari WebDriver returned an invalid response") from None
        if response.is_error:
            known = {"session not created", "invalid session id", "stale element reference", "no such element",
                     "no such window", "javascript error", "timeout", "script timeout", "element click intercepted",
                     "element not interactable", "unexpected alert open", "invalid argument", "unknown error"}
            code = value.get("error") if isinstance(value, dict) else None
            code = code if code in known else "unknown error"
            message = value.get("message", "") if isinstance(value, dict) else ""
            hint = ""
            if "remote automation" in message.lower():
                hint = "; enable Safari Settings > Developer > Allow remote automation"
            elif "session not created" == code:
                hint = "; check Safari automation permissions and whether another automation session is active"
            raise DriverError(f"Safari WebDriver: {code}{hint}")
        return value

    def command(self, method, path, body=None):
        if not self.session:
            raise DriverError("Safari session is closed")
        return self.request(method, f"/session/{quote(self.session, safe='')}{path}", body)

    def script(self, script, *args):
        return self.command("POST", "/execute/sync", {"script": script, "args": list(args)})

    def close(self):
        try:
            if self.session:
                session, self.session = self.session, None
                try:
                    self.request("DELETE", f"/session/{quote(session, safe='')}")
                except DriverError:
                    pass
        finally:
            self.client.close()
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
