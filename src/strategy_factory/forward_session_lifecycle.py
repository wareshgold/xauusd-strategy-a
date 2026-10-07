from __future__ import annotations

"""Immutable demo-forward session lifecycle and reconciliation contracts.

Research/operations boundary only. This module never generates signals,
places orders, changes strategy parameters, or authorizes production.
"""

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any

from .forward_session_factory import DemoForwardSession


class ForwardSessionLifecycleError(ValueError):
    """Raised when a demo-forward lifecycle transition is invalid."""


class ForwardSessionState(str, Enum):
    PREPARED = "PREPARED"
    STARTED = "STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


_ALLOWED_TRANSITIONS = {
    ForwardSessionState.PREPARED: {ForwardSessionState.STARTED},
    ForwardSessionState.STARTED: {ForwardSessionState.RUNNING},
    ForwardSessionState.RUNNING: {ForwardSessionState.COMPLETED},
    ForwardSessionState.COMPLETED: set(),
}


@dataclass(frozen=True)
class DemoForwardSessionEvent:
    sequence: int
    session_id: str
    session_fingerprint: str
    strategy_id: str
    strategy_revision: str
    manifest_revision: str
    execution_semantics: str
    state: ForwardSessionState
    occurred_utc: str
    post_holdout_tuning: bool
    production_decision: bool
    event_fingerprint: str

    def _payload(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "session_id": self.session_id,
            "session_fingerprint": self.session_fingerprint,
            "strategy_id": self.strategy_id,
            "strategy_revision": self.strategy_revision,
            "manifest_revision": self.manifest_revision,
            "execution_semantics": self.execution_semantics,
            "state": self.state.value,
            "occurred_utc": self.occurred_utc,
            "post_holdout_tuning": self.post_holdout_tuning,
            "production_decision": self.production_decision,
        }

    def validate(self) -> None:
        if self.sequence < 1 or not self.session_id:
            raise ForwardSessionLifecycleError("session event identity is incomplete")
        if len(self.session_fingerprint) != 64:
            raise ForwardSessionLifecycleError("session_fingerprint must be SHA-256")
        if not self.strategy_id or not self.strategy_revision:
            raise ForwardSessionLifecycleError("session event strategy identity is incomplete")
        if not self.manifest_revision or not self.execution_semantics:
            raise ForwardSessionLifecycleError("session event contract is incomplete")
        if self.post_holdout_tuning:
            raise ForwardSessionLifecycleError("post-holdout tuning is forbidden")
        if self.production_decision:
            raise ForwardSessionLifecycleError("session lifecycle cannot authorize production")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        if self.event_fingerprint != expected:
            raise ForwardSessionLifecycleError("session event fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self._payload(), "event_fingerprint": self.event_fingerprint}


class DemoForwardSessionLifecycle:
    """Append-only in-memory lifecycle ledger for one frozen session."""

    def __init__(self, session: DemoForwardSession) -> None:
        session.validate()
        self.session = session
        self._events: list[DemoForwardSessionEvent] = []

    @property
    def state(self) -> ForwardSessionState:
        if not self._events:
            return ForwardSessionState.PREPARED
        return self._events[-1].state

    def _append(self, state: ForwardSessionState, occurred_utc: str) -> DemoForwardSessionEvent:
        current = self.state
        if state not in _ALLOWED_TRANSITIONS[current]:
            raise ForwardSessionLifecycleError(
                f"invalid lifecycle transition {current.value} -> {state.value}"
            )
        event = DemoForwardSessionEvent(
            sequence=len(self._events) + 1,
            session_id=self.session.session_id,
            session_fingerprint=self.session.fingerprint,
            strategy_id=self.session.strategy_id,
            strategy_revision=self.session.strategy_revision,
            manifest_revision=self.session.manifest_revision,
            execution_semantics=self.session.execution_semantics,
            state=state,
            occurred_utc=occurred_utc,
            post_holdout_tuning=False,
            production_decision=False,
            event_fingerprint="",
        )
        fingerprint = hashlib.sha256(
            json.dumps(event._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        event = DemoForwardSessionEvent(**event._payload(), event_fingerprint=fingerprint)
        event.validate()
        self._events.append(event)
        return event

    def start(self, *, occurred_utc: str) -> DemoForwardSessionEvent:
        return self._append(ForwardSessionState.STARTED, occurred_utc)

    def run(self, *, occurred_utc: str) -> DemoForwardSessionEvent:
        return self._append(ForwardSessionState.RUNNING, occurred_utc)

    def complete(self, *, occurred_utc: str) -> DemoForwardSessionEvent:
        return self._append(ForwardSessionState.COMPLETED, occurred_utc)

    def assert_frozen_identity(
        self,
        *,
        strategy_revision: str,
        manifest_revision: str,
        execution_semantics: str,
        post_holdout_tuning: bool = False,
    ) -> None:
        if post_holdout_tuning:
            raise ForwardSessionLifecycleError("post-holdout tuning is forbidden after session preparation")
        if strategy_revision != self.session.strategy_revision:
            raise ForwardSessionLifecycleError("strategy revision changed during forward session")
        if manifest_revision != self.session.manifest_revision:
            raise ForwardSessionLifecycleError("manifest revision changed during forward session")
        if execution_semantics != self.session.execution_semantics:
            raise ForwardSessionLifecycleError("execution semantics changed during forward session")

    def entries(self) -> tuple[DemoForwardSessionEvent, ...]:
        return tuple(self._events)


@dataclass(frozen=True)
class MT5ReconciliationReceipt:
    """Audit-only result binding MT5 reconciliation to a frozen session."""

    reconciliation_revision: str
    reconciliation_id: str
    session_id: str
    session_fingerprint: str
    broker_server: str
    symbol: str
    reconciled: bool
    observed_positions: int
    matched_positions: int
    mismatched_positions: int
    detail: str
    fingerprint: str

    def _payload(self) -> dict[str, Any]:
        return {
            "reconciliation_revision": self.reconciliation_revision,
            "reconciliation_id": self.reconciliation_id,
            "session_id": self.session_id,
            "session_fingerprint": self.session_fingerprint,
            "broker_server": self.broker_server,
            "symbol": self.symbol,
            "reconciled": self.reconciled,
            "observed_positions": self.observed_positions,
            "matched_positions": self.matched_positions,
            "mismatched_positions": self.mismatched_positions,
            "detail": self.detail,
        }

    def validate(self) -> None:
        if not self.reconciliation_id or not self.session_id:
            raise ForwardSessionLifecycleError("reconciliation identity is incomplete")
        if len(self.session_fingerprint) != 64:
            raise ForwardSessionLifecycleError("session_fingerprint must be SHA-256")
        if not self.broker_server or not self.symbol:
            raise ForwardSessionLifecycleError("MT5 reconciliation endpoint identity is incomplete")
        if min(self.observed_positions, self.matched_positions, self.mismatched_positions) < 0:
            raise ForwardSessionLifecycleError("reconciliation counts cannot be negative")
        if self.matched_positions + self.mismatched_positions != self.observed_positions:
            raise ForwardSessionLifecycleError("reconciliation counts are inconsistent")
        expected = hashlib.sha256(
            json.dumps(self._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        if self.fingerprint != expected:
            raise ForwardSessionLifecycleError("reconciliation fingerprint mismatch")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}


def bind_mt5_reconciliation(
    *,
    session: DemoForwardSession,
    lifecycle: DemoForwardSessionLifecycle,
    reconciliation_id: str,
    broker_server: str,
    symbol: str,
    observed_positions: int,
    matched_positions: int,
    mismatched_positions: int,
    detail: str = "MT5 reconciliation bound to completed demo-forward session",
) -> MT5ReconciliationReceipt:
    session.validate()
    if lifecycle.session.fingerprint != session.fingerprint:
        raise ForwardSessionLifecycleError("lifecycle is bound to a different session")
    if lifecycle.state is not ForwardSessionState.COMPLETED:
        raise ForwardSessionLifecycleError("MT5 reconciliation requires COMPLETED forward session")
    if any(
        event.session_fingerprint != session.fingerprint
        or event.strategy_revision != session.strategy_revision
        or event.manifest_revision != session.manifest_revision
        or event.execution_semantics != session.execution_semantics
        for event in lifecycle.entries()
    ):
        raise ForwardSessionLifecycleError("session lifecycle identity drift detected")

    receipt = MT5ReconciliationReceipt(
        reconciliation_revision="MT5-RECONCILIATION-1",
        reconciliation_id=reconciliation_id,
        session_id=session.session_id,
        session_fingerprint=session.fingerprint,
        broker_server=broker_server,
        symbol=symbol,
        reconciled=mismatched_positions == 0,
        observed_positions=observed_positions,
        matched_positions=matched_positions,
        mismatched_positions=mismatched_positions,
        detail=detail,
        fingerprint="",
    )
    fingerprint = hashlib.sha256(
        json.dumps(receipt._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    final = MT5ReconciliationReceipt(**receipt._payload(), fingerprint=fingerprint)
    final.validate()
    return final
