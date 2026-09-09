from sp2l_engine.acquisition_manifest import AcquisitionManifest, fingerprint_bytes


def test_raw_fingerprint_is_stable():
    assert fingerprint_bytes(b"xauusd-fixture") == fingerprint_bytes(b"xauusd-fixture")
    assert fingerprint_bytes(b"xauusd-fixture") != fingerprint_bytes(b"xauusd-fixture-v2")


def test_manifest_canonical_json_is_order_stable():
    manifest = AcquisitionManifest(
        provider="Twelve Data",
        instrument="XAU/USD",
        interval="1min",
        requested_start_utc="2026-01-01T00:00:00+00:00",
        requested_end_utc="2026-01-01T01:00:00+00:00",
        actual_first_timestamp_utc="2026-01-01T00:00:00+00:00",
        actual_last_timestamp_utc="2026-01-01T00:59:00+00:00",
        row_count=60,
        request_timestamp_utc="2026-09-09T00:00:00+00:00",
        source_timezone="Australia/Sydney",
        source_version="fixture",
        raw_sha256="raw",
        normalized_sha256="normalized",
        response_metadata={"interval": "1min", "symbol": "XAU/USD"},
    )
    text = manifest.canonical_json()
    assert text.index('"interval"') < text.index('"provider"')
    assert '"raw_sha256":"raw"' in text
