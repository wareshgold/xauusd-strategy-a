"""Safety contract checks for the Strategy B read-only observer."""
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_strategy_b_forward_observer.py"


def executable_source_without_module_docstring(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        tree.body.pop(0)
    return ast.unparse(tree)


def test_observer_has_no_order_execution_api_or_live_gateway_import():
    source = executable_source_without_module_docstring(RUNNER)
    assert "order_send" not in source
    assert "TRADE_ACTION_DEAL" not in source
    assert "TRADE_ACTION_PENDING" not in source
    assert "live_mt5_gateway" not in source


def test_observer_is_opt_in_and_uses_explicit_broker_symbol_mapping():
    source = RUNNER.read_text(encoding="utf-8")
    assert 'os.getenv("STRATEGY_B_OBSERVER_ENABLE", "false")' in source
    assert 'SOURCE_SYMBOL = "XAUUSD"' in source
    assert 'os.getenv("STRATEGY_B_SYMBOL", "XAUUSD.ecn")' in source
    assert 'os.getenv("STRATEGY_B_POLL_SECONDS", "0.5")' in source
    assert 'if SYMBOL not in (SOURCE_SYMBOL, "XAUUSD.ecn"):' in source
    assert 'EXPLICIT_BROKER_SUFFIX_ADAPTER' in source


def test_observer_uses_strategy_b_isolated_paths_and_lock():
    source = RUNNER.read_text(encoding="utf-8")
    assert 'ARTIFACT_DIR = ROOT / "artifacts" / "strategy-b-forward"' in source
    assert 'STATE_FILE = RUNTIME_DIR / "strategy_b_forward_observer_state.json"' in source
    assert 'LOCK_FILE = RUNTIME_DIR / "strategy_b_forward_observer.lock"' in source
