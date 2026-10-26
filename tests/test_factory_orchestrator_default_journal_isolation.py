from __future__ import annotations

from strategy_factory.orchestrator import FactoryOrchestrator
from strategy_factory.worker import FactoryWorker, FactoryWorkerFleet


def test_orchestrator_default_journal_is_in_memory() -> None:
    """Implicit construction must never write to the operator's runtime journal."""
    orchestrator = FactoryOrchestrator(
        fleet=FactoryWorkerFleet(workers=[FactoryWorker(worker_id="W-TEST")])
    )

    assert orchestrator.events.path is None
