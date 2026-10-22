"""Safety contract checks for the Strategy B read-only observer."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_strategy_b_forward_observer.py"


def test_observer_has_no_order_execution_api_or_live_gateway_import():
    source = RUNNER.read_text(encoding="utf-8")
    assert "order_send" not in source
    assert "TRADE_ACTION_DEAL" not in source
    assert "TRADE_ACTION_PENDING" not in source
    assert "live_mt5_gateway" not in source


def test_observer_is_opt_in_and_exact_symbol_only():
    source = RUNNER.read_text(encoding="utf-8")
    assert 'os.getenv("STRATEGY_B_OBSERVER_ENABLE", "false")' in source
    assert 'os.getenv("STRATEGY_B_SYMBOL", "XAUUSD")' in source
    assert 'if SYMBOL != "XAUUSD":' in source


def test_observer_uses_strategy_b_isolated_paths_and_lock():
    source = RUNNER.read_text(encoding="utf-8")
    assert 'ARTIFACT_DIR = ROOT / "artifacts" / "strategy-b-forward"' in source
    assert 'STATE_FILE = RUNTIME_DIR / "strategy_b_forward_observer_state.json"' in source
    assert 'LOCK_FILE = RUNTIME_DIR / "strategy_b_forward_observer.lock"' in source
