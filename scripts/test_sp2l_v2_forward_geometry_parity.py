"""Deterministic research-only parity test for the V2 forward geometry.

This test compares the exact research V2 detector with the V2 geometry embedded
in the multi-symbol forward runner using a synthetic BUY and SELL fixture.

It does not connect to MT5, place orders, tune parameters, or emit signals for
production. It validates implementation parity only.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2_DETECTOR = ROOT / "scripts" / "sp2l_strategy_a_v2_detector.py"
FORWARD_RUNNER = ROOT / "scripts" / "run_sp2l_author_replica_multi_symbol_forward_test.py"

CONTRACT = {
    "P_GAP_PRICE": 1.0,
    "SPIKE_MULTIPLIER": 1.5,
    "MAX_SL_DISTANCE": 10.0,
    "TP_R": 1.0,
}


def _load_functions(path: Path, names: set[str]) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    selected = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names
    ]
    namespace = dict(CONTRACT)
    # The V2 detector's setup helper is needed by detect_setup().
    if "detect_setup" in names:
        helper_nodes = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in {"_body", "_setup"}
        ]
        selected = helper_nodes + selected
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(path), "exec"), namespace)
    return {name: namespace[name] for name in names}


def _fixture(direction: str) -> list[dict]:
    if direction == "BUY":
        return [
            {"time": 1, "open": 100.0, "high": 101.2, "low": 99.8, "close": 101.0},
            {"time": 2, "open": 102.0, "high": 105.5, "low": 101.8, "close": 105.0},
            {"time": 3, "open": 106.0, "high": 107.2, "low": 106.0, "close": 107.0},
            {"time": 4, "open": 106.5, "high": 107.0, "low": 105.5, "close": 106.7},
        ]
    return [
        {"time": 1, "open": 101.0, "high": 101.2, "low": 99.8, "close": 100.0},
        {"time": 2, "open": 99.0, "high": 99.2, "low": 95.5, "close": 96.0},
        {"time": 3, "open": 95.0, "high": 95.0, "low": 93.8, "close": 94.0},
        {"time": 4, "open": 94.5, "high": 95.0, "low": 93.5, "close": 94.0},
    ]


def _assert_equal(a: dict, b: dict, fields: tuple[str, ...]) -> None:
    for field in fields:
        assert a[field] == b[field], f"{field}: V2={a[field]!r} forward={b[field]!r}"


def main() -> int:
    v2 = _load_functions(
        V2_DETECTOR,
        {"detect_setup", "find_first_entry"},
    )
    forward = _load_functions(
        FORWARD_RUNNER,
        {"detect", "find_latest_candidate", "find_first_entry"},
    )

    for direction in ("BUY", "SELL"):
        candles = _fixture(direction)

        setup = v2["detect_setup"](candles[:3])
        assert setup is not None, f"V2 setup missing: {direction}"
        entry = v2["find_first_entry"](candles, 2, setup)
        assert entry is not None, f"V2 entry missing: {direction}"

        candidate = forward["find_latest_candidate"](candles, "XAUUSD.ecn")
        assert candidate is not None, f"forward candidate missing: {direction}"
        assert candidate["direction"] == direction

        _assert_equal(
            entry,
            candidate,
            ("direction", "trigger_time", "theoretical_entry", "sl", "risk", "tp"),
        )

    print(
        "PASS: V2 detector and multi-symbol forward runner geometry are "
        "equivalent on deterministic BUY/SELL fixtures."
    )
    print(
        "NOTE: This test does not establish signal-population or execution "
        "parity; see docs/research/SP2L_V2_FORWARD_PARITY_CHECKPOINT_20260929.md."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
