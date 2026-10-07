from __future__ import annotations

from pathlib import Path

import pytest

from strategy_factory.mt5_reconciliation_adapter import (
    MT5ReconciliationAdapterError,
    as_factory_reconciliation_dict,
    build_existing_mt5_reconciliation,
    normalize_existing_reconciliation_report,
)


def report_fixture() -> dict:
    return {
        "symbol": "XAUUSD.ecn",
        "mt5_closed_position_count": 5,
        "common_positions": 4,
        "event_only_positions": [101],
        "mt5_only_positions": [202],
        "position_mismatches": [{"position_id": 303, "delta_mt5_minus_event": 0.02}],
        "account": {"server": "OtetGroup-MT5"},
    }


def test_normalizes_existing_report_without_strategy_logic():
    obs = normalize_existing_reconciliation_report(
        report_fixture(),
        reconciliation_id="REC-SYNTH-1",
    )

    assert obs.observed_positions == 5
    assert obs.matched_positions == 3
    assert obs.mismatched_positions == 3
    assert obs.broker_server == "OtetGroup-MT5"
    assert obs.symbol == "XAUUSD.ecn"


def test_factory_contract_shape_is_exact():
    obs = normalize_existing_reconciliation_report(
        report_fixture(),
        reconciliation_id="REC-SYNTH-2",
    )
    assert as_factory_reconciliation_dict(obs) == {
        "reconciliation_id": "REC-SYNTH-2",
        "broker_server": "OtetGroup-MT5",
        "symbol": "XAUUSD.ecn",
        "observed_positions": 5,
        "matched_positions": 3,
        "mismatched_positions": 3,
        "detail": obs.detail,
    }


def test_missing_report_field_fails_closed():
    report = report_fixture()
    del report["account"]

    with pytest.raises(MT5ReconciliationAdapterError, match="required fields"):
        normalize_existing_reconciliation_report(report, reconciliation_id="REC")


def test_invalid_pnl_mismatch_count_fails_closed():
    report = report_fixture()
    report["common_positions"] = 0

    with pytest.raises(MT5ReconciliationAdapterError, match="exceeds"):
        normalize_existing_reconciliation_report(report, reconciliation_id="REC")


def test_builder_uses_injected_existing_report_builder(tmp_path: Path):
    seen = {}

    def fake_builder(args):
        seen["symbol"] = args.symbol
        seen["magic"] = args.magic
        seen["event_file"] = args.event_file
        return report_fixture()

    obs = build_existing_mt5_reconciliation(
        event_file=tmp_path / "events.jsonl",
        symbol="XAUUSD.ecn",
        magic=26092201,
        reconciliation_id="REC-SYNTH-3",
        report_builder=fake_builder,
    )

    assert seen == {
        "symbol": "XAUUSD.ecn",
        "magic": 26092201,
        "event_file": tmp_path / "events.jsonl",
    }
    assert obs.mismatched_positions == 3
