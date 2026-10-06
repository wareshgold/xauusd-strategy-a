from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .metrics import ResearchMetrics
from .test_contract import ExecutionSemantics


class ExecutionKernelError(ValueError):
    """Raised when deterministic historical execution inputs are invalid."""


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class AmbiguityPolicy(str, Enum):
    BLOCK = "BLOCK"
    STOP_FIRST = "STOP_FIRST"
    TARGET_FIRST = "TARGET_FIRST"


@dataclass(frozen=True)
class MarketEvent:
    """One chronologically ordered market observation.

    TICK_FEASIBLE events must represent actual ordered observations. A bar's
    OHLC range is never silently treated as an ordered tick stream.
    """

    timestamp: str
    sequence: int
    bid: float | None = None
    ask: float | None = None
    high: float | None = None
    low: float | None = None

    def validate(self) -> None:
        if not self.timestamp:
            raise ExecutionKernelError("market event timestamp is required")
        if self.sequence < 0:
            raise ExecutionKernelError("market event sequence cannot be negative")
        if all(value is None for value in (self.bid, self.ask, self.high, self.low)):
            raise ExecutionKernelError("market event must contain price observations")
        numeric = (self.bid, self.ask, self.high, self.low)
        if any(value is not None and value <= 0 for value in numeric):
            raise ExecutionKernelError("market event prices must be positive")


@dataclass(frozen=True)
class EntryInstruction:
    trade_id: str
    side: Side
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_price: float

    def validate(self) -> None:
        if not self.trade_id or self.entry_price <= 0 or self.risk_price <= 0:
            raise ExecutionKernelError("entry identity and positive prices are required")
        if self.side is Side.BUY:
            if not self.stop_loss < self.entry_price < self.take_profit:
                raise ExecutionKernelError("BUY requires SL < entry < TP")
        elif not self.stop_loss > self.entry_price > self.take_profit:
            raise ExecutionKernelError("SELL requires SL > entry > TP")


@dataclass(frozen=True)
class TradeOutcome:
    trade_id: str
    side: Side
    entry_price: float
    exit_price: float | None
    exit_reason: str
    net_r: float | None
    ambiguous: bool
    entry_sequence: int
    exit_sequence: int | None

    def validate(self) -> None:
        if not self.trade_id or not self.exit_reason:
            raise ExecutionKernelError("trade outcome identity is required")
        if self.ambiguous and self.net_r is not None:
            raise ExecutionKernelError("ambiguous trade cannot have a decisive R result")
        if not self.ambiguous and self.net_r is None:
            raise ExecutionKernelError("decisive trade requires an R result")


@dataclass(frozen=True)
class KernelResult:
    execution_semantics: ExecutionSemantics
    ambiguity_policy: AmbiguityPolicy
    trades: tuple[TradeOutcome, ...]
    metrics: ResearchMetrics

    def validate(self) -> None:
        if not isinstance(self.execution_semantics, ExecutionSemantics):
            raise ExecutionKernelError("execution semantics must be explicit")
        if not isinstance(self.ambiguity_policy, AmbiguityPolicy):
            raise ExecutionKernelError("ambiguity policy must be explicit")
        for trade in self.trades:
            trade.validate()
        self.metrics.validate()


def _hit_levels(
    instruction: EntryInstruction,
    event: MarketEvent,
) -> tuple[bool, bool]:
    if event.high is None or event.low is None:
        return False, False
    if instruction.side is Side.BUY:
        return event.low <= instruction.stop_loss, event.high >= instruction.take_profit
    return event.high >= instruction.stop_loss, event.low <= instruction.take_profit


def _decisive_outcome(
    instruction: EntryInstruction,
    reason: str,
    sequence: int,
    exit_price: float,
) -> TradeOutcome:
    if instruction.side is Side.BUY:
        r = (exit_price - instruction.entry_price) / instruction.risk_price
    else:
        r = (instruction.entry_price - exit_price) / instruction.risk_price
    return TradeOutcome(
        trade_id=instruction.trade_id,
        side=instruction.side,
        entry_price=instruction.entry_price,
        exit_price=exit_price,
        exit_reason=reason,
        net_r=r,
        ambiguous=False,
        entry_sequence=sequence - 1,
        exit_sequence=sequence,
    )


class HistoricalExecutionKernel:
    """Generic deterministic execution kernel, independent of strategy geometry."""

    def execute(
        self,
        *,
        semantics: ExecutionSemantics,
        instructions: Sequence[EntryInstruction],
        events: Sequence[MarketEvent],
        ambiguity_policy: AmbiguityPolicy = AmbiguityPolicy.BLOCK,
    ) -> KernelResult:
        if not isinstance(semantics, ExecutionSemantics):
            raise ExecutionKernelError("execution semantics must be explicit")
        if not isinstance(ambiguity_policy, AmbiguityPolicy):
            raise ExecutionKernelError("ambiguity policy must be explicit")
        for instruction in instructions:
            instruction.validate()
        ordered = list(events)
        for event in ordered:
            event.validate()
        if any(
            (ordered[i].timestamp, ordered[i].sequence)
            >= (ordered[i + 1].timestamp, ordered[i + 1].sequence)
            for i in range(len(ordered) - 1)
        ):
            raise ExecutionKernelError("market events must be strictly chronological")

        outcomes: list[TradeOutcome] = []
        for instruction in instructions:
            entry_event = next(
                (event for event in ordered if self._entry_seen(instruction, event)),
                None,
            )
            if entry_event is None:
                continue
            for event in ordered:
                if (event.timestamp, event.sequence) < (
                    entry_event.timestamp,
                    entry_event.sequence,
                ):
                    continue
                stop_hit, target_hit = _hit_levels(instruction, event)
                if not stop_hit and not target_hit:
                    continue

                if stop_hit and target_hit:
                    if ambiguity_policy is AmbiguityPolicy.BLOCK:
                        outcomes.append(
                            TradeOutcome(
                                trade_id=instruction.trade_id,
                                side=instruction.side,
                                entry_price=instruction.entry_price,
                                exit_price=None,
                                exit_reason="AMBIGUOUS_SAME_EVENT",
                                net_r=None,
                                ambiguous=True,
                                entry_sequence=entry_event.sequence,
                                exit_sequence=event.sequence,
                            )
                        )
                        break
                    if ambiguity_policy is AmbiguityPolicy.STOP_FIRST:
                        outcomes.append(_decisive_outcome(
                            instruction, "STOP", event.sequence, instruction.stop_loss
                        ))
                        break
                    outcomes.append(_decisive_outcome(
                        instruction, "TARGET", event.sequence, instruction.take_profit
                    ))
                    break

                if stop_hit:
                    outcomes.append(_decisive_outcome(
                        instruction, "STOP", event.sequence, instruction.stop_loss
                    ))
                    break
                outcomes.append(_decisive_outcome(
                    instruction, "TARGET", event.sequence, instruction.take_profit
                ))
                break

        metrics = _metrics(outcomes)
        result = KernelResult(
            execution_semantics=semantics,
            ambiguity_policy=ambiguity_policy,
            trades=tuple(outcomes),
            metrics=metrics,
        )
        result.validate()
        return result

    @staticmethod
    def _entry_seen(instruction: EntryInstruction, event: MarketEvent) -> bool:
        if instruction.side is Side.BUY:
            return (event.ask if event.ask is not None else event.high) is not None and (
                event.ask if event.ask is not None else event.high
            ) >= instruction.entry_price
        return (event.bid if event.bid is not None else event.low) is not None and (
            event.bid if event.bid is not None else event.low
        ) <= instruction.entry_price


def _metrics(outcomes: Sequence[TradeOutcome]) -> ResearchMetrics:
    decisive = [trade for trade in outcomes if not trade.ambiguous]
    wins = [trade for trade in decisive if (trade.net_r or 0.0) > 0]
    losses = [trade for trade in decisive if (trade.net_r or 0.0) <= 0]
    gross_profit = sum(trade.net_r or 0.0 for trade in wins)
    gross_loss = sum(trade.net_r or 0.0 for trade in losses)
    net_r = sum(trade.net_r or 0.0 for trade in decisive)

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for trade in decisive:
        equity += trade.net_r or 0.0
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    profit_factor = None if gross_loss == 0 else gross_profit / abs(gross_loss)
    win_rate = 0.0 if not decisive else len(wins) / len(decisive)
    return ResearchMetrics(
        trades=len(outcomes),
        decisive_trades=len(decisive),
        wins=len(wins),
        losses=len(losses),
        ambiguous=len(outcomes) - len(decisive),
        win_rate=win_rate,
        net_r=net_r,
        profit_factor=profit_factor,
        max_drawdown_r=max_dd,
        gross_profit_r=gross_profit,
        gross_loss_r=gross_loss,
    )
