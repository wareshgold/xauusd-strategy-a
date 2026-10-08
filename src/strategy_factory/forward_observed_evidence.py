from __future__ import annotations

"""Immutable observed-evidence contract for a completed demo-forward stream.

This module records only facts already emitted by the forward event ledger.
It deliberately does not convert observations into R, win/loss semantics,
profitability thresholds, parameter choices, canonical rules, or production
authorization.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping


class ForwardObservedEvidenceError(ValueError):
    """Raised when observed forward evidence is incomplete or inconsistent."""


@dataclass(frozen=True)
class ForwardTradeObservation:
    """One immutable observed lifecycle-close record."""

    deal_id: int
    order_id: int
    position_id: int
    signal_id: str | None
    entry_price: float | None
    exit_price: float | None
    profit: float
    commission: float
    swap: float
    fee: float
    net: float
    pips_result: float | None

    def validate(self) -> None:
        if self.deal_id <= 0 or self.order_id <= 0 or self.position_id <= 0:
            raise ForwardObservedEvidenceError("trade observation identity is incomplete")
        if self.net != self.profit + self.commission + self.swap + self.fee:
            raise ForwardObservedEvidenceError("trade observation net does not equal observed components")
        for name, value in {
            "profit": self.profit,
            "commission": self.commission,
            "swap": self.swap,
            "fee": self.fee,
            "net": self.net,
        }.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ForwardObservedEvidenceError(f"{name} must be numeric")
        if self.pips_result is not None and not isinstance(
            self.pips_result, (int, float)
        ):
            raise ForwardObservedEvidenceError("pips_result must be numeric or None")


@dataclass(frozen=True)
class ForwardObservedEvidence:
    """Immutable forward observations bound to one frozen Factory session."""

    evidence_revision: str
    session_id: str
    session_fingerprint: str
    handoff_fingerprint: str
    strategy_revision: str
    manifest_revision: str
    execution_semantics: str
    broker_server: str
    symbol: str
    runner_completed: bool
    reconciliation_id: str
    observed_positions: int
    matched_positions: int
    mismatched_positions: int
    trades: tuple[ForwardTradeObservation, ...]
    fingerprint: str

    @staticmethod
    def _payload(values: Mapping[str, Any]) -> bytes:
        return json.dumps(
            values, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "evidence_revision": self.evidence_revision,
            "session_id": self.session_id,
            "session_fingerprint": self.session_fingerprint,
            "handoff_fingerprint": self.handoff_fingerprint,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "execution_semantics": self.execution_semantics,
            "broker_server": self.broker_server,
            "symbol": self.symbol,
            "runner_completed": self.runner_completed,
            "reconciliation_id": self.reconciliation_id,
            "observed_positions": self.observed_positions,
            "matched_positions": self.matched_positions,
            "mismatched_positions": self.mismatched_positions,
            "trades": [self._trade_dict(t) for t in self.trades],
        }

    @staticmethod
    def _trade_dict(trade: ForwardTradeObservation) -> dict[str, Any]:
        return {
            "deal_id": trade.deal_id,
            "order_id": trade.order_id,
            "position_id": trade.position_id,
            "signal_id": trade.signal_id,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "profit": trade.profit,
            "commission": trade.commission,
            "swap": trade.swap,
            "fee": trade.fee,
            "net": trade.net,
            "pips_result": trade.pips_result,
        }

    def validate(self) -> None:
        required = (
            self.evidence_revision,
            self.session_id,
            self.session_fingerprint,
            self.handoff_fingerprint,
            self.strategy_revision,
            self.manifest_revision,
            self.execution_semantics,
            self.broker_server,
            self.symbol,
            self.reconciliation_id,
        )
        if any(not value for value in required):
            raise ForwardObservedEvidenceError("forward evidence identity is incomplete")
        if not self.runner_completed:
            raise ForwardObservedEvidenceError("incomplete forward runner cannot produce observed evidence")
        counts = (
            self.observed_positions,
            self.matched_positions,
            self.mismatched_positions,
        )
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in counts):
            raise ForwardObservedEvidenceError("reconciliation counts must be non-negative integers")
        if self.matched_positions + self.mismatched_positions > self.observed_positions:
            raise ForwardObservedEvidenceError("reconciliation counts exceed observed positions")
        seen_deals: set[int] = set()
        for trade in self.trades:
            trade.validate()
            if trade.deal_id in seen_deals:
                raise ForwardObservedEvidenceError("duplicate trade observation deal_id")
            seen_deals.add(trade.deal_id)
        expected = hashlib.sha256(
            self._payload(self._fingerprint_payload())
        ).hexdigest()
        if self.fingerprint != expected:
            raise ForwardObservedEvidenceError("forward observed evidence fingerprint mismatch")

    def as_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        self.validate()
        data = self._fingerprint_payload()
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data


def build_forward_observed_evidence(
    *,
    session_id: str,
    session_fingerprint: str,
    handoff_fingerprint: str,
    strategy_revision: str,
    manifest_revision: str,
    execution_semantics: str,
    broker_server: str,
    symbol: str,
    runner_completed: bool,
    reconciliation_id: str,
    observed_positions: int,
    matched_positions: int,
    mismatched_positions: int,
    trades: Iterable[ForwardTradeObservation],
    evidence_revision: str = "FORWARD-OBSERVED-EVIDENCE-1",
) -> ForwardObservedEvidence:
    result = ForwardObservedEvidence(
        evidence_revision=evidence_revision,
        session_id=session_id,
        session_fingerprint=session_fingerprint,
        handoff_fingerprint=handoff_fingerprint,
        strategy_revision=strategy_revision,
        manifest_revision=manifest_revision,
        execution_semantics=execution_semantics,
        broker_server=broker_server,
        symbol=symbol,
        runner_completed=runner_completed,
        reconciliation_id=reconciliation_id,
        observed_positions=observed_positions,
        matched_positions=matched_positions,
        mismatched_positions=mismatched_positions,
        trades=tuple(trades),
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        result._payload(result._fingerprint_payload())
    ).hexdigest()
    final = ForwardObservedEvidence(**{**result.__dict__, "fingerprint": fingerprint})
    final.validate()
    return final


def observations_from_lifecycle_events(
    events: Iterable[Mapping[str, Any]],
) -> tuple[ForwardTradeObservation, ...]:
    """Extract close observations without inferring missing execution facts."""
    observations: list[ForwardTradeObservation] = []
    for event in events:
        if event.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        try:
            entry = int(event.get("entry", -1))
        except (TypeError, ValueError) as exc:
            raise ForwardObservedEvidenceError("lifecycle entry is not an integer") from exc
        if entry == 0:
            continue
        required = ("deal", "order", "position", "profit", "commission", "swap", "net")
        missing = [name for name in required if event.get(name) is None]
        if missing:
            raise ForwardObservedEvidenceError(
                "lifecycle close omitted required observed fields: " + ", ".join(missing)
            )
        observations.append(
            ForwardTradeObservation(
                deal_id=int(event["deal"]),
                order_id=int(event["order"]),
                position_id=int(event["position"]),
                signal_id=(
                    str(event["signal_id"])
                    if event.get("signal_id") is not None
                    else None
                ),
                entry_price=(
                    float(event["entry_price"])
                    if event.get("entry_price") is not None
                    else None
                ),
                exit_price=(
                    float(event["exit_price"])
                    if event.get("exit_price") is not None
                    else None
                ),
                profit=float(event["profit"]),
                commission=float(event["commission"]),
                swap=float(event["swap"]),
                fee=float(event.get("fee", 0.0) or 0.0),
                net=float(event["net"]),
                pips_result=(
                    float(event["pips_result"])
                    if event.get("pips_result") is not None
                    else None
                ),
            )
        )
    return tuple(observations)
