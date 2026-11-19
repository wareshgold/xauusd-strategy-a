"""Partial-close research matrix: one 0.02-lot position split into two 0.01 legs.

Research-only definitions. No MT5 access, order placement, or runner changes.
The 27 variants are 3 fixed-volume references plus 24 risk-normalized variants.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from enum import StrEnum

from research.capital_matrix.matrix import (
    INITIAL_CAPITAL, RISK_LEVELS, SIZING_MODES, BrokerSpec, risk_budget,
)

PARTIAL_LEG_LOTS = Decimal("0.01")
PARTIAL_TOTAL_LOTS = Decimal("0.02")
PARTIAL_TP1_R = Decimal("1")
PARTIAL_TP2_R = (Decimal("2"), Decimal("3"))
PARTIAL_RUNNER_TP_R = Decimal("4")
TRAIL_ACTIVATION = Decimal("0.40")
TRAIL_DISTANCE = Decimal("0.40")


class PartialExit(StrEnum):
    TP2_2R = "TP2_2R"
    TP2_3R = "TP2_3R"
    RUNNER_4R = "RUNNER_4R"


@dataclass(frozen=True, slots=True)
class PartialRunSpec:
    run_id: str
    exit_mode: PartialExit
    sizing_mode: str | None
    risk_fraction: Decimal | None
    fixed_volume_reference: bool = False
    initial_lots: Decimal = PARTIAL_TOTAL_LOTS
    first_leg_lots: Decimal = PARTIAL_LEG_LOTS
    second_leg_lots: Decimal = PARTIAL_LEG_LOTS

    @property
    def tp2_r(self) -> Decimal:
        if self.exit_mode is PartialExit.TP2_2R:
            return Decimal("2")
        if self.exit_mode is PartialExit.TP2_3R:
            return Decimal("3")
        return PARTIAL_RUNNER_TP_R

    @property
    def is_runner(self) -> bool:
        return self.exit_mode is PartialExit.RUNNER_4R


def build_partial_matrix() -> tuple[PartialRunSpec, ...]:
    runs: list[PartialRunSpec] = []
    modes = (
        (PartialExit.TP2_2R, "TP1_1R_TP2_2R"),
        (PartialExit.TP2_3R, "TP1_1R_TP2_3R"),
        (PartialExit.RUNNER_4R, "TP1_1R_RUNNER_4R"),
    )
    # Fixed-volume references: one 0.02-lot entry, close 0.01 at 1R.
    for exit_mode, suffix in modes:
        runs.append(PartialRunSpec(
            run_id=f"PARTIAL_FIXED_002LOT_{suffix}",
            exit_mode=exit_mode, sizing_mode=None, risk_fraction=None,
            fixed_volume_reference=True,
        ))
    # Risk-normalized: total position risk is the requested budget. Quantize
    # total volume down in 0.02-lot increments so both equal legs remain 0.01 multiples.
    for sizing_mode in SIZING_MODES:
        for risk in RISK_LEVELS:
            for exit_mode, suffix in modes:
                runs.append(PartialRunSpec(
                    run_id=f"PARTIAL_{sizing_mode}_{int(risk*10000):04d}_{suffix}",
                    exit_mode=exit_mode, sizing_mode=sizing_mode,
                    risk_fraction=risk,
                ))
    result = tuple(runs)
    if len(result) != 27 or len({r.run_id for r in result}) != 27:
        raise AssertionError("partial matrix must contain exactly 27 unique variants")
    return result


@dataclass(frozen=True, slots=True)
class PartialSizing:
    requested_risk_usd: Decimal
    actual_risk_usd: Decimal
    total_lots: Decimal
    leg_lots: Decimal
    feasible: bool
    reason: str


def size_partial_run(
    run: PartialRunSpec, *, initial_capital: Decimal,
    current_equity: Decimal, stop_distance_price: Decimal, broker: BrokerSpec,
) -> PartialSizing:
    if stop_distance_price <= 0:
        raise ValueError("stop distance must be positive")
    risk_per_lot = (stop_distance_price / broker.tick_size) * broker.tick_value_per_lot
    if run.fixed_volume_reference:
        total = run.initial_lots
        actual = total * risk_per_lot
        feasible = (
            total == PARTIAL_TOTAL_LOTS
            and run.first_leg_lots >= broker.volume_min
            and run.second_leg_lots >= broker.volume_min
            and run.first_leg_lots % broker.volume_step == 0
            and run.second_leg_lots % broker.volume_step == 0
            and total <= broker.volume_max
        )
        return PartialSizing(actual, actual, total, PARTIAL_LEG_LOTS, feasible,
                             "FIXED_002LOT_REFERENCE" if feasible else "FIXED_VOLUME_NOT_SPLITTABLE")
    assert run.risk_fraction is not None and run.sizing_mode is not None
    budget = risk_budget(
        initial_capital=initial_capital, current_equity=current_equity,
        risk_fraction=run.risk_fraction, sizing_mode=run.sizing_mode,
    )
    raw_total = budget / risk_per_lot
    two_leg_step = broker.volume_step * 2
    total = (raw_total / two_leg_step).to_integral_value(rounding=ROUND_DOWN) * two_leg_step
    total = min(total, broker.volume_max)
    leg = total / 2
    if total < broker.volume_min * 2 or leg < broker.volume_min:
        return PartialSizing(budget, Decimal("0"), Decimal("0"), Decimal("0"),
                             False, "RISK_BUDGET_CANNOT_FUND_TWO_MINIMUM_PARTIAL_LEGS")
    actual = total * risk_per_lot
    if actual > budget:
        raise AssertionError("partial sizing exceeded aggregate risk budget")
    return PartialSizing(budget, actual, total, leg, True, "OK")


if __name__ == "__main__":
    matrix = build_partial_matrix()
    print(f"PARTIAL_MATRIX_COUNT={len(matrix)}")
    print("FIXED_VOLUME_REFERENCES=3")
    print("RISK_NORMALIZED_VARIANTS=24")
