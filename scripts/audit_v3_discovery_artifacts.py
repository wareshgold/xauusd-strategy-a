#!/usr/bin/env python3
"""Fail-closed integrity audit and manifest writer for V3 Discovery artifacts.

This audits one completed run without changing its JSON/CSV/snapshot inputs.
The generated manifest is a small, portable record of hashes, row counts,
provenance, and audit checks. Research-only; it does not select a strategy.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


INTEGER_FIELDS = (
    "signals", "decisive", "wins", "losses", "ambiguous", "gap_exposed",
    "trail_exits", "tp_exits", "original_sl_exits",
)
FLOAT_FIELDS = (
    "win_rate_decisive_pct", "net_R", "profit_factor", "max_drawdown_R",
    "gross_profit_usd", "gross_loss_usd", "net_profit_usd",
    "avg_R_per_decisive", "avg_usd_per_decisive", "activation_pct",
)
IDENTITY_FIELDS = ("trigger_time", "direction", "theoretical_entry", "initial_sl")


class AuditError(RuntimeError):
    """Raised when an artifact or provenance invariant fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise AuditError(f"{label} file is missing: {path}")
    return path.resolve()


def read_csv(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise AuditError(f"{label} CSV has no header")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise AuditError(f"{label} CSV contains malformed row widths")
        return list(reader.fieldnames), rows


def as_int(value: Any, label: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f"{label} is not an integer: {value!r}") from exc
    return parsed


def as_float(value: Any, label: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f"{label} is not numeric: {value!r}") from exc
    if not math.isfinite(parsed):
        raise AuditError(f"{label} is not finite")
    return parsed


def compare_summary(json_matrix: list[dict[str, Any]], csv_rows: list[dict[str, str]]) -> None:
    by_name = {str(row.get("name")): row for row in json_matrix}
    csv_by_name = {str(row.get("name")): row for row in csv_rows}
    if len(by_name) != len(json_matrix) or len(csv_by_name) != len(csv_rows):
        raise AuditError("duplicate variant names in JSON matrix or summary CSV")
    if set(by_name) != set(csv_by_name):
        raise AuditError("JSON matrix and summary CSV variant sets differ")

    for name, source in by_name.items():
        observed = csv_by_name[name]
        for field in INTEGER_FIELDS:
            if as_int(observed.get(field), f"{name}.{field}") != as_int(
                source.get(field), f"JSON {name}.{field}"
            ):
                raise AuditError(f"summary mismatch: {name}.{field}")
        for field in FLOAT_FIELDS:
            expected = as_float(source.get(field), f"JSON {name}.{field}")
            actual = as_float(observed.get(field), f"{name}.{field}")
            if expected is None or actual is None:
                if expected is not actual:
                    raise AuditError(f"summary mismatch: {name}.{field}")
            elif not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-9):
                raise AuditError(f"summary mismatch: {name}.{field}")


def trade_identity(row: dict[str, str], variant: str) -> tuple[int, str, float, float]:
    missing = [field for field in IDENTITY_FIELDS if field not in row]
    if missing:
        raise AuditError(f"trades CSV missing identity fields: {','.join(missing)}")
    return (
        as_int(row["trigger_time"], f"{variant}.trigger_time"),
        row["direction"],
        float(row["theoretical_entry"]),
        float(row["initial_sl"]),
    )


def audit_run(run_json: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    run_json = require_file(run_json, "Discovery JSON")
    run_dir = run_json.parent
    stem = run_json.stem
    summary_path = require_file(run_dir / f"{stem}_SUMMARY.csv", "Summary CSV")
    trades_path = require_file(run_dir / f"{stem}_TRADES.csv", "Trades CSV")
    snapshot_path = require_file(run_dir / f"{stem}_SNAPSHOT.md", "Snapshot")

    try:
        payload = json.loads(run_json.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Discovery JSON cannot be parsed: {exc}") from exc

    if payload.get("research_only") is not True:
        raise AuditError("Discovery JSON is not explicitly marked research_only")
    if payload.get("version") != "SP2L_V3_CONTROLLED_DISCOVERY_20261007":
        raise AuditError("unexpected Discovery version")
    if payload.get("timeframe") != "M1":
        raise AuditError("unexpected Discovery timeframe")

    provenance = payload.get("dataset_provenance")
    population = payload.get("frozen_population")
    matrix = payload.get("matrix")
    if not isinstance(provenance, dict) or not isinstance(population, dict):
        raise AuditError("JSON provenance sections are missing")
    if not isinstance(matrix, list) or not matrix:
        raise AuditError("JSON matrix is missing or empty")
    if population.get("source") != "FROZEN_V3_ENTRY_CSV":
        raise AuditError("run did not use the frozen V3 entry CSV")
    if population.get("policy") != "ONE_SHARED_SIGNAL_ENTRY_POPULATION_FOR_ALL_EXIT_VARIANTS":
        raise AuditError("unexpected frozen population policy")

    dataset_path = require_file(Path(str(provenance.get("artifact") or "")), "M1 source")
    entry_path = require_file(Path(str(population.get("artifact") or "")), "Frozen entry source")
    dataset_hash = sha256_file(dataset_path)
    entry_hash = sha256_file(entry_path)
    if dataset_hash.lower() != str(provenance.get("content_sha256") or "").lower():
        raise AuditError("M1 source SHA-256 does not match Discovery provenance")
    if entry_hash.lower() != str(population.get("content_sha256") or "").lower():
        raise AuditError("frozen entry source SHA-256 does not match Discovery provenance")
    if provenance.get("byte_size") is not None:
        if dataset_path.stat().st_size != as_int(provenance["byte_size"], "M1 byte_size"):
            raise AuditError("M1 source byte size does not match Discovery provenance")

    variant_count = as_int(payload.get("discovery_grid", {}).get("variant_count"), "grid.variant_count")
    signal_count = as_int(population.get("signals"), "frozen_population.signals")
    if len(matrix) != variant_count:
        raise AuditError("JSON matrix count does not match declared variant count")
    if signal_count <= 0:
        raise AuditError("frozen population signal count must be positive")

    summary_fields, summary_rows = read_csv(summary_path, "Summary")
    trades_fields, trade_rows = read_csv(trades_path, "Trades")
    if "name" not in summary_fields:
        raise AuditError("summary CSV has no name column")
    if "variant" not in trades_fields:
        raise AuditError("trades CSV has no variant column")
    if len(summary_rows) != variant_count:
        raise AuditError("summary CSV row count does not match declared variant count")
    if len(trade_rows) != variant_count * signal_count:
        raise AuditError("trades CSV row count does not equal variants × frozen population")

    compare_summary(matrix, summary_rows)

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in trade_rows:
        grouped.setdefault(row["variant"], []).append(row)
    expected_names = {str(row["name"]) for row in matrix}
    if set(grouped) != expected_names:
        raise AuditError("trades CSV variant set does not match JSON matrix")
    canonical_identities: set[tuple[int, str, float, float]] | None = None
    for name, rows in grouped.items():
        if len(rows) != signal_count:
            raise AuditError(f"{name} has {len(rows)} trades; expected {signal_count}")
        identities = {trade_identity(row, name) for row in rows}
        if len(identities) != signal_count:
            raise AuditError(f"{name} contains duplicate frozen trade identities")
        if canonical_identities is None:
            canonical_identities = identities
        elif identities != canonical_identities:
            raise AuditError(f"{name} does not replay the same frozen entry population")

    json_hash = sha256_file(run_json)
    snapshot_text = snapshot_path.read_text(encoding="utf-8")
    expected_snapshot_line = f"JSON SHA256: {json_hash}"
    if expected_snapshot_line not in snapshot_text:
        raise AuditError("snapshot JSON SHA-256 does not match the JSON artifact")

    artifacts = {
        "discovery_json": {
            "path": str(run_json), "sha256": json_hash, "bytes": run_json.stat().st_size,
        },
        "summary_csv": {
            "path": str(summary_path.resolve()),
            "sha256": sha256_file(summary_path), "bytes": summary_path.stat().st_size,
            "rows": len(summary_rows),
        },
        "trades_csv": {
            "path": str(trades_path.resolve()),
            "sha256": sha256_file(trades_path), "bytes": trades_path.stat().st_size,
            "rows": len(trade_rows),
        },
        "snapshot_md": {
            "path": str(snapshot_path.resolve()),
            "sha256": sha256_file(snapshot_path), "bytes": snapshot_path.stat().st_size,
        },
        "m1_source": {
            "path": str(dataset_path), "sha256": dataset_hash, "bytes": dataset_path.stat().st_size,
        },
        "frozen_entry_source": {
            "path": str(entry_path), "sha256": entry_hash, "bytes": entry_path.stat().st_size,
            "rows": signal_count,
        },
    }
    manifest = {
        "schema": "SP2L_V3_DISCOVERY_EVIDENCE_MANIFEST_V1",
        "research_only": True,
        "audit_status": "PASS",
        "audit_scope": [
            "artifact existence and SHA-256",
            "M1 and frozen-entry provenance binding",
            "JSON/CSV variant and row-count consistency",
            "same frozen trade identities across every variant",
            "summary CSV agreement with JSON matrix",
            "snapshot-to-JSON SHA-256 binding",
        ],
        "run": {
            "version": payload["version"],
            "symbol": payload.get("symbol"),
            "timeframe": payload.get("timeframe"),
            "window_utc": payload.get("window_utc"),
            "m1_bars": payload.get("bars"),
            "variants": variant_count,
            "frozen_entry_rows": signal_count,
        },
        "dataset_provenance": provenance,
        "frozen_population": population,
        "execution_assumptions": payload.get("execution_assumptions"),
        "exit_policy": payload.get("exit_policy"),
        "artifacts": artifacts,
        "limitations": [
            "M1 OHLC replay; not tick-level broker execution.",
            "Spread, slippage, and commission are not modeled.",
            "Discovery ranking is not a canonical rule or production decision.",
            "This audit does not establish statistical significance or out-of-sample edge.",
        ],
    }

    if manifest_path is None:
        manifest_path = run_dir / f"{stem}_EVIDENCE_MANIFEST.json"
    manifest_path = manifest_path.resolve()
    if manifest_path.exists():
        raise AuditError(f"refusing to overwrite existing manifest: {manifest_path}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    manifest_hash = sha256_file(manifest_path)
    return {
        "status": "PASS",
        "variants": variant_count,
        "signals_per_variant": signal_count,
        "trades": len(trade_rows),
        "m1_sha256": dataset_hash,
        "entry_sha256": entry_hash,
        "manifest": str(manifest_path),
        "manifest_sha256": manifest_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-json", required=True, help="Path to the Discovery JSON output")
    parser.add_argument("--manifest", default=None, help="Optional new manifest path; existing files are never overwritten")
    args = parser.parse_args()
    try:
        result = audit_run(
            Path(args.run_json),
            Path(args.manifest) if args.manifest else None,
        )
    except (AuditError, OSError, ValueError) as exc:
        print(f"AUDIT=FAIL reason={exc}", file=sys.stderr)
        return 1
    print(
        "AUDIT=PASS "
        f"variants={result['variants']} "
        f"signals={result['signals_per_variant']} "
        f"trades={result['trades']} "
        f"manifest={result['manifest']} "
        f"manifest_sha256={result['manifest_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
