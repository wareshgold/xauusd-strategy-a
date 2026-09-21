"""Deterministic aggregation tests for the SP2L report engine.

These tests do not connect to MT5 or Telegram. They validate pure
aggregation behavior over fixture journal rows only.
"""

import json
from datetime import datetime, timezone

from scripts.live_report_engine import (
    ReportConfig,
    build_report,
    classify_signals,
    load_report_config,
    performance_metrics,
    report_to_json,
)

START = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 21, 0, 0, tzinfo=timezone.utc)
GENERATED = "2026-09-20T12:00:00+00:00"


def signal(sid: str, ts: str, status: str = "APPROVED") -> dict:
    return {
        "signal_id": sid,
        "status": status,
        "direction": "BUY",
        "timestamp_utc": ts,
        "recorded_at_utc": ts,
        "symbol": "XAUUSD.ecn",
    }


def trade(sid: str, ts: str, status: str, result: str | None = None, r: float | None = None) -> dict:
    row = {
        "signal_id": sid,
        "status": status,
        "direction": "BUY",
        "recorded_at_utc": ts,
        "symbol": "XAUUSD.ecn",
    }
    if result is not None:
        row["result"] = result
    if r is not None:
        row["r_multiple"] = r
    return row


def test_daily_aggregation_counts_win_loss_ambiguous():
    signals = [
        signal("S1", "2026-09-16T14:00:00+00:00"),
        signal("S2", "2026-09-16T15:00:00+00:00"),
        signal("S3", "2026-09-16T16:00:00+00:00"),
    ]
    trades = [
        trade("S1", "2026-09-16T14:30:00+00:00", "CLOSED", "WIN", 2.0),
        trade("S2", "2026-09-16T15:30:00+00:00", "CLOSED", "LOSS", -1.0),
        trade("S3", "2026-09-16T16:30:00+00:00", "DRY_RUN"),
    ]
    report = build_report(
        "daily", START, END, GENERATED, signals, trades,
        ReportConfig(pip_size=0.1),
    )
    assert report["signals"] == {
        "total": 3, "win": 1, "loss": 1, "ambiguous": 1, "duplicates_rejected": 0,
    }
    assert report["performance"]["net_r"] == 1.0
    assert report["performance"]["profit_factor"] == 2.0
    assert report["performance"]["win_rate_pct"] == 50.0
    assert report["execution"]["closed_trades"] == 2
    assert report["execution"]["dry_run_trades"] == 1
    assert report["execution"]["broker_reconciliation_status"] == "PARTIAL"


def test_weekly_aggregation_includes_daily_breakdown_and_trade_list():
    signals = [
        signal("S1", "2026-09-15T14:00:00+00:00"),
        signal("S2", "2026-09-16T14:00:00+00:00"),
    ]
    trades = [
        trade("S1", "2026-09-15T14:30:00+00:00", "CLOSED", "WIN", 3.0),
        trade("S2", "2026-09-16T14:30:00+00:00", "CLOSED", "LOSS", -1.0),
    ]
    report = build_report(
        "weekly", START, END, GENERATED, signals, trades,
        ReportConfig(pip_size=0.1),
    )
    assert report["report_type"] == "weekly"
    assert report["signals"]["total"] == 2
    assert report["performance"]["net_r"] == 2.0
    dates = [row["date"] for row in report["daily_breakdown"]["rows"]]
    assert dates == ["2026-09-15", "2026-09-16"]
    summary = report["trade_list_summary"]
    assert [row["signal_id"] for row in summary] == ["S1", "S2"]
    assert summary[0]["result"] == "WIN"
    assert summary[1]["result"] == "LOSS"


def test_monthly_aggregation_includes_weekly_breakdown_and_equity():
    signals = [signal("S1", "2026-09-15T14:00:00+00:00"), signal("S2", "2026-09-22T14:00:00+00:00")]
    trades = [
        trade("S1", "2026-09-15T14:30:00+00:00", "CLOSED", "WIN", 1.0),
        trade("S2", "2026-09-22T14:30:00+00:00", "CLOSED", "LOSS", -2.0),
    ]
    report = build_report(
        "monthly", datetime(2026, 9, 1, tzinfo=timezone.utc), datetime(2026, 10, 1, tzinfo=timezone.utc),
        GENERATED, signals, trades, ReportConfig(),
    )
    assert report["signals"]["total"] == 2
    assert report["performance"]["net_r"] == -1.0
    weeks = [row["week"] for row in report["weekly_breakdown"]["rows"]]
    assert weeks == ["2026-W38", "2026-W39"]
    assert report["equity_summary"]["equity_end_r"] == -1.0
    assert report["equity_summary"]["max_drawdown_r"] == 2.0


def test_ambiguous_covers_unresolved_journal_state():
    # CLOSED with non-WIN/LOSS result, open trade, and signal without trades.
    signals = [signal("S1", "2026-09-16T14:00:00+00:00"), signal("S2", "2026-09-16T15:00:00+00:00")]
    trades = [
        trade("S1", "2026-09-16T14:30:00+00:00", "CLOSED", "BREAKEVEN", 0.0),
        trade("S2", "2026-09-16T15:30:00+00:00", "OPEN"),
    ]
    signals.append(signal("S3", "2026-09-16T16:00:00+00:00"))
    counts = classify_signals(signals, trades)
    assert counts["ambiguous"] == 3
    assert counts["win"] == 0 and counts["loss"] == 0


def test_empty_journal_case_is_deterministic_and_null_safe():
    report = build_report("daily", START, END, GENERATED, [], [], ReportConfig())
    assert report["signals"] == {
        "total": 0, "win": 0, "loss": 0, "ambiguous": 0, "duplicates_rejected": 0,
    }
    assert report["performance"]["net_r"] == 0.0
    assert report["performance"]["profit_factor"] is None
    assert report["performance"]["win_rate_pct"] is None
    assert report["performance"]["net_pips"] is None
    assert report["performance"]["pips_basis"] == "NOT_CONFIGURED"
    assert report["performance"]["max_drawdown_r"] == 0.0
    assert report["execution"]["open_trades"] == 0
    assert report["execution"]["closed_trades"] == 0
    assert report["execution"]["broker_reconciliation_status"] == "NO_DATA"


def test_deterministic_output_ignores_input_order_and_float_noise():
    signals = [signal("S1", "2026-09-16T14:00:00+00:00"), signal("S2", "2026-09-17T14:00:00+00:00")]
    trades = [
        trade("S1", "2026-09-16T14:30:00+00:00", "CLOSED", "WIN", 1.5),
        trade("S2", "2026-09-17T14:30:00+00:00", "CLOSED", "LOSS", -0.5),
    ]
    config = ReportConfig(pip_size=0.1)
    first = build_report("weekly", START, END, GENERATED, signals, trades, config)
    second = build_report("weekly", START, END, GENERATED, list(reversed(signals)), list(reversed(trades)), config)
    assert report_to_json(first) == report_to_json(second)


def test_net_pips_requires_explicit_pip_size():
    closed = [
        {
            "signal_id": "S1", "status": "CLOSED", "result": "WIN", "direction": "BUY",
            "signal_entry": 4370.0, "broker_price": 4372.0, "r_multiple": 2.0,
            "recorded_at_utc": "2026-09-16T14:30:00+00:00",
        }
    ]
    without = performance_metrics(closed, pip_size=None)
    assert without["net_pips"] is None
    assert without["pips_basis"] == "NOT_CONFIGURED"
    with_pip = performance_metrics(closed, pip_size=0.1)
    assert with_pip["net_pips"] == 20.0
    assert with_pip["pips_basis"] == "EXPLICIT_PIP_SIZE"


def test_config_echoes_live_trading_and_geometry_status():
    config = load_report_config({
        "LIVE_TRADING_ENABLE": "false",
        "SP2L_GEOMETRY_STATUS": "UNRESOLVED_FROZEN_GEOMETRY_GATE",
        "REPORT_PIP_SIZE": "0.1",
    })
    assert config.live_trading_enabled is False
    assert config.geometry_status == "UNRESOLVED_FROZEN_GEOMETRY_GATE"
    assert config.pip_size == 0.1


def test_json_serialization_is_sorted_and_stable():
    report = build_report("daily", START, END, GENERATED, [], [], ReportConfig())
    text = report_to_json(report)
    assert json.loads(text) == report
    assert text == report_to_json(build_report("daily", START, END, GENERATED, [], [], ReportConfig()))
