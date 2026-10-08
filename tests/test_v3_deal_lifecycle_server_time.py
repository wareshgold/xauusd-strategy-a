"""Regression tests for RR2/TRAIL4 MT5 history-clock reconciliation."""

import ast
from datetime import datetime as RealDateTime, timedelta, timezone
from pathlib import Path


RUNNER = Path(__file__).parents[1] / "scripts" / "run_sp2l_v3_xauusd_forward_test.py"


def _extract_functions():
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    wanted = {"_mt5_server_offset_seconds", "_mt5_history_bounds_utc"}
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    assert {node.name for node in nodes} == wanted
    return nodes


def test_history_bounds_convert_utc_to_observed_server_clock():
    fixed_utc = RealDateTime(2026, 10, 8, 6, 46, 38, tzinfo=timezone.utc)

    class FixedDateTime(RealDateTime):
        @classmethod
        def now(cls, tz=None):
            return fixed_utc if tz is not None else fixed_utc.replace(tzinfo=None)

    class FakeMT5:
        def symbol_info_tick(self, symbol):
            return type("Tick", (), {
                "time": int((fixed_utc + timedelta(hours=3)).timestamp())
            })()

    class Runner:
        @staticmethod
        def log_event(event):
            raise AssertionError(f"unexpected clock diagnostic: {event}")

    namespace = {
        "datetime": FixedDateTime,
        "timezone": timezone,
        "mt5": FakeMT5(),
        "runner": Runner(),
    }
    exec(compile(ast.Module(body=_extract_functions(), type_ignores=[]),
                  str(RUNNER), "exec"), namespace)

    start, end = namespace["_mt5_history_bounds_utc"](
        fixed_utc, fixed_utc + timedelta(seconds=120), "XAUUSD.ecn"
    )

    assert start == fixed_utc + timedelta(hours=3)
    assert end == fixed_utc + timedelta(hours=3, seconds=120)


def test_symbol_lifecycle_queries_history_with_converted_bounds():
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    fn = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_run_scoped_symbol_lifecycle"
    )
    calls = [
        node for node in ast.walk(fn)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "history_deals_get"
    ]
    assert len(calls) == 1
    args = calls[0].args
    assert len(args) >= 2
    assert isinstance(args[0], ast.Name) and args[0].id == "start_api"
    assert isinstance(args[1], ast.Name) and args[1].id == "end_api"
