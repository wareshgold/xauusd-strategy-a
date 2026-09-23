"""Offline tests: symbol probe mapping, deterministic simulator, session
report aggregation, and the Strategy A adapter activation gates."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.live_signal_simulator as sim
import scripts.live_session_report as session_report
import scripts.mt5_symbol_probe as probe
import scripts.strategy_a_signal_adapter as adapter
import scripts.telegram_diagnostic as tg_diag


# ---------------------------------------------------------------------------
# Symbol probe (pure mapping logic — no MT5 connection)
# ---------------------------------------------------------------------------


class FakeInfo:
    def __init__(self, name, trade_mode, path="Metals"):
        self.name = name
        self.trade_mode = trade_mode
        self.path = path
        self.visible = True
        self.digits = 2
        self.trade_stops_level = 0
        self.volume_min = 0.01
        self.volume_step = 0.01
        self.volume_max = 100.0
        self.trade_tick_value = 1.0
        self.trade_tick_size = 0.01
        self.trade_contract_size = 100.0
        self.description = name


class FakeMt5:
    """Minimal MT5 stub: one openable, one CLOSEONLY, one non-gold symbol."""

    def __init__(self):
        self.symbols = [
            SimpleNamespace(name="XAUUSD.ecn"),
            SimpleNamespace(name="XAUUSD.pro"),
            SimpleNamespace(name="EURUSD.ecn"),
        ]
        self.infos = {
            # Raw MT5 SYMBOL_TRADE_MODE_* codes: 3=CLOSEONLY, 4=FULL.
            "XAUUSD.ecn": FakeInfo("XAUUSD.ecn", 3),  # CLOSEONLY
            "XAUUSD.pro": FakeInfo("XAUUSD.pro", 4),  # FULL
            "EURUSD.ecn": FakeInfo("EURUSD.ecn", 4),
        }

    def symbols_get(self):
        return self.symbols

    def symbol_select(self, name, enable):
        return name in self.infos

    def symbol_info(self, name):
        return self.infos.get(name)


def test_probe_maps_trade_modes_and_openable_flag():
    rows = probe.probe_symbols(FakeMt5())
    by_name = {r["name"]: r for r in rows}
    assert by_name["XAUUSD.ecn"]["trade_mode_name"] == "CLOSEONLY"
    assert by_name["XAUUSD.ecn"]["openable"] is False
    assert by_name["XAUUSD.pro"]["trade_mode_name"] == "FULL"
    assert by_name["XAUUSD.pro"]["openable"] is True
    # Non-gold symbols are filtered out entirely.
    assert "EURUSD.ecn" not in by_name
    # Openable symbols sort first.
    assert rows[0]["name"] == "XAUUSD.pro"


# ---------------------------------------------------------------------------
# Deterministic simulator
# ---------------------------------------------------------------------------


def test_simulator_is_deterministic_per_seed():
    a = sim.simulate_signal(42, symbol="XAUUSD.ecn")
    b = sim.simulate_signal(42, symbol="XAUUSD.ecn")
    assert a == b
    c = sim.simulate_signal(43, symbol="XAUUSD.ecn")
    assert c["signal_id"] != a["signal_id"]


def test_simulator_payload_passes_gateway_shape():
    payload = sim.simulate_signal(1)
    for key in ("direction", "symbol", "entry", "sl", "tp", "volume", "signal_id", "source", "status"):
        assert key in payload
    assert payload["status"] == "APPROVED"
    assert payload["source"] == "SIMULATOR_TEST_ONLY"
    assert payload["sl"] != payload["entry"] != payload["tp"]


def test_verify_chain_against_tmp_journal(tmp_path):
    journal = tmp_path / "journal"
    processed = tmp_path / "processed"
    journal.mkdir()
    processed.mkdir()
    (journal / "signals.jsonl").write_text(
        '{"signal_id": "SIM-X", "status": "APPROVED"}\n', encoding="utf-8"
    )
    (journal / "trades.jsonl").write_text(
        '{"signal_id": "SIM-X", "status": "DRY_RUN", "symbol": "XAUUSD.ecn", '
        '"execution_json": {"request": {"symbol": "XAUUSD.ecn"}}}\n',
        encoding="utf-8",
    )
    (processed / "20260921T000000Z_approved_signal.json").write_text("{}", encoding="utf-8")

    result = sim.verify_chain("SIM-X", journal_dir=journal, processed_dir=processed)
    assert result["chain_ok"] is True
    assert all(result["checks"].values())


def test_verify_chain_reports_missing_trade(tmp_path):
    journal = tmp_path / "journal"
    journal.mkdir()
    (journal / "signals.jsonl").write_text(
        '{"signal_id": "SIM-Y", "status": "APPROVED"}\n', encoding="utf-8"
    )
    (journal / "trades.jsonl").write_text("", encoding="utf-8")
    result = sim.verify_chain("SIM-Y", journal_dir=journal, processed_dir=tmp_path)
    assert result["chain_ok"] is False
    assert result["checks"]["trade_recorded_dry_run"] is False


def test_explicit_signal_id_namespaces_without_changing_values():
    """The signal ID namespace never affects the seed-derived values."""
    base = sim.simulate_signal(7)
    named = sim.simulate_signal(7, signal_id="SIM-20260921T091500Z-0007")
    for key in ("direction", "entry", "sl", "tp", "volume", "status", "source"):
        assert named[key] == base[key]
    assert named["signal_id"] == "SIM-20260921T091500Z-0007"
    assert base["signal_id"] == sim.signal_id_for(7)


def test_signal_id_for_prefers_explicit_then_run_id():
    assert sim.signal_id_for(7, run_id="R1", explicit_id="CUSTOM-1") == "CUSTOM-1"
    assert sim.signal_id_for(7, run_id="R1") == "SIM-R1-0007"
    assert sim.signal_id_for(7).startswith("SIM-")


def test_repeated_runs_same_seed_get_distinct_ids(tmp_path, monkeypatch):
    """Acceptance: repeated deterministic test runs stay unique per run —
    without touching duplicate protection (values identical, IDs differ)."""
    first = sim.simulate_signal(7, signal_id=sim.signal_id_for(7, run_id="RUN-A"))
    second = sim.simulate_signal(7, signal_id=sim.signal_id_for(7, run_id="RUN-B"))
    assert first["signal_id"] != second["signal_id"]
    assert first["entry"] == second["entry"]  # deterministic values preserved


# ---------------------------------------------------------------------------
# Session report
# ---------------------------------------------------------------------------


def _write_journal(tmp_path, rows_by_file):
    for name, rows in rows_by_file.items():
        path = tmp_path / name
        path.write_text("".join(_jsonl(r) for r in rows), encoding="utf-8")


def _jsonl(row) -> str:
    import json

    return json.dumps(row) + "\n"


def test_session_stats_counts_statuses(tmp_path):
    _write_journal(tmp_path, {
        "signals.jsonl": [
            {"signal_id": "S1", "status": "APPROVED", "timestamp_utc": "2026-09-21T05:00:00+00:00"},
            {"signal_id": "S2", "status": "DUPLICATE_REJECTED", "timestamp_utc": "2026-09-21T05:01:00+00:00"},
        ],
        "trades.jsonl": [
            {"signal_id": "S1", "status": "DRY_RUN", "timestamp_utc": "2026-09-21T05:00:01+00:00"},
        ],
        "market_snapshots.jsonl": [
            {"bid": 4355.0, "ask": 4355.5, "time_utc": "2026-09-21T05:00:00+00:00"},
        ],
    })
    stats = session_report.collect_session_stats(
        signals_path=tmp_path / "signals.jsonl",
        trades_path=tmp_path / "trades.jsonl",
        snapshots_path=tmp_path / "market_snapshots.jsonl",
    )
    assert stats["signals_total"] == 2
    assert stats["approved"] == 1
    assert stats["duplicate_rejected"] == 1
    assert stats["dry_run"] == 1
    assert stats["last_tick"]["bid"] == 4355.0


def test_session_report_template_contains_safety_footer(tmp_path):
    stats = session_report.collect_session_stats(
        signals_path=tmp_path / "signals.jsonl",
        trades_path=tmp_path / "trades.jsonl",
        snapshots_path=tmp_path / "market_snapshots.jsonl",
    )
    text = session_report.format_session_report(
        stats, period_label="2026-09-21 → 2026-09-21 (UTC)", mode="DRY-RUN"
    )
    assert "SP2L Live Session Monitor" in text
    assert "Mode: DRY-RUN" in text
    assert "Live trading: OFF" in text
    assert "UNRESOLVED_FROZEN_GEOMETRY_GATE" in text
    assert "not a trading signal" in text


def test_week_start_is_monday_utc():
    # 2026-09-16 is a Wednesday -> week start must be Monday 2026-09-14.
    now = datetime(2026, 9, 16, 15, 30, tzinfo=timezone.utc)
    start = session_report._week_start_utc(now)
    assert start.weekday() == 0
    assert start.date().isoformat() == "2026-09-14"


# ---------------------------------------------------------------------------
# Strategy A adapter (prepared but inactive)
# ---------------------------------------------------------------------------


SCANNER_RECORD = {
    "direction": "long",
    "entry": 4355.0,
    "sl": 4345.0,
    "tp": 4371.0,
    "volume": 0.01,
    "signal_id": "SA-20260921-001",
    "source": "SCANNER_HUMAN_APPROVED",
    "status": "APPROVED",
}


def test_adapter_inactive_by_default(monkeypatch):
    monkeypatch.delenv("STRATEGY_A_ADAPTER_ENABLE", raising=False)
    monkeypatch.delenv("STRATEGY_A_ADAPTER_SOURCE", raising=False)
    state = adapter.adapter_state()
    assert state["adapter_active"] is False
    with pytest.raises(adapter.AdapterError, match="INACTIVE"):
        adapter.map_scanner_record(SCANNER_RECORD, symbol="XAUUSD.ecn")


def test_adapter_requires_both_activation_keys(monkeypatch):
    monkeypatch.setenv("STRATEGY_A_ADAPTER_ENABLE", "true")
    monkeypatch.delenv("STRATEGY_A_ADAPTER_SOURCE", raising=False)
    assert adapter.adapter_state()["adapter_active"] is False
    monkeypatch.setenv("STRATEGY_A_ADAPTER_SOURCE", "human_validation_gate")
    assert adapter.adapter_state()["adapter_active"] is True


def test_adapter_maps_approved_record_verbatim(monkeypatch):
    monkeypatch.setenv("STRATEGY_A_ADAPTER_ENABLE", "true")
    monkeypatch.setenv("STRATEGY_A_ADAPTER_SOURCE", "human_validation_gate")
    payload = adapter.map_scanner_record(SCANNER_RECORD, symbol="XAUUSD.ecn")
    assert payload["direction"] == "BUY"  # normalized from 'long'
    assert payload["entry"] == 4355.0  # echoed, never recomputed
    assert payload["status"] == "APPROVED"
    assert payload["source"] == "SCANNER_HUMAN_APPROVED"


def test_adapter_refuses_unapproved_status(monkeypatch):
    monkeypatch.setenv("STRATEGY_A_ADAPTER_ENABLE", "true")
    monkeypatch.setenv("STRATEGY_A_ADAPTER_SOURCE", "human_validation_gate")
    record = {**SCANNER_RECORD, "status": "PENDING"}
    with pytest.raises(adapter.AdapterError, match="APPROVED"):
        adapter.map_scanner_record(record, symbol="XAUUSD.ecn")


def test_adapter_never_invents_missing_geometry(monkeypatch):
    monkeypatch.setenv("STRATEGY_A_ADAPTER_ENABLE", "true")
    monkeypatch.setenv("STRATEGY_A_ADAPTER_SOURCE", "human_validation_gate")
    record = {k: v for k, v in SCANNER_RECORD.items() if k != "sl"}
    with pytest.raises(adapter.AdapterError, match="never invents"):
        adapter.map_scanner_record(record, symbol="XAUUSD.ecn")


def test_adapter_refuses_malformed_geometry(monkeypatch):
    monkeypatch.setenv("STRATEGY_A_ADAPTER_ENABLE", "true")
    monkeypatch.setenv("STRATEGY_A_ADAPTER_SOURCE", "human_validation_gate")
    bad = {**SCANNER_RECORD, "sl": 4360.0}  # BUY with sl above entry
    with pytest.raises(adapter.AdapterError, match="BUY requires"):
        adapter.map_scanner_record(bad, symbol="XAUUSD.ecn")


def test_adapter_batch_all_or_nothing(monkeypatch):
    monkeypatch.setenv("STRATEGY_A_ADAPTER_ENABLE", "true")
    monkeypatch.setenv("STRATEGY_A_ADAPTER_SOURCE", "human_validation_gate")
    bad = {**SCANNER_RECORD, "signal_id": "X", "status": "REJECTED"}
    with pytest.raises(adapter.AdapterError):
        adapter.map_scanner_batch([SCANNER_RECORD, bad], symbol="XAUUSD.ecn")


# ---------------------------------------------------------------------------
# Telegram configuration diagnostic (test-only)
# ---------------------------------------------------------------------------


def test_diagnostic_reports_not_configured_without_secrets(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    result = tg_diag.diagnose()
    assert result["configured"] is False
    assert result["delivery_mode"] == "MOCK"
    assert result["bot_token_fingerprint"] is None
    assert result["chat_id_fingerprint"] is None
    assert result["get_me"] is None  # no network call requested


def test_diagnostic_masks_credentials_never_exposes_them(monkeypatch):
    token = "123456789:AAAbbbCCCdddEEEfffGGGhhhIIIjjjKKKlll"
    chat = "-1004342109034"
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", token)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", chat)
    result = tg_diag.diagnose(env=dict(os.environ))
    assert result["configured"] is True
    assert result["delivery_mode"] == "REAL"
    # Masked fingerprints only: never the full secret in the result.
    assert result["bot_token_fingerprint"] == token[:4] + "..." + token[-4:]
    assert result["chat_id_fingerprint"] == chat[:4] + "..." + chat[-4:]
    assert token not in json.dumps(result)
    assert chat not in json.dumps(result)


def test_get_me_skipped_without_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    result = tg_diag.diagnose(do_get_me=True, env={})
    assert result["get_me"] == {"ok": False, "detail": "NOT_CONFIGURED (no token)"}
