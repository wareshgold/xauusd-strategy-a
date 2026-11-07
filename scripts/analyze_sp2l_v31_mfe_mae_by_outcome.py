#!/usr/bin/env python
"""Aggregate-only MFE/MAE attribution by realized position outcome.

Reads the private weekly audit ZIP and historical MT5 ticks. It emits no ticket,
position id, account id, exact price, timestamp, comment, or raw trade row.
It never submits, modifies, or closes orders.
"""
from __future__ import annotations
import argparse, json, zipfile, statistics
from collections import Counter
from datetime import datetime, timezone
import MetaTrader5 as mt5

SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
EPS = 0.005
MFE_LEVELS = (0.40, 0.80, 1.00)
MAE_LEVELS = (-1.00, -2.00)


def load_json(z, name):
    with z.open(name) as f:
        return json.load(f)


def num(v):
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def stats(values):
    xs = list(values)
    if not xs:
        return {"count": 0}
    return {
        "count": len(xs),
        "mean": round(statistics.mean(xs), 3),
        "median": round(statistics.median(xs), 3),
        "min": round(min(xs), 3),
        "max": round(max(xs), 3),
    }


def classify(net):
    if net > EPS:
        return "winner"
    if net < -EPS:
        return "loser"
    return "flat"


def group_summary(rows):
    nets = [r["net"] for r in rows]
    mfes = [r["mfe"] for r in rows]
    maes = [r["mae"] for r in rows]
    finals = [r["final_mark"] for r in rows]
    nrows = len(rows)
    thresholds = {
        f"mfe_at_least_{level:.2f}": sum(x >= level for x in mfes)
        for level in MFE_LEVELS
    }
    thresholds.update({
        f"mae_at_most_{level:.2f}": sum(x <= level for x in maes)
        for level in MAE_LEVELS
    })
    return {
        "positions": nrows,
        "realized_net_currency": {
            "sum": round(sum(nets), 2),
            "mean": round(statistics.mean(nets), 3) if nets else None,
            "median": round(statistics.median(nets), 3) if nets else None,
        },
        "mfe_currency": stats(mfes),
        "mae_currency": stats(maes),
        "final_tick_mark_currency": stats(finals),
        "threshold_counts": thresholds,
        "threshold_pct_of_group": {
            key: round(100 * value / nrows, 1) if nrows else None
            for key, value in thresholds.items()
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", help="Path to private weekly audit ZIP")
    ap.add_argument("--mt5-terminal-path",
                    default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    args = ap.parse_args()

    with zipfile.ZipFile(args.bundle) as z:
        deals = load_json(z, "raw/mt5_history_deals.json")

    selected = [
        d for d in deals
        if d.get("symbol") == SYMBOL and str(d.get("magic")) == str(MAGIC)
    ]
    positions = {}
    for deal in selected:
        pid = deal.get("position_id")
        if pid is None:
            continue
        p = positions.setdefault(str(pid), {
            "ins": [], "outs": [], "net": 0.0
        })
        entry_code = int(deal.get("entry", -1))
        if entry_code == 0:
            p["ins"].append(deal)
        elif entry_code == 1:
            p["outs"].append(deal)
        for field in ("profit", "commission", "swap", "fee"):
            p["net"] += num(deal.get(field))

    eligible = []
    excluded = Counter()
    for p in positions.values():
        if len(p["ins"]) != 1 or len(p["outs"]) != 1:
            excluded["not_exactly_one_IN_and_one_OUT"] += 1
            continue
        entry, exit_deal = p["ins"][0], p["outs"][0]
        direction = int(entry.get("type", -1))
        if direction not in (0, 1):
            excluded["unknown_direction"] += 1
            continue
        if int(exit_deal.get("time", 0)) < int(entry.get("time", 0)):
            excluded["invalid_time_order"] += 1
            continue
        eligible.append((entry, exit_deal, p["net"], "BUY" if direction == 0 else "SELL"))

    if not mt5.initialize(path=str(args.mt5_terminal_path)):
        print(json.dumps({
            "status": "MT5_INIT_FAILED",
            "last_error": mt5.last_error()
        }, indent=2))
        return

    try:
        info = mt5.symbol_info(SYMBOL)
        if info is None:
            print(json.dumps({
                "status": "SYMBOL_INFO_UNAVAILABLE",
                "last_error": mt5.last_error()
            }, indent=2))
            return
        contract = num(info.trade_contract_size)
        rows = []
        tick_count = 0
        no_tick = 0
        invalid_quote = 0
        invalid_trade_data = 0

        for entry, exit_deal, net, direction_name in eligible:
            t0 = int(entry.get("time", 0))
            t1 = int(exit_deal.get("time", 0))
            t0ms = int(entry.get("time_msc", t0 * 1000))
            t1ms = int(exit_deal.get("time_msc", t1 * 1000))
            start = datetime.fromtimestamp(max(0, t0 - 1), timezone.utc)
            end = datetime.fromtimestamp(t1 + 1, timezone.utc)
            ticks = mt5.copy_ticks_range(
                SYMBOL, start, end, mt5.COPY_TICKS_INFO
            )
            if ticks is None or len(ticks) == 0:
                no_tick += 1
                continue
            tick_count += len(ticks)

            entry_price = num(entry.get("price"))
            volume = num(entry.get("volume"))
            if entry_price <= 0 or volume <= 0 or contract <= 0:
                invalid_trade_data += 1
                continue

            is_buy = int(entry["type"]) == 0
            moves = []
            for tick in ticks:
                tick_ms = (
                    int(tick["time_msc"])
                    if "time_msc" in tick.dtype.names
                    else int(tick["time"]) * 1000
                )
                if tick_ms < t0ms or tick_ms > t1ms:
                    continue
                bid, ask = num(tick["bid"]), num(tick["ask"])
                mark = bid if is_buy else ask
                if mark <= 0:
                    invalid_quote += 1
                    continue
                move = (mark - entry_price) if is_buy else (entry_price - mark)
                moves.append(move * contract * volume)

            if not moves:
                no_tick += 1
                continue

            rows.append({
                "net": net,
                "mfe": max(0.0, max(moves)),
                "mae": min(0.0, min(moves)),
                "final_mark": moves[-1],
                "direction": direction_name,
                "outcome": classify(net),
            })

        groups = {
            name: [r for r in rows if r["outcome"] == name]
            for name in ("winner", "loser", "flat")
        }
        direction_groups = {
            name: [r for r in rows if r["direction"] == name]
            for name in ("BUY", "SELL")
        }
        loss_rows = groups["loser"]
        loss_thresholds = {
            f"losers_with_mfe_at_least_{level:.2f}": sum(
                r["mfe"] >= level for r in loss_rows
            )
            for level in MFE_LEVELS
        }

        result = {
            "scope": {
                "symbol": SYMBOL,
                "magic": MAGIC,
                "price_basis": "BUY marked at bid; SELL marked at ask",
                "currency_basis": "gross tick mark-to-market uses contract size and entry volume; realized outcome sums deal profit, commission, swap and fee",
                "classification": "winner > 0.005; loser < -0.005; otherwise flat",
                "privacy": "aggregate_only",
            },
            "population": {
                "filtered_positions": len(positions),
                "eligible_single_IN_single_OUT": len(eligible),
                "tick_coverage_positions": len(rows),
                "no_tick_positions": no_tick,
                "excluded_counts": dict(excluded),
                "invalid_trade_data_positions": invalid_trade_data,
            },
            "tick_data": {
                "total_ticks_returned_before_millisecond_filter": tick_count,
                "invalid_side_quotes_skipped": invalid_quote,
                "contract_size_used": contract,
            },
            "by_realized_outcome": {
                name: group_summary(group) for name, group in groups.items()
            },
            "losing_positions_that_had_favorable_excursion": {
                "loser_count": len(loss_rows),
                "counts": loss_thresholds,
                "pct_of_losers": {
                    key: round(100 * value / len(loss_rows), 1)
                    if loss_rows else None
                    for key, value in loss_thresholds.items()
                },
            },
            "by_entry_direction": {
                name: group_summary(group)
                for name, group in direction_groups.items()
            },
            "limitations": [
                "MFE/MAE are gross tick mark-to-market excursions, not realized P/L; realized outcome includes deal profit, commission, swap and fee.",
                "Only positions with exactly one IN and one OUT deal are included; multi-deal lifecycles are excluded.",
                "The MFE threshold counts show that a level was reached at some point, not that a hypothetical stop would have filled there.",
                "No counterfactual trailing, stop execution, slippage, or intrabar fill simulation is performed.",
                "Historical tick timestamps are queried in timezone-aware UTC and filtered by deal millisecond timestamps.",
                "No canonical SP2L geometry, P-Gap, AB=CD, SL-anchor, fill, or execution rule is inferred or changed.",
                "This script reads historical data only; it does not submit, modify, or close orders.",
            ],
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
