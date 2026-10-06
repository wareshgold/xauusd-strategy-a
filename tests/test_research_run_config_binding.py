from dataclasses import replace

import pytest

from strategy_factory.dashboard_config import ForwardConfig, ResearchConfig, build_config
from strategy_factory.dashboard_config_provenance import bind_dashboard_config
from strategy_factory.dashboard_config_provenance_ledger import DashboardConfigProvenanceLedger
from strategy_factory.datasets import DatasetRegistry
from strategy_factory.runs import ResearchRunLedger, ResearchRunError
from strategy_factory.test_contract import ExecutionSemantics, HistoricalTestSpec, TestDataset, DatasetRole
from strategy_factory.usage import DatasetUsageLedger
from strategy_factory.research_run_config_binding import (
    ResearchRunConfigBindingError,
    bind_research_run_config,
)
from strategy_factory.research_run_config_binding_ledger import (
    ResearchRunConfigBindingLedger,
    ResearchRunConfigBindingLedgerError,
)


def make_run():
    dataset = TestDataset(
        dataset_id="DATA-001", role=DatasetRole.DEVELOPMENT, data_revision="R1",
        start="2026-01-01T00:00:00Z", end="2026-02-01T00:00:00Z",
        source="TEST", immutable=False,
    )
    registry = DatasetRegistry()
    registry.register(dataset, "CONTENT-ABC")
    spec = HistoricalTestSpec(
        test_id="TEST-001", strategy_id="SP2L-A", strategy_revision="STRAT-001",
        dataset=dataset, execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
        parameters={"trail": 2},
    )
    runs = ResearchRunLedger(registry, DatasetUsageLedger(registry))
    run = runs.create(
        spec, manifest_revision="MANIFEST-001", run_id="RUN-001",
        observed_fingerprint="CONTENT-ABC", purpose="DEVELOPMENT",
    )
    return run


def make_provenance():
    config = build_config(
        revision="DASHBOARD-CONFIG-1",
        research=ResearchConfig(),
        forward=ForwardConfig(),
    )
    return bind_dashboard_config(config)


def test_binding_is_deterministic_and_exact():
    run = make_run()
    provenance = make_provenance()
    a = bind_research_run_config(run, provenance)
    b = bind_research_run_config(run, provenance)
    assert a == b
    assert a.run_fingerprint == run.fingerprint
    assert a.config_fingerprint == provenance.config_fingerprint
    a.validate()


def test_tampered_binding_is_rejected():
    binding = bind_research_run_config(make_run(), make_provenance())
    with pytest.raises(ResearchRunConfigBindingError, match="fingerprint mismatch"):
        replace(binding, config_fingerprint="other").validate()


def test_wrong_run_identity_is_rejected():
    run = make_run()
    binding = bind_research_run_config(run, make_provenance())
    other = replace(run, run_id="RUN-OTHER")
    with pytest.raises(ResearchRunConfigBindingLedgerError, match="does not match research run"):
        ResearchRunConfigBindingLedger().record(other, binding)


def test_ledger_is_idempotent():
    run = make_run()
    binding = bind_research_run_config(run, make_provenance())
    ledger = ResearchRunConfigBindingLedger()
    assert ledger.record(run, binding) == ledger.record(run, binding)


def test_ledger_rejects_conflicting_binding_for_run():
    run = make_run()
    first = bind_research_run_config(run, make_provenance())
    second_provenance = bind_dashboard_config(
        build_config(
            revision="DASHBOARD-CONFIG-2",
            research=ResearchConfig(p_gap_price=2.0),
            forward=ForwardConfig(),
        )
    )
    second = bind_research_run_config(run, second_provenance)
    ledger = ResearchRunConfigBindingLedger()
    ledger.record(run, first)
    with pytest.raises(ResearchRunConfigBindingLedgerError, match="conflicting"):
        ledger.record(run, second)


def test_ledger_can_require_registered_config_provenance():
    run = make_run()
    provenance = make_provenance()
    config_ledger = DashboardConfigProvenanceLedger()
    config_ledger.record(provenance)
    binding = bind_research_run_config(run, provenance)
    ledger = ResearchRunConfigBindingLedger(config_ledger)
    ledger.record(run, binding)
    assert ledger.get(run.run_id).binding == binding


def test_ledger_rejects_unregistered_config_provenance():
    run = make_run()
    provenance = make_provenance()
    binding = bind_research_run_config(run, provenance)
    ledger = ResearchRunConfigBindingLedger(DashboardConfigProvenanceLedger())
    with pytest.raises(ResearchRunConfigBindingLedgerError, match="not registered"):
        ledger.record(run, binding)


def test_ledger_rejects_tampered_config_provenance_reference():
    run = make_run()
    provenance = make_provenance()
    config_ledger = DashboardConfigProvenanceLedger()
    config_ledger.record(provenance)
    binding = bind_research_run_config(run, provenance)
    bad = replace(binding, config_provenance_fingerprint="0" * 64)
    ledger = ResearchRunConfigBindingLedger(config_ledger)
    with pytest.raises(ResearchRunConfigBindingLedgerError, match="fingerprint mismatch"):
        ledger.record(run, bad)
