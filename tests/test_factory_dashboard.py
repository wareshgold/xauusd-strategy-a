import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts import factory_dashboard as dashboard


def test_station_for_prefers_declared_station_over_ambiguous_detail():
    worker = {
        "station": "robustness",
        "job_type": "TELEMETRY_DEMO_ONLY",
        "detail": "DEMO_ONLY: Robustness; lifecycle telemetry smoke test.",
        "phase": "ROBUSTNESS",
    }

    assert dashboard.station_for(worker) == "robustness"


def test_completed_demo_snapshot_is_not_labeled_as_live_outage(monkeypatch):
    workers = [
        {
            "worker_id": "demo-robustness",
            "job_id": "FACTORY-DEMO-TEST-05",
            "job_type": "TELEMETRY_DEMO_ONLY",
            "station": "robustness",
            "state": "COMPLETED",
            "progress": 100,
            "heartbeat_utc": "2026-10-10T07:28:52+00:00",
            "telemetry_health": "STALE",
            "heartbeat_age_s": 105,
            "detail": "DEMO_ONLY: Robustness; lifecycle telemetry smoke test.",
            "output_artifact": "demo://test",
        }
    ]
    monkeypatch.setattr(dashboard, "DEMO_MODE", True)
    monkeypatch.setattr(dashboard, "git_state", lambda: {
        "branch": "research/factory-candidate-lab-20261010",
        "head": "test",
        "origin": "test",
        "root": "test-root",
    })
    monkeypatch.setattr(dashboard, "worker_state", lambda: (workers, "STALE"))

    page = dashboard.html_page()

    assert "DEMO SNAPSHOT · RUN COMPLETE" in page
    assert "FACTORY TELEMETRY NEEDS ATTENTION" not in page
    assert "ROBUSTNESS LAB" in page
