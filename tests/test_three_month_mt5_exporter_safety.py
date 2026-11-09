"""Static safety guard for the read-only three-month MT5 acquisition utility."""
import ast
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_sp2l_three_month_mt5_data.py"


class TestMt5ExporterSafety(unittest.TestCase):
    def test_exporter_contains_no_trading_or_inventory_api_calls(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        forbidden = {
            "order_send", "order_check", "positions_get", "orders_get",
            "history_deals_get", "history_orders_get", "symbol_select",
        }
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(forbidden.isdisjoint(calls), sorted(forbidden.intersection(calls)))

    def test_exporter_reads_only_historical_market_data_and_symbol_metadata(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        mt5_calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "mt5"
        }
        allowed = {
            "initialize", "shutdown", "terminal_info", "account_info",
            "symbol_info", "copy_ticks_range", "copy_rates_range", "last_error",
        }
        self.assertTrue(mt5_calls.issubset(allowed), sorted(mt5_calls - allowed))
        self.assertIn("copy_ticks_range", mt5_calls)
        self.assertIn("copy_rates_range", mt5_calls)
        self.assertIn("symbol_info", mt5_calls)


if __name__ == "__main__":
    unittest.main()
