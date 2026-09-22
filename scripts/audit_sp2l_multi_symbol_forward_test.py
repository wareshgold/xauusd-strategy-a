"""Deterministic audit for the SP2L multi-symbol author-replica forward stream.

Research-only telemetry analysis. This module never changes detection geometry,
canonical status, order semantics, or promotion gates.

It consumes runtime/forward-test/SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl and
reports observed facts only: candidates, attempts, execution outcomes, pending
placement observations, lifecycle opens/closes, realized pips/net where
telemetry contains them, and linkage/missing-measurement integrity.

No metric is used to select parameters or define Strategy A.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_EVENTS = Path("artifacts/forward-test/SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl")


def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            rows.append({"event": "INVALID_JSON", "line": line_no})
            continue
        row["_line"] = line_no
        rows.append(row)
    return rows


def audit(events: list[dict]) -> dict:
    candidates = {}
    attempts = {}
    lifecycle = []
    pending_order_lifecycle = []
    telegram = Counter()
    failure_reasons = Counter()
    symbols = defaultdict(lambda: Counter())
    duplicate_events = Counter()

    seen_lifecycle_deals = set()
    seen_order_results = set()

    for e in events:
        event = e.get("event")
        symbol = str(e.get("symbol") or "UNKNOWN")

        if event == "CANDIDATE":
            sid = str(e.get("signal_id") or "")
            if sid:
                candidates[sid] = e
                symbols[symbol]["candidates"] += 1

        elif event == "ORDER_ATTEMPT":
            sid = str(e.get("signal_id") or "")
            if sid:
                attempts[sid] = e
                symbols[symbol]["attempts"] += 1

        elif event == "ORDER_RESULT":
            sid = str(e.get("signal_id") or "")
            order_id = int(e.get("tracked_order") or 0)
            if order_id and order_id in seen_order_results:
                duplicate_events["duplicate_order_result"] += 1
            elif order_id:
                seen_order_results.add(order_id)
            if sid:
                attempts.setdefault(sid, {})["result_event"] = e
                ok = bool(e.get("success"))
                symbols[symbol]["execution_success" if ok else "execution_failure"] += 1
                if not ok:
                    result = e.get("result") or {}
                    reason = str(result.get("reason") or result.get("error") or "UNKNOWN")
                    failure_reasons[reason] += 1

        elif event == "PENDING_ORDER_LIFECYCLE":
            pending_order_lifecycle.append(e)

        elif event == "TELEGRAM_SIGNAL":
            telegram["success" if e.get("success") else "failure"] += 1

        elif event == "TELEGRAM_DEAL_LIFECYCLE":
            lifecycle.append(e)
            deal_id = int(e.get("deal") or 0)
            if deal_id and deal_id in seen_lifecycle_deals:
                duplicate_events["duplicate_lifecycle_deal"] += 1
            elif deal_id:
                seen_lifecycle_deals.add(deal_id)
            entry = int(e.get("entry", -1))
            symbols[symbol]["lifecycle_open" if entry == 0 else "lifecycle_close"] += 1

    closed = [e for e in lifecycle if int(e.get("entry", -1)) != 0]
    measured_pips = [float(e["pips_result"]) for e in closed if e.get("pips_result") is not None]
    measured_net = [float(e["net"]) for e in closed if e.get("net") is not None]
    wins = sum(x > 0 for x in measured_pips)
    losses = sum(x < 0 for x in measured_pips)
    flat = sum(x == 0 for x in measured_pips)

    pending_states = {}
    for e in pending_order_lifecycle:
        order_id = int(e.get("order", 0) or 0)
        if order_id:
            pending_states.setdefault(order_id, set()).add(str(e.get("state")))

    successful_order_ids = {
        int(e.get("tracked_order"))
        for e in events
        if e.get("event") == "ORDER_RESULT"
        and e.get("success")
        and e.get("tracked_order")
    }
    lifecycle_orders = {int(e.get("order")) for e in lifecycle if e.get("order")}
    unmatched_lifecycle_orders = sorted(lifecycle_orders - successful_order_ids)

    result_signal_ids = {
        str(e.get("signal_id")) for e in events
        if e.get("event") == "ORDER_RESULT" and e.get("signal_id")
    }
    result_without_attempt = sorted(result_signal_ids - set(attempts))
    attempt_without_candidate = sorted(set(attempts) - set(candidates))

    successful = sum(v["execution_success"] for v in symbols.values())
    failed = sum(v["execution_failure"] for v in symbols.values())

    return {
        "classification": {
            "overall": "OBSERVED_FORWARD_RESEARCH",
            "source_rules": "UNCHANGED",
            "canonical_promotion": "NOT_PERFORMED",
        },
        "events": {
            "total": len(events),
            "invalid_json_lines": sum(e.get("event") == "INVALID_JSON" for e in events),
        },
        "signals": {
            "unique_candidates": len(candidates),
            "unique_attempts": len(attempts),
            "candidate_without_attempt": sorted(set(candidates) - set(attempts)),
            "attempt_without_candidate": attempt_without_candidate,
            "order_result_without_attempt": result_without_attempt,
        },
        "execution": {
            "successful": successful,
            "failed": failed,
            "failure_reasons": dict(sorted(failure_reasons.items())),
            "success_rate_among_attempts": successful / len(attempts) if attempts else None,
            "accepted_order_placements": sum(1 for e in events if e.get("event") == "ORDER_RESULT" and e.get("success") and e.get("tracked_order")),
            "immediate_deals_reported": sum(1 for e in events if e.get("event") == "ORDER_RESULT" and e.get("success") and e.get("tracked_deal")),
            "accepted_without_immediate_deal": sum(1 for e in events if e.get("event") == "ORDER_RESULT" and e.get("success") and e.get("tracked_order") and not e.get("tracked_deal")),
        },
        "lifecycle": {
            "open_events": sum(v["lifecycle_open"] for v in symbols.values()),
            "close_events": len(closed),
            "measured_close_pips": len(measured_pips),
            "missing_close_pips": len(closed) - len(measured_pips),
            "wins": wins,
            "losses": losses,
            "flat": flat,
            "win_rate_among_measured_closes": wins / len(measured_pips) if measured_pips else None,
            "sum_pips": sum(measured_pips) if measured_pips else 0.0,
            "sum_net": sum(measured_net) if measured_net else 0.0,
        },
        "telegram": dict(telegram),
        "symbols": {k: dict(v) for k, v in sorted(symbols.items())},
        "integrity": {
            "duplicate_order_result_events": duplicate_events["duplicate_order_result"],
            "duplicate_lifecycle_deal_events": duplicate_events["duplicate_lifecycle_deal"],
            "all_symbols_observed": sorted(symbols),
        },
        "pending_order_lifecycle": {
            "events": len(pending_order_lifecycle),
            "orders_observed": len(pending_states),
            "states": {state: sum(state in states for states in pending_states.values()) for state in sorted({s for states in pending_states.values() for s in states})},
            "orders_with_terminal_cancel_or_expiry": sum(any(s in states for s in {"CANCELED", "EXPIRED", "REJECTED"}) for states in pending_states.values()),
        },
        "linkage": {
            "successful_order_ids": len(successful_order_ids),
            "lifecycle_order_ids": len(lifecycle_orders),
            "unmatched_lifecycle_orders": unmatched_lifecycle_orders,
        },
        "geometry_measurements": {
            "note": "Observed telemetry only; these fields do not establish canonical geometry.",
            "candidate_rows_with_risk": sum(
                1 for e in candidates.values()
                if isinstance(e.get("candidate"), dict) and e["candidate"].get("risk") is not None
            ),
            "candidate_rows_with_secondary_2x": sum(
                1 for e in candidates.values()
                if isinstance(e.get("f13_2x"), dict)
                and e["f13_2x"].get("secondary_entry") is not None
            ),
        },
    }


def markdown(report: dict) -> str:
    ex = report["execution"]
    lc = report["lifecycle"]
    sig = report["signals"]
    lines = [
        "# SP2L Multi-Symbol Forward Audit",
        "",
        "Classification: OBSERVED_FORWARD_RESEARCH",
        "",
        "Telemetry-only report. It does not define, validate, or promote Strategy A geometry.",
        "",
        "## Coverage",
        f"- Unique candidates: **{sig['unique_candidates']}**",
        f"- Unique execution attempts: **{sig['unique_attempts']}**",
        f"- Candidates without attempt: **{len(sig['candidate_without_attempt'])}**",
        f"- Attempts without candidate: **{len(sig['attempt_without_candidate'])}**",
        f"- Order results without attempt: **{len(sig['order_result_without_attempt'])}**",
        f"- Successful order-result records: **{ex['successful']}**",
        f"- Accepted placements with immediate deal ID: **{ex['immediate_deals_reported']}**",
        f"- Accepted placements without immediate deal ID: **{ex['accepted_without_immediate_deal']}**",
        f"- Failed execution results: **{ex['failed']}**",
        "",
        "## Lifecycle",
        f"- Opens observed: **{lc['open_events']}**",
        f"- Closes observed: **{lc['close_events']}**",
        f"- Closes with measured pips: **{lc['measured_close_pips']}**",
        f"- Closes missing pips: **{lc['missing_close_pips']}**",
        f"- Measured wins/losses/flat: **{lc['wins']} / {lc['losses']} / {lc['flat']}**",
        f"- Win rate among measured closes: **{lc['win_rate_among_measured_closes']}**",
        f"- Sum pips: **{lc['sum_pips']:.2f}**",
        f"- Sum net: **{lc['sum_net']:.2f}**",
        "",
        "## Execution failures",
    ]
    if ex["failure_reasons"]:
        lines.extend(f"- {k}: **{v}**" for k, v in ex["failure_reasons"].items())
    else:
        lines.append("- None recorded.")
    lines += [
        "",
        "## Pending-order lifecycle",
        f"- Lifecycle events: **{report['pending_order_lifecycle']['events']}**",
        f"- Orders observed: **{report['pending_order_lifecycle']['orders_observed']}**",
        f"- Terminal canceled/expired/rejected orders: **{report['pending_order_lifecycle']['orders_with_terminal_cancel_or_expiry']}**",
        "",
        "## Integrity",
        f"- Successful order IDs linked to lifecycle telemetry: **{report['linkage']['successful_order_ids']}**",
        f"- Lifecycle order IDs: **{report['linkage']['lifecycle_order_ids']}**",
        f"- Unmatched lifecycle order IDs: **{len(report['linkage']['unmatched_lifecycle_orders'])}**",
        "",
        "## Duplicate / linkage integrity",
        f"- Duplicate order-result events: **{report['integrity']['duplicate_order_result_events']}**",
        f"- Duplicate lifecycle-deal events: **{report['integrity']['duplicate_lifecycle_deal_events']}**",
        "",
        "## Source boundary",
        "- P-Gap, spike, SL, TP, fill semantics, and pending-order lifecycle remain research telemetry.",
        "- No parameter selection, canonical promotion, or production BUY/SELL decision is performed by this audit.",
    ]
    return "\\n".join(lines) + "\\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    report = audit(read_events(args.events))
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
