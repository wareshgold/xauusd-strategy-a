"""Isolated fixtures for the live V3.1 shared-runtime entry function.

Loads only the AST of find_first_entry from the supplied runtime source file.
It does not import or execute the Runner module and never connects to MT5.
Research-only: pins current implementation behavior, not canonical geometry.
"""
from __future__ import annotations

import ast
import os
import unittest
from pathlib import Path


def load_runtime_function():
    source = os.environ.get("SP2L_RUNTIME_SOURCE")
    if not source:
        raise RuntimeError("Set SP2L_RUNTIME_SOURCE to the local shared Runner source file")
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"Runtime source not found: {path}")

    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    node = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "find_first_entry"
    )
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"MAX_SL_DISTANCE": 10.0, "TP_R": 4.0}
    exec(compile(module, str(path), "exec"), namespace)
    return namespace["find_first_entry"]


class TestRuntimeFinalArrayElementCanTrigger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.find_first_entry = staticmethod(load_runtime_function())

    def test_buy_final_array_bar_is_included_and_stamped(self):
        candles = [
            {"time": 0, "low": 90.0, "high": 100.0},
            {"time": 60, "low": 95.0, "high": 101.0},
            {"time": 120, "low": 100.0, "high": 102.0},
            {"time": 180, "low": 99.0, "high": 103.0},
        ]
        result = self.find_first_entry(candles, 2, {"direction": "BUY", "symbol": "XAUUSD.ecn"})
        self.assertIsNotNone(result)
        self.assertEqual(result["direction"], "BUY")
        self.assertEqual(result["trigger_time"], candles[-1]["time"])
        self.assertEqual(result["theoretical_entry"], candles[-1]["low"])
        self.assertNotIn("secondary_entry_2x", result)

    def test_sell_final_array_bar_is_included_and_stamped(self):
        candles = [
            {"time": 0, "low": 100.0, "high": 110.0},
            {"time": 60, "low": 99.0, "high": 105.0},
            {"time": 120, "low": 98.0, "high": 100.0},
            {"time": 180, "low": 97.0, "high": 101.0},
        ]
        result = self.find_first_entry(candles, 2, {"direction": "SELL", "symbol": "XAUUSD.ecn"})
        self.assertIsNotNone(result)
        self.assertEqual(result["direction"], "SELL")
        self.assertEqual(result["trigger_time"], candles[-1]["time"])
        self.assertEqual(result["theoretical_entry"], candles[-1]["high"])
        self.assertNotIn("secondary_entry_2x", result)

    def test_no_trigger_when_final_bar_does_not_break_previous_extreme(self):
        buy = [
            {"time": 0, "low": 90.0, "high": 100.0},
            {"time": 60, "low": 95.0, "high": 101.0},
            {"time": 120, "low": 100.0, "high": 102.0},
            {"time": 180, "low": 100.0, "high": 103.0},
        ]
        sell = [
            {"time": 0, "low": 100.0, "high": 110.0},
            {"time": 60, "low": 99.0, "high": 105.0},
            {"time": 120, "low": 98.0, "high": 100.0},
            {"time": 180, "low": 97.0, "high": 100.0},
        ]
        self.assertIsNone(self.find_first_entry(buy, 2, {"direction": "BUY"}))
        self.assertIsNone(self.find_first_entry(sell, 2, {"direction": "SELL"}))


if __name__ == "__main__":
    unittest.main()
