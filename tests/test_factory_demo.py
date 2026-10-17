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


def test_publish_defaults_to_isolated_demo_status(monkeypatch, tmp_path):
    import scripts.run_factory_demo as demo

    published = {}
    monkeypatch.setattr(demo, "ROOT", tmp_path)

    def capture_publish(workers, path):
        published["workers"] = workers
        published["path"] = path

    monkeypatch.setattr(demo, "publish_workers", capture_publish)

    assert demo.main(["--publish"]) == 0
    assert published["path"] == tmp_path / "runtime" / "factory_demo_status.json"
    assert published["path"] != tmp_path / "runtime" / "factory_worker_status.json"
    assert all(worker["job_type"] == "TELEMETRY_DEMO_ONLY" for worker in published["workers"])


def test_publish_refuses_live_worker_status_path(monkeypatch, tmp_path):
    import scripts.run_factory_demo as demo
    import pytest

    monkeypatch.setattr(demo, "ROOT", tmp_path)
    monkeypatch.setattr(
        demo,
        "publish_workers",
        lambda workers, path: pytest.fail("must reject before publishing"),
    )

    with pytest.raises(SystemExit) as exc:
        demo.main([
            "--publish",
            "--status-file",
            str(tmp_path / "runtime" / "factory_worker_status.json"),
        ])

    assert exc.value.code == 2
