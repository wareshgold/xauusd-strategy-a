"""Read-only SP2L forward-test P&L reconciliation against MT5 history.

This diagnostic never places, modifies, or cancels orders. It compares:
1) SP2L forward event-ledger closed-trade net values
2) MT5 history deals for the same symbol/magic
3) MT5 account balance/equity snapshot

The event ledger is evidence, not canonical strategy logic.
Use this tool on PS3 while the live forward runner remains untouched on PS1.

Usage:
    python scripts/reconcile_sp2l_forward_mt5.py
    python scripts/reconcile_sp2l_forward_mt5.py --date 2026-10-06
    python scripts/reconcile_sp2l_forward_mt5.py --event-file path/to/events.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "forward-test"
DEFAULT_EVENT = ARTIFACTS / "SP2L_V3_XAUUSD_RR2_ACT10_TRAIL2_FORWARD_EVENTS.jsonl"
IRAN_TZ = ZoneInfo("Asia/Tehran")
DEFAULT_SYMBOL = "XAUUSD.ecn"
DEFAULT_MAGIC = 26092201
EPSILON = 0.01


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Read-only SP2L event-ledger vs MT5 P&L reconciliation")
    p.add_argument("--date", help="Tehran calendar date YYYY-MM-DD; default: today")
    p.add_argument("--event-file", type=Path, default=DEFAULT_EVENT)
    p.add_argument("--symbol", default=DEFAULT_SYMBOL)
    p.add_argument("--magic", type=int, default=DEFAULT_MAGIC)
    p.add_argument("--json", action="store_true", dest="as_json")
    return p.parse_args()


def tehran_day_bounds(day_text: str | None) -> tuple[datetime, datetime, str]:
    if day_text:
        day = datetime.strptime(day_text, "%Y-%m-%d").date()
    else:
        day = datetime.now(IRAN_TZ).date()
    start_local = datetime.combine(day, time.min, tzinfo=IRAN_TZ)
    end_local = datetime.combine(day, time.max, tzinfo=IRAN_TZ)
    return start_local, end_local, day.isoformat()


def utc_epoch(dt: datetime) -> float:
    return dt.astimezone(timezone.utc).timestamp()


def load_event_ledger(path: Path, day: str, symbol: str) -> dict:
    closed = []
    lifecycle_by_position: dict[int, list[dict]] = defaultdict(list)
    order_results = []
    signals = 0

    if not path.exists():
        raise FileNotFoundError(f"event file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if ev.get("symbol") not in (None, "", symbol):
                continue

            try:
                ts = datetime.fromisoformat(str(ev.get("ts_utc", "")).replace("Z", "+00:00"))
                local_day = ts.astimezone(IRAN_TZ).date().isoformat()
            except (ValueError, TypeError):
                continue

            if local_day != day:
                continue

            kind = ev.get("event")
            if kind == "TELEGRAM_SIGNAL":
                signals += 1
            elif kind == "ORDER_RESULT":
                order_results.append(ev)
            elif kind == "TELEGRAM_DEAL_LIFECYCLE":
                position_id = int(ev.get("position") or ev.get("position_id") or 0)
                lifecycle_by_position[position_id].append(ev)
                # Dashboard currently uses this field for its daily net.
                entry = int(ev.get("entry", -1))
                if entry != getattr(mt5, "DEAL_ENTRY_IN", 0):
                    closed.append(
                        {
                            "position_id": position_id,
                            "event_ts": ts.isoformat(),
                            "net": float(ev.get("net", 0.0) or 0.0),
                            "profit": float(ev.get("profit", 0.0) or 0.0),
                            "commission": float(ev.get("commission", 0.0) or 0.0),
                            "swap": float(ev.get("swap", 0.0) or 0.0),
                            "fee": float(ev.get("fee", 0.0) or 0.0),
                            "entry": entry,
                            "ticket": int(ev.get("deal") or ev.get("ticket") or 0),
                        }
                    )

    return {
        "signals": signals,
        "closed": closed,
        "lifecycle_by_position": lifecycle_by_position,
        "order_results": order_results,
    }


def mt5_deals(start: datetime, end: datetime, symbol: str, magic: int) -> list[dict]:
    deals = mt5.history_deals_get(start, end, group=f"*{symbol}*")
    if deals is None:
        raise RuntimeError(f"history_deals_get failed: {mt5.last_error()}")

    out = []
    for d in deals:
        row = d._asdict()
        if str(row.get("symbol") or "") != symbol:
            continue
        if int(row.get("magic") or 0) != magic:
            continue
        row["net"] = (
            float(row.get("profit") or 0.0)
            + float(row.get("commission") or 0.0)
            + float(row.get("swap") or 0.0)
            + float(row.get("fee") or 0.0)
        )
        out.append(row)
    return out


def mt5_closed_positions(deals: list[dict]) -> dict[int, dict]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for d in deals:
        pid = int(d.get("position_id") or 0)
        if pid:
            grouped[pid].append(d)

    closed = {}
    for pid, rows in grouped.items():
        entries = {int(r.get("entry") or 0) for r in rows}
        # Position is treated as closed when MT5 contains an OUT/OUT_BY deal.
        out_rows = [
            r for r in rows
            if int(r.get("entry") or 0) in (
                getattr(mt5, "DEAL_ENTRY_OUT", 1),
                getattr(mt5, "DEAL_ENTRY_OUT_BY", 2),
            )
        ]
        if not out_rows:
            continue
        closed[pid] = {
            "position_id": pid,
            "deals": len(rows),
            "out_deals": len(out_rows),
            "net": sum(float(r["net"]) for r in rows),
            "profit": sum(float(r.get("profit") or 0.0) for r in rows),
            "commission": sum(float(r.get("commission") or 0.0) for r in rows),
            "swap": sum(float(r.get("swap") or 0.0) for r in rows),
            "fee": sum(float(r.get("fee") or 0.0) for r in rows),
            "entry_types": sorted(entries),
        }
    return closed


def fmt(x: float) -> str:
    return f"{x:+.2f}"


def build_report(args: argparse.Namespace) -> dict:
    start, end, day = tehran_day_bounds(args.date)

    event_data = load_event_ledger(args.event_file, day, args.symbol)

    terminal_path = None
    if not mt5.initialize():
        raise RuntimeError(f"mt5.initialize() failed: {mt5.last_error()}")

    try:
        account = mt5.account_info()
        terminal = mt5.terminal_info()
        deals = mt5_deals(start, end, args.symbol, args.magic)
        mt5_positions = mt5_closed_positions(deals)
    finally:
        mt5.shutdown()

    event_by_pos = {}
    for row in event_data["closed"]:
        pid = int(row["position_id"])
        if pid:
            event_by_pos[pid] = row

    event_net = sum(r["net"] for r in event_data["closed"])
    mt5_net = sum(r["net"] for r in mt5_positions.values())

    common = sorted(set(event_by_pos) & set(mt5_positions))
    event_only = sorted(set(event_by_pos) - set(mt5_positions))
    mt5_only = sorted(set(mt5_positions) - set(event_by_pos))

    mismatches = []
    for pid in common:
        e = event_by_pos[pid]["net"]
        m = mt5_positions[pid]["net"]
        delta = m - e
        if abs(delta) > EPSILON:
            mismatches.append(
                {
                    "position_id": pid,
                    "event_net": e,
                    "mt5_net": m,
                    "delta_mt5_minus_event": delta,
                }
            )

    return {
        "date_tehran": day,
        "symbol": args.symbol,
        "magic": args.magic,
        "event_file": str(args.event_file),
        "event_signals": event_data["signals"],
        "event_closed_count": len(event_data["closed"]),
        "event_net_usd": event_net,
        "mt5_deal_count": len(deals),
        "mt5_closed_position_count": len(mt5_positions),
        "mt5_net_usd": mt5_net,
        "delta_mt5_minus_event_usd": mt5_net - event_net,
        "common_positions": len(common),
        "event_only_positions": event_only,
        "mt5_only_positions": mt5_only,
        "position_mismatches": mismatches,
        "account": {
            "login": int(account.login) if account else None,
            "server": str(account.server) if account else None,
            "balance": float(account.balance) if account else None,
            "equity": float(account.equity) if account else None,
            "profit": float(account.profit) if account else None,
            "trade_mode": int(account.trade_mode) if account else None,
        },
        "terminal_connected": bool(terminal.connected) if terminal else False,
    }


def print_report(r: dict) -> None:
    print("=" * 72)
    print("SP2L FORWARD ↔ MT5 READ-ONLY RECONCILIATION")
    print("=" * 72)
    print(f"Tehran date       : {r['date_tehran']}")
    print(f"Symbol / magic    : {r['symbol']} / {r['magic']}")
    print(f"Event file        : {r['event_file']}")
    print()
    print(f"Event signals     : {r['event_signals']}")
    print(f"Event closed      : {r['event_closed_count']}")
    print(f"Event net USD     : {fmt(r['event_net_usd'])}")
    print()
    print(f"MT5 deals         : {r['mt5_deal_count']}")
    print(f"MT5 closed pos.   : {r['mt5_closed_position_count']}")
    print(f"MT5 net USD       : {fmt(r['mt5_net_usd'])}")
    print(f"NET DELTA         : {fmt(r['delta_mt5_minus_event_usd'])}")
    print()
    print(f"Common positions  : {r['common_positions']}")
    print(f"Event-only        : {r['event_only_positions']}")
    print(f"MT5-only          : {r['mt5_only_positions']}")
    print(f"P&L mismatches    : {len(r['position_mismatches'])}")
    for m in r["position_mismatches"]:
        print(
            f"  position {m['position_id']}: "
            f"event={fmt(m['event_net'])} "
            f"mt5={fmt(m['mt5_net'])} "
            f"delta={fmt(m['delta_mt5_minus_event'])}"
        )
    print()
    a = r["account"]
    print(
        f"Account snapshot   : {a['login']} @ {a['server']} "
        f"balance={a['balance']:.2f} equity={a['equity']:.2f} "
        f"floating_profit={a['profit']:.2f}"
    )
    print(f"Terminal connected : {r['terminal_connected']}")
    print()
    status = (
        "PASS: event and MT5 closed-position P&L reconcile within $0.01."
        if not r["event_only_positions"]
        and not r["mt5_only_positions"]
        and not r["position_mismatches"]
        else "MISMATCH: inspect position-level rows above; do not treat Dashboard P&L as MT5 truth yet."
    )
    print(status)


def main() -> int:
    args = parse_args()
    try:
        report = build_report(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
