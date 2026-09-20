"""Telegram report formatting and delivery-logging tests (offline).

These tests never touch the network: the shared Telegram client is
monkeypatched. They validate templates, deterministic rendering, and the
report_log record contract (timestamp, type, response, success/failure).
"""

from datetime import datetime, timezone

import scripts.live_journal as live_journal
from scripts.live_report_engine import ReportConfig, build_report
from scripts.live_report_telegram import format_report, report_text_sha256, send_report

START = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 21, 0, 0, tzinfo=timezone.utc)
GENERATED = "2026-09-20T12:00:00+00:00"


def weekly_report() -> dict:
    signals = [
        {"signal_id": "S1", "status": "APPROVED", "direction": "BUY",
         "timestamp_utc": "2026-09-15T14:00:00+00:00", "recorded_at_utc": "2026-09-15T14:00:00+00:00"},
    ]
    trades = [
        {"signal_id": "S1", "status": "CLOSED", "result": "WIN", "direction": "BUY",
         "r_multiple": 2.0, "signal_entry": 4370.0, "broker_price": 4372.0, "broker_net": 20.0,
         "recorded_at_utc": "2026-09-15T14:30:00+00:00"},
    ]
    return build_report(
        "weekly", START, END, GENERATED, signals, trades, ReportConfig(pip_size=0.1),
    )


def test_report_template_contains_required_sections():
    text = format_report(weekly_report())
    assert text.startswith("SP2L Weekly Report — RESEARCH")
    assert "Trading Period:" in text
    assert "Signals:" in text
    assert "- Total signals: 1" in text
    assert "- WIN count: 1" in text
    assert "- LOSS count: 0" in text
    assert "- AMBIGUOUS count: 0" in text
    assert "- Net pips: 20.00 (basis: EXPLICIT_PIP_SIZE)" in text
    assert "- Net R: 2.0000" in text
    assert "- Max drawdown: 0.0000 R" in text
    assert "- Open trades: 0" in text
    assert "- Closed trades: 1" in text
    assert "- Broker reconciliation status: RECONCILED" in text
    assert "- Geometry status: UNRESOLVED_FROZEN_GEOMETRY_GATE" in text
    assert "- Live trading status: DISABLED (LIVE_TRADING_ENABLE=false)" in text
    assert "Daily breakdown" in text
    assert "Trade list summary:" in text


def test_daily_template_contains_date_line():
    report = build_report("daily", START, END, GENERATED, [], [], ReportConfig())
    text = format_report(report)
    assert text.startswith("SP2L Daily Report — RESEARCH")
    assert text.splitlines()[1].startswith("Date: 2026-09-14")


def test_formatting_is_deterministic():
    assert format_report(weekly_report()) == format_report(weekly_report())


def test_missing_pip_size_renders_n_a_not_invented():
    report = build_report("weekly", START, END, GENERATED, [], [], ReportConfig())
    text = format_report(report)
    assert "- Net pips: n/a (pip size not configured)" in text


def test_send_failure_is_logged(monkeypatch, tmp_path):
    from scripts.telegram_client import TelegramSendResult

    monkeypatch.setattr(live_journal, "REPORT_LOG", tmp_path / "report_log.jsonl")
    monkeypatch.setattr(
        "scripts.live_report_telegram.send_telegram_message",
        lambda text: TelegramSendResult(success=False, detail="EXCEPTION: timeout", response=None),
    )
    record = send_report(
        format_report(weekly_report()),
        report_type="weekly",
        period_start_utc=START.isoformat(),
        period_end_utc=END.isoformat(),
        period_label="weekly:2026-09-14",
        report_timestamp_utc=GENERATED,
        sent_at_utc="2026-09-20T12:00:05+00:00",
    )
    assert record["success"] is False
    assert record["telegram_status"] == "EXCEPTION: timeout"
    logged = live_journal.read_jsonl(tmp_path / "report_log.jsonl")
    assert len(logged) == 1
    assert logged[0]["report_type"] == "weekly"
    assert logged[0]["success"] is False
    assert logged[0]["report_timestamp_utc"] == GENERATED
    assert logged[0]["report_text_sha256"] == report_text_sha256(format_report(weekly_report()))


def test_send_success_is_logged_with_response(monkeypatch, tmp_path):
    from scripts.telegram_client import TelegramSendResult

    monkeypatch.setattr(live_journal, "REPORT_LOG", tmp_path / "report_log.jsonl")
    monkeypatch.setattr(
        "scripts.live_report_telegram.send_telegram_message",
        lambda text: TelegramSendResult(
            success=True, detail="HTTP_200", response={"ok": True, "result": {"message_id": 42}},
        ),
    )
    record = send_report(
        "SP2L Weekly Report — RESEARCH",
        report_type="weekly",
        period_start_utc=START.isoformat(),
        period_end_utc=END.isoformat(),
        period_label="weekly:2026-09-14",
        report_timestamp_utc=GENERATED,
        sent_at_utc="2026-09-20T12:00:05+00:00",
    )
    assert record["success"] is True
    assert record["telegram_response"]["result"]["message_id"] == 42
    logged = live_journal.read_jsonl(tmp_path / "report_log.jsonl")
    assert logged[0]["telegram_status"] == "HTTP_200"


def test_unconfigured_credentials_log_failure(monkeypatch, tmp_path):
    from scripts import telegram_client

    monkeypatch.setattr(live_journal, "REPORT_LOG", tmp_path / "report_log.jsonl")
    monkeypatch.setattr(
        "scripts.live_report_telegram.send_telegram_message",
        telegram_client.send_telegram_message,
    )
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    record = send_report(
        "SP2L Weekly Report — RESEARCH",
        report_type="weekly",
        period_start_utc=START.isoformat(),
        period_end_utc=END.isoformat(),
        period_label="weekly:2026-09-14",
        report_timestamp_utc=GENERATED,
        sent_at_utc="2026-09-20T12:00:05+00:00",
    )
    assert record["success"] is False
    assert record["telegram_status"] == "NOT_CONFIGURED"
