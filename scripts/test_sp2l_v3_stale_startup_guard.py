"""Regression tests for the V3 stale-startup candidate guard.

The production runner imports MT5 and the live forward runner, so these tests
extract only the dependency-free guard function from the exact production
source. This keeps the regression test runnable without an MT5 terminal.
"""
from __future__ import annotations

import ast
from pathlib import Path


SOURCE = Path(__file__).with_name("run_sp2l_v3_xauusd_forward_test.py")


def load_guard():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    node = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_candidate_is_stale"
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace["_candidate_is_stale"]


def test_candidate_at_watermark_is_stale():
    guard = load_guard()
    assert guard({"trigger_time": 100}, 100) is True


def test_candidate_before_watermark_is_stale():
    guard = load_guard()
    assert guard({"trigger_time": 99}, 100) is True


def test_candidate_after_watermark_is_fresh():
    guard = load_guard()
    assert guard({"trigger_time": 101}, 100) is False


def test_missing_candidate_or_watermark_is_not_stale():
    guard = load_guard()
    assert guard(None, 100) is False
    assert guard({"trigger_time": 100}, None) is False
