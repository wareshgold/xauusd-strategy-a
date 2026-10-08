from __future__ import annotations

import hashlib

import pytest

from strategy_factory.forward_session_factory import (
    DemoForwardSessionFactory,
    ForwardSessionError,
)
from strategy_factory.models import GateResult, GateStatus


def _gate():
    return GateResult(
        name="FRESH_HOLDOUT_TO_FORWARD",
        status=GateStatus.PASS,
        evidence="holdout=HOLDOUT-1;forward=FWD-1",
        details={
            "strategy_revision": "REV-1",
            "manifest_revision": "MANIFEST-1",
            "holdout_dataset_id": "HOLDOUT-DATA-1",
            "holdout_dataset_sha256": "a" * 64,
            "holdout_artifact_id": "HOLDOUT-ART-1",
            "handoff_fingerprint": "c" * 64,
            "production_decision": False,
        },
    )


def _record():
    class Record:
        strategy_id = "SP2L-A"
        strategy_revision = "REV-1"
        manifest_revision = "MANIFEST-1"
        execution_semantics = "BAR_CLOSE_RESEARCH"
        dataset_id = "HOLDOUT-DATA-1"
        def validate(self):
            return None
    return Record()


def test_demo_forward_session_freezes_contract():
    result = DemoForwardSessionFactory().prepare(
        gate=type("R", (), {"gate": _gate()})(),
        source_record=_record(),
        session_id="FWD-SESSION-1",
        forward_dataset_id="FWD-DATA-1",
        forward_dataset_artifact_id="FWD-ART-1",
        forward_dataset_content_sha256="b" * 64,
    )
    session = result.session
    assert result.ready
    assert session.strategy_revision == "REV-1"
    assert session.manifest_revision == "MANIFEST-1"
    assert session.production_decision is False
    assert session.handoff_fingerprint == "c" * 64
    assert session.post_holdout_tuning is False
    session.validate()


def test_demo_forward_session_rejects_non_pass_gate():
    gate = GateResult(
        name="FRESH_HOLDOUT_TO_FORWARD",
        status=GateStatus.FAIL,
        evidence="",
        details={},
    )
    with pytest.raises(ForwardSessionError, match="Gate PASS"):
        DemoForwardSessionFactory().prepare(
            gate=type("R", (), {"gate": gate})(),
            source_record=_record(),
            session_id="FWD-SESSION-1",
            forward_dataset_id="FWD-DATA-1",
            forward_dataset_artifact_id="FWD-ART-1",
            forward_dataset_content_sha256="b" * 64,
        )


def test_demo_forward_session_rejects_post_holdout_tuning():
    with pytest.raises(ForwardSessionError, match="post-holdout"):
        DemoForwardSessionFactory().prepare(
            gate=type("R", (), {"gate": _gate()})(),
            source_record=_record(),
            session_id="FWD-SESSION-1",
            forward_dataset_id="FWD-DATA-1",
            forward_dataset_artifact_id="FWD-ART-1",
            forward_dataset_content_sha256="b" * 64,
            post_holdout_tuning=True,
        )


def test_demo_forward_session_rejects_reused_forward_dataset():
    with pytest.raises(ForwardSessionError, match="must differ"):
        DemoForwardSessionFactory().prepare(
            gate=type("R", (), {"gate": _gate()})(),
            source_record=_record(),
            session_id="FWD-SESSION-1",
            forward_dataset_id="HOLDOUT-DATA-1",
            forward_dataset_artifact_id="FWD-ART-1",
            forward_dataset_content_sha256="b" * 64,
        )


def test_demo_forward_session_is_deterministic():
    kwargs = dict(
        gate=type("R", (), {"gate": _gate()})(),
        source_record=_record(),
        session_id="FWD-SESSION-1",
        forward_dataset_id="FWD-DATA-1",
        forward_dataset_artifact_id="FWD-ART-1",
        forward_dataset_content_sha256=hashlib.sha256(b"forward").hexdigest(),
    )
    a = DemoForwardSessionFactory().prepare(**kwargs).session
    b = DemoForwardSessionFactory().prepare(**kwargs).session
    assert a == b


def test_demo_forward_session_rejects_missing_handoff_fingerprint(tmp_path):
    gate = _gate()
    gate.details.pop("handoff_fingerprint")
    with pytest.raises(ForwardSessionError, match="handoff fingerprint"):
        DemoForwardSessionFactory().prepare(
            gate=type("R", (), {"gate": gate})(),
            source_record=_record(),
            session_id="FWD-SESSION-1",
            forward_dataset_id="FWD-DATA-1",
            forward_dataset_artifact_id="FWD-ART-1",
            forward_dataset_content_sha256="b" * 64,
        )
