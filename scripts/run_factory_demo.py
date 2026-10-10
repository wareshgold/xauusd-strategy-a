from __future__ import annotations

"""Safe telemetry demo for the SP2L Factory.

This script demonstrates worker-to-dashboard telemetry only. It does NOT run
research gates, build/accept evidence, consume Holdout, prepare a forward
session, start MT5, or create BUY/SELL decisions. DEMO_ONLY is intentionally
not represented as a research PASS.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strategy_factory.telemetry import DEFAULT_STATUS_FILE, publish_workers  # noqa: E402


STAGES = (
    ("source", "Source resolution"),
    ("discovery", "Discovery"),
    ("candidate_lab", "Candidate Lab"),
    ("validation", "Validation"),
    ("robustness", "Robustness"),
    ("holdout", "Holdout"),
    ("forward_gate", "Forward Gate"),
    ("forward_session", "Forward Session"),
    ("runtime_observer", "Runtime / MT5 Observer"),
)


def _run_id(now: datetime) -> str:
    return f"FACTORY-DEMO-{now.strftime('%Y%m%d-%H%M%S')}"


def build_demo_workers(run_id: str, now: datetime) -> list[dict[str, Any]]:
    """Return deterministic stage identities with explicitly non-research status."""
    workers = []
    for index, (stage_id, label) in enumerate(STAGES, start=1):
        fingerprint = hashlib.sha256(f"{run_id}:{stage_id}".encode("utf-8")).hexdigest()
        workers.append(
            {
                "worker_id": f"demo-{stage_id}",
                "job_id": f"{run_id}-{index:02d}",
                "job_type": "TELEMETRY_DEMO_ONLY",
                "station": stage_id if stage_id in {
                    "discovery", "robustness", "holdout", "forward_gate"
                } else "idle",
                "phase": stage_id.upper(),
                "state": "COMPLETED",
                "started_utc": now.isoformat(),
                "heartbeat_utc": now.isoformat(),
                "progress": 100.0,
                "detail": (
                    f"DEMO_ONLY: {label}; lifecycle telemetry smoke test. "
                    "No research gate or evidence was evaluated."
                ),
                "output_artifact": f"demo://{fingerprint}",
                "error": None,
            }
        )
    return workers


def render(run_id: str, workers: list[dict[str, Any]], published_path: Path | None) -> None:
    print("=" * 64)
    print("SP2L FACTORY — TELEMETRY DEMO ONLY")
    print("=" * 64)
    print(f"Run ID: {run_id}")
    print("Purpose: worker lifecycle / dashboard plumbing smoke test")
    print("Research gates: NOT EXECUTED")
    print("Evidence / Holdout: NOT CREATED OR CONSUMED")
    print("Forward session / MT5: NOT STARTED")
    print("Production decision: FALSE")
    print("-" * 64)
    for worker in workers:
        label = worker["phase"].replace("_", " ")
        print(f"{label:<22} DEMO_ONLY  {worker['progress']:>3.0f}%")
    if published_path is not None:
        print("-" * 64)
        print(f"Worker telemetry published: {published_path}")
    print("=" * 64)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publish",
        action="store_true",
        help=(
            "write DEMO_ONLY workers to runtime/factory_worker_status.json for "
            "dashboard inspection; this replaces the current worker snapshot"
        ),
    )
    parser.add_argument(
        "--status-file",
        type=Path,
        default=DEFAULT_STATUS_FILE,
        help="optional telemetry destination (used only with --publish)",
    )
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    run_id = _run_id(now)
    workers = build_demo_workers(run_id, now)
    published_path = None
    if args.publish:
        publish_workers(workers, path=args.status_file)
        published_path = args.status_file
    render(run_id, workers, published_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
