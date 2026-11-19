"""Deterministic capital-management experiment matrix and risk sizing.

Research-only. This module does not connect to MT5, place orders, or modify
runner configuration. Execution replay is intentionally a separate phase.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from enum import StrEnum
from typing import Iterable


INITIAL_CAPITAL = Decimal("1000")
RISK_LEVELS = tuple(Decimal(x) for x in ("0.0025", "0.0050", "0.0075", "0.0100"))
FIXED_TP_R = tuple(Decimal(x) for x in ("1", "1.5", "2", "3", "4"))
DUAL_TP_PAIRS = (
    (Decimal("1"), Decimal("2")),
    (Decimal("1"), Decimal("3")),
    (Decimal("1"), Decimal("4")),
    (Decimal("1.5"), Decimal("3")),
    (Decimal("2"), Decimal("4")),
)
SIZING_MODES = ("COMPOUND", "FIXED_BASE")
RUNNER_VERSION = "SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101"


class Family(StrEnum):
    FIXED_TP = "FIXED_TP"
    DUAL_INDEPENDENT = "DUAL_INDEPENDENT"
    EXACT_RUNNER = "EXACT_RUNNER"
    NORMALIZED_RUNNER = "NORMALIZED_RUNNER"


@dataclass(frozen=True, slots=True)
class RunSpec:
    run_id: str
    family: Family
    sizing_mode: str | None
    risk_fraction: Decimal | None
    tp_r: Decimal | None = None
    tp1_r: Decimal | None = None
    tp2_r: Decimal | None = None
    volume_lots: Decimal | None = None
    runner_version: str | None = None

    @property
    def is_fixed_volume_reference(self) -> bool:
        return self.family is Family.EXACT_RUNNER


def build_matrix() -> tuple[RunSpec, ...]:
    """Return the agreed 89 primary configurations in stable deterministic order."""
    runs: list[RunSpec] = []
    for mode in SIZING_MODES:
        for risk in RISK_LEVELS:
            for tp in FIXED_TP_R:
                runs.append(RunSpec(
                    run_id=f"FTP_{mode}_{int(risk * 10000):04d}_TP{str(tp).replace('.', 'P')}",
                    family=Family.FIXED_TP, sizing_mode=mode, risk_fraction=risk, tp_r=tp,
                ))
    for mode in SIZING_MODES:
        for risk in RISK_LEVELS:
            for tp1, tp2 in DUAL_TP_PAIRS:
                runs.append(RunSpec(
                    run_id=(f"DUAL_{mode}_{int(risk * 10000):04d}_"
                            f"{str(tp1).replace('.', 'P')}_{str(tp2).replace('.', 'P')}"),
                    family=Family.DUAL_INDEPENDENT, sizing_mode=mode,
                    risk_fraction=risk, tp1_r=tp1, tp2_r=tp2,
                ))
    runs.append(RunSpec(
        run_id="RUNNER_EXACT_001LOT", family=Family.EXACT_RUNNER,
        sizing_mode=None, risk_fraction=None, volume_lots=Decimal("0.01"),
        runner_version=RUNNER_VERSION,
    ))
    for mode in SIZING_MODES:
        for risk in RISK_LEVELS:
            runs.append(RunSpec(
                run_id=f"RUNNER_NORMALIZED_{mode}_{int(risk * 10000):04d}",
                family=Family.NORMALIZED_RUNNER, sizing_mode=mode,
                risk_fraction=risk, tp_r=Decimal("4"),
                runner_version=RUNNER_VERSION,
            ))
    result = tuple(runs)
    if len(result) != 89 or len({r.run_id for r in result}) != 89:
        raise AssertionError("matrix definition must contain exactly 89 unique runs")
    return result


@dataclass(frozen=True, slots=True)
class BrokerSpec:
    """Contract metadata required to translate price risk into lot volume."""
    tick_size: Decimal
    tick_value_per_lot: Decimal
    volume_min: Decimal
    volume_max: Decimal
    volume_step: Decimal

    def __post_init__(self) -> None:
        if min(self.tick_size, self.tick_value_per_lot, self.volume_min,
               self.volume_max, self.volume_step) <= 0:
            raise ValueError("broker contract values must be positive")
        if self.volume_max < self.volume_min:
            raise ValueError("volume_max must be >= volume_min")


@dataclass(frozen=True, slots=True)
class SizedLeg:
    requested_risk_usd: Decimal
    actual_risk_usd: Decimal
    volume_lots: Decimal
    feasible: bool
    reason: str


def _floor_to_step(value: Decimal, step: Decimal) -> Decimal:
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def risk_budget(
    *,
    initial_capital: Decimal,
    current_equity: Decimal,
    risk_fraction: Decimal,
    sizing_mode: str,
) -> Decimal:
    if initial_capital <= 0 or current_equity <= 0:
        raise ValueError("capital and equity must be positive")
    if not (Decimal("0") < risk_fraction <= Decimal("1")):
        raise ValueError("risk_fraction must be in (0, 1]")
    if sizing_mode == "COMPOUND":
        basis = current_equity
    elif sizing_mode == "FIXED_BASE":
        basis = initial_capital
    else:
        raise ValueError(f"unsupported sizing mode: {sizing_mode}")
    return basis * risk_fraction


def size_leg(
    *,
    budget_usd: Decimal,
    stop_distance_price: Decimal,
    broker: BrokerSpec,
) -> SizedLeg:
    """Size down to broker step; never round up beyond the risk budget."""
    if budget_usd <= 0 or stop_distance_price <= 0:
        raise ValueError("budget and stop distance must be positive")
    risk_per_lot = (stop_distance_price / broker.tick_size) * broker.tick_value_per_lot
    raw_lots = budget_usd / risk_per_lot
    lots = min(_floor_to_step(raw_lots, broker.volume_step), broker.volume_max)
    if lots < broker.volume_min:
        return SizedLeg(budget_usd, Decimal("0"), Decimal("0"), False,
                        "RISK_BUDGET_BELOW_MINIMUM_VOLUME")
    actual = lots * risk_per_lot
    if actual > budget_usd:
        raise AssertionError("volume quantization exceeded requested risk")
    return SizedLeg(budget_usd, actual, lots, True, "OK")


def size_run(
    run: RunSpec,
    *,
    initial_capital: Decimal,
    current_equity: Decimal,
    stop_distance_price: Decimal,
    broker: BrokerSpec,
) -> tuple[SizedLeg, ...]:
    """Size one or two legs; dual legs split the aggregate risk budget equally."""
    if run.family is Family.EXACT_RUNNER:
        lots = run.volume_lots or Decimal("0")
        per_lot = (stop_distance_price / broker.tick_size) * broker.tick_value_per_lot
        actual = lots * per_lot
        feasible = broker.volume_min <= lots <= broker.volume_max
        return (SizedLeg(actual, actual, lots, feasible,
                         "EXACT_REFERENCE_VOLUME" if feasible else "EXACT_VOLUME_OUTSIDE_BROKER_LIMITS"),)
    assert run.risk_fraction is not None and run.sizing_mode is not None
    total = risk_budget(
        initial_capital=initial_capital, current_equity=current_equity,
        risk_fraction=run.risk_fraction, sizing_mode=run.sizing_mode,
    )
    legs = 2 if run.family is Family.DUAL_INDEPENDENT else 1
    each = total / legs
    return tuple(size_leg(budget_usd=each, stop_distance_price=stop_distance_price,
                          broker=broker) for _ in range(legs))


def matrix_counts(runs: Iterable[RunSpec]) -> dict[str, int]:
    counts = {family.value: 0 for family in Family}
    for run in runs:
        counts[run.family.value] += 1
    counts["TOTAL"] = sum(counts.values())
    return counts
