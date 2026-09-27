from unittest.mock import Mock

import httpx
import pytest

from jev_safari.browser import ActionUncertain, Browser, StalePage
from jev_safari.webdriver import DriverError, WebDriver


def fake_browser(kind="click"):
    browser = Browser.__new__(Browser)
    browser.driver = Mock()
    browser.fresh = Mock(return_value=True)
    browser.resolve = Mock(return_value="observed-element")
    browser.after_input = None
    action = {"id": "e1", "node": 1, "kind": kind, "label": "Test"}
    page = {"actions": [action]}
    return browser, action, page


def test_stale_page_never_dispatches_input():
    browser, action, page = fake_browser()
    browser.fresh.return_value = False
    with pytest.raises(StalePage):
        browser.act(action, page)
    browser.driver.command.assert_not_called()


def test_unobserved_action_is_rejected():
    browser, action, page = fake_browser()
    with pytest.raises(ValueError):
        browser.act({**action, "node": 999}, page)
    browser.driver.command.assert_not_called()


def test_input_failure_is_not_retryable_staleness():
    browser, action, page = fake_browser()
    browser.driver.command.side_effect = DriverError("stale element reference")
    with pytest.raises(ActionUncertain):
        browser.act(action, page)
    assert browser.driver.command.call_count == 1


def test_failed_fill_after_clear_never_retries():
    browser, action, page = fake_browser("fill")
    browser.driver.command.side_effect = [None, DriverError("timeout")]
    with pytest.raises(ActionUncertain):
        browser.act(action, page, text="hello")
    assert browser.driver.command.call_count == 2


def test_mutation_transport_timeout_is_sent_once():
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("untrusted server detail with secret data")
    driver = WebDriver.__new__(WebDriver)
    driver.session = "test"
    driver.client = httpx.Client(base_url="http://127.0.0.1:1234", transport=httpx.MockTransport(handler))
    with pytest.raises(DriverError, match="connection failed") as exc:
        driver.command("POST", "/element/id/click", {})
    assert "secret data" not in str(exc.value)
    assert len(calls) == 1


def test_driver_error_does_not_expose_response_details():
    response = {"value": {"error": "session not created", "message": "private detail"}}
    driver = WebDriver.__new__(WebDriver)
    driver.session = "test"
    driver.client = httpx.Client(base_url="http://127.0.0.1:1234", transport=httpx.MockTransport(
        lambda _: httpx.Response(500, json=response)))
    with pytest.raises(DriverError, match="session not created") as exc:
        driver.command("POST", "/url", {"url": "about:blank"})
    assert "private detail" not in str(exc.value)


def test_repeated_page_changes_are_bounded():
    from jev_safari.agent import Agent
    agent = Agent.__new__(Agent)
    agent.max_steps = 2
    agent.state = {"status": "ready"}
    agent.command = Mock(return_value={"status": "ready"})
    with pytest.raises(RuntimeError, match="repeated page changes"):
        list(agent.run())
    assert agent.command.call_count == 6


def test_live_smoke_result_checks_save_count():
    from jev_safari.cli import verify_smoke
    browser = Mock()
    browser.evaluate.return_value = {
        "message": "Safari integration test", "category": "Research", "enabled": True,
        "result": "Saved: Safari integration test | Research | enabled", "save_count": 2,
    }
    assert not verify_smoke(browser)["verified"]
    browser.evaluate.return_value["save_count"] = 1
    assert verify_smoke(browser)["verified"]
