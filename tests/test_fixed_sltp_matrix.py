"""Offline tests for the RESEARCH-ONLY fixed SL/TP winrate matrix.

Proves, without touching MT5 or the network:
- the session filter is DST-safe (NY wall clock 03:00..16:59, Mon-Fri);
- the synthetic exit simulator resolves first-touch correctly (walk starts at
  entry_index + 1, exactly like the live engine) and marks both-touch candles
  AMBIGUOUS (conservative);
- width cells are per-width symmetric (SL dist == TP dist) and direction-aware;
- aggregation is deterministic and pip-mode aware (REPO_PIP vs INDEX_POINT);
- the module reuses the frozen author-replica detection code unchanged and
  never places orders.
"""
from __future__ import annotations

import importlib.util
import inspect
from datetime import datetime, timezone

import pytest

import scripts.run_sp2l_fixed_sltp_matrix as m


def ts_utc(iso: str) -> int:
    return int(datetime.fromisoformat(iso).timestamp())


# ---------------------------------------------------------------- session filter

@pytest.mark.parametrize(
    "iso,expected",
    [
        ("2026-09-22T07:00:00+00:00", True),   # 03:00 NY exactly -> in
        ("2026-09-22T06:59:00+00:00", False),  # 02:59 NY -> before London open
        ("2026-09-22T19:59:00+00:00", True),   # 15:59 NY -> in-session
        ("2026-09-22T20:59:00+00:00", True),   # 16:59 NY -> last in-session minute
        ("2026-09-22T21:00:00+00:00", False),  # 17:00 NY -> closed
        ("2026-09-20T12:00:00+00:00", False),  # Sunday
        ("2026-09-19T12:00:00+00:00", False),  # Saturday
        # winter date (EST, UTC-5): 08:00 London == 03:00 NY == 08:00 UTC
        ("2026-01-20T08:00:00+00:00", True),
        ("2026-01-20T07:59:00+00:00", False),
    ],
)
def test_session_filter_ny_wall_clock(iso, expected):
    assert m.in_london_to_ny_session(ts_utc(iso)) is expected


def test_session_filter_summer_london_open():
    # Summer: London 08:00 BST == 07:00 UTC == 03:00 EDT -> 07:00 UTC is the edge
    assert m.in_london_to_ny_session(ts_utc("2026-09-22T07:00:00+00:00")) is True
    assert m.in_london_to_ny_session(ts_utc("2026-09-22T06:59:00+00:00")) is False


# ---------------------------------------------------------------- exit simulator

_BASE = ts_utc("2026-09-22T12:00:00+00:00")


def _c(seconds_from_base, o, h, l, c):
    t = _BASE + seconds_from_base
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


def test_exit_first_touch_tp_only_is_win():
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),   # entry minute (index 0)
        _c(60, 100.0, 101.5, 99.9, 101.4),  # first walked candle (index 1)
    ]
    assert m.fixed_exit_outcome(candles, 0, "BUY", sl=99.0, tp=100.5) == "WIN"


def test_exit_first_touch_sl_only_is_loss():
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),
        _c(60, 100.0, 100.2, 98.5, 98.6),
    ]
    assert m.fixed_exit_outcome(candles, 0, "BUY", sl=99.0, tp=101.0) == "LOSS"


def test_exit_both_touch_is_ambiguous():
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),
        _c(60, 100.0, 101.5, 98.5, 100.0),
    ]
    assert m.fixed_exit_outcome(candles, 0, "BUY", sl=99.0, tp=101.0) == "AMBIGUOUS"


def test_exit_sell_direction_mirrored():
    # SELL: sl above entry, tp below entry
    sl_loss = [_c(0, 100.0, 100.1, 99.9, 100.0), _c(60, 100.0, 101.5, 100.5, 101.0)]
    assert m.fixed_exit_outcome(sl_loss, 0, "SELL", sl=101.0, tp=99.0) == "LOSS"
    tp_win = [_c(0, 100.0, 100.1, 99.9, 100.0), _c(60, 100.0, 100.2, 98.5, 98.6)]
    assert m.fixed_exit_outcome(tp_win, 0, "SELL", sl=101.0, tp=99.0) == "WIN"


def test_exit_unresolved_returns_none():
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),
        _c(60, 100.0, 100.1, 99.9, 100.0),
    ]
    assert m.fixed_exit_outcome(candles, 0, "BUY", sl=99.0, tp=101.0) is None


def test_exit_does_not_look_at_entry_candle():
    # The entry candle itself touches TP, but the walk must start AFTER it.
    # Second candle sits entirely BETWEEN sl and tp -> nothing touches -> None.
    candles = [
        _c(0, 100.0, 101.5, 99.9, 101.4),   # touches tp=100.5 on the entry bar
        _c(60, 100.3, 100.45, 100.1, 100.2),  # fully inside (99, 100.5) -> no touch
    ]
    assert m.fixed_exit_outcome(candles, 0, "BUY", sl=99.0, tp=100.5) is None


# ---------------------------------------------------------------- width cells

def _cands():
    return [
        {"index": 0, "time": 1, "direction": "BUY", "entry": 100.0},
        {"index": 0, "time": 2, "direction": "SELL", "entry": 100.0},
    ]


def test_width_cell_symmetric_levels_and_counts():
    # dist 1.0 -> BUY: sl=99/tp=101 ; SELL: sl=101/tp=99
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),
        _c(60, 100.0, 100.9, 99.1, 100.5),  # touches neither side for either direction
    ]
    cell = m._width_cell(candles, _cands(), dist=1.0)
    assert cell["wins"] == 0 and cell["losses"] == 0
    assert cell["unresolved"] == 2

    # Same candle one tick wider: BUY hits TP while SELL hits SL (symmetry proof)
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),
        _c(60, 100.0, 101.2, 99.8, 101.0),
    ]
    cell = m._width_cell(candles, _cands(), dist=1.0)
    assert cell["by_direction"]["BUY"]["WIN"] == 1
    assert cell["by_direction"]["SELL"]["LOSS"] == 1


def test_mode_summary_uses_pip_size_per_mode():
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0),
        _c(60, 100.0, 100.25, 99.9, 100.2),  # +0.25 move: reaches 0.2 dist, not 20
    ]
    cands = [{"index": 0, "time": 1, "direction": "BUY", "entry": 100.0}]
    repo = m._mode_summary(candles, cands, [20], pip_size=0.01)   # dist 0.2
    point = m._mode_summary(candles, cands, [20], pip_size=1.0)   # dist 20
    assert repo["widths"]["20"]["sl_tp_distance_price"] == pytest.approx(0.2)
    assert point["widths"]["20"]["sl_tp_distance_price"] == pytest.approx(20.0)
    assert repo["widths"]["20"]["by_direction"]["BUY"]["WIN"] == 1
    assert point["widths"]["20"]["by_direction"]["BUY"]["UNRESOLVED"] == 1


def test_aggregation_deterministic():
    # Three independent candidates, each with its own entry+outcome candles:
    # the walk stops at first touch, so each candidate contributes exactly one WIN.
    candles = [
        _c(0, 100.0, 100.1, 99.9, 100.0), _c(60, 100.0, 101.2, 99.8, 101.0),
        _c(120, 100.0, 100.1, 99.9, 100.0), _c(180, 100.0, 101.2, 99.8, 101.0),
        _c(240, 100.0, 100.1, 99.9, 100.0), _c(300, 100.0, 101.2, 99.8, 101.0),
    ]
    cands = [
        {"index": 0, "time": 1, "direction": "BUY", "entry": 100.0},
        {"index": 2, "time": 2, "direction": "BUY", "entry": 100.0},
        {"index": 4, "time": 3, "direction": "BUY", "entry": 100.0},
    ]
    a = m._width_cell(candles, cands, dist=1.0)
    b = m._width_cell(candles, cands, dist=1.0)
    assert a == b and a["wins"] == 3


# ---------------------------------------------------------------- frozen reuse + safety

def test_detection_is_imported_unchanged_from_author_replica():
    spec = importlib.util.spec_from_file_location("sp2l_replica_direct", m.REPLAY_SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # exec_module re-executes the file, so identity differs by design; the
    # frozen-reuse contract is: same function name, same source text.
    assert m.detect_signal.__name__ == "signal"
    assert inspect.getsource(m.detect_signal) == inspect.getsource(mod.signal)


def test_module_places_no_orders():
    text = open(m.__file__, encoding="utf-8").read()
    for banned in ("order_send", "order_check", "TRADE_ACTION_DEAL", "positions_get"):
        assert banned not in text
    assert m.REPLAY_SOURCE.exists()
