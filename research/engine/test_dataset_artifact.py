from research.engine.dataset_artifact import DatasetArtifact, canonicalize_json, fingerprint_bytes


def test_fingerprint_bytes_is_stable():
    assert fingerprint_bytes(b"abc") == fingerprint_bytes(b"abc")
    assert fingerprint_bytes(b"abc") != fingerprint_bytes(b"abd")


def test_canonicalize_json_is_key_order_independent():
    assert canonicalize_json({"b": 2, "a": 1}) == b'{"a":1,"b":2}'


def test_dataset_artifact_identity_is_stable():
    artifact = DatasetArtifact(
        provider="Twelve Data",
        instrument="XAU/USD",
        interval="1min",
        requested_start_utc=None,
        requested_end_utc=None,
        retrieval_timestamp_utc="2026-09-09T08:40:00+00:00",
        source_timezone="Australia/Sydney",
        source_version=None,
        row_count=5000,
        actual_start_utc="2026-09-05T21:17:00+00:00",
        actual_end_utc="2026-09-09T08:36:00+00:00",
        raw_sha256="raw",
        normalized_sha256="normalized",
        quality_status="PASS",
    )
    assert artifact.fingerprint() == artifact.fingerprint()
    assert '"provider":"Twelve Data"' in artifact.canonical_json()
