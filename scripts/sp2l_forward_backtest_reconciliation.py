"""Deterministic research-only SP2L forward/backtest reconciliation harness.

This tool reconciles already-produced artifacts. It does not fetch MT5 data,
change detector geometry, normalize timestamps, or place orders.

Inputs:
  --backtest-json  historical research backtest report
  --forward-jsonl  forward runner event log
  --output         reconciliation JSON report

Fail-closed classifications:
  DATA_GAP, TIMESTAMP_UNRESOLVED, SESSION_MISMATCH,
  DETECTOR_MISMATCH, EXECUTION_MISMATCH, MATCH

No numeric tolerance is invented. Exact source values are compared.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CLASSIFICATIONS = {
    "DATA_GAP",
    "TIMESTAMP_UNRESOLVED",
    "SESSION_MISMATCH",
    "DETECTOR_MISMATCH",
    "EXECUTION_MISMATCH",
    "MATCH",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{lineno}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Expected object at {path}:{lineno}")
        rows.append(value)
    return rows


def first_present(obj: dict[str, Any], *paths: str) -> Any:
    for path in paths:
        cur: Any = obj
        ok = True
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                ok = False
                break
            cur = cur[part]
        if ok:
            return cur
    return None


def normalize_candidate(row: dict[str, Any], index: int) -> dict[str, Any]:
    signal_time = first_present(row, "signal_time", "candidate.signal_time", "trigger_time")
    direction = first_present(row, "direction", "candidate.direction")
    entry = first_present(row, "entry", "candidate.entry", "theoretical_entry")
    sl = first_present(row, "sl", "candidate.sl")
    tp = first_present(row, "tp", "candidate.tp")
    result = first_present(row, "result")
    return {
        "candidate_id": f"{signal_time}_{direction}" if signal_time is not None and direction else f"BACKTEST_{index:05d}",
        "trigger_time_raw": signal_time,
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "result": result,
        "source_index": index,
        "source": row,
    }


def extract_backtest_candidates(report: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    outcomes = report.get("outcomes", {})
    if isinstance(outcomes, dict):
        for symbol_result in outcomes.values():
            if not isinstance(symbol_result, dict):
                continue
            details = symbol_result.get("signals_detail", [])
            if isinstance(details, list):
                for row in details:
                    if isinstance(row, dict):
                        candidates.append(row)

    # Also support a flat signals_detail report.
    if not candidates and isinstance(report.get("signals_detail"), list):
        candidates.extend(
            x for x in report["signals_detail"] if isinstance(x, dict)
        )

    normalized = [
        normalize_candidate(row, i) for i, row in enumerate(candidates)
    ]
    normalized.sort(key=lambda x: (x["trigger_time_raw"] is None, x["trigger_time_raw"] or 0))
    return normalized


def event_map(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_id: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        sid = event.get("signal_id")
        if sid is not None:
            by_id.setdefault(str(sid), []).append(event)
    return by_id


def candidate_events(candidate: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signal_time = candidate["trigger_time_raw"]
    direction = candidate["direction"]
    wanted = f"AUTHOR_REPLICA_FT_{signal_time}_{direction}" if signal_time is not None and direction else None
    if wanted:
        exact = [e for e in events if str(e.get("signal_id", "")) == wanted]
        if exact:
            return exact

    # No timezone conversion or fuzzy timestamp matching is allowed.
    # We can only match an explicit exact trigger_time field if present.
    exact_time = []
    for e in events:
        c = e.get("candidate")
        et = None
        if isinstance(c, dict):
            et = c.get("trigger_time")
        if et is None:
            et = e.get("trigger_time")
        if et is not None and signal_time is not None and int(et) == int(signal_time):
            exact_time.append(e)
    return exact_time


def extract_forward_candidate(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    rows = [e for e in events if e.get("event") == "CANDIDATE"]
    return rows[0] if rows else None


def extract_order_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        e for e in events
        if e.get("event") in {
            "ORDER_ATTEMPT",
            "ORDER_RESULT",
            "ORDER_REJECTED",
            "ORDER_PLACED",
            "EXECUTION_MISS",
            "TELEGRAM_DEAL_LIFECYCLE",
        }
    ]


def exact_level_match(back: dict[str, Any], forward_candidate: dict[str, Any]) -> bool:
    c = forward_candidate.get("candidate")
    if not isinstance(c, dict):
        return False
    # signal_id is only an index key. Never let it override the raw trigger
    # timestamp carried by the candidate payload.
    trigger_match = c.get("trigger_time") == back["trigger_time_raw"]
    return (
        trigger_match
        and c.get("direction") == back["direction"]
        and c.get("theoretical_entry") == back["entry"]
        and c.get("sl") == back["sl"]
        and c.get("tp") == back["tp"]
    )


def session_value(report: dict[str, Any], candidate: dict[str, Any]) -> Any:
    # Backtest report can only establish that the research session filter was
    # enabled. It does not necessarily store per-row eligibility.
    flag = report.get("research_session_filter", {}).get("enabled")
    if "session_eligible" in candidate["source"]:
        return candidate["source"]["session_eligible"]
    return None if flag is None else "FILTER_ENABLED_NOT_ROW_TAGGED"


def classify(
    back: dict[str, Any],
    report: dict[str, Any],
    matching_events: list[dict[str, Any]],
    all_events: list[dict[str, Any]],
) -> dict[str, Any]:
    notes: list[str] = []
    if back["trigger_time_raw"] is None:
        return {"classification": "DATA_GAP", "notes": ["Historical trigger_time is missing."]}

    if not matching_events:
        # If the forward log contains candidates but none can be tied to this
        # exact raw trigger timestamp, do not guess a timezone shift.
        candidate_events_all = [e for e in all_events if e.get("event") == "CANDIDATE"]
        if candidate_events_all:
            return {
                "classification": "TIMESTAMP_UNRESOLVED",
                "notes": [
                    "No exact forward candidate match by raw trigger timestamp.",
                    "Timezone/terminal timestamp normalization was intentionally not attempted.",
                ],
            }
        return {
            "classification": "DATA_GAP",
            "notes": ["No forward CANDIDATE evidence is present in the supplied log."],
        }

    fc = extract_forward_candidate(matching_events)
    if fc is None:
        return {"classification": "DATA_GAP", "notes": ["Matched events lack a CANDIDATE record."]}

    if not exact_level_match(back, fc):
        return {
            "classification": "DETECTOR_MISMATCH",
            "notes": ["Exact trigger identity exists but direction/entry/SL/TP differs."],
        }

    # Session mismatch is only assertable when both sides explicitly expose
    # row-level eligibility. Never infer forward eligibility from absence.
    hist_session = back["source"].get("session_eligible")
    forward_session = fc.get("session_eligible")
    if hist_session is not None and forward_session is not None and hist_session != forward_session:
        return {
            "classification": "SESSION_MISMATCH",
            "notes": [f"Historical session_eligible={hist_session}; forward={forward_session}."],
        }

    orders = extract_order_events(matching_events)
    if not orders:
        return {
            "classification": "EXECUTION_MISMATCH",
            "notes": ["Candidate and theoretical levels match, but no execution/lifecycle evidence exists."],
        }

    if any(e.get("event") == "ORDER_REJECTED" for e in orders):
        return {
            "classification": "EXECUTION_MISMATCH",
            "notes": ["Candidate matched, but broker/order lifecycle contains ORDER_REJECTED."],
        }

    if any(e.get("event") == "EXECUTION_MISS" for e in orders):
        return {
            "classification": "EXECUTION_MISMATCH",
            "notes": ["Candidate matched, but forward log records EXECUTION_MISS."],
        }

    if any(e.get("event") == "ORDER_PLACED" for e in orders):
        notes.append("ORDER_PLACED evidence exists.")
        return {"classification": "MATCH", "notes": notes}

    return {
        "classification": "EXECUTION_MISMATCH",
        "notes": ["Execution evidence exists but no accepted order placement is recorded."],
    }


def reconcile(report: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = extract_backtest_candidates(report)
    rows = []
    for candidate in candidates:
        matches = candidate_events(candidate, events)
        verdict = classify(candidate, report, matches, events)
        fc = extract_forward_candidate(matches) if matches else None
        order_events = extract_order_events(matches)
        rows.append({
            "candidate_id": candidate["candidate_id"],
            "trigger_time_raw": candidate["trigger_time_raw"],
            "trigger_time_interpreted": None,
            "detector_match": verdict["classification"] not in {"DETECTOR_MISMATCH", "DATA_GAP", "TIMESTAMP_UNRESOLVED"},
            "session_historical": session_value(report, candidate),
            "session_forward": fc.get("session_eligible") if fc else None,
            "entry_historical": candidate["entry"],
            "sl_historical": candidate["sl"],
            "tp_historical": candidate["tp"],
            "entry_forward": first_present(fc or {}, "candidate.theoretical_entry"),
            "sl_forward": first_present(fc or {}, "candidate.sl"),
            "tp_forward": first_present(fc or {}, "candidate.tp"),
            "forward_visible": bool(matches),
            "order_state": [e.get("event") for e in order_events],
            "fill_state": "unknown",
            "lifecycle_state": "observed" if any(e.get("event") == "TELEGRAM_DEAL_LIFECYCLE" for e in order_events) else "not_proven",
            "classification": verdict["classification"],
            "evidence_refs": {
                "backtest_source_index": candidate["source_index"],
                "forward_event_count": len(matches),
            },
            "notes": verdict["notes"],
        })

    counts = {name: 0 for name in sorted(CLASSIFICATIONS)}
    for row in rows:
        counts[row["classification"]] += 1

    return {
        "status": "RESEARCH_ONLY",
        "canonical": False,
        "harness": "SP2L_FORWARD_BACKTEST_RECONCILIATION_V1",
        "timestamp_policy": "EXACT_RAW_ONLY_NO_NORMALIZATION",
        "numeric_policy": "EXACT_SOURCE_VALUES_NO_INVENTED_TOLERANCE",
        "candidates": len(rows),
        "classification_counts": counts,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtest-json", type=Path, required=True)
    parser.add_argument("--forward-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = load_json(args.backtest_json)
    events = load_jsonl(args.forward_jsonl)
    result = reconcile(report, events)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "candidates": result["candidates"],
        "classification_counts": result["classification_counts"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
