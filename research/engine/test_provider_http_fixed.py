import io
from urllib.error import HTTPError
from urllib.request import Request

from . import provider_http
from .provider_http import RetryPolicy, read_with_retries


def test_429_retries_then_succeeds(monkeypatch):
    calls = {"n": 0}
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b"ok"
    def fake_urlopen(request, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            raise HTTPError(request.full_url, 429, "rate limited", {}, io.BytesIO())
        return Response()
    monkeypatch.setattr(provider_http, "urlopen", fake_urlopen)
    sleeps = []
    assert read_with_retries(Request("https://example.test"), policy=RetryPolicy(max_retries=3, backoff_seconds=0.01), sleep=sleeps.append) == b"ok"
    assert calls["n"] == 3
    assert sleeps == [0.01, 0.02]


def test_429_exhaustion_raises(monkeypatch):
    def fake_urlopen(request, timeout):
        raise HTTPError(request.full_url, 429, "rate limited", {}, io.BytesIO())
    monkeypatch.setattr(provider_http, "urlopen", fake_urlopen)
    import pytest
    with pytest.raises(HTTPError) as exc:
        read_with_retries(Request("https://example.test"), policy=RetryPolicy(max_retries=2, backoff_seconds=0), sleep=lambda _: None)
    assert exc.value.code == 429


def test_non_429_is_not_retried(monkeypatch):
    calls = {"n": 0}
    def fake_urlopen(request, timeout):
        calls["n"] += 1
        raise HTTPError(request.full_url, 500, "server error", {}, io.BytesIO())
    monkeypatch.setattr(provider_http, "urlopen", fake_urlopen)
    import pytest
    with pytest.raises(HTTPError) as exc:
        read_with_retries(Request("https://example.test"), policy=RetryPolicy(max_retries=3, backoff_seconds=0), sleep=lambda _: None)
    assert exc.value.code == 500
    assert calls["n"] == 1
