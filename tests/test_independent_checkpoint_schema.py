from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "research"
    / "schemas"
    / "independent-audit-checkpoint-v1.schema.json"
)
DIGEST = "a" * 64


@pytest.fixture(scope="module")
def schema():
    value = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(value)
    return value


@pytest.fixture(scope="module")
def validator(schema):
    return Draft202012Validator(schema, format_checker=FormatChecker())


def valid_request():
    return {
        "schema_version": "sp2l.audit-checkpoint.request.v1",
        "request_id": DIGEST,
        "audit_identity": "synthetic-audit",
        "environment_identity": "synthetic-test",
        "audit_sequence": 1,
        "entry_sha256": DIGEST,
        "previous_checkpoint_digest": None,
        "previous_checkpoint_revision": None,
        "audit_file_identity": "synthetic-file-id",
        "audit_byte_size": 256,
        "writer_build": "synthetic-build",
    }


def valid_receipt():
    return {
        "schema_version": "sp2l.audit-checkpoint.receipt.v1",
        "request_id": DIGEST,
        "request_sha256": DIGEST,
        "service_identity": "synthetic-checkpoint-service",
        "checkpoint_revision": "revision-1",
        "accepted_audit_sequence": 1,
        "accepted_entry_sha256": DIGEST,
        "accepted_audit_byte_size": 256,
        "previous_checkpoint_digest": None,
        "acknowledged_at": "2026-10-29T12:00:00Z",
        "authentication": {"kind": "synthetic-test-only"},
    }


def test_checkpoint_schema_is_valid_draft_2020_12(schema):
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "urn:sp2l:independent-audit-checkpoint-v1"


@pytest.mark.parametrize("factory", [valid_request, valid_receipt])
def test_valid_synthetic_contract_envelopes_pass(validator, factory):
    assert list(validator.iter_errors(factory())) == []


@pytest.mark.parametrize(
    ("factory", "field", "bad_value"),
    [
        (valid_request, "request_id", "not-a-sha256"),
        (valid_request, "audit_sequence", 0),
        (valid_request, "schema_version", "unknown.version"),
        (valid_receipt, "request_sha256", "not-a-sha256"),
        (valid_receipt, "accepted_audit_sequence", 0),
        (valid_receipt, "acknowledged_at", "not-a-date"),
        (valid_receipt, "acknowledged_at", "2026-10-29T12:00:00"),
        (valid_receipt, "schema_version", "unknown.version"),
    ],
)
def test_malformed_checkpoint_envelopes_fail_closed(validator, factory, field, bad_value):
    value = factory()
    value[field] = bad_value
    assert list(validator.iter_errors(value))


@pytest.mark.parametrize("factory", [valid_request, valid_receipt])
def test_unknown_top_level_fields_are_rejected(validator, factory):
    value = factory()
    value["unreviewed_field"] = "must-not-be-ignored"
    assert list(validator.iter_errors(value))


def test_receipt_with_wrong_shape_cannot_pass_as_request_or_receipt(validator):
    value = valid_receipt()
    value.pop("authentication")
    value["audit_identity"] = "not-a-receipt-field"
    assert list(validator.iter_errors(value))


def _test_only_receipt_matches_request(request, receipt):
    """Contract predicate for tests only; not runtime or service implementation."""
    return (
        receipt["request_id"] == request["request_id"]
        and receipt["request_sha256"] == request["request_id"]
        and receipt["accepted_audit_sequence"] == request["audit_sequence"]
        and receipt["accepted_entry_sha256"] == request["entry_sha256"]
        and receipt["accepted_audit_byte_size"] == request["audit_byte_size"]
        and receipt["previous_checkpoint_digest"] == request["previous_checkpoint_digest"]
    )


def test_synthetic_receipt_must_match_request_identity_and_checkpoint_fields():
    request = valid_request()
    receipt = valid_receipt()
    assert _test_only_receipt_matches_request(request, receipt)


@pytest.mark.parametrize(
    ("receipt_field", "bad_value"),
    [
        ("request_id", "b" * 64),
        ("request_sha256", "b" * 64),
        ("accepted_audit_sequence", 2),
        ("accepted_entry_sha256", "b" * 64),
        ("accepted_audit_byte_size", 257),
        ("previous_checkpoint_digest", "b" * 64),
    ],
)
def test_synthetic_receipt_mismatch_is_rejected(receipt_field, bad_value):
    request = valid_request()
    receipt = valid_receipt()
    receipt[receipt_field] = bad_value
    assert not _test_only_receipt_matches_request(request, receipt)
