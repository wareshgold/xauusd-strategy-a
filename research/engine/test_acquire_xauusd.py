import json
from pathlib import Path

import pytest

from .acquisition_request import AcquisitionRequest
from . import acquire_xauusd, provider_http


def payload():
    return {
        "meta": {"symbol": "XAU/USD", "interval": "1min", "type": "Precious Metal"},
        "values": [
            {"datetime": "2026-09-09 18:36:00", "open": "4402.905", "high": "4402.905", "low": "4401.79593", "close": "4401.90825"},
            {"datetime": "2026-09-09 18:35:00", "open": "4403.1", "high": "4403.2", "low": "4402.8", "close": "4402.9"},
        ],
    }


def test_acquisition_never_prints_api_key(monkeypatch, tmp_path, capsys):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(payload(), separators=(",", ":")).encode()

    seen = {}
    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        return Response()

    monkeypatch.setattr(provider_http, "urlopen", fake_urlopen)
    request = AcquisitionRequest("XAU/USD", "1min", 2, source_timezone="Australia/Sydney")
    manifest, artifact = acquire_xauusd.acquire(request, api_key="SECRET", output_dir=tmp_path)
    output = capsys.readouterr().out
    assert "SECRET" not in output
    assert "SECRET" in seen["url"]
    assert artifact.quality_status == "PASS"
    assert manifest.source_timezone == "Australia/Sydney"
    assert (tmp_path / "raw" / "time_series.json").exists()
    assert (tmp_path / "normalized" / "candles.json").exists()


def test_acquisition_blocks_bad_ohlc(monkeypatch, tmp_path):
    bad = payload()
    bad["values"][0]["high"] = "4401.0"

    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(bad).encode()

    monkeypatch.setattr(provider_http, "urlopen", lambda request, timeout: Response())
    request = AcquisitionRequest("XAU/USD", "1min", 2, source_timezone="Australia/Sydney")
    with pytest.raises(ValueError, match="OHLC invariant violated"):
        acquire_xauusd.acquire(request, api_key="SECRET", output_dir=tmp_path)
