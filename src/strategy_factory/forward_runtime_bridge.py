from __future__ import annotations

"""Research-only bridge from a frozen demo-forward session to a real runner."""

from dataclasses import dataclass
from typing import Any, Callable

from .forward_session_factory import DemoForwardSession
from .forward_session_lifecycle import (
    DemoForwardSessionLifecycle,
    MT5ReconciliationReceipt,
    bind_mt5_reconciliation,
)


class ForwardRuntimeBridgeError(RuntimeError):
    """Raised when a forward runtime cannot be bound to its frozen session."""


@dataclass(frozen=True)
class ForwardRuntimeResult:
    session_id: str
    session_fingerprint: str
    handoff_fingerprint: str
    lifecycle_events: tuple[Any, ...]
    reconciliation: MT5ReconciliationReceipt
    runner_result: Any


def run_bound_forward(
    *,
    session: DemoForwardSession,
    run_forward: Callable[[], Any],
    reconcile: Callable[[Any], dict[str, Any]],
    started_utc: str,
    running_utc: str,
    completed_utc: str,
) -> ForwardRuntimeResult:
    """Run an injected forward adapter under a frozen Factory session.

    run_forward is the existing real forward runner/adapter. reconcile returns
    observed MT5 facts only; this bridge does not inspect trades or decide
    whether the strategy is profitable.
    """
    session.validate()
    lifecycle = DemoForwardSessionLifecycle(session)
    lifecycle.start(occurred_utc=started_utc)
    lifecycle.assert_frozen_identity(
        strategy_revision=session.strategy_revision,
        manifest_revision=session.manifest_revision,
        execution_semantics=session.execution_semantics,
    )
    lifecycle.run(occurred_utc=running_utc)

    try:
        runner_result = run_forward()
    except Exception as exc:
        raise ForwardRuntimeBridgeError(
            f"bound forward runner failed for session {session.session_id!r}: {exc}"
        ) from exc

    lifecycle.assert_frozen_identity(
        strategy_revision=session.strategy_revision,
        manifest_revision=session.manifest_revision,
        execution_semantics=session.execution_semantics,
    )
    lifecycle.complete(occurred_utc=completed_utc)

    try:
        reconciliation = reconcile(runner_result)
    except Exception as exc:
        raise ForwardRuntimeBridgeError(
            f"MT5 reconciliation failed for session {session.session_id!r}: {exc}"
        ) from exc

    required = {
        "reconciliation_id",
        "broker_server",
        "symbol",
        "observed_positions",
        "matched_positions",
        "mismatched_positions",
    }
    missing = sorted(required.difference(reconciliation))
    if missing:
        raise ForwardRuntimeBridgeError(
            "reconciliation adapter omitted required observed fields: "
            + ", ".join(missing)
        )

    receipt = bind_mt5_reconciliation(
        session=session,
        lifecycle=lifecycle,
        reconciliation_id=str(reconciliation["reconciliation_id"]),
        broker_server=str(reconciliation["broker_server"]),
        symbol=str(reconciliation["symbol"]),
        observed_positions=int(reconciliation["observed_positions"]),
        matched_positions=int(reconciliation["matched_positions"]),
        mismatched_positions=int(reconciliation["mismatched_positions"]),
        detail=str(
            reconciliation.get(
                "detail",
                "MT5 reconciliation bound by Forward Runtime Bridge",
            )
        ),
    )
    return ForwardRuntimeResult(
        session_id=session.session_id,
        session_fingerprint=session.fingerprint,
        handoff_fingerprint=session.handoff_fingerprint,
        lifecycle_events=lifecycle.entries(),
        reconciliation=receipt,
        runner_result=runner_result,
    )
