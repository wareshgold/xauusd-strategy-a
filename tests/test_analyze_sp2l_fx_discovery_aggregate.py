import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze_sp2l_fx_discovery_aggregate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sp2l_fx_aggregate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_blank_pf_all_wins_is_reconstructable():
    module = load_module()
    assert module.reconstruct_gross(6.0, None, 6, 0) == (6.0, 0.0)


def test_blank_pf_zero_trade_row_is_reconstructable():
    module = load_module()
    assert module.reconstruct_gross(0.0, None, 0, 0) == (0.0, 0.0)


def test_blank_pf_with_losses_is_invalid():
    module = load_module()
    profit, loss = module.reconstruct_gross(-2.0, None, 1, 3)
    assert profit != profit
    assert loss != loss


def test_finite_pf_reconstruction_is_preserved():
    module = load_module()
    profit, loss = module.reconstruct_gross(2.0, 2.0, 3, 1)
    assert round(profit, 12) == round(4.0, 12)
    assert round(loss, 12) == round(2.0, 12)
