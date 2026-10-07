from __future__ import annotations

"""Research-only Factory-bound orchestration for a frozen demo forward.

This layer composes existing contracts. It does not define strategy geometry,
generate BUY/SELL decisions, place orders, or decide profitability.
"""

from dataclasses import dataclass
from typing import Any, Callable

from .forward_runtime_bridge import ForwardRuntimeResult, run_bound_forward
from .forward_session_factory import DemoForwardSession


class ForwardOrchestrationError(RuntimeError):
    """Raised when Factory-bound forward orchestration cannot complete."""


@dataclass(frozen=True)
class FactoryBoundForwardResult:
    """Audit result returned after a bound forward run and broker reconciliation."""

    runtime: ForwardRuntimeResult

    @property
    def session_id(self) -> str:
        return self.runtime.session_id

    @property
    def reconciled(self) -> bool:
        return self.runtime.reconciliation.reconciled

    @property
    def production_decision(self) -> bool:
        return False


def run_factory_bound_forward(
    *,
    session: DemoForwardSession,
    run_forward: Callable[[], Any],
    reconcile: Callable[[Any], dict[str, Any]],
    started_utc: str,
    running_utc: str,
    completed_utc: str,
) -> FactoryBoundForwardResult:
    """Execute an already-frozen demo-forward contract.

    The supplied runner and reconciliation functions are intentionally
    injected. The orchestration layer only composes the existing runtime
    bridge and therefore cannot invent strategy or execution semantics.
    """
    try:
        runtime = run_bound_forward(
            session=session,
            run_forward=run_forward,
            reconcile=reconcile,
            started_utc=started_utc,
            running_utc=running_utc,
            completed_utc=completed_utc,
        )
    except Exception as exc:
        if isinstance(exc, ForwardOrchestrationError):
            raise
        raise ForwardOrchestrationError(
            f"Factory-bound forward failed for session {session.session_id!r}: {exc}"
        ) from exc

    if runtime.reconciliation.session_fingerprint != session.fingerprint:
        raise ForwardOrchestrationError(
            "Factory-bound forward reconciliation fingerprint drifted"
        )
    if runtime.session_fingerprint != session.fingerprint:
        raise ForwardOrchestrationError(
            "Factory-bound forward session fingerprint drifted"
        )
    if runtime.reconciliation.reconciled is False:
        # This is an observed reconciliation result, not a trade decision.
        # Keep it explicit so callers cannot mistake a mismatch for success.
        return FactoryBoundForwardResult(runtime=runtime)

    return FactoryBoundForwardResult(runtime=runtime)
