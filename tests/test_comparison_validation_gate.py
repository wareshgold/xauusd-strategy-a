from dataclasses import replace
import hashlib, json
import pytest

from strategy_factory.comparison_validation_gate import (
    ComparisonValidationGateStatus,
    evaluate_comparison_validation_gate,
)
from strategy_factory.multiple_comparison import adjust_p_values
from strategy_factory.research_comparison import ComparisonObservation, ResearchComparison
from strategy_factory.statistical_comparison_evidence import bind_statistical_comparison_evidence
from strategy_factory.statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger
from strategy_factory.statistical_comparison_governance import StatisticalComparisonUsageLedger


def comparison():
    base = ComparisonObservation("base", "r"*64, "b"*64, 10, .5, .2, None, .1, .3)
    cand = ComparisonObservation("candidate", "c"*64, "d"*64, 10, .6, .3, None, .2, .4)
    x = ResearchComparison("REV", "SP2L", "R1", "DEVELOPMENT", base, (cand,), 1, (.1,), (.1,), (None,), "")
    fp = hashlib.sha256(json.dumps(x._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return replace(x, fingerprint=fp)


def chain():
    c = comparison()
    a = adjust_p_values((.01,), method="HOLM")
    e = bind_statistical_comparison_evidence(c, a)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(e)
    return c, a, e, registry


def test_unified_gate_passes_registered_governed_evidence():
    c, a, e, registry = chain()
    result = evaluate_comparison_validation_gate(c, a, e, registry, StatisticalComparisonUsageLedger())
    assert result.status is ComparisonValidationGateStatus.PASS
    assert result.registered is True
    assert result.governed is True
    assert result.blocking_reasons == ()
    result.validate()


def test_unregistered_evidence_is_blocked():
    c = comparison()
    a = adjust_p_values((.01,), method="HOLM")
    e = bind_statistical_comparison_evidence(c, a)
    result = evaluate_comparison_validation_gate(c, a, e, StatisticalComparisonEvidenceLedger(), StatisticalComparisonUsageLedger())
    assert result.status is ComparisonValidationGateStatus.BLOCKED
    assert "STATISTICAL_COMPARISON_EVIDENCE_NOT_REGISTERED" in result.blocking_reasons


def test_tampered_evidence_fails_closed():
    c, a, e, registry = chain()
    bad = replace(e, fingerprint="0"*64)
    result = evaluate_comparison_validation_gate(c, a, bad, registry, StatisticalComparisonUsageLedger())
    assert result.status is ComparisonValidationGateStatus.FAIL
    assert result.governed is False


def test_validation_role_cannot_be_used_for_optimization():
    c, a, e, registry = chain()
    c2 = replace(c, dataset_role="UNTOUCHED_VALIDATION")
    fp = hashlib.sha256(json.dumps(c2._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    c2 = replace(c2, fingerprint=fp)
    e2 = bind_statistical_comparison_evidence(c2, a)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(e2)
    result = evaluate_comparison_validation_gate(
        c2, a, e2, registry, StatisticalComparisonUsageLedger(), purpose="OPTIMIZATION"
    )
    assert result.status is ComparisonValidationGateStatus.BLOCKED



def test_holdout_gate_blocks_mapping_only_pin_even_with_matching_record_identity():
    from types import SimpleNamespace
    from strategy_factory.dataset_manifest import DatasetManifest, DatasetManifestRegistry

    c, a, _, _ = chain()
    c2 = replace(c, dataset_role="FRESH_HOLDOUT")
    fp = hashlib.sha256(
        json.dumps(c2._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    c2 = replace(c2, fingerprint=fp)
    e2 = bind_statistical_comparison_evidence(c2, a)
    evidence_ledger = StatisticalComparisonEvidenceLedger()
    evidence_ledger.record(e2)

    manifest = DatasetManifest.create(
        manifest_revision="DATASET-MANIFEST-1",
        dataset_id="HOLDOUT-001",
        dataset_role="FRESH_HOLDOUT",
        data_revision="DATA-REV-001",
        dataset_fingerprint="a" * 64,
        immutable=True,
    )
    manifest_registry = DatasetManifestRegistry({manifest.dataset_id: manifest.fingerprint})
    manifest_registry.register(manifest)
    observations = (c2.baseline, *c2.candidates)
    records = {
        observation.run_id: SimpleNamespace(
            fingerprint=observation.research_record_fingerprint,
            dataset_role="FRESH_HOLDOUT",
            dataset_id=manifest.dataset_id,
            dataset_fingerprint=manifest.dataset_fingerprint,
            data_revision=manifest.data_revision,
            validate=lambda: None,
        )
        for observation in observations
    }
    class RecordLedger:
        def get(self, run_id):
            return records[run_id]

    result = evaluate_comparison_validation_gate(
        c2, a, e2, evidence_ledger, StatisticalComparisonUsageLedger(),
        research_record_ledger=RecordLedger(),
        dataset_manifest_registry=manifest_registry,
    )

    assert result.status is ComparisonValidationGateStatus.BLOCKED
    assert "DATASET_PIN_TRUST_ROOT_UNAUTHENTICATED" in result.blocking_reasons
    assert result.governed is False


def test_holdout_gate_rejects_caller_claimed_authenticated_registry():
    from types import SimpleNamespace

    c, a, _, _ = chain()
    c2 = replace(c, dataset_role="FRESH_HOLDOUT")
    fp = hashlib.sha256(
        json.dumps(c2._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    c2 = replace(c2, fingerprint=fp)
    e2 = bind_statistical_comparison_evidence(c2, a)
    evidence_ledger = StatisticalComparisonEvidenceLedger()
    evidence_ledger.record(e2)

    observations = (c2.baseline, *c2.candidates)
    records = {
        observation.run_id: SimpleNamespace(
            fingerprint=observation.research_record_fingerprint,
            dataset_role="FRESH_HOLDOUT",
            dataset_id="HOLDOUT-001",
            dataset_fingerprint="a" * 64,
            data_revision="DATA-REV-001",
            validate=lambda: None,
        )
        for observation in observations
    }
    class RecordLedger:
        def get(self, run_id):
            return records[run_id]

    class CallerClaimedTrustedRegistry:
        # A caller-controlled property is not an authenticated trust root.
        has_authenticated_external_trust_root = True
        validate_called = False

        def validate_record(self, record, expected_role):
            self.validate_called = True
            return None

    manifest_registry = CallerClaimedTrustedRegistry()
    result = evaluate_comparison_validation_gate(
        c2, a, e2, evidence_ledger, StatisticalComparisonUsageLedger(),
        research_record_ledger=RecordLedger(),
        dataset_manifest_registry=manifest_registry,
    )

    assert result.status is ComparisonValidationGateStatus.BLOCKED
    assert "DATASET_PIN_TRUST_ROOT_UNAUTHENTICATED" in result.blocking_reasons
    assert result.governed is False
    assert manifest_registry.validate_called is False


def test_self_declared_fresh_holdout_role_requires_record_provenance_ledger():
    c, a, _, _ = chain()
    # Re-fingerprint a caller-relabelled DEVELOPMENT comparison. Internal
    # hash consistency alone must not authenticate the claimed holdout role.
    c2 = replace(c, dataset_role="FRESH_HOLDOUT")
    fp = hashlib.sha256(
        json.dumps(c2._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    c2 = replace(c2, fingerprint=fp)
    e2 = bind_statistical_comparison_evidence(c2, a)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(e2)

    result = evaluate_comparison_validation_gate(
        c2, a, e2, registry, StatisticalComparisonUsageLedger()
    )

    assert result.status is ComparisonValidationGateStatus.BLOCKED
    assert "RESEARCH_RECORD_PROVENANCE_LEDGER_REQUIRED" in result.blocking_reasons
    assert result.governed is False


def test_holdout_role_with_empty_record_ledger_is_blocked():
    from strategy_factory.research_record import ResearchRecordLedger

    c, a, _, registry = chain()
    c2 = replace(c, dataset_role="UNTOUCHED_VALIDATION")
    fp = hashlib.sha256(
        json.dumps(c2._fingerprint_payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    c2 = replace(c2, fingerprint=fp)
    e2 = bind_statistical_comparison_evidence(c2, a)
    registry = StatisticalComparisonEvidenceLedger()
    registry.record(e2)

    result = evaluate_comparison_validation_gate(
        c2, a, e2, registry, StatisticalComparisonUsageLedger(),
        research_record_ledger=ResearchRecordLedger(),
    )

    assert result.status is ComparisonValidationGateStatus.BLOCKED
    assert any(
        reason.startswith("RESEARCH_RECORD_PROVENANCE_UNRESOLVED:")
        for reason in result.blocking_reasons
    )
    assert result.governed is False
