"""Isolated offline MA observation recorder.

Consumes an explicit frozen JSON input. It does not detect candidates, access MT5,
import the Runner, infer bar boundaries, or perform trading/execution actions.
The caller supplies candidate observations and their capture timestamps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.research.ma_decision_observation import build_observation_record

EVIDENCE_MODE = "OFFLINE_REPLAY"
INPUT_SCHEMA_VERSION = "MA_OFFLINE_OBSERVER_INPUT_V1"
OUTPUT_SCHEMA_VERSION = "MA_OFFLINE_OBSERVER_OUTPUT_V1"
MANIFEST_SCHEMA_VERSION = "MA_OFFLINE_OBSERVER_MANIFEST_V1"


def _canonical_json_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _load_and_validate_input(input_bytes):
    try:
        payload = json.loads(input_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("input must be valid UTF-8 JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("input root must be an object")
    required = {
        "schema_version", "run_id", "process_session_id", "source_revision",
        "current_m1_bar_open_server_epoch",
        "last_completed_m1_bar_open_server_epoch",
        "last_completed_m1_bar_close_server_epoch",
        "server_utc_offset_seconds", "bars_snapshot", "observations",
    }
    if set(payload) != required:
        raise ValueError("input must contain exactly the documented top-level fields")
    if payload["schema_version"] != INPUT_SCHEMA_VERSION:
        raise ValueError("unsupported input schema_version")
    for key in ("run_id", "process_session_id", "source_revision"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    if not isinstance(payload["bars_snapshot"], list) or len(payload["bars_snapshot"]) < 2:
        raise ValueError("bars_snapshot must contain at least two bars")
    if not isinstance(payload["observations"], list) or not payload["observations"]:
        raise ValueError("observations must be a non-empty list")

    seen_ids = set()
    previous_sequence = -1
    for observation in payload["observations"]:
        if not isinstance(observation, dict) or set(observation) != {
            "candidate_id", "poll_sequence", "trigger_time_server_epoch",
            "decision_observed_at_utc", "decision_monotonic_ns",
        }:
            raise ValueError("each observation must contain exactly the documented fields")
        candidate_id = observation["candidate_id"]
        sequence = observation["poll_sequence"]
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("candidate_id must be a non-empty string")
        if candidate_id in seen_ids:
            raise ValueError("candidate_id values must be unique within a run")
        seen_ids.add(candidate_id)
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= previous_sequence:
            raise ValueError("poll_sequence values must be strictly increasing non-negative integers")
        previous_sequence = sequence
        trigger_time = observation["trigger_time_server_epoch"]
        if isinstance(trigger_time, bool) or not isinstance(trigger_time, int):
            raise ValueError("trigger_time_server_epoch must be an integer server-epoch bar time")
        if not isinstance(observation["decision_observed_at_utc"], str):
            raise ValueError("decision_observed_at_utc must be supplied as a string")
        monotonic = observation["decision_monotonic_ns"]
        if isinstance(monotonic, bool) or not isinstance(monotonic, int) or monotonic < 0:
            raise ValueError("decision_monotonic_ns must be a non-negative integer")

    return payload


def run_offline_observer(*, input_path, output_dir):
    """Write one immutable JSONL evidence file and manifest into a new directory.

    output_dir must not exist. Only two files are created there:
    observations.jsonl and manifest.json. Existing output is never overwritten.
    """
    source_path = Path(input_path).resolve(strict=True)
    target_dir = Path(output_dir).resolve()
    if target_dir == source_path.parent or target_dir in source_path.parents:
        raise ValueError("output directory cannot contain the input file")
    if target_dir.exists():
        raise FileExistsError(f"refusing to reuse existing output directory: {target_dir}")
    input_bytes = source_path.read_bytes()
    payload = _load_and_validate_input(input_bytes)
    input_hash = _sha256(input_bytes)

    records = []
    for item in payload["observations"]:
        record = build_observation_record(
            candidate_id=item["candidate_id"],
            process_session_id=payload["process_session_id"],
            poll_sequence=item["poll_sequence"],
            trigger_time_server_epoch=item["trigger_time_server_epoch"],
            current_m1_bar_open_server_epoch=payload["current_m1_bar_open_server_epoch"],
            last_completed_m1_bar_open_server_epoch=payload["last_completed_m1_bar_open_server_epoch"],
            last_completed_m1_bar_close_server_epoch=payload["last_completed_m1_bar_close_server_epoch"],
            server_utc_offset_seconds=payload["server_utc_offset_seconds"],
            bars_snapshot=payload["bars_snapshot"],
            decision_observed_at_utc=item["decision_observed_at_utc"],
            decision_monotonic_ns=item["decision_monotonic_ns"],
        )
        records.append({
            "output_schema_version": OUTPUT_SCHEMA_VERSION,
            "evidence_mode": EVIDENCE_MODE,
            "run_id": payload["run_id"],
            "source_revision": payload["source_revision"],
            "input_sha256": input_hash,
            "observation": record,
        })

    jsonl_bytes = b"".join(_canonical_json_bytes(row) + bytes((10,)) for row in records)
    manifest = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "evidence_mode": EVIDENCE_MODE,
        "run_id": payload["run_id"],
        "source_revision": payload["source_revision"],
        "input_schema_version": INPUT_SCHEMA_VERSION,
        "input_sha256": input_hash,
        "output_file": "observations.jsonl",
        "output_sha256": _sha256(jsonl_bytes),
        "observation_count": len(records),
        "alignment_status_counts": {
            status: sum(
                row["observation"]["alignment_status"] == status for row in records
            )
            for status in sorted({
                row["observation"]["alignment_status"] for row in records
            })
        },
    }
    manifest_bytes = _canonical_json_bytes(manifest) + bytes((10,))

    # mkdir without exist_ok and exclusive file creation prevent accidental reuse.
    target_dir.mkdir(parents=True, exist_ok=False)
    try:
        with (target_dir / "observations.jsonl").open("xb") as stream:
            stream.write(jsonl_bytes)
        with (target_dir / "manifest.json").open("xb") as stream:
            stream.write(manifest_bytes)
    except Exception:
        # Preserve partial evidence for inspection; never silently delete it.
        raise

    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Write immutable OFFLINE_REPLAY MA observation evidence from a frozen JSON input."
    )
    parser.add_argument("--input", required=True, help="Frozen observer input JSON")
    parser.add_argument("--output-dir", required=True, help="New output directory; must not already exist")
    args = parser.parse_args(argv)
    manifest = run_offline_observer(input_path=args.input, output_dir=args.output_dir)
    print(json.dumps(manifest, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
