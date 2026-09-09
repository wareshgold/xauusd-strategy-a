"""F10: structural invalidation must remain independent of risk budget.

Research-only. This fixture does not choose the unresolved source stop anchor.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateTrade:
    entry: float
    structural_anchor: float


@dataclass(frozen=True)
class RiskResult:
    risk_fraction: float
    position_size: float
    entry: float
    stop: float


def position_size(account_equity: float, risk_fraction: float, entry: float,
                  stop: float, value_per_price_unit: float) -> float:
    risk_amount = account_equity * risk_fraction
    distance = abs(entry - stop)
    if distance <= 0 or value_per_price_unit <= 0:
        raise ValueError("invalid risk inputs")
    return risk_amount / (distance * value_per_price_unit)


def evaluate(candidate: CandidateTrade, account_equity: float,
             risk_fraction: float, value_per_price_unit: float) -> RiskResult:
    size = position_size(account_equity, risk_fraction, candidate.entry,
                         candidate.structural_anchor, value_per_price_unit)
    return RiskResult(risk_fraction, size, candidate.entry,
                      candidate.structural_anchor)


def f10_cases():
    return {
        "base_structural_stop": CandidateTrade(entry=103.0, structural_anchor=99.0),
        "wick_candidate": CandidateTrade(entry=103.0, structural_anchor=98.5),
        "body_candidate": CandidateTrade(entry=103.0, structural_anchor=100.0),
        "relevant_swing_candidate": CandidateTrade(entry=103.0, structural_anchor=101.5),
    }
