from __future__ import annotations

from dataclasses import replace

import pytest

from strategy_factory.dashboard_config import (
    ForwardConfig,
    ResearchConfig,
    build_config,
)
from strategy_factory.dashboard_config_provenance import (
    DashboardConfigProvenanceError,
    bind_dashboard_config,
)
from strategy_factory.dashboard_config_provenance_ledger import (
    DashboardConfigProvenanceLedger,
    DashboardConfigProvenanceLedgerError,
)


def config():
    return build_config(
        revision="DASHBOARD-CONFIG-TEST-1",
        research=ResearchConfig(),
        forward=ForwardConfig(),
    )


def test_binding_is_deterministic_and_preserves_config_identity():
    cfg = config()
    a = bind_dashboard_config(cfg)
    b = bind_dashboard_config(cfg)

    assert a == b
    assert a.config_revision == cfg.revision
    assert a.config_fingerprint == cfg.fingerprint
    assert a.apply_mode == "STAGED_FORWARD_CONFIG"
    a.validate()


def test_invalid_config_is_rejected():
    cfg = replace(config(), fingerprint="tampered")
    with pytest.raises(DashboardConfigProvenanceError, match="invalid dashboard config"):
        bind_dashboard_config(cfg)


def test_tampered_provenance_is_rejected():
    provenance = bind_dashboard_config(config())
    with pytest.raises(DashboardConfigProvenanceError, match="fingerprint mismatch"):
        replace(provenance, config_fingerprint="other").validate()


def test_unsupported_apply_mode_is_rejected():
    provenance = bind_dashboard_config(config())
    bad = replace(provenance, apply_mode="LIVE_EXECUTION")
    with pytest.raises(DashboardConfigProvenanceError, match="fingerprint mismatch"):
        bad.validate()


def test_ledger_is_idempotent():
    ledger = DashboardConfigProvenanceLedger()
    provenance = bind_dashboard_config(config())

    first = ledger.record(provenance)
    second = ledger.record(provenance)

    assert first == second
    assert ledger.contains(provenance.config_revision)
    assert ledger.get(provenance.config_revision) == first


def test_ledger_rejects_conflicting_revision():
    ledger = DashboardConfigProvenanceLedger()
    first = bind_dashboard_config(config())
    second = bind_dashboard_config(
        build_config(
            revision=first.config_revision,
            research=ResearchConfig(p_gap_price=2.0),
            forward=ForwardConfig(),
        )
    )

    ledger.record(first)
    with pytest.raises(
        DashboardConfigProvenanceLedgerError,
        match="conflicting dashboard configuration provenance",
    ):
        ledger.record(second)


def test_ledger_rejects_tampered_entry():
    ledger = DashboardConfigProvenanceLedger()
    provenance = bind_dashboard_config(config())
    bad = replace(provenance, fingerprint="tampered")

    with pytest.raises(DashboardConfigProvenanceLedgerError, match="fingerprint mismatch"):
        ledger.record(bad)


def test_ledger_serialization_is_sorted_and_validated():
    ledger = DashboardConfigProvenanceLedger()
    ledger.record(bind_dashboard_config(config()))
    payload = ledger.as_dict()

    assert len(payload) == 1
    assert payload[0]["config_revision"] == "DASHBOARD-CONFIG-TEST-1"
    assert payload[0]["apply_mode"] == "STAGED_FORWARD_CONFIG"
