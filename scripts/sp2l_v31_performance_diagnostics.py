"""Read-only SP2L V3.1 daily performance diagnostics.

Reusable analytics module embedded in the Trading Intelligence dashboard.
Consumes Runner-recorded filesystem events only; never accesses MT5 or broker
APIs. All classifications are descriptive, not causal.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone, timedelta
import os

DEFAULT_START = os.getenv("SP2L_DIAGNOSTICS_START", "2026-11-04")
DEFAULT_END = os.getenv("SP2L_DIAGNOSTICS_END", "2026-11-05")
TRAIL_ACTIVATION_PRICE = 0.40
TEHRAN = timezone(timedelta(hours=3, minutes=30))


def _num(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _dt(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
    except (TypeError, ValueError):
        return None


def _day(value):
    stamp = _dt(value)
    return stamp.astimezone(TEHRAN).date().isoformat() if stamp else None


def _side(event):
    for key in ("direction", "side"):
        value = event.get(key)
        if str(value).upper() in ("BUY", "SELL"):
            return str(value).upper()
    signal = event.get("signal_id")
    if isinstance(signal, str):
        suffix = signal.rsplit(":", 1)[-1].upper()
        if suffix in ("BUY", "SELL"):
            return suffix
    # POSITION_LIFECYCLE uses MT5 position type: 0=BUY, 1=SELL.
    if event.get("event") == "POSITION_LIFECYCLE":
        try:
            return {0: "BUY", 1: "SELL"}.get(int(event.get("type")))
        except (TypeError, ValueError):
            return None
    return None


def _build_diagnostics(events, start_date=DEFAULT_START, end_date=DEFAULT_END):
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        raise ValueError("end_date must be on or after start_date")

    # Keep one Runner-recorded lifecycle row per broker deal identifier.
    unique_deals = {}
    for event in events:
        if event.get("event") != "TELEGRAM_DEAL_LIFECYCLE":
            continue
        deal_id = event.get("deal")
        if deal_id is not None:
            unique_deals.setdefault(str(deal_id), event)

    grouped = defaultdict(list)
    for event in unique_deals.values():
        position = event.get("position")
        if position is not None:
            grouped[str(position)].append(event)

    position_events = defaultdict(list)
    trail_events = defaultdict(list)
    for event in events:
        position = event.get("position")
        if position is None:
            continue
        key = str(position)
        if event.get("event") == "POSITION_LIFECYCLE":
            position_events[key].append(event)
        elif event.get("event") in ("TRAIL_UPDATE", "TRAIL_DEFERRED"):
            trail_events[key].append(event)

    trades = []
    for position_id, deals in grouped.items():
        deals.sort(key=lambda row: row.get("ts_utc") or "")
        exits = [d for d in deals if d.get("entry") in (1, 3)]
        if not exits:
            continue
        close_event = exits[-1]
        close_day = _day(close_event.get("ts_utc"))
        if not close_day or not (start <= date.fromisoformat(close_day) <= end):
            continue
        net_values = [_num(d.get("net")) for d in deals]
        known_net = [v for v in net_values if v is not None]
        net = round(sum(known_net), 2) if known_net else None
        side = next((_side(d) for d in deals if _side(d)), None)
        samples = position_events.get(position_id, [])
        entry_prices = [_num(d.get("entry_price")) for d in deals if d.get("entry") == 0]
        entry = next((v for v in entry_prices if v is not None), None)
        if entry is None:
            entry = next((_num(e.get("price_open")) for e in samples
                          if _num(e.get("price_open")) is not None), None)
        favorable = []
        adverse = []
        for sample in samples:
            px = _num(sample.get("price_current"))
            open_px = _num(sample.get("price_open"))
            ref = entry if entry is not None else open_px
            sample_side = _side(sample) or side
            if px is None or ref is None or sample_side not in ("BUY", "SELL"):
                continue
            move = px - ref if sample_side == "BUY" else ref - px
            favorable.append(max(0.0, move))
            adverse.append(max(0.0, -move))
        mfe = max(favorable) if favorable else None
        mae = max(adverse) if adverse else None

        t_events = trail_events.get(position_id, [])
        successful = [e for e in t_events if e.get("event") == "TRAIL_UPDATE" and e.get("success") is True]
        failed = [e for e in t_events if e.get("event") == "TRAIL_UPDATE" and e.get("success") is False]
        deferred = [e for e in t_events if e.get("event") == "TRAIL_DEFERRED"]
        success_keys = {
            str(e.get("completed_bar_time")) for e in successful
            if e.get("completed_bar_time") is not None
        }
        unresolved_deferred = [
            e for e in deferred
            if e.get("completed_bar_time") is None
            or str(e.get("completed_bar_time")) not in success_keys
        ]
        activated = any(
            (_num(e.get("favorable_move")) or 0) >= TRAIL_ACTIVATION_PRICE
            for e in successful + failed
        )
        trades.append({
            "position_id": position_id,
            "close_day_local": close_day,
            "side": side or "UNKNOWN",
            "net": net,
            "deal_count": len(deals),
            "exit_deal_count": len(exits),
            "entry": entry,
            "sampled_mfe_price": round(mfe, 4) if mfe is not None else None,
            "sampled_mae_price": round(mae, 4) if mae is not None else None,
            "price_sample_count": len(favorable),
            "trail_success": len(successful),
            "trail_failed": len(failed),
            "trail_deferred": len(deferred),
            "trail_deferred_unrecovered_same_bar": len(unresolved_deferred),
            "trail_activation_observed": activated,
            "trail_evidence": "TRAIL_UPDATE favorable_move" if activated else (
                "sampled POSITION_LIFECYCLE excursion only" if mfe is not None and mfe >= TRAIL_ACTIVATION_PRICE
                else "not established from available events"
            ),
            "canonical": False,
        })

    def summarize(rows):
        known = [r for r in rows if r["net"] is not None]
        return {
            "closed_position_groups": len(rows),
            "net_sum_runner_recorded": round(sum(r["net"] for r in known), 2),
            "wins": sum(r["net"] > 0 for r in known),
            "losses": sum(r["net"] < 0 for r in known),
            "breakeven": sum(r["net"] == 0 for r in known),
            "unknown_net": len(rows) - len(known),
            "buy": summarize_side(rows, "BUY"),
            "sell": summarize_side(rows, "SELL"),
            "trailing": {
                "positions_with_success": sum(r["trail_success"] > 0 for r in rows),
                "positions_with_failed_update": sum(r["trail_failed"] > 0 for r in rows),
                "positions_with_deferred_update": sum(r["trail_deferred"] > 0 for r in rows),
                "positions_with_unrecovered_deferred_same_bar": sum(
                    r["trail_deferred_unrecovered_same_bar"] > 0 for r in rows
                ),
                "losses_with_unrecovered_deferred_same_bar": sum(
                    r["net"] is not None and r["net"] < 0
                    and r["trail_deferred_unrecovered_same_bar"] > 0 for r in rows
                ),
            },
            "sampled_excursions": {
                "positions_with_price_samples": sum(r["price_sample_count"] > 0 for r in rows),
                "positions_with_mfe_at_least_activation": sum(
                    r["sampled_mfe_price"] is not None and r["sampled_mfe_price"] >= TRAIL_ACTIVATION_PRICE
                    for r in rows
                ),
                "positions_with_mae_greater_than_mfe": sum(
                    r["sampled_mae_price"] is not None and r["sampled_mfe_price"] is not None
                    and r["sampled_mae_price"] > r["sampled_mfe_price"] for r in rows
                ),
            },
        }

    def summarize_side(rows, side):
        subset = [r for r in rows if r["side"] == side and r["net"] is not None]
        return {
            "positions": len(subset),
            "net": round(sum(r["net"] for r in subset), 2),
            "wins": sum(r["net"] > 0 for r in subset),
            "losses": sum(r["net"] < 0 for r in subset),
        }

    daily = []
    cursor = start
    while cursor <= end:
        day = cursor.isoformat()
        rows = [r for r in trades if r["close_day_local"] == day]
        daily.append({"date_local": day, **summarize(rows), "trades": rows})
        cursor = date.fromordinal(cursor.toordinal() + 1)

    return {
        "date_start_local": start.isoformat(),
        "date_end_local": end.isoformat(),
        "timezone": "Asia/Tehran (UTC+03:30 fixed offset)",
        "daily": daily,
        "overall": summarize(trades),
        "trades": sorted(trades, key=lambda r: (r["close_day_local"], r["position_id"])),
        "data_limits": [
            "P&L is the sum of Runner-recorded TELEGRAM_DEAL_LIFECYCLE net fields, grouped by position; it is not broker-reconciled account equity.",
            "A position group is assigned to the Tehran-local date of its last recorded OUT/OUT_BY deal. Multi-exit positions may span dates.",
            "MFE/MAE are sampled POSITION_LIFECYCLE price observations, not tick-complete excursions; absent samples mean unknown, not zero.",
            "Trailing counts are correlated by position. A deferred update is considered recovered only when a successful TRAIL_UPDATE for the same completed M1 bar is present in this event window.",
            "Direction comparison is descriptive. It cannot prove market trend or that an entry direction was wrong.",
            "No market tick/bar replay is included; exact counterfactual P&L with a different trailing rule is unavailable.",
        ],
        "thresholds": {"trailing_activation_price": TRAIL_ACTIVATION_PRICE},
        "mt5_queried": False,
        "broker_state_verified": False,
    }
