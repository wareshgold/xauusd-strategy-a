import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts import run_factory_synthetic_e2e as synthetic_run
from strategy_factory.worker_journal_audit import inspect_worker_journal_file_consistency


def test_synthetic_e2e_persists_real_lifecycle_and_isolated_dashboard_snapshot(tmp_path):
    status_path = tmp_path / "factory_demo_status.json"
    journal_path = tmp_path / "factory_demo_job_events.jsonl"
    now = datetime(2026, 10, 11, 12, 30, 0, tzinfo=timezone.utc)

    report = synthetic_run.run_synthetic_e2e(
        status_path=status_path,
        journal_path=journal_path,
        now=now,
    )

    status = json.loads(status_path.read_text(encoding="utf-8"))
    workers = status["workers"]
    audit = inspect_worker_journal_file_consistency(workers, path=journal_path)

    assert report["mode"] == "SYNTHETIC_ONLY"
    assert report["strategy_edge_claim"] is False
    assert report["production_decisions"] == 0
    assert report["result_accepted"] is True
    assert report["handoff_accepted"] is True
    assert report["event_types"] == [
        "QUEUED",
        "DISPATCHED",
        "COMPLETED",
        "HANDOFF_ACCEPTED",
    ]
    assert report["worker_state"] == "COMPLETED"
    assert report["worker_output_artifact"] == report["evidence_id"]
    assert report["dataset_content_sha256"]
    assert status["workers"][0]["job_id"] == report["run_id"]
    assert status["workers"][0]["state"] == "COMPLETED"
    assert audit["status"] == "CONSISTENT"
    assert audit["journal_integrity"]["status"] == "VALID"
    assert audit["journal_event_count"] == 4
    assert audit["finding_count"] == 0
    assert Path(report["journal_path"]) == journal_path.resolve()


def test_demo_dashboard_audits_demo_journal_not_live_journal(tmp_path, monkeypatch):
    from scripts import factory_dashboard as dashboard

    status_path = tmp_path / "factory_demo_status.json"
    journal_path = tmp_path / "factory_demo_job_events.jsonl"
    synthetic_run.run_synthetic_e2e(
        status_path=status_path,
        journal_path=journal_path,
        now=datetime(2026, 10, 11, 12, 31, 0, tzinfo=timezone.utc),
    )
    status = json.loads(status_path.read_text(encoding="utf-8"))

    monkeypatch.setattr(dashboard, "DEMO_MODE", True)
    monkeypatch.setattr(dashboard, "DEMO_JOB_EVENTS_FILE", journal_path)
    monkeypatch.setattr(dashboard, "worker_state", lambda: (status["workers"], "STALE"))

    panel = dashboard.journal_audit_panel(status["workers"])

    assert "CONSISTENT" in panel
    assert "VALID" in panel
    assert str(journal_path.resolve()) in panel
    assert "READ ONLY · NO REPAIR / RETRY" in panel


@pytest.mark.parametrize(
    ("status_path", "journal_path"),
    [
        (synthetic_run.LIVE_STATUS, synthetic_run.DEFAULT_JOURNAL),
        (synthetic_run.DEFAULT_STATUS, synthetic_run.LIVE_JOURNAL),
        (synthetic_run.PRESERVED_DEMO_STATUS, synthetic_run.DEFAULT_JOURNAL),
    ],
)
def test_synthetic_e2e_refuses_live_factory_paths(status_path, journal_path):
    with pytest.raises(ValueError, match="refuses to overwrite live or pre-existing Factory runtime paths"):
        synthetic_run.run_synthetic_e2e(
            status_path=status_path,
            journal_path=journal_path,
            now=datetime(2026, 10, 11, 12, 32, 0, tzinfo=timezone.utc),
        )


@pytest.mark.parametrize("existing_kind", ["status", "journal", "both"])
def test_synthetic_e2e_refuses_to_reuse_existing_outputs_and_preserves_bytes(
    tmp_path, existing_kind
):
    status_path = tmp_path / "existing-status.json"
    journal_path = tmp_path / "existing-journal.jsonl"
    if existing_kind in {"status", "both"}:
        status_path.write_bytes(b'{"user_owned":"status"}\n')
    if existing_kind in {"journal", "both"}:
        journal_path.write_bytes(b'{"user_owned":"journal"}\n')

    status_before = status_path.read_bytes() if status_path.exists() else None
    journal_before = journal_path.read_bytes() if journal_path.exists() else None

    with pytest.raises(FileExistsError, match="refuses to reuse existing output files"):
        synthetic_run.run_synthetic_e2e(
            status_path=status_path,
            journal_path=journal_path,
            now=datetime(2026, 10, 11, 12, 33, 0, tzinfo=timezone.utc),
        )

    assert (status_path.read_bytes() if status_path.exists() else None) == status_before
    assert (journal_path.read_bytes() if journal_path.exists() else None) == journal_before
