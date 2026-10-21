"""Read-only audit of runner-owned trailing exits and post-exit XAUUSD price path.

This tool does not place or modify orders. It joins TRAIL_UPDATE events to MT5
history by position ID, includes observed deal costs, and measures price
excursions only on fully completed M1 bars after the exit minute. OHLC cannot
establish intrabar ordering, so the exit minute is deliberately excluded.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENT_LOG = ROOT / "artifacts" / "forward-test" / "SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl"
OUT = ROOT / "artifacts" / "research-audits"
DEFAULT_MAGIC = 26092201
DEFAULT_HORIZONS = (5, 15, 30, 60)


def field(obj, name, default=0):
    value = getattr(obj, name, default)
    return default if value is None else value


def load_trail_events(path: Path, symbol: str):
    raw = path.read_bytes()
    by_position = {}
    for line_number, raw_line in enumerate(raw.splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        if event.get("event") != "TRAIL_UPDATE" or event.get("symbol") != symbol:
            continue
        position = int(event.get("position", 0) or 0)
        if position <= 0:
            continue
        by_position.setdefault(position, []).append(event)
    return by_position, hashlib.sha256(raw).hexdigest()


def aggregate_position_deals(deals, symbol: str, magic: int):
    """Aggregate one MT5 position's actual deal records; never infer SL/TP from deals."""
    selected = [d for d in (deals or []) if str(field(d, "symbol", "")) == symbol]
    entries = [
        d for d in selected
        if int(field(d, "entry", -1)) == mt5.DEAL_ENTRY_IN
        and int(field(d, "magic", 0) or 0) == magic
    ]
    if not entries:
        return {"history_status": "RUNNER_ENTRY_NOT_FOUND"}
    entries.sort(key=lambda d: (int(field(d, "time", 0)), int(field(d, "ticket", 0))))
    position_id = int(field(entries[0], "position_id", 0) or 0)
    exits = [
        d for d in selected
        if int(field(d, "entry", -1)) in (
            mt5.DEAL_ENTRY_OUT,
            getattr(mt5, "DEAL_ENTRY_OUT_BY", mt5.DEAL_ENTRY_OUT),
        )
    ]
    entry_volume = sum(float(field(d, "volume", 0.0) or 0.0) for d in entries)
    if entry_volume <= 0:
        return {"history_status": "INVALID_ENTRY_VOLUME", "position_id": position_id}
    entry_price = sum(
        float(field(d, "price", 0.0) or 0.0) * float(field(d, "volume", 0.0) or 0.0)
        for d in entries
    ) / entry_volume
    costs = {
        "observed_gross_profit_usd": sum(float(field(d, "profit", 0.0) or 0.0) for d in selected),
        "observed_commission_usd": sum(float(field(d, "commission", 0.0) or 0.0) for d in selected),
        "observed_swap_usd": sum(float(field(d, "swap", 0.0) or 0.0) for d in selected),
        "observed_fee_usd": sum(float(field(d, "fee", 0.0) or 0.0) for d in selected),
    }
    costs["observed_net_usd"] = sum(costs.values())
    if not exits:
        return {
            "history_status": "POSITION_STILL_OPEN_OR_NO_EXIT_DEAL",
            "position_id": position_id,
            "direction": "BUY" if int(field(entries[0], "type", -1)) == mt5.DEAL_TYPE_BUY else "SELL",
            "entry_time": int(field(entries[0], "time", 0)),
            "entry_price": entry_price,
            "volume": entry_volume,
            **costs,
        }
    exits.sort(key=lambda d: (int(field(d, "time", 0)), int(field(d, "ticket", 0))))
    exit_volume = sum(float(field(d, "volume", 0.0) or 0.0) for d in exits)
    exit_price = (
        sum(float(field(d, "price", 0.0) or 0.0) * float(field(d, "volume", 0.0) or 0.0) for d in exits) / exit_volume
        if exit_volume > 0 else float(field(exits[-1], "price", 0.0) or 0.0)
    )
    return {
        "history_status": "CLOSED",
        "position_id": position_id,
        "direction": "BUY" if int(field(entries[0], "type", -1)) == mt5.DEAL_TYPE_BUY else "SELL",
        "entry_time": int(field(entries[0], "time", 0)),
        "exit_time": int(field(exits[-1], "time", 0)),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "volume": entry_volume,
        "entry_deals": len(entries),
        "exit_deals": len(exits),
        "exit_reason_code": int(field(exits[-1], "reason", -1)),
        **costs,
    }


def price_excursions(direction: str, reference_price: float, bars, start_epoch: int, end_epoch: int):
    """Compute price-only MFE/MAE on bars wholly within [start_epoch, end_epoch)."""
    chosen = [
        b for b in bars
        if start_epoch <= int(b["time"]) < end_epoch
    ]
    if not chosen:
        return {"mfe_price": None, "mae_price": None, "bars": 0}
    if direction == "BUY":
        mfe = max(max(0.0, float(b["high"]) - reference_price) for b in chosen)
        mae = max(max(0.0, reference_price - float(b["low"])) for b in chosen)
    else:
        mfe = max(max(0.0, reference_price - float(b["low"])) for b in chosen)
        mae = max(max(0.0, float(b["high"]) - reference_price) for b in chosen)
    return {"mfe_price": mfe, "mae_price": mae, "bars": len(chosen)}


def post_exit_excursions(direction: str, exit_price: float, bars, exit_time: int, horizons=DEFAULT_HORIZONS):
    # Exclude the entire exit minute: M1 OHLC cannot tell whether its extremes
    # occurred before or after the actual deal timestamp.
    first_full_minute = (int(exit_time) // 60 + 1) * 60
    result = {"post_exit_start_epoch": first_full_minute}
    for minutes in horizons:
        metrics = price_excursions(
            direction, exit_price, bars,
            first_full_minute, first_full_minute + int(minutes) * 60,
        )
        result[f"post_exit_{minutes}m_mfe_price"] = metrics["mfe_price"]
        result[f"post_exit_{minutes}m_mae_price"] = metrics["mae_price"]
        result[f"post_exit_{minutes}m_bars"] = metrics["bars"]
    return result


def parse_horizons(raw: str):
    try:
        values = sorted(set(int(x.strip()) for x in raw.split(",") if x.strip()))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("horizons must be comma-separated positive minutes") from exc
    if not values or any(x <= 0 for x in values):
        raise argparse.ArgumentTypeError("horizons must be comma-separated positive minutes")
    return tuple(values)


def fetch_m1(symbol: str, start_epoch: int, end_epoch: int):
    import numpy as np

    start = datetime.fromtimestamp(start_epoch, timezone.utc)
    end = datetime.fromtimestamp(end_epoch, timezone.utc)
    chunks = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=7), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, chunk_end)
        if rates is None:
            raise RuntimeError(f"copy_rates_range failed: {mt5.last_error()}")
        if len(rates):
            chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)
    if not chunks:
        return [], hashlib.sha256(b"").hexdigest()
    rates = np.concatenate(chunks)
    rates.sort(order="time")
    _, unique_idx = np.unique(rates["time"], return_index=True)
    rates = rates[np.sort(unique_idx)]
    bars = [
        {"time": int(b["time"]), "high": float(b["high"]), "low": float(b["low"]), "close": float(b["close"])}
        for b in rates
    ]
    return bars, hashlib.sha256(rates.tobytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mt5-path", required=True)
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--magic", type=int, default=DEFAULT_MAGIC)
    parser.add_argument("--event-log", type=Path, default=DEFAULT_EVENT_LOG)
    parser.add_argument("--horizons", default="5,15,30,60")
    args = parser.parse_args()
    horizons = parse_horizons(args.horizons)
    if not args.event_log.is_file():
        raise RuntimeError(f"Event log not found: {args.event_log}")
    trail_events, event_sha = load_trail_events(args.event_log, args.symbol)
    if not trail_events:
        raise RuntimeError(f"No TRAIL_UPDATE positions found for {args.symbol} in {args.event_log}")

    if not mt5.initialize(path=args.mt5_path):
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        info = mt5.symbol_info(args.symbol)
        if info is None or float(field(info, "point", 0.0) or 0.0) <= 0:
            raise RuntimeError(f"Invalid symbol metadata for {args.symbol}: {mt5.last_error()}")
        rows = []
        for position_id, events in sorted(trail_events.items()):
            deals = mt5.history_deals_get(position=position_id)
            if deals is None:
                rows.append({
                    "position_id": position_id,
                    "history_status": "HISTORY_QUERY_FAILED",
                    "history_error": str(mt5.last_error()),
                    "trail_updates": len(events),
                })
                continue
            trade = aggregate_position_deals(deals, args.symbol, args.magic)
            row = {
                **trade,
                "trail_updates": len(events),
                "first_trail_bar_time": min(int(e.get("completed_bar_time", 0) or 0) for e in events),
                "last_trail_bar_time": max(int(e.get("completed_bar_time", 0) or 0) for e in events),
                "trail_distance_price_logged": float(events[-1].get("trail_distance_price", 0.0) or 0.0),
                "last_requested_sl": float(events[-1].get("new_sl", 0.0) or 0.0),
                "last_trail_send_success": bool(events[-1].get("success", False)),
                "last_trail_retcode": events[-1].get("retcode"),
                "point_size": float(info.point),
                "digits": int(info.digits),
            }
            if trade.get("history_status") != "CLOSED":
                rows.append(row)
                continue
            entry_time, exit_time = int(trade["entry_time"]), int(trade["exit_time"])
            entry_minute_end = (entry_time // 60 + 1) * 60
            exit_minute_start = (exit_time // 60) * 60
            data_start = min(entry_minute_end, exit_minute_start)
            data_end = (exit_time // 60 + 1) * 60 + max(horizons) * 60
            bars, bars_sha = fetch_m1(args.symbol, data_start, data_end)
            pre = price_excursions(
                trade["direction"], float(trade["entry_price"]), bars,
                entry_minute_end, exit_minute_start,
            )
            row.update({
                "pre_exit_completed_bar_mfe_price": pre["mfe_price"],
                "pre_exit_completed_bar_mae_price": pre["mae_price"],
                "pre_exit_completed_bars": pre["bars"],
                "m1_bars_sha256": bars_sha,
                **post_exit_excursions(trade["direction"], float(trade["exit_price"]), bars, exit_time, horizons),
            })
            last_event = events[-1]
            last_sl = float(last_event.get("new_sl", 0.0) or 0.0)
            entry_price = float(trade["entry_price"])
            if last_sl > 0:
                locked = last_sl - entry_price if trade["direction"] == "BUY" else entry_price - last_sl
                row["last_requested_sl_locked_price"] = locked
                row["last_requested_sl_locked_points"] = locked / float(info.point)
            rows.append(row)
        OUT.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = OUT / f"SP2L_RR2_TRAIL4_POST_EXIT_AUDIT_{stamp}"
        csv_path = base.with_suffix(".csv")
        fields = sorted({key for row in rows for key in row})
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        payload = {
            "status": "COMPLETE",
            "research_only": True,
            "read_only": True,
            "symbol": args.symbol,
            "magic": args.magic,
            "event_log": str(args.event_log),
            "event_log_sha256": event_sha,
            "positions_with_trail_events": len(trail_events),
            "point_size": float(info.point),
            "digits": int(info.digits),
            "post_exit_horizons_minutes": horizons,
            "exit_minute_policy": "exclude the entire exit minute; first post-exit bar starts at the next full M1 minute",
            "quote_basis": "MT5 M1 OHLC chart prices; bid/ask spread and executable close-side quote are not reconstructed",
            "cost_policy": "observed net = sum of MT5 deal profit + commission + swap + fee; modeled price excursions are price-only and are not P&L",
            "limitations": [
                "M1 OHLC cannot establish intrabar ordering.",
                "MT5 M1 OHLC does not reconstruct executable bid/ask prices, spread, slippage, or tick sequence; SELL-side excursion values are chart-price diagnostics, not executable outcomes.",
                "Post-exit excursions do not simulate an alternative stop or guarantee that a wider stop would have filled at a particular price.",
                "Only positions represented by TRAIL_UPDATE events in the supplied event log are analyzed.",
            ],
            "rows": rows,
        }
        raw = json.dumps(payload, indent=2, ensure_ascii=False)
        json_path = base.with_suffix(".json")
        json_path.write_text(raw, encoding="utf-8")
        print(json.dumps({
            "status": "COMPLETE",
            "positions": len(trail_events),
            "rows": len(rows),
            "event_log_sha256": event_sha,
            "csv": str(csv_path),
            "json": str(json_path),
            "research_only": True,
        }, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
