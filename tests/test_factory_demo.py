from datetime import datetime, timezone

from scripts.run_factory_demo import build_demo_workers
from strategy_factory.starnet_adapter import build_world_state


def test_demo_workers_use_only_valid_starnet_stations():
    now = datetime(2026, 10, 10, tzinfo=timezone.utc)
    workers = build_demo_workers("FACTORY-DEMO-TEST", now)

    state = build_world_state(workers)

    assert len(state.workers) == 9
    assert all(worker.job_type == "TELEMETRY_DEMO_ONLY" for worker in state.workers)
    assert state.production_locked is True
    assert state.buy_sell_generation == 0
    assert {worker.station for worker in state.workers} <= {
        "discovery", "stability", "robustness", "holdout", "forward", "idle"
    }
