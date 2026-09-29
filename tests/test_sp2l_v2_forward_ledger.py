import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sp2l_v2_forward_ledger import (
    ensure_state, record_detected, record_order_result, record_deal,
    record_expired_order, summarize,
)


def candidate():
    return {
        "signal_id": "XAUUSD.ecn:100:BUY",
        "symbol": "XAUUSD.ecn",
        "direction": "BUY",
        "trigger_time": 100,
        "theoretical_entry": 100.0,
        "sl": 99.0,
        "tp": 101.0,
        "risk": 1.0,
    }


def test_lifecycle_closed():
    state = {}
    c = candidate()
    record_detected(state, c)
    record_order_result(state, c, {"ok": True, "order": 123})
    record_deal(state, {"signal_id": c["signal_id"]}, {
        "entry": 0, "deal": 10, "order": 123, "position": 20,
        "entry_price": 100.1, "entry_slippage": 0.1,
    })
    record_deal(state, {"signal_id": c["signal_id"]}, {
        "entry": 1, "deal": 11, "order": 123, "position": 20,
        "exit_price": 99.0, "actual_r": -1.0, "net": -10.0, "reason": 4,
    })
    assert state["v2_forward_ledger"]["signals"][c["signal_id"]]["status"] == "CLOSED"
    assert summarize(state)["closed"] == 1


def test_lifecycle_rejected():
    state = {}
    c = candidate()
    record_detected(state, c)
    record_order_result(state, c, {"ok": False, "reason": "REJECTED"})
    assert summarize(state)["rejected"] == 1


def test_lifecycle_expired():
    state = {}
    c = candidate()
    record_order_result(state, c, {"ok": True, "order": 123})
    record_expired_order(state, 123)
    assert summarize(state)["expired"] == 1
