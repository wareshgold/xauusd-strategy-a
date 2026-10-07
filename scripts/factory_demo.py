from __future__ import annotations

"""Deterministic visual demo for the Tycoon Factory dashboard.

This writes DEMO telemetry to a separate file. It never touches live worker
telemetry and never executes Strategy A or produces trading decisions.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "runtime" / "factory_demo_status.json"

WORKERS = [
    ("DEMO-W01", "DISCOVERY", "Discovery Lab", "RUNNING", 68.0, "Scanning frozen signal population"),
    ("DEMO-W02", "STABILITY", "Stability Lab", "HEARTBEAT", 44.0, "Evaluating chronological sub-windows"),
    ("DEMO-W03", "ROBUSTNESS", "Robustness Lab", "RUNNING", 31.0, "Comparing research variants"),
    ("DEMO-W04", "HOLDOUT", "Holdout Vault", "QUEUED", 0.0, "Waiting for frozen validation input"),
    ("DEMO-W05", "FORWARD", "Forward Ops", "IDLE", 0.0, "No live job attached"),
]


def build_payload() -> dict:
    return {
        "schema_version": 1,
        "mode": "DEMO",
        "research_only": True,
        "production_decisions": 0,
        "workers": [
            {
                "worker_id": worker_id,
                "job_id": f"DEMO-{job_type}-001" if state != "IDLE" else None,
                "job_type": job_type,
                "station": station,
                "phase": job_type,
                "state": state,
                "started_utc": None,
                "heartbeat_utc": None,
                "progress": progress,
                "detail": detail,
                "output_artifact": None,
                "error": None,
            }
            for worker_id, job_type, station, state, progress, detail in WORKERS
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_payload(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"DEMO telemetry written: {args.output}")


if __name__ == "__main__":
    main()
