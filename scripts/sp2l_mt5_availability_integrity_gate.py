"""Read-only structural integrity gate for raw MT5 availability artifacts.

This gate verifies artifact provenance and internal consistency only. It does not
infer market sessions, maintenance windows, holidays, UTC offsets, DST, or
trading rules. A structural pass is not evidence that history is complete.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RAW_INTERPRETATION = "RAW_AVAILABILITY_MATRIX_ONLY"
NOT_PERFORMED = ("session_close_inference", "utc_offset_inference", "dst_inference", "holiday_inference", "execution_or_signal_logic")
ALLOWED_WINDOW_STATUSES = {
    "ACQUIRED",
    "PARTIAL_OUT_OF_WINDOW_RESULTS_DISCARDED",
    "NO_DATA",
    "NO_DATA_IN_REQUESTED_INTERVAL",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: timestamp must be a non-empty string")
    text = value.strip().replace("Z", "+00:00")
    try:
        result = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{label}: invalid ISO timestamp {value!r}") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{label}: timestamp must include a UTC offset")
    if result.utcoffset().total_seconds() != 0:
        raise ValueError(f"{label}: expected a UTC timestamp, got {value!r}")
    return result.astimezone(timezone.utc)


def _safe_artifact_path(manifest_path: Path, name: Any, label: str) -> Path:
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"manifest {label} must be a filename")
    relative = Path(name)
    if relative.is_absolute() or relative.name != name or name in {".", ".."}:
        raise ValueError(f"manifest {label} must be a sibling filename, got {name!r}")
    path = manifest_path.parent / relative
    if not path.is_file():
        raise ValueError(f"missing {label} artifact: {path}")
    return path


def evaluate_availability_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Validate manifest hashes and consistency of daily/gap artifacts.

    Returns STRUCTURAL_INTEGRITY_PASS or STRUCTURAL_INTEGRITY_FAIL. The function
    never classifies a gap as a market closure and never edits source artifacts.
    """
    source = Path(manifest_path)
    errors: list[str] = []
    summary: dict[str, Any] = {
        "source_manifest": str(source),
        "mode": "RESEARCH_MT5_AVAILABILITY_INTEGRITY_GATE",
        "canonical": False,
        "research_interpretation": "RAW_AVAILABILITY_ONLY_NOT_SESSION_APPROVED",
        "market_session_approval": "NOT_ESTABLISHED",
        "source_artifacts_modified": False,
    }

    try:
        if not source.is_file():
            raise ValueError(f"manifest not found: {source}")
        manifest = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest root must be a JSON object")

        if manifest.get("interpretation_status") != RAW_INTERPRETATION:
            errors.append(f"interpretation_status must remain {RAW_INTERPRETATION}")
        for key in NOT_PERFORMED:
            if manifest.get(key) != "NOT_PERFORMED":
                errors.append(f"{key} must remain NOT_PERFORMED")

        required_identity = {
            "dataset_id": str,
            "provider": str,
            "symbol": str,
            "timeframe": str,
        }
        for key, expected_type in required_identity.items():
            if not isinstance(manifest.get(key), expected_type) or not manifest[key].strip():
                errors.append(f"manifest field {key!r} must be a non-empty string")

        windows = manifest.get("windows")
        if not isinstance(windows, list):
            errors.append("manifest windows must be an array")
            windows = []
        if manifest.get("window_count") != len(windows):
            errors.append("window_count does not match manifest windows length")

        indices: set[int] = set()
        window_by_index: dict[int, dict[str, Any]] = {}
        for position, window in enumerate(windows):
            label = f"windows[{position}]"
            if not isinstance(window, dict):
                errors.append(f"{label} must be an object")
                continue
            index = window.get("window_index")
            if not isinstance(index, int) or isinstance(index, bool) or index <= 0:
                errors.append(f"{label}.window_index must be a positive integer")
                continue
            if index in indices:
                errors.append(f"duplicate window_index: {index}")
            indices.add(index)
            window_by_index[index] = window
            status = window.get("status")
            if status not in ALLOWED_WINDOW_STATUSES:
                errors.append(f"{label}.status is unsupported: {status!r}")
            try:
                start = _utc_timestamp(window.get("requested_start_utc"), f"{label}.requested_start_utc")
                end = _utc_timestamp(window.get("requested_end_utc"), f"{label}.requested_end_utc")
                if end <= start:
                    errors.append(f"{label}: requested_end_utc must be after requested_start_utc")
            except ValueError as exc:
                errors.append(str(exc))
            if status in {"ACQUIRED", "PARTIAL_OUT_OF_WINDOW_RESULTS_DISCARDED"}:
                for key in ("actual_first_utc", "actual_last_utc"):
                    try:
                        _utc_timestamp(window.get(key), f"{label}.{key}")
                    except ValueError as exc:
                        errors.append(str(exc))
                for key in ("actual_bar_count", "day_count", "gap_count", "non_chronological_count"):
                    value = window.get(key)
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                        errors.append(f"{label}.{key} must be a non-negative integer")

        daily_path = _safe_artifact_path(source, manifest.get("daily_artifact"), "daily")
        gaps_path = _safe_artifact_path(source, manifest.get("gap_artifact"), "gap")
        for key, path in (("daily_artifact_sha256", daily_path), ("gap_artifact_sha256", gaps_path)):
            expected = manifest.get(key)
            if not isinstance(expected, str) or len(expected) != 64:
                errors.append(f"manifest {key} must be a 64-character SHA-256")
            elif _sha256(path).lower() != expected.lower():
                errors.append(f"SHA-256 mismatch for {path.name}")

        with daily_path.open("r", newline="", encoding="utf-8-sig") as handle:
            daily_rows = list(csv.DictReader(handle))
        with gaps_path.open("r", encoding="utf-8") as handle:
            gaps = json.load(handle)
        if not isinstance(gaps, list):
            errors.append("gap artifact root must be a JSON array")
            gaps = []

        daily_by_window: dict[int, list[dict[str, str]]] = {}
        for position, row in enumerate(daily_rows):
            label = f"daily_rows[{position}]"
            try:
                index = int(row["window_index"])
                count = int(row["m1_bar_count"])
                if index not in window_by_index:
                    errors.append(f"{label}: unknown window_index {index}")
                if count <= 0:
                    errors.append(f"{label}: m1_bar_count must be positive")
                first = _utc_timestamp(row["first_m1_utc"], f"{label}.first_m1_utc")
                last = _utc_timestamp(row["last_m1_utc"], f"{label}.last_m1_utc")
                if last < first:
                    errors.append(f"{label}: last_m1_utc precedes first_m1_utc")
                _utc_timestamp(row["first_m1_utc"], f"{label}.first_m1_utc")
                daily_by_window.setdefault(index, []).append(row)
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"{label}: invalid row ({exc})")

        gaps_by_window: dict[int, list[dict[str, Any]]] = {}
        for position, gap in enumerate(gaps):
            label = f"gaps[{position}]"
            if not isinstance(gap, dict):
                errors.append(f"{label} must be an object")
                continue
            index = gap.get("window_index")
            if not isinstance(index, int) or isinstance(index, bool) or index not in window_by_index:
                errors.append(f"{label}: unknown or invalid window_index {index!r}")
                continue
            gaps_by_window.setdefault(index, []).append(gap)
            try:
                previous = _utc_timestamp(gap.get("previous_bar_utc"), f"{label}.previous_bar_utc")
                following = _utc_timestamp(gap.get("next_bar_utc"), f"{label}.next_bar_utc")
                interval = (following - previous).total_seconds() / 60
                reported_interval = gap.get("interval_minutes")
                if not isinstance(reported_interval, (int, float)) or isinstance(reported_interval, bool):
                    errors.append(f"{label}.interval_minutes must be numeric")
                elif abs(float(reported_interval) - interval) > 1e-9:
                    errors.append(f"{label}.interval_minutes disagrees with timestamps")
                expected_kind = "gap" if interval > 1 else "non_chronological"
                if gap.get("kind") != expected_kind:
                    errors.append(f"{label}.kind disagrees with timestamp interval")
                expected_missing = max(0, int(round(interval)) - 1) if interval > 1 else 0
                if gap.get("missing_m1_bars") != expected_missing:
                    errors.append(f"{label}.missing_m1_bars disagrees with timestamp interval")
            except (TypeError, ValueError) as exc:
                errors.append(f"{label}: invalid interval ({exc})")

        for index, window in window_by_index.items():
            status = window.get("status")
            drows = daily_by_window.get(index, [])
            w_gaps = gaps_by_window.get(index, [])
            if status not in {"ACQUIRED", "PARTIAL_OUT_OF_WINDOW_RESULTS_DISCARDED"}:
                if drows or w_gaps:
                    errors.append(f"window {index}: non-acquired window must not have daily/gap rows")
                continue
            if len(drows) != window.get("day_count"):
                errors.append(f"window {index}: day_count disagrees with daily artifact")
            if sum(int(r["m1_bar_count"]) for r in drows if r.get("m1_bar_count", "").isdigit()) != window.get("actual_bar_count"):
                errors.append(f"window {index}: actual_bar_count disagrees with daily artifact")
            if len(w_gaps) != window.get("gap_count"):
                errors.append(f"window {index}: gap_count disagrees with gap artifact")
            non_chronological = sum(g.get("kind") == "non_chronological" for g in w_gaps)
            if non_chronological != window.get("non_chronological_count"):
                errors.append(f"window {index}: non_chronological_count disagrees with gap artifact")

        summary.update({
            "dataset_id": manifest.get("dataset_id"),
            "symbol": manifest.get("symbol"),
            "timeframe": manifest.get("timeframe"),
            "window_count": len(windows),
            "daily_row_count": len(daily_rows),
            "gap_record_count": len(gaps),
            "no_data_window_count": sum(w.get("status") in {"NO_DATA", "NO_DATA_IN_REQUESTED_INTERVAL"} for w in windows if isinstance(w, dict)),
            "acquired_window_count": sum(w.get("status") in {"ACQUIRED", "PARTIAL_OUT_OF_WINDOW_RESULTS_DISCARDED"} for w in windows if isinstance(w, dict)),
        })
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(str(exc))

    summary["errors"] = errors
    summary["status"] = "STRUCTURAL_INTEGRITY_FAIL" if errors else "STRUCTURAL_INTEGRITY_PASS"
    summary["meaning"] = (
        "Artifact hashes and checked internal counts/timestamps are consistent; market-session cause and historical completeness remain unverified."
        if not errors else
        "Artifact integrity or internal consistency checks failed; do not treat this dataset as structurally verified."
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Path to an existing raw availability manifest")
    args = parser.parse_args()
    result = evaluate_availability_manifest(args.manifest)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "STRUCTURAL_INTEGRITY_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
