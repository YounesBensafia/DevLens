import pytest
import requests

from devlens.llm.client import send_request
from devlens.llm.exception import LLMClientError


class _DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_send_request_returns_json(monkeypatch):
    expected = {"ok": True}

    def fake_post(*args, **kwargs):
        return _DummyResponse(expected)

    monkeypatch.setattr("devlens.llm.client.requests.post", fake_post)

    result = send_request({"sample": "payload"})
    assert result == expected


def test_send_request_wraps_request_exception(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.exceptions.Timeout("network timeout")

    monkeypatch.setattr("devlens.llm.client.requests.post", fake_post)

    with pytest.raises(LLMClientError) as exc_info:
        send_request({})

    assert "Request failed" in str(exc_info.value)
