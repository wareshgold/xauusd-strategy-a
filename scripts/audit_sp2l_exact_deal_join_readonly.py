#!/usr/bin/env python3
"""Deterministic, read-only exact-ID join audit for normalized SP2L evidence JSONL.

This is an evidence reconciliation utility, not a broker adapter or fill model.
It never infers a deal from timestamp proximity and never edits input files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    rows: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            rejected.append({"line": line_number, "reason": "INVALID_JSON", "detail": str(exc)})
            continue
        if not isinstance(value, dict):
            rejected.append({"line": line_number, "reason": "ROW_NOT_OBJECT"})
            continue
        value = dict(value)
        value["_audit_line"] = line_number
        rows.append(value)
    return {
        "path": path.name,
        "sha256": sha256_bytes(raw),
        "byte_size": len(raw),
        "rows": rows,
        "rejected": rejected,
        "raw_nonblank_lines": sum(1 for line in raw.splitlines() if line.strip()),
    }


def nonempty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def positive_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value)) and float(value) > 0


def _index(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = row.get(key)
        if nonempty(value):
            result[str(value)].append(row)
    return dict(result)


def audit_join(events_path: Path, deals_path: Path) -> dict[str, Any]:
    event_file = load_jsonl(events_path)
    deal_file = load_jsonl(deals_path)
    events, deals = event_file["rows"], deal_file["rows"]
    events_by_id = _index(events, "deal_id")
    deals_by_id = _index(deals, "deal_id")
    events_by_event_id = _index(events, "event_id")

    duplicate_event_ids = sorted(k for k, v in events_by_event_id.items() if len(v) > 1)
    duplicate_deal_ids = sorted(k for k, v in deals_by_id.items() if len(v) > 1)
    claims_by_deal = {k: len(v) for k, v in events_by_id.items() if k}
    multi_claim_deal_ids = sorted(k for k, n in claims_by_deal.items() if n > 1)

    event_results: list[dict[str, Any]] = []
    matched_event_lines: set[int] = set()
    matched_deal_lines: set[int] = set()
    confirmed = 0
    ambiguous = 0
    unmatched_events = 0
    for event in sorted(events, key=lambda x: x["_audit_line"]):
        line = event["_audit_line"]
        event_id = event.get("event_id")
        deal_id = event.get("deal_id")
        result: dict[str, Any] = {
            "source_event_line": line,
            "event_id": event_id,
            "deal_id": deal_id,
            "status": "UNMATCHED",
            "reason_codes": [],
            "candidate_deal_lines": [],
        }
        if not nonempty(event_id):
            result["reason_codes"].append("MISSING_EVENT_ID")
        elif str(event_id) in duplicate_event_ids:
            result["reason_codes"].append("DUPLICATE_EVENT_ID")
        if not nonempty(deal_id):
            result["reason_codes"].append("MISSING_EVENT_DEAL_ID")
        else:
            candidates = deals_by_id.get(str(deal_id), [])
            result["candidate_deal_lines"] = [d["_audit_line"] for d in candidates]
            if len(candidates) == 0:
                result["reason_codes"].append("NO_DEAL_WITH_EXACT_ID")
            elif len(candidates) > 1 or str(deal_id) in duplicate_deal_ids:
                result["status"] = "AMBIGUOUS"
                result["reason_codes"].append("DUPLICATE_BROKER_DEAL_ID")
                ambiguous += 1
            elif str(deal_id) in multi_claim_deal_ids:
                result["status"] = "AMBIGUOUS"
                result["reason_codes"].append("MULTIPLE_EVENTS_CLAIM_SAME_DEAL")
                ambiguous += 1
            else:
                deal = candidates[0]
                if not nonempty(event_id) or str(event_id) in duplicate_event_ids:
                    result["status"] = "AMBIGUOUS"
                    result["reason_codes"].append("INVALID_OR_DUPLICATE_EVENT_ID")
                    ambiguous += 1
                    event_results.append(result)
                    continue
                conflicts = []
                for key in ("order_id", "position_id"):
                    left, right = event.get(key), deal.get(key)
                    if nonempty(left) and nonempty(right) and str(left) != str(right):
                        conflicts.append(key.upper())
                if conflicts:
                    result["status"] = "AMBIGUOUS"
                    result["reason_codes"].append("CONFLICTING_LINK_FIELDS:" + ",".join(conflicts))
                    ambiguous += 1
                else:
                    missing = []
                    if not nonempty(deal.get("execution_time_original")):
                        missing.append("EXECUTION_TIME")
                    if not positive_number(deal.get("execution_price")):
                        missing.append("EXECUTION_PRICE")
                    if not positive_number(deal.get("executed_volume")):
                        missing.append("EXECUTED_VOLUME")
                    if missing:
                        result["status"] = "IDENTITY_MATCH_INCOMPLETE"
                        result["reason_codes"].append("MISSING_OR_INVALID_DEAL_FIELDS:" + ",".join(missing))
                        matched_event_lines.add(line)
                        matched_deal_lines.add(deal["_audit_line"])
                    else:
                        result["status"] = "CONFIRMED_IDENTITY_FIELDS_COMPLETE"
                        result["reason_codes"].append("EXACT_DEAL_ID_AND_LINK_FIELDS_CONSISTENT")
                        matched_event_lines.add(line)
                        matched_deal_lines.add(deal["_audit_line"])
                        confirmed += 1
        if result["status"] == "UNMATCHED":
            unmatched_events += 1
            if not result["reason_codes"]:
                result["reason_codes"].append("NO_CONFIRMED_JOIN")
        event_results.append(result)

    deal_results: list[dict[str, Any]] = []
    unmatched_deals = 0
    for deal in sorted(deals, key=lambda x: x["_audit_line"]):
        line = deal["_audit_line"]
        deal_id = deal.get("deal_id")
        result = {
            "broker_deal_line": line,
            "deal_id": deal_id,
            "status": "UNMATCHED",
            "reason_codes": [],
            "candidate_event_lines": [],
        }
        if not nonempty(deal_id):
            result["reason_codes"].append("MISSING_DEAL_ID")
        else:
            candidates = events_by_id.get(str(deal_id), [])
            result["candidate_event_lines"] = [e["_audit_line"] for e in candidates]
            if str(deal_id) in duplicate_deal_ids:
                result["status"] = "AMBIGUOUS"
                result["reason_codes"].append("DUPLICATE_BROKER_DEAL_ID")
            elif len(candidates) > 1:
                result["status"] = "AMBIGUOUS"
                result["reason_codes"].append("MULTIPLE_EVENTS_CLAIM_SAME_DEAL")
            elif len(candidates) == 0:
                result["reason_codes"].append("NO_EVENT_WITH_EXACT_ID")
            else:
                matching_event = candidates[0]
                event_result = next(x for x in event_results if x["source_event_line"] == matching_event["_audit_line"])
                if event_result["status"] == "CONFIRMED_IDENTITY_FIELDS_COMPLETE":
                    result["status"] = "MATCHED_CONFIRMED"
                    result["reason_codes"].append("EXACT_DEAL_ID_AND_LINK_FIELDS_CONSISTENT")
                elif event_result["status"] == "IDENTITY_MATCH_INCOMPLETE":
                    result["status"] = "MATCHED_IDENTITY_INCOMPLETE"
                    result["reason_codes"].extend(event_result["reason_codes"])
                else:
                    result["status"] = "AMBIGUOUS"
                    result["reason_codes"].extend(event_result["reason_codes"])
        if result["status"] == "UNMATCHED":
            unmatched_deals += 1
        deal_results.append(result)

    return {
        "contract": "sp2l-exact-id-join-audit-v1",
        "classification": "RESEARCH_ONLY_NOT_A_FILL_MODEL",
        "inputs": {
            "source_events": {k: v for k, v in event_file.items() if k not in ("rows", "rejected")},
            "broker_deals": {k: v for k, v in deal_file.items() if k not in ("rows", "rejected")},
        },
        "row_counts": {
            "source_event_raw_nonblank_lines": event_file["raw_nonblank_lines"],
            "source_event_parsed_rows": len(events),
            "source_event_rejected_rows": len(event_file["rejected"]),
            "broker_deal_raw_nonblank_lines": deal_file["raw_nonblank_lines"],
            "broker_deal_parsed_rows": len(deals),
            "broker_deal_rejected_rows": len(deal_file["rejected"]),
        },
        "integrity_and_duplicates": {
            "duplicate_event_ids": duplicate_event_ids,
            "duplicate_broker_deal_ids": duplicate_deal_ids,
            "deal_ids_claimed_by_multiple_events": multi_claim_deal_ids,
        },
        "join_summary": {
            "confirmed_identity_and_execution_fields_complete": confirmed,
            "identity_match_but_execution_fields_incomplete": sum(x["status"] == "IDENTITY_MATCH_INCOMPLETE" for x in event_results),
            "ambiguous_source_events": sum(x["status"] == "AMBIGUOUS" for x in event_results),
            "unmatched_source_events": unmatched_events,
            "ambiguous_broker_deals": sum(x["status"] == "AMBIGUOUS" for x in deal_results),
            "unmatched_broker_deals": unmatched_deals,
            "time_proximity_used_for_join": False,
            "ohlc_used_to_infer_fill": False,
        },
        "source_event_results": event_results,
        "broker_deal_results": deal_results,
        "rejected_rows": {
            "source_events": event_file["rejected"],
            "broker_deals": deal_file["rejected"],
        },
        "limitations": [
            "Exact deal_id equality is necessary for this join but does not independently prove source authenticity.",
            "CONFIRMED_IDENTITY_FIELDS_COMPLETE means exact-ID linkage and required fields are present; it does not validate timestamp correctness, trade direction semantics, accounting, or strategy parity.",
            "Order/position identifiers are compared only when both sides provide a non-empty value.",
            "This utility does not infer missing IDs, timestamps, prices, volumes, fills, or event ordering.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True, type=Path, help="normalized source-event JSONL snapshot")
    parser.add_argument("--deals", required=True, type=Path, help="normalized broker-deal JSONL export")
    parser.add_argument("--output", required=True, type=Path, help="new JSON report path; must not already exist")
    args = parser.parse_args()
    if not args.events.is_file() or not args.deals.is_file():
        parser.error("--events and --deals must refer to existing files")
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    report = audit_join(args.events, args.deals)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "source_event_sha256": report["inputs"]["source_events"]["sha256"],
        "broker_deal_sha256": report["inputs"]["broker_deals"]["sha256"],
        "join_summary": report["join_summary"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
