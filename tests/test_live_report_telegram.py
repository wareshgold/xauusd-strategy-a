"""Telegram report formatting and delivery-logging tests (offline).

These tests never touch the network (the shared client is monkeypatched or
credentials are absent). They validate the compact HTML template,
deterministic rendering, and the report_log record contract (timestamp,
type, response, success/failure).
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


def test_compact_weekly_template():
    text = format_report(weekly_report())
    assert text.startswith("📊 SP2L Weekly Report")
    assert "🗓 2026-09-14 → 2026-09-21 · America/New_York" in text
    assert "<b>Signals</b>" in text
    assert "Total <b>1</b> · ✅ 1 · ❌ 0 · ⚠️ 0" in text
    assert "Win rate: <b>100.00%</b>" in text
    assert "<b>Performance</b>" in text
    assert "Net R: <b>+2.00</b>" in text
    assert "Net Pips: <b>+20.00</b>" in text
    assert "Profit Factor: <b>—</b>" in text  # no losing trade -> undefined
    assert "Max Drawdown: 0.00 R" in text
    assert "<b>Daily</b>" in text
    assert "Tue 15 · 1W 0L 0A · +2.00R" in text
    assert "<b>Execution</b>" in text
    assert "Closed 1 · Open 0" in text
    assert "Reconciliation: RECONCILED" in text
    assert "🟡 Research mode — not a trading signal" in text
    assert "🟢 Live trading: OFF" in text
    assert "🧭 Geometry gate: UNRESOLVED_FROZEN_GEOMETRY_GATE" in text


def test_no_trade_dump_on_telegram():
    text = format_report(weekly_report())
    assert "Trade list" not in text
    assert "signal_id" not in text
    assert "S1 " not in text
    assert "r_multiple" not in text
    assert "pips=" not in text


def test_ambiguous_footnote_only_when_present():
    signals = [
        {"signal_id": "S1", "status": "APPROVED", "direction": "BUY",
         "timestamp_utc": "2026-09-15T14:00:00+00:00", "recorded_at_utc": "2026-09-15T14:00:00+00:00"},
    ]
    trades = [
        {"signal_id": "S1", "status": "CLOSED", "result": None, "direction": "BUY",
         "recorded_at_utc": "2026-09-15T14:30:00+00:00"},
    ]
    report = build_report(
        "weekly", START, END, GENERATED, signals, trades, ReportConfig(),
    )
    text = format_report(report)
    assert "⚠️ 1" in text
    assert "outcome unresolved in journal" in text


def test_pips_line_omitted_without_explicit_pip_size():
    report = build_report("weekly", START, END, GENERATED, [], [], ReportConfig())
    text = format_report(report)
    assert "Net Pips" not in text
    assert "Win rate: <b>—</b>" in text


def test_daily_template():
    report = build_report("daily", START, END, GENERATED, [], [], ReportConfig())
    text = format_report(report)
    assert text.startswith("📊 SP2L Daily Report")
    assert "<b>Daily</b>" not in text  # breakdown only on weekly/monthly
    assert "Closed 0 · Open 0" in text
    assert "Reconciliation: NO_DATA" in text


def test_monthly_template_has_weeks_and_equity():
    report = build_report(
        "monthly",
        datetime(2026, 9, 1, tzinfo=timezone.utc), datetime(2026, 10, 1, tzinfo=timezone.utc),
        GENERATED,
        [{"signal_id": "S1", "status": "APPROVED", "direction": "BUY",
          "timestamp_utc": "2026-09-15T14:00:00+00:00", "recorded_at_utc": "2026-09-15T14:00:00+00:00"}],
        [{"signal_id": "S1", "status": "CLOSED", "result": "WIN", "direction": "BUY",
          "r_multiple": 3.0, "recorded_at_utc": "2026-09-15T14:30:00+00:00"}],
        ReportConfig(),
    )
    text = format_report(report)
    assert text.startswith("📊 SP2L Monthly Report")
    assert "<b>Weeks</b>" in text
    assert "W38 · 1W 0L 0A · +3.00R" in text
    assert "<b>Equity (R)</b>" in text
    assert "End +3.00 · Peak 3.00 · Trough +0.00 · Max DD 0.00" in text


def test_dynamic_values_are_html_escaped():
    report = build_report(
        "daily", START, END, GENERATED, [], [],
        ReportConfig(geometry_status="UNRESOLVED<FROZEN>&GATE"),
    )
    text = format_report(report)
    assert "UNRESOLVED&lt;FROZEN&gt;&amp;GATE" in text


def test_formatting_is_deterministic():
    assert format_report(weekly_report()) == format_report(weekly_report())


def test_send_failure_is_logged(monkeypatch, tmp_path):
    from scripts.telegram_client import TelegramSendResult

    monkeypatch.setattr(live_journal, "REPORT_LOG", tmp_path / "report_log.jsonl")
    monkeypatch.setattr(
        "scripts.live_report_telegram.send_telegram_message",
        lambda text, **kwargs: TelegramSendResult(success=False, detail="EXCEPTION: timeout", response=None),
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
        lambda text, **kwargs: TelegramSendResult(
            success=True, detail="HTTP_200", response={"ok": True, "result": {"message_id": 42}},
        ),
    )
    record = send_report(
        "📊 SP2L Weekly Report",
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
        "📊 SP2L Weekly Report",
        report_type="weekly",
        period_start_utc=START.isoformat(),
        period_end_utc=END.isoformat(),
        period_label="weekly:2026-09-14",
        report_timestamp_utc=GENERATED,
        sent_at_utc="2026-09-20T12:00:05+00:00",
    )
    assert record["success"] is False
    assert record["telegram_status"] == "NOT_CONFIGURED"


def test_client_sends_parse_mode_when_requested(monkeypatch):
    """The report layer requests HTML parsing; plain text stays the default."""
    import json as json_module
    from types import SimpleNamespace

    from scripts import telegram_client

    captured = {}

    class _FakeResponse:
        status = 200

        def __init__(self, payload: bytes):
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return self._payload

    def fake_urlopen(request, timeout=None):
        captured["data"] = request.data
        return _FakeResponse(json_module.dumps({"ok": True}).encode("utf-8"))

    monkeypatch.setattr(telegram_client, "urlopen", fake_urlopen)

    result = telegram_client.send_telegram_message(
        "<b>hi</b>", bot_token="t", chat_id="c", parse_mode="HTML",
    )
    assert result.success is True
    assert b"parse_mode=HTML" in captured["data"]

    captured.clear()
    telegram_client.send_telegram_message("plain", bot_token="t", chat_id="c")
    assert b"parse_mode" not in captured["data"]
