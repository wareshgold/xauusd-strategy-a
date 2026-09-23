"""Tests for the weekly backtest artifact -> report-journal conversion.

Offline only: builds a synthetic author-replica source artifact and
validates conversion rules, engine compatibility, and determinism.
"""

import json
from pathlib import Path

from scripts.backtest_weekly_journal import main as convert_main
from scripts.live_report_engine import ReportConfig, build_report
from scripts.telegram_client import telegram_delivery_status

SYNTHETIC_SOURCE = {
    "research_only": True,
    "week_start_utc": "2026-09-14T00:00:00+00:00",
    "week_end_utc": "2026-09-18T23:59:59+00:00",
    "signals": [
        {
            "signal_time_utc": "2026-09-14T01:46:00+00:00",
            "date_utc": "2026-09-14",
            "direction": "BUY",
            "entry": 4336.78,
            "sl": 4333.62,
            "tp": 4339.94,
            "risk": 3.16,
            "outcome": "WIN",
            "R": 1.0,
            "exit_time_utc": "2026-09-14T02:00:00+00:00",
            "exit_price": 4339.94,
            "reason": "TP",
        },
        {
            "signal_time_utc": "2026-09-15T10:00:00+00:00",
            "date_utc": "2026-09-15",
            "direction": "SELL",
            "entry": 4340.0,
            "sl": 4342.0,
            "tp": 4338.0,
            "risk": 2.0,
            "outcome": "LOSS",
            "R": -1.0,
            "exit_time_utc": "2026-09-15T10:30:00+00:00",
            "exit_price": 4342.0,
            "reason": "SL",
        },
        {
            "signal_time_utc": "2026-09-14T08:25:00+00:00",
            "date_utc": "2026-09-14",
            "direction": "SELL",
            "entry": 4328.18,
            "sl": 4330.25,
            "tp": 4326.11,
            "risk": 2.07,
            "outcome": "AMBIGUOUS",
            "R": None,
            "exit_time_utc": "2026-09-14T08:30:00+00:00",
            "exit_price": "",
            "reason": "SL_AND_TP_SAME_BAR",
        },
    ],
    "summary": {"wins": 1, "losses": 1, "ambiguous": 1, "open_or_unresolved": 0, "total_R": 0, "profit_factor": 1.0},
}


def convert(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "source.json"
    source.write_text(json.dumps(SYNTHETIC_SOURCE), encoding="utf-8")
    journal_dir = tmp_path / "journal_backtest"
    code = convert_main([
        "--source", str(source),
        "--journal-dir", str(journal_dir),
        "--trade-journal-out", str(tmp_path / "trade_journal.json"),
        "--validation-out", str(tmp_path / "validation.json"),
        "--pip-size", "0.1",
    ])
    return code, journal_dir, json.loads((tmp_path / "validation.json").read_text(encoding="utf-8"))


def test_conversion_rows_and_required_fields(tmp_path):
    code, journal_dir, validation = convert(tmp_path)
    assert code == 0
    trades = [json.loads(line) for line in (journal_dir / "trades.jsonl").read_text(encoding="utf-8").splitlines()]
    signals = [json.loads(line) for line in (journal_dir / "signals.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(trades) == len(signals) == 3

    win_row = next(t for t in trades if t["result"] == "WIN")
    assert win_row["status"] == "CLOSED"
    assert win_row["direction"] == "BUY"
    assert win_row["r_multiple"] == 1.0
    assert win_row["signal_entry"] == 4336.78
    assert win_row["sl"] == 4333.62 and win_row["tp"] == 4339.94
    assert win_row["exit_price"] == 4339.94
    assert win_row["pips"] == 31.6  # (4339.94-4336.78)/0.1, explicit pip size
    assert win_row["holding_minutes"] == 14.0
    assert win_row["closed_at_utc"] == "2026-09-14T02:00:00+00:00"

    loss_row = next(t for t in trades if t["result"] == "LOSS")
    assert loss_row["pips"] == -20.0
    assert loss_row["holding_minutes"] == 30.0

    ambig_row = next(t for t in trades if t["result"] is None)
    assert ambig_row["status"] == "CLOSED"
    assert ambig_row["r_multiple"] is None
    assert ambig_row["exit_price"] is None
    assert ambig_row["pips"] is None  # never invented for unresolved outcome
    assert ambig_row["holding_minutes"] == 5.0

    trade_journal = json.loads((tmp_path / "trade_journal.json").read_text(encoding="utf-8"))
    required = {
        "signal_timestamp_utc", "direction", "entry", "stop_loss", "take_profit",
        "exit_time_utc", "exit_price", "result", "pips", "r_multiple", "holding_minutes",
    }
    assert required <= set(trade_journal["trades"][0].keys())
    assert trade_journal["pips_basis"] == "EXPLICIT_PIP_SIZE"


def test_validation_reproduces_source_summary(tmp_path):
    code, _, validation = convert(tmp_path)
    assert code == 0
    assert validation["consistency_ok"] is True
    assert validation["signal_count"] == 3
    assert (validation["win"], validation["loss"], validation["ambiguous"]) == (1, 1, 1)
    assert validation["duplicate_signal_ids"] == []
    assert validation["duplicate_time_direction_entry"] == []
    # The same-bar AMBIGUOUS row is CLOSED with no determinate outcome:
    # counted as missing outcome, never resolved by invention.
    assert validation["missing_outcome"] == 1
    assert validation["closed_missing_exit_price"] == 1
    assert validation["open_or_unresolved"] == 0
    assert validation["recomputed_net_r"] == 0.0
    assert validation["recomputed_profit_factor"] == 1.0


def test_engine_consumes_converted_journal(tmp_path):
    _, journal_dir, _ = convert(tmp_path)
    report = build_report(
        "weekly",
        __import__("datetime").datetime(2026, 9, 14, tzinfo=__import__("datetime").timezone.utc),
        __import__("datetime").datetime(2026, 9, 19, tzinfo=__import__("datetime").timezone.utc),
        "2026-09-20T12:00:00+00:00",
        [json.loads(line) for line in (journal_dir / "signals.jsonl").read_text(encoding="utf-8").splitlines()],
        [json.loads(line) for line in (journal_dir / "trades.jsonl").read_text(encoding="utf-8").splitlines()],
        ReportConfig(pip_size=0.1, session_timezone="UTC"),
    )
    assert report["signals"] == {"total": 3, "win": 1, "loss": 1, "ambiguous": 1, "duplicates_rejected": 0}
    assert report["performance"]["net_r"] == 0.0
    assert report["performance"]["net_pips"] == 11.6  # 31.6 - 20.0 + 0 (ambiguous unresolved)
    assert report["execution"]["closed_trades"] == 3


def test_conversion_is_deterministic(tmp_path):
    code1, journal_dir_1, _ = convert(tmp_path / "run1")
    code2, journal_dir_2, _ = convert(tmp_path / "run2")
    assert code1 == code2 == 0
    for name in ("signals.jsonl", "trades.jsonl"):
        assert (journal_dir_1 / name).read_bytes() == (journal_dir_2 / name).read_bytes()


def test_telegram_destination_status_reports_mode(monkeypatch, tmp_path):
    # env={} is empty, but read_telegram_env falls back to config/telegram.json;
    # point that fallback at a missing file so the test stays machine-isolated.
    from scripts import telegram_client as _tc
    monkeypatch.setattr(_tc, "TELEGRAM_CONFIG", tmp_path / "missing.json")
    missing = telegram_delivery_status({})
    assert missing == {"bot_configured": False, "chat_configured": False, "mode": "MOCK"}
    full = telegram_delivery_status({"TELEGRAM_BOT_TOKEN": "x", "TELEGRAM_CHAT_ID": "y"})
    assert full == {"bot_configured": True, "chat_configured": True, "mode": "REAL"}
    partial = telegram_delivery_status({"TELEGRAM_BOT_TOKEN": "x"})
    assert partial["mode"] == "MOCK" and partial["chat_configured"] is False
