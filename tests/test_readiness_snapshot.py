from dataclasses import replace

import pytest

from strategy_factory.models import StrategyPassport
from strategy_factory.snapshot import build_readiness_snapshot, manifest_fingerprint
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.source_ledger import SourceResolutionLedger


def passport(manifest):
    return StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="GEOMETRY-PENDING",
        code_revision="CODE-PENDING",
        data_revision="DATA-PENDING",
        execution_model="TICK_FEASIBLE_RESEARCH_ONLY",
        parameter_set={"canonical": False},
    )


def test_snapshot_is_deterministic():
    manifest = build_sp2l_research_manifest()
    ledger = SourceResolutionLedger()
    a = build_readiness_snapshot(manifest, passport(manifest), ledger)
    b = build_readiness_snapshot(manifest, passport(manifest), ledger)

    assert a.as_dict() == b.as_dict()
    assert len(a.fingerprint) == 64
    assert len(manifest_fingerprint(manifest)) == 64


def test_snapshot_is_blocked_and_auditable():
    manifest = build_sp2l_research_manifest()
    snap = build_readiness_snapshot(manifest, passport(manifest), SourceResolutionLedger())

    assert snap.source_readiness["status"] == "BLOCKED"
    assert snap.passport_eligibility["canonical_strategy"] == "NOT_ELIGIBLE"
    assert snap.passport_eligibility["production"] == "NOT_ELIGIBLE"
    assert snap.source_readiness["missing_questions"] == 18


def test_snapshot_fingerprint_detects_tampering():
    manifest = build_sp2l_research_manifest()
    snap = build_readiness_snapshot(manifest, passport(manifest), SourceResolutionLedger())
    tampered = replace(snap, fingerprint="0" * 64)

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        tampered.validate()


def test_snapshot_changes_when_manifest_changes():
    manifest = build_sp2l_research_manifest()
    snap_a = build_readiness_snapshot(manifest, passport(manifest), SourceResolutionLedger())

    manifest.revision = "SOURCE-LEDGER-TEST-CHANGE"
    snap_b = build_readiness_snapshot(manifest, passport(manifest), SourceResolutionLedger())

    assert snap_a.manifest_fingerprint != snap_b.manifest_fingerprint
    assert snap_a.fingerprint != snap_b.fingerprint
