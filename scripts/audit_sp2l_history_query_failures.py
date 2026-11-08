"""Read-only, anonymized audit of MT5 deal-history query failure events in a private ZIP."""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


EVENT_PATH = "raw/runner_files/forward_events.jsonl"
DEALS_PATH = "raw/mt5_history_deals.json"
ORDERS_PATH = "raw/mt5_history_orders.json"


def _id(value):
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return str(number) if number > 0 else None


def _detail_category(detail):
    text = str(detail or "")
    match = re.search(r"MT5 last_error=\((-?\d+)", text)
    if match:
        return "MT5_LAST_ERROR_" + match.group(1)
    if "MT5 returned None" in text:
        return "MT5_RETURNED_NONE"
    if "query function unavailable" in text:
        return "QUERY_FUNCTION_UNAVAILABLE"
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*Error|[A-Za-z_][A-Za-z0-9_]*Exception):", text)
    if match:
        return "PYTHON_" + match.group(1).upper()
    if not text:
        return "DETAIL_MISSING"
    return "OTHER_DETAIL"


def _event_time_day(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return "NAIVE_TIMESTAMP"
        return parsed.astimezone().date().isoformat()
    except (TypeError, ValueError, OverflowError):
        return "INVALID_TIMESTAMP"


def build_report(events, deals, orders):
    failures = [e for e in events if e.get("event") == "MT5_DEAL_HISTORY_QUERY_FAILED"]

    order_tickets = {_id(x.get("ticket")) for x in orders}
    order_tickets.discard(None)
    deal_order_ids = {_id(x.get("order")) for x in deals}
    deal_order_ids.discard(None)
    deal_position_ids = {_id(x.get("position_id")) for x in deals}
    deal_position_ids.discard(None)

    by_query = defaultdict(list)
    by_detail = Counter()
    by_day = Counter()
    by_final_status = Counter()
    signatures = Counter()
    query_target_pairs = set()

    for event in failures:
        query = str(event.get("query") or "UNKNOWN_QUERY")
        target = _id(event.get("target"))
        detail = str(event.get("detail") or "")
        by_query[query].append(event)
        by_detail[_detail_category(detail)] += 1
        by_day[_event_time_day(event.get("ts_utc"))] += 1
        signatures[(query, target, detail)] += 1
        if target:
            query_target_pairs.add((query, target))

        if query == "history_orders_get":
            status = "PRESENT_IN_FINAL_ORDER_HISTORY" if target in order_tickets else "NOT_FOUND_IN_FINAL_ORDER_HISTORY"
        elif query == "history_deals_get(ticket)":
            status = "PRESENT_IN_FINAL_DEAL_HISTORY" if target in deal_order_ids else "NOT_FOUND_IN_FINAL_DEAL_HISTORY"
        elif query == "history_deals_get(position)":
            status = "PRESENT_IN_FINAL_POSITION_DEALS" if target in deal_position_ids else "NOT_FOUND_IN_FINAL_POSITION_DEALS"
        else:
            status = "UNCLASSIFIABLE_QUERY"
        by_final_status[status] += 1

    report = {
        "event_count": len(failures),
        "unique_failure_signatures": len(signatures),
        "repeated_signature_emissions": sum(count - 1 for count in signatures.values() if count > 1),
        "unique_query_target_pairs": len(query_target_pairs),
        "detail_categories": dict(sorted(by_detail.items())),
        "utc_day_buckets": dict(sorted(by_day.items())),
        "final_history_target_status": dict(sorted(by_final_status.items())),
        "query_families": {},
        "failure_rate": "UNAVAILABLE_WITHOUT_TOTAL_QUERY_ATTEMPT_DENOMINATOR",
    }

    for query, rows in sorted(by_query.items()):
        targets = {_id(e.get("target")) for e in rows}
        targets.discard(None)
        query_signatures = {
            (str(e.get("query") or "UNKNOWN_QUERY"), _id(e.get("target")), str(e.get("detail") or ""))
            for e in rows
        }
        report["query_families"][query] = {
            "emitted_events": len(rows),
            "distinct_targets": len(targets),
            "distinct_failure_signatures": len(query_signatures),
        }
    return report


def load_report(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError("ZIP_CRC_FAILURE")
        events = []
        with archive.open(EVENT_PATH) as stream:
            for line in stream:
                if not line.strip():
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        deals = json.loads(archive.read(DEALS_PATH))
        orders = json.loads(archive.read(ORDERS_PATH))
    return build_report(events, deals, orders)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()
    report = load_report(args.zip_path)
    print("SP2L_HISTORY_QUERY_FAILURE_AUDIT_V1")
    print("ZIP_CRC=PASS")
    print("RAW_FAILURE_EVENT_COUNT={}".format(report["event_count"]))
    print("UNIQUE_FAILURE_SIGNATURES={}".format(report["unique_failure_signatures"]))
    print("REPEATED_SIGNATURE_EMISSIONS={}".format(report["repeated_signature_emissions"]))
    print("UNIQUE_QUERY_TARGET_PAIRS={}".format(report["unique_query_target_pairs"]))
    for query, values in report["query_families"].items():
        print("QUERY={} EVENTS={} DISTINCT_TARGETS={} SIGNATURES={}".format(
            query, values["emitted_events"], values["distinct_targets"], values["distinct_failure_signatures"]))
    for category, count in report["detail_categories"].items():
        print("DETAIL_CATEGORY={} COUNT={}".format(category, count))
    for status, count in report["final_history_target_status"].items():
        print("FINAL_HISTORY_STATUS={} COUNT={}".format(status, count))
    print("UTC_DAY_BUCKETS={}".format(len(report["utc_day_buckets"])))
    print("FAILURE_RATE=UNAVAILABLE_NO_TOTAL_QUERY_ATTEMPT_DENOMINATOR")
    print("NOTE=Targets are anonymized; event count is emitted diagnostics, not total API failures.")


if __name__ == "__main__":
    main()
