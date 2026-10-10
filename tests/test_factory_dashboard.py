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


def _dashboard_test_base(monkeypatch):
    monkeypatch.setattr(dashboard, "DEMO_MODE", False)
    monkeypatch.setattr(dashboard, "git_state", lambda: {
        "branch": "research/factory-candidate-lab-20261010",
        "head": "test",
        "origin": "test",
        "root": "test-root",
    })
    monkeypatch.setattr(dashboard, "worker_state", lambda: ([], "OFFLINE"))


def test_dashboard_shows_valid_read_only_journal_audit(monkeypatch):
    _dashboard_test_base(monkeypatch)
    monkeypatch.setattr(
        dashboard,
        "inspect_worker_journal_file_consistency",
        lambda workers: {
            "status": "CONSISTENT",
            "journal_event_count": 3,
            "finding_count": 0,
            "findings": [],
            "automatic_action_performed": False,
            "journal_integrity": {
                "status": "VALID",
                "path": "runtime/factory_job_events.jsonl",
                "sha256": "a" * 64,
                "automatic_repair_performed": False,
            },
        },
    )

    page = dashboard.html_page()

    assert "JOB JOURNAL INTEGRITY · READ-ONLY AUDIT" in page
    assert "CONSISTENT" in page
    assert "VALID" in page
    assert "runtime/factory_job_events.jsonl" in page
    assert "a" * 64 in page
    assert "READ ONLY · NO REPAIR / RETRY" in page


def test_dashboard_surfaces_invalid_journal_as_review_required(monkeypatch):
    _dashboard_test_base(monkeypatch)
    monkeypatch.setattr(
        dashboard,
        "inspect_worker_journal_file_consistency",
        lambda workers: {
            "status": "REVIEW_REQUIRED",
            "journal_event_count": None,
            "finding_count": 1,
            "findings": [{
                "code": "JOURNAL_INTEGRITY_REVIEW_REQUIRED",
                "detail": "invalid journal <payload>",
            }],
            "automatic_action_performed": False,
            "journal_integrity": {
                "status": "INVALID_REVIEW_REQUIRED",
                "path": "runtime/factory_job_events.jsonl",
                "sha256": "b" * 64,
                "automatic_repair_performed": False,
            },
        },
    )

    page = dashboard.html_page()

    assert "REVIEW_REQUIRED" in page
    assert "INVALID_REVIEW_REQUIRED" in page
    assert "JOURNAL_INTEGRITY_REVIEW_REQUIRED" in page
    assert "invalid journal &lt;payload&gt;" in page
    assert "NO REPAIR / RETRY" in page
    assert "invalid journal <payload>" not in page
