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


def test_completed_synthetic_e2e_snapshot_is_not_labeled_as_live_outage(monkeypatch):
    workers = [
        {
            "worker_id": "SYNTH-W01",
            "job_id": "SYNTH-E2E-TEST-01",
            "job_type": "SYNTHETIC_FACTORY_E2E_V1",
            "station": "discovery",
            "phase": "SYNTHETIC_E2E",
            "state": "COMPLETED",
            "progress": 100,
            "heartbeat_utc": "2026-10-11T05:06:49+00:00",
            "telemetry_health": "OFFLINE",
            "heartbeat_age_s": 3600,
            "detail": "Research run accepted",
            "output_artifact": "SYNTH-EVIDENCE-SYNTH-E2E-TEST-01",
        }
    ]
    monkeypatch.setattr(dashboard, "DEMO_MODE", True)
    monkeypatch.setattr(dashboard, "git_state", lambda: {
        "branch": "research/factory-candidate-lab-20261010",
        "head": "test",
        "origin": "test",
        "root": "test-root",
    })
    monkeypatch.setattr(dashboard, "worker_state", lambda: (workers, "OFFLINE"))

    page = dashboard.html_page()

    assert "DEMO SNAPSHOT · RUN COMPLETE" in page
    assert "FACTORY TELEMETRY NEEDS ATTENTION" not in page
    assert "DISCOVERY LAB" in page


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

def test_dashboard_surfaces_missing_journal_as_review_required(monkeypatch):
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
                "detail": "journal file is missing",
            }],
            "automatic_action_performed": False,
            "journal_integrity": {
                "status": "MISSING_REVIEW_REQUIRED",
                "path": "runtime/factory_job_events.jsonl",
                "sha256": None,
                "automatic_repair_performed": False,
            },
        },
    )

    page = dashboard.html_page()

    assert "REVIEW_REQUIRED" in page
    assert "MISSING_REVIEW_REQUIRED" in page
    assert "JOURNAL_INTEGRITY_REVIEW_REQUIRED" in page
    assert "NO REPAIR / RETRY" in page


def test_dashboard_surfaces_unreadable_journal_as_review_required(monkeypatch):
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
                "detail": "journal cannot be read",
            }],
            "automatic_action_performed": False,
            "journal_integrity": {
                "status": "UNREADABLE_REVIEW_REQUIRED",
                "path": "runtime/factory_job_events.jsonl",
                "sha256": None,
                "automatic_repair_performed": False,
            },
        },
    )

    page = dashboard.html_page()

    assert "REVIEW_REQUIRED" in page
    assert "UNREADABLE_REVIEW_REQUIRED" in page
    assert "JOURNAL_INTEGRITY_REVIEW_REQUIRED" in page
    assert "NO REPAIR / RETRY" in page



def test_completed_worker_card_does_not_label_last_update_as_heartbeat():
    worker = {
        "worker_id": "done-01",
        "station": "discovery",
        "state": "COMPLETED",
        "progress": 100,
        "telemetry_health": "OFFLINE",
        "heartbeat_age_s": 4672,
    }

    card = dashboard.worker_card(worker, 1)

    assert "COMPLETED" in card
    assert "HB 4672s" not in card
    assert "LAST UPDATE" not in card


def test_running_worker_card_shows_heartbeat_age():
    worker = {
        "worker_id": "run-01",
        "station": "discovery",
        "state": "RUNNING",
        "progress": 40,
        "telemetry_health": "LIVE",
        "heartbeat_age_s": 12,
    }

    card = dashboard.worker_card(worker, 1)

    assert "HB 12s" in card


def test_git_state_labels_detached_head_and_missing_upstream(monkeypatch):
    def fake_run(*args):
        if args == ("git", "branch", "--show-current"):
            return ""
        if args == ("git", "rev-parse", "--short", "HEAD"):
            return "9d3f1ad"
        if args == ("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"):
            return ""
        return ""

    monkeypatch.setattr(dashboard, "_run", fake_run)

    state = dashboard.git_state()

    assert state["branch"] == "DETACHED"
    assert state["head"] == "9d3f1ad"
    assert state["origin"] == "NOT CONFIGURED"


def test_station_card_separates_lifecycle_counts_and_only_activates_live_worker():
    workers = [
        {"worker_id": "w-run", "station": "discovery", "state": "RUNNING", "telemetry_health": "LIVE"},
        {"worker_id": "w-stale", "station": "discovery", "state": "HEARTBEAT", "telemetry_health": "STALE"},
        {"worker_id": "w-queue", "station": "discovery", "state": "QUEUED", "telemetry_health": "LIVE"},
        {"worker_id": "w-done", "station": "discovery", "state": "COMPLETED", "telemetry_health": "OFFLINE"},
        {"worker_id": "w-fail", "station": "discovery", "state": "FAILED", "telemetry_health": "OFFLINE"},
    ]

    card = dashboard.station_card("discovery", workers)

    assert "5 assigned" in card
    assert "2 running" in card
    assert "1 queued" in card
    assert "1 completed" in card
    assert "1 failed" in card
    assert "station room-active" in card
    assert card.count("station-unit active") == 1


def test_station_room_stays_idle_without_running_live_heartbeat():
    workers = [
        {"worker_id": "w-done", "station": "discovery", "state": "COMPLETED", "telemetry_health": "OFFLINE"},
        {"worker_id": "w-stale", "station": "discovery", "state": "RUNNING", "telemetry_health": "STALE"},
    ]

    card = dashboard.station_card("discovery", workers)

    assert "station room-idle" in card
    assert "2 assigned" in card
    assert "1 running" in card


def test_station_world_animation_requires_live_heartbeat():
    workers = [
        {
            "worker_id": "w-live",
            "station": "discovery",
            "state": "RUNNING",
            "progress": 10,
            "telemetry_health": "LIVE",
        },
        {
            "worker_id": "w-stale",
            "station": "stability",
            "state": "RUNNING",
            "progress": 20,
            "telemetry_health": "STALE",
        },
    ]

    rendered = dashboard.station_world(workers)

    assert '"telemetry_health": "LIVE"' in rendered
    assert '"telemetry_health": "STALE"' in rendered
    assert 'w.telemetry_health==="LIVE"' in rendered


def test_station_and_worker_cards_normalize_whitespace_in_state_and_health():
    worker = {
        "worker_id": "w-padded",
        "station": "discovery",
        "state": " RUNNING ",
        "progress": 25,
        "telemetry_health": " LIVE ",
        "heartbeat_age_s": 8,
    }

    card = dashboard.worker_card(worker, 1)
    station = dashboard.station_card("discovery", [worker])
    world = dashboard.station_world([worker])

    assert "RUNNING" in card
    assert "HB 8s" in card
    assert "1 running" in station
    assert "station room-active" in station
    assert station.count("station-unit active") == 1
    assert '"telemetry_health": "LIVE"' in world
    assert 'w.telemetry_health==="LIVE"' in world


def test_telemetry_panels_normalize_whitespace_in_active_and_feed_state_labels():
    workers = [
        {
            "worker_id": "w-padded",
            "job_id": "JOB-PADDED",
            "state": " RUNNING ",
            "progress": 35,
            "heartbeat_utc": "2026-11-25T08:00:00+00:00",
            "detail": "Research in progress",
        }
    ]

    panels = dashboard.telemetry_panels(workers)

    assert 'class="job-state ok">RUNNING</span>' in panels
    assert "<span>RUNNING</span>" in panels
    assert " RUNNING " not in panels
