"""SP2L 8-hour read-only health reconciliation.

Research/diagnostic only. This script NEVER places, modifies, or cancels orders.
It compares:
  1) implementation-aligned M1 replay candidates,
  2) candidates emitted by the live forward event log,
  3) MT5 orders/deals for the active account + magic.

Canonical=False. The V3 geometry remains research implementation and is not
promoted to source-confirmed Strategy A.

Important:
- The live runner has a startup freshness watermark. Candidates at/before the
  latest START watermark are reported separately and are not counted as
  "missing live candidates".
- No guessed fill semantics are introduced. MT5 reconciliation uses exact
  signal/order/deal identifiers where the event log provides them.
- Historical M1 replay cannot reproduce tick-level bid/ask trailing exactly;
  therefore this version reports observed MT5 USD and does not fabricate an
  "expected USD" value.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

import sp2l_v3_config as cfg


CANONICAL = False
DEFAULT_EVENT_FILE = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "forward-test"
    / "SP2L_V3_XAUUSD_RR2_ACT10_TRAIL2_FORWARD_EVENTS.jsonl"
)


def parse_args():
    p = argparse.ArgumentParser(description="SP2L 8h read-only health reconciliation")
    p.add_argument("--hours", type=float, default=8.0)
    p.add_argument("--mt5-path", default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    p.add_argument("--symbol", default="XAUUSD.ecn")
    p.add_argument("--magic", type=int, default=26092201)
    p.add_argument("--event-file", default=str(DEFAULT_EVENT_FILE))
    p.add_argument("--output-dir", default="artifacts/forward-test")
    return p.parse_args()


def iso(ts):
    if ts is None:
        return "-"
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def mt5_server_offset_seconds(symbol: str) -> int:
    """Return the broker/server clock offset used by MT5 bar timestamps."""
    tick = mt5.symbol_info_tick(symbol)
    tick_ts = int(getattr(tick, "time", 0) or 0) if tick else 0
    if tick_ts <= 0:
        raise RuntimeError("MT5 server clock unavailable: no symbol tick")
    delta = tick_ts - int(datetime.now(timezone.utc).timestamp())
    hours = round(delta / 3600)
    if abs(delta - hours * 3600) > 900 or not (-12 <= hours <= 14):
        raise RuntimeError(f"MT5 server offset is not a stable whole-hour offset: {delta}s")
    return int(hours * 3600)


def server_ts_from_utc_dt(utc_dt: datetime, server_offset_seconds: int) -> int:
    return int(utc_dt.timestamp()) + int(server_offset_seconds)


def server_dt_for_mt5_api(utc_dt: datetime, server_offset_seconds: int) -> datetime:
    return datetime.fromtimestamp(
        server_ts_from_utc_dt(utc_dt, server_offset_seconds),
        tz=timezone.utc,
    )


def event_ts(obj):
    try:
        return datetime.fromisoformat(str(obj["ts_utc"]).replace("Z", "+00:00"))
    except Exception:
        return None


def load_events(path: Path):
    events = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                events.append(obj)
        except Exception:
            continue
    return events


def candidate_key(c):
    return (c["symbol"], int(c["trigger_time"]), c["direction"])


def replay_candidates(rates, symbol, start_ts, end_ts):
    """Replay cfg's existing implementation causally, bar by bar.

    We expose the existing V3 implementation rather than inventing new geometry.
    At each completed bar, only candidates whose trigger_time is already inside
    the observed prefix can be considered. Duplicate candidate keys are removed.
    """
    out = {}
    candles = []
    for row in rates:
        candles.append({
            "time": int(row["time"]),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        })
        if len(candles) < 3:
            continue
        try:
            c = cfg.find_latest_candidate(candles, symbol)
        except Exception:
            continue
        if not c:
            continue
        ts = int(c["trigger_time"])
        if start_ts <= ts <= end_ts:
            out[candidate_key(c)] = c
    return sorted(out.values(), key=lambda x: (int(x["trigger_time"]), x["direction"]))


def fmt_candidate(c):
    return (
        f'{c["direction"]} {iso(c["trigger_time"])} '
        f'entry={float(c["theoretical_entry"]):.2f} '
        f'sl={float(c["sl"]):.2f} '
        f'tp={float(c["tp"]):.2f}'
    )


def main():
    args = parse_args()
    event_path = Path(args.event_file)
    now = datetime.now(timezone.utc)
    end_dt = now
    start_dt = now - timedelta(hours=args.hours)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    print("SP2L V3 — 8H HEALTH RECONCILIATION")
    print("READ-ONLY / RESEARCH ONLY / canonical=false")
    print(f"WINDOW UTC: {start_dt.isoformat()} -> {end_dt.isoformat()}")
    print()

    if not mt5.initialize(path=args.mt5_path, timeout=60000):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        account = mt5.account_info()
        info = mt5.symbol_info(args.symbol)
        if account is None or info is None:
            raise SystemExit(f"MT5 account/symbol unavailable: {mt5.last_error()}")

        if not mt5.symbol_select(args.symbol, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

        login = int(getattr(account, "login", 0) or 0)
        point = float(getattr(info, "point", 0.0) or 0.0)
        digits = int(getattr(info, "digits", 0) or 0)
        contract_size = float(getattr(info, "trade_contract_size", 0.0) or 0.0)

        print("=== ACCOUNT / SYMBOL ===")
        print(f"ACCOUNT={login}")
        print(f"SERVER={getattr(account, 'server', '-')}")
        print(f"SYMBOL={args.symbol}")
        print(f"POINT={point}")
        print(f"DIGITS={digits}")
        print(f"CONTRACT_SIZE={contract_size}")
        print(f"MAGIC={args.magic}")
        print()

        events = load_events(event_path)
        window_events = [
            e for e in events
            if (t := event_ts(e)) is not None and start_dt <= t <= end_dt
        ]

        starts = [
            e for e in events
            if e.get("event") == "START"
            and int(e.get("account_login", 0) or 0) == login
            and (t := event_ts(e)) is not None
            and t <= end_dt
        ]
        latest_start = max(starts, key=event_ts) if starts else None
        # Event timestamps are UTC; MT5 candle/order timestamps in this
        # terminal use broker/server-clock epoch values. Convert the runner
        # START instant before comparing it with candidate trigger_time.
        server_offset_seconds = mt5_server_offset_seconds(args.symbol)
        window_start_server_ts = start_ts + server_offset_seconds
        window_end_server_ts = end_ts + server_offset_seconds
        session_start_dt = event_ts(latest_start) if latest_start else start_dt
        session_start_ts = max(
            window_start_server_ts,
            server_ts_from_utc_dt(session_start_dt, server_offset_seconds),
        )

        print("=== RUNNER SESSION ===")
        print(f"EVENT_FILE={event_path}")
        print(f"EVENTS_TOTAL={len(events)}")
        print(f"EVENTS_IN_WINDOW={len(window_events)}")
        if latest_start:
            print(f"LATEST_START_UTC={session_start_dt.isoformat()}")
            print(f"LATEST_START_ACCOUNT={login}")
            print(f"MT5_SERVER_OFFSET_SECONDS={server_offset_seconds}")
            print(f"LATEST_START_SERVER_TS={session_start_ts}")
            print(f"LATEST_START_SERVER_TIME={iso(session_start_ts)}")
        else:
            print("LATEST_START_UTC=NOT_FOUND")
            print(f"MT5_SERVER_OFFSET_SECONDS={server_offset_seconds}")
            print(f"LATEST_START_SERVER_TS={session_start_ts}")
        print()

        # Match the live runner's 120-bar (2h) warm-up window so a setup
        # formed shortly before the health window can still produce a trigger
        # inside the window. Warm-up bars are never counted as 8h candidates.
        rates = mt5.copy_rates_range(
            args.symbol,
            mt5.TIMEFRAME_M1,
            server_dt_for_mt5_api(start_dt - timedelta(seconds=7200), server_offset_seconds),
            server_dt_for_mt5_api(end_dt, server_offset_seconds),
        )
        if rates is None:
            raise SystemExit(f"M1 copy_rates_range failed: {mt5.last_error()}")

        rates = list(rates)
        print("=== MARKET DATA ===")
        print(f"M1_BARS={len(rates)}")
        if rates:
            print(f"M1_FIRST={iso(rates[0]['time'])}")
            print(f"M1_LAST={iso(rates[-1]['time'])}")
        print()

        all_replay = replay_candidates(
            rates,
            args.symbol,
            window_start_server_ts,
            window_end_server_ts,
        )
        session_replay = [
            c for c in all_replay if int(c["trigger_time"]) >= session_start_ts
        ]

        live_candidates = []
        for e in events:
            if e.get("event") != "CANDIDATE":
                continue
            if e.get("symbol") != args.symbol:
                continue
            t = event_ts(e)
            if t is None or t < session_start_dt or t > end_dt:
                continue
            c = e.get("candidate") or {}
            if c.get("direction") not in ("BUY", "SELL"):
                continue
            if int(c.get("trigger_time", 0) or 0) < session_start_ts:
                continue
            live_candidates.append(c)

        live_map = {candidate_key(c): c for c in live_candidates}
        replay_map = {candidate_key(c): c for c in session_replay}
        missing = [c for k, c in replay_map.items() if k not in live_map]
        unexpected = [c for k, c in live_map.items() if k not in replay_map]

        print("=== DETECTOR RECONCILIATION ===")
        print(f"REPLAY_CANDIDATES_IN_8H={len(all_replay)}")
        print(f"REPLAY_CANDIDATES_AFTER_LATEST_START={len(session_replay)}")
        print(f"LIVE_CANDIDATE_EVENTS_AFTER_LATEST_START={len(live_candidates)}")
        print(f"MISSING_LIVE_CANDIDATES={len(missing)}")
        print(f"UNEXPECTED_LIVE_CANDIDATES={len(unexpected)}")
        if missing:
            print("\n-- MISSING --")
            for c in missing:
                print(fmt_candidate(c))
        if unexpected:
            print("\n-- UNEXPECTED --")
            for c in unexpected:
                print(fmt_candidate(c))
        print()

        # Exact event-side order mapping.
        order_results = []
        for e in events:
            if e.get("event") != "ORDER_RESULT":
                continue
            t = event_ts(e)
            if t is None or t < session_start_dt or t > end_dt:
                continue
            result = e.get("result") or {}
            if e.get("symbol") != args.symbol:
                continue
            order_results.append({
                "ts_utc": e.get("ts_utc"),
                "signal_id": e.get("signal_id"),
                "direction": e.get("direction"),
                "order": int(result.get("order", e.get("tracked_order", 0)) or 0),
                "deal": int(result.get("deal", e.get("tracked_deal", 0)) or 0),
                "success": bool(result.get("ok", False)),
                "retcode": int(result.get("retcode", -1) or -1),
                "entry": e.get("entry"),
                "sl": e.get("sl"),
                "tp": e.get("tp"),
            })

        print("=== LIVE ORDER EVENTS ===")
        print(f"ORDER_RESULT_EVENTS={len(order_results)}")
        for o in order_results:
            print(
                f'{o["ts_utc"]} {o["direction"]} order={o["order"]} '
                f'ok={o["success"]} retcode={o["retcode"]} '
                f'entry={o["entry"]} sl={o["sl"]} tp={o["tp"]}'
            )
        print()

        # MT5 history. We deliberately do not infer fills from price touching;
        # actual broker orders/deals are the execution truth.
        # Reconcile the broker history against the whole active runner session,
        # not merely the trailing 8h reporting window. A runner START can be
        # older than 8h while its lifecycle events are still intentionally in
        # scope; querying only start_dt falsely labels those earlier orders as
        # "missing". This is a history-scope fix only and does not alter any
        # strategy/detector/execution rule.
        hist_start_dt = session_start_dt if latest_start else start_dt
        hist_from = server_dt_for_mt5_api(hist_start_dt, server_offset_seconds)
        hist_to = server_dt_for_mt5_api(end_dt, server_offset_seconds)
        orders = list(mt5.history_orders_get(hist_from, hist_to, group=args.symbol) or [])
        deals = list(mt5.history_deals_get(hist_from, hist_to, group=args.symbol) or [])

        orders = [
            o for o in orders
            if int(getattr(o, "magic", 0) or 0) == args.magic
            and int(getattr(o, "ticket", 0) or 0) > 0
        ]
        deals = [
            d for d in deals
            if int(getattr(d, "magic", 0) or 0) == args.magic
            and int(getattr(d, "ticket", 0) or 0) > 0
        ]

        print("=== MT5 HISTORY ===")
        print(f"MT5_HISTORY_START_UTC={hist_start_dt.isoformat()}")
        print(f"MT5_HISTORY_END_UTC={end_dt.isoformat()}")
        print(f"MT5_ORDERS={len(orders)}")
        print(f"MT5_DEALS={len(deals)}")

        # ORDER_RESULT is the execution-attempt record. Pending-order and
        # TELEGRAM_DEAL_LIFECYCLE events also carry broker order tickets and
        # are authoritative observations of the actual broker-side order/deal
        # linkage. Include all of them so a later lifecycle event is not
        # incorrectly reported as an "MT5 order without event result".
        observed_event_order_ids = set()
        lifecycle_order_ids = set()
        for e in events:
            if e.get("symbol") != args.symbol:
                continue
            t = event_ts(e)
            if t is None or t < session_start_dt or t > end_dt:
                continue
            event_name = e.get("event")
            order_id = 0
            if event_name == "ORDER_RESULT":
                result = e.get("result") or {}
                order_id = int(result.get("order", e.get("tracked_order", 0)) or 0)
            elif event_name in ("PENDING_ORDER_LIFECYCLE", "TELEGRAM_DEAL_LIFECYCLE"):
                order_id = int(e.get("order", 0) or 0)
                if order_id:
                    lifecycle_order_ids.add(order_id)
            if order_id:
                observed_event_order_ids.add(order_id)

        order_result_ids = {o["order"] for o in order_results if o["order"]}
        mt5_order_ids = {int(o.ticket) for o in orders}
        missing_orders = sorted(observed_event_order_ids - mt5_order_ids)
        unexpected_orders = sorted(mt5_order_ids - observed_event_order_ids)

        print(f"EVENT_ORDER_RESULT_IDS={len(order_result_ids)}")
        print(f"EVENT_OBSERVED_ORDER_IDS={len(observed_event_order_ids)}")
        print(f"EVENT_LIFECYCLE_ORDER_IDS={len(lifecycle_order_ids)}")
        print(f"EVENT_ORDERS_MISSING_IN_MT5_HISTORY={len(missing_orders)}")
        print(f"MT5_ORDERS_WITHOUT_EVENT_OBSERVATION={len(unexpected_orders)}")
        if missing_orders:
            print(f"MISSING_MT5_ORDER_IDS={missing_orders}")
        if unexpected_orders:
            print(f"UNEXPECTED_MT5_ORDER_IDS={unexpected_orders}")
        print()

        # Actual P&L is reported exactly from MT5 deals. For open positions,
        # current floating profit is reported separately and is not treated as
        # realized P&L.
        exit_deals = [
            d for d in deals
            if int(getattr(d, "entry", -1)) in (
                getattr(mt5, "DEAL_ENTRY_OUT", 1),
                getattr(mt5, "DEAL_ENTRY_OUT_BY", 3),
            )
        ]
        realized_profit = sum(float(getattr(d, "profit", 0.0) or 0.0) for d in exit_deals)
        commissions = sum(float(getattr(d, "commission", 0.0) or 0.0) for d in exit_deals)
        swaps = sum(float(getattr(d, "swap", 0.0) or 0.0) for d in exit_deals)
        realized_net = realized_profit + commissions + swaps

        positions = list(mt5.positions_get(symbol=args.symbol) or [])
        positions = [
            p for p in positions
            if int(getattr(p, "magic", 0) or 0) == args.magic
        ]
        floating = sum(float(getattr(p, "profit", 0.0) or 0.0) for p in positions)

        print("=== USD RECONCILIATION ===")
        print(f"REALIZED_EXIT_DEALS={len(exit_deals)}")
        print(f"MT5_REALIZED_PROFIT_USD={realized_profit:.2f}")
        print(f"MT5_EXIT_COMMISSION_USD={commissions:.2f}")
        print(f"MT5_EXIT_SWAP_USD={swaps:.2f}")
        print(f"MT5_REALIZED_NET_USD={realized_net:.2f}")
        print(f"OPEN_POSITIONS={len(positions)}")
        print(f"MT5_FLOATING_PROFIT_USD={floating:.2f}")
        print()

        status = "PASS" if not missing and not missing_orders else "RECONCILIATION_GAP"
        print("=== HEALTH STATUS ===")
        print(f"STATUS={status}")
        print("CANONICAL=false")
        print("NO_ORDERS_SENT=true")
        print("NO_ORDERS_MODIFIED=true")

        output = {
            "version": "SP2L_8H_HEALTH_RECONCILIATION_20261005",
            "canonical": False,
            "read_only": True,
            "window_start_utc": start_dt.isoformat(),
            "window_end_utc": end_dt.isoformat(),
            "mt5_window_start_server_ts": window_start_server_ts,
            "mt5_window_end_server_ts": window_end_server_ts,
            "account_login": login,
            "server": getattr(account, "server", None),
            "symbol": args.symbol,
            "magic": args.magic,
            "point": point,
            "latest_runner_start_utc": session_start_dt.isoformat() if latest_start else None,
            "mt5_server_offset_seconds": server_offset_seconds,
            "latest_runner_start_server_ts": session_start_ts,
            "latest_runner_start_server_time": iso(session_start_ts),
            "m1_bars": len(rates),
            "m1_warmup_seconds": 7200,
            "replay_candidates_8h": len(all_replay),
            "replay_candidates_after_latest_start": len(session_replay),
            "live_candidate_events_after_latest_start": len(live_candidates),
            "missing_live_candidates": [candidate_key(c) for c in missing],
            "unexpected_live_candidates": [candidate_key(c) for c in unexpected],
            "event_order_results": order_results,
            "mt5_order_count": len(orders),
            "mt5_deal_count": len(deals),
            "missing_mt5_orders": missing_orders,
            "unexpected_mt5_orders": unexpected_orders,
            "realized_profit_usd": realized_profit,
            "realized_commission_usd": commissions,
            "realized_swap_usd": swaps,
            "realized_net_usd": realized_net,
            "open_positions": len(positions),
            "floating_profit_usd": floating,
            "status": status,
        }

        outdir = Path(args.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        outfile = outdir / f"SP2L_8H_HEALTH_RECONCILIATION_{stamp}.json"
        outfile.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"REPORT_JSON={outfile}")

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()