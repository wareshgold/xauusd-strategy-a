from __future__ import annotations

from .fixtures import FixtureExpectation, StrategyFixture


def build_sp2l_synthetic_fixtures() -> list[StrategyFixture]:
    """Declarative SP2L fixtures.

    These fixtures intentionally test only source-resolved semantics. They do
    not invent P-Gap geometry, F12 fill semantics, F10 stop anchors, or C06
    lifetime semantics.
    """
    return [
        StrategyFixture(
            fixture_id="SP2L-F13-001",
            description="2X midpoint is exactly 50% of Entry-SL distance.",
            input_data={
                "rule_id": "SP2L.F13",
                "entry": 100.0,
                "sl": 90.0,
                "expected_2x": 95.0,
                "source_confirmed": True,
            },
            expected=FixtureExpectation.ACCEPT,
        ),
        StrategyFixture(
            fixture_id="SP2L-C05-001",
            description="MA filter contract identifies the 15-minute MA50.",
            input_data={
                "rule_id": "SP2L.MA_FILTER",
                "timeframe": "M15",
                "period": 50,
                "source_confirmed": True,
            },
            expected=FixtureExpectation.ACCEPT,
        ),
        StrategyFixture(
            fixture_id="SP2L-F12-001",
            description="F12 retrace semantics remain blocked until fill meaning is resolved.",
            input_data={
                "rule_id": "SP2L.F12",
                "trigger": "previous_candle_extreme",
                "unresolved": [
                    "touch_vs_penetration",
                    "intrabar_vs_close",
                    "executable_entry",
                    "fill_semantics",
                ],
            },
            expected=FixtureExpectation.BLOCKED,
        ),
        StrategyFixture(
            fixture_id="SP2L-F10-001",
            description="F10 stop anchor remains blocked until exact anchor is resolved.",
            input_data={
                "rule_id": "SP2L.F10",
                "statement": "behind_spike_start_candle",
                "unresolved": ["exact_stop_anchor"],
            },
            expected=FixtureExpectation.BLOCKED,
        ),
        StrategyFixture(
            fixture_id="SP2L-C06-001",
            description="C06 pending lifetime remains blocked until candle-count semantics are resolved.",
            input_data={
                "rule_id": "SP2L.C06",
                "statement": "delete_unfilled_buy_limit_within_1_to_2_candidate_candles",
                "unresolved": ["fixed_vs_context_dependent_lifetime"],
            },
            expected=FixtureExpectation.BLOCKED,
        ),
        StrategyFixture(
            fixture_id="SP2L-C01-001",
            description="P.GAP terminology is source-confirmed but executable geometry is not assumed.",
            input_data={
                "rule_id": "SP2L.PGAP",
                "statement": "P.GAP_is_not_Common_GAP",
                "valid_bo_is_p_gap": True,
                "geometry_formula_defined": False,
            },
            expected=FixtureExpectation.BLOCKED,
        ),
    ]


def evaluate_sp2l_fixture(data: dict[str, object]) -> None:
    if data.get("source_confirmed") is True:
        if data.get("rule_id") == "SP2L.F13":
            entry = float(data["entry"])
            sl = float(data["sl"])
            expected = float(data["expected_2x"])
            midpoint = entry - ((entry - sl) / 2.0)
            if abs(midpoint - expected) > 1e-12:
                raise ValueError("F13 2X midpoint does not match the source rule.")
            return

        if data.get("rule_id") == "SP2L.MA_FILTER":
            if data.get("timeframe") != "M15" or data.get("period") != 50:
                raise ValueError("MA filter does not match the source-confirmed M15 MA50 contract.")
            return

    if data.get("unresolved"):
        from .fixtures import FixtureBlocked

        raise FixtureBlocked(
            f"Unresolved source semantics: {', '.join(str(x) for x in data['unresolved'])}"
        )

    if data.get("geometry_formula_defined") is False:
        from .fixtures import FixtureBlocked

        raise FixtureBlocked("P.GAP executable geometry is not source-resolved.")

    raise ValueError("Fixture has no deterministic source-approved evaluation.")
