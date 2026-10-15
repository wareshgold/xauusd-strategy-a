from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "scripts" / "live_dashboard.py"


def _source():
    return DASHBOARD.read_text(encoding="utf-8")


def test_live_dashboard_points_to_v3_rr2_trail4_artifacts():
    source = _source()
    assert 'STATE_FILE = ROOT / "runtime" / "sp2l_v3_xauusd_rr2_trail4_forward_state.json"' in source
    assert 'EVENTS = ROOT / "artifacts" / "forward-test" / "SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl"' in source
    assert "sp2l_multi_symbol_forward_state.json" not in source
    assert "SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl" not in source


def test_live_dashboard_distinguishes_state_freshness_from_event_progress():
    source = _source()
    assert "State-file freshness (not a heartbeat)" in source
    assert "V3 event log last write" in source
    assert "A running process or fresh state file alone does not prove a successful market poll" in source


def test_live_dashboard_has_read_only_cpu_delta_and_event_ledger():
    source = _source()
    assert "def _process_cpu_delta(pid: int) -> str:" in source
    assert "GetProcessTimes" in source
    assert "def recent_trade_ledger(events: list[dict]) -> str:" in source
    assert "TELEGRAM_DEAL_LIFECYCLE" in source
    assert "dashboard environment is not substituted" in source


def test_live_dashboard_source_parses_as_python():
    ast.parse(_source())
