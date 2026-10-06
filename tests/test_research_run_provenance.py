import pytest

from strategy_factory.datasets import DatasetArtifact, DatasetRegistry
from strategy_factory.evidence import EvidenceBundle, EvidenceLedger
from strategy_factory.models import GateStatus
from strategy_factory.metrics import ResearchMetrics
from strategy_factory.provenance import provenance_gate
from strategy_factory.runs import ResearchRunError, ResearchRunLedger
from strategy_factory.test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset
from strategy_factory.usage import DatasetUsageLedger


def make_dataset(role=DatasetRole.DEVELOPMENT, dataset_id="DATA-001", immutable=False):
    return TestDataset(
        dataset_id=dataset_id,
        role=role,
        data_revision="R1",
        start="2026-01-01T00:00:00Z",
        end="2026-02-01T00:00:00Z",
        source="RESEARCH_FIXTURE",
        immutable=immutable,
    )


def make_spec(dataset, test_id="TEST-001"):
    return HistoricalTestSpec(
        test_id=test_id,
        strategy_id="SP2L-A",
        strategy_revision="STRAT-001",
        dataset=dataset,
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
        parameters={"trail": 2, "activation": 10},
    )


VALID_METRICS = ResearchMetrics(
    trades=10,
    decisive_trades=10,
    wins=6,
    losses=4,
    ambiguous=0,
    win_rate=0.6,
    net_r=2.5,
    profit_factor=1.4,
    max_drawdown_r=1.2,
    gross_profit_r=6.0,
    gross_loss_r=-3.5,
)

def make_run():
    registry = DatasetRegistry()
    dataset = make_dataset()
    registry.register(dataset, "CONTENT-ABC")
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    run = runs.create(
        make_spec(dataset),
        manifest_revision="MANIFEST-001",
        run_id="RUN-001",
        observed_fingerprint="CONTENT-ABC",
        purpose="DEVELOPMENT",
    )
    return runs, run


def test_run_identity_is_deterministic():
    _, run_a = make_run()
    _, run_b = make_run()
    assert run_a.fingerprint == run_b.fingerprint
    assert run_a.as_dict() == run_b.as_dict()


def test_run_cannot_use_changed_dataset_content():
    registry = DatasetRegistry()
    dataset = make_dataset()
    registry.register(dataset, "CONTENT-ABC")
    runs = ResearchRunLedger(registry, DatasetUsageLedger(registry))
    with pytest.raises(Exception):
        runs.create(
            make_spec(dataset),
            manifest_revision="MANIFEST-001",
            run_id="RUN-001",
            observed_fingerprint="CONTENT-CHANGED",
        )


def test_run_id_cannot_change_provenance():
    runs, run = make_run()
    dataset = make_dataset(dataset_id="DATA-002")
    runs.registry.register(dataset, "CONTENT-XYZ")
    with pytest.raises(ResearchRunError):
        runs.create(
            make_spec(dataset),
            manifest_revision="MANIFEST-002",
            run_id="RUN-001",
            observed_fingerprint="CONTENT-XYZ",
        )
    assert runs.get("RUN-001") == run


def test_holdout_run_cannot_be_used_for_fitting():
    registry = DatasetRegistry()
    dataset = make_dataset(DatasetRole.FRESH_HOLDOUT, immutable=True)
    registry.register(dataset, "CONTENT-HOLDOUT")
    runs = ResearchRunLedger(registry, DatasetUsageLedger(registry))
    with pytest.raises(Exception):
        runs.create(
            make_spec(dataset),
            manifest_revision="MANIFEST-001",
            run_id="RUN-HOLDOUT",
            observed_fingerprint="CONTENT-HOLDOUT",
            purpose="OPTIMIZATION",
        )


def test_artifact_identity_is_carried_into_run():
    registry = DatasetRegistry()
    artifact = DatasetArtifact("ART-001", "data/dev.csv", "a" * 64, 100, "CSV")
    dataset = make_dataset()
    registry.register(dataset, "a" * 64, artifact=artifact)
    runs = ResearchRunLedger(registry, DatasetUsageLedger(registry))
    run = runs.create(
        make_spec(dataset),
        manifest_revision="MANIFEST-001",
        run_id="RUN-ART",
        observed_fingerprint="a" * 64,
        artifact=artifact,
    )
    assert run.artifact_id == "ART-001"


def test_evidence_requires_matching_run_provenance():
    runs, run = make_run()
    ledger = EvidenceLedger(runs)
    evidence = EvidenceBundle(
        evidence_id="EVID-001",
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        metrics=ResearchMetrics(
            trades=10, decisive_trades=10, wins=6, losses=4, ambiguous=0,
            win_rate=0.6, net_r=2.5, profit_factor=1.4, max_drawdown_r=1.2,
            gross_profit_r=6.0, gross_loss_r=-3.5,
        ),
        result={"source": "test"},
    )
    ledger.record(evidence)
    assert ledger.get("EVID-001") == evidence


def test_evidence_with_wrong_run_fingerprint_is_rejected():
    runs, run = make_run()
    ledger = EvidenceLedger(runs)
    evidence = EvidenceBundle(
        evidence_id="EVID-001",
        run_id=run.run_id,
        run_fingerprint="0" * 64,
        result_revision="RESULT-001",
        metrics=ResearchMetrics(
            trades=10, decisive_trades=10, wins=6, losses=4, ambiguous=0,
            win_rate=0.6, net_r=2.5, profit_factor=1.4, max_drawdown_r=1.2,
            gross_profit_r=6.0, gross_loss_r=-3.5,
        ),
        result={"source": "test"},
    )
    with pytest.raises(ResearchRunError):
        ledger.record(evidence)


def test_provenance_gate_blocks_missing_provenance():
    result = provenance_gate(run=None, evidence=None)
    assert result.status is GateStatus.BLOCKED


def test_provenance_gate_passes_exact_match():
    runs, run = make_run()
    evidence = EvidenceBundle(
        evidence_id="EVID-001",
        run_id=run.run_id,
        run_fingerprint=run.fingerprint,
        result_revision="RESULT-001",
        result={"trades": 10},
    )
    assert provenance_gate(run=run, evidence=evidence).status is GateStatus.PASS


def test_provenance_gate_fails_mismatch():
    runs, run = make_run()
    evidence = EvidenceBundle(
        evidence_id="EVID-001",
        run_id=run.run_id,
        run_fingerprint="f" * 64,
        result_revision="RESULT-001",
        result={"trades": 10},
    )
    assert provenance_gate(run=run, evidence=evidence).status is GateStatus.FAIL
