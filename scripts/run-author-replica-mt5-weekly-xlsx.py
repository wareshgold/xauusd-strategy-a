"""Research-only weekly XLSX export for the existing author-replica SP2L implementation.

This script reuses the existing signal() implementation and does not define canonical Strategy A.
It fetches a lookback buffer from MT5, filters signals to the requested UTC week, and evaluates
outcomes only through the last returned bar. Outcomes that do not hit SL/TP inside the available
week are marked OPEN_OR_UNRESOLVED rather than guessed.
"""
from __future__ import annotations

import importlib.util
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

SOURCE_SCRIPT = Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
START = datetime.fromisoformat(os.getenv("WEEK_START_UTC", "2026-09-14T00:00:00+00:00")).astimezone(timezone.utc)
END = datetime.fromisoformat(os.getenv("WEEK_END_UTC", "2026-09-18T23:59:59+00:00")).astimezone(timezone.utc)
OUT = Path(os.getenv("WEEKLY_XLSX", "artifacts/SP2L_author_replica_2026-09-14_2026-09-18.xlsx"))

spec = importlib.util.spec_from_file_location("sp2l_nonoverlap", SOURCE_SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit(f"Cannot load {SOURCE_SCRIPT}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def utc(ts: int) -> datetime:
    return datetime.fromtimestamp(int(ts), timezone.utc)

def auto_width(ws):
    for col in ws.columns:
        width = min(max(len(str(cell.value or "")) for cell in col) + 2, 42)
        ws.column_dimensions[get_column_letter(col[0].column)].width = width

if not mt5.initialize():
    raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
try:
    if not mt5.symbol_select(SYMBOL, True):
        raise SystemExit(f"symbol_select failed: {mt5.last_error()}")

    rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, END, N)
    if rates is None or len(rates) == 0:
        raise SystemExit(f"No MT5 data: {mt5.last_error()}")

    candles = [
        {"time": int(r[0]), "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4])}
        for r in rates
    ]

    start_ts = START.timestamp()
    end_ts = END.timestamp()
    signals = []

    for i in range(4, len(candles)):
        s = mod.signal(candles, i)
        if not s:
            continue
        direction, entry, sl = s
        signal_time = candles[i - 1]["time"]
        if not (start_ts <= signal_time <= end_ts):
            continue

        risk = abs(entry - sl)
        if risk <= 0 or risk > mod.MAX_SL:
            continue

        tp = entry + mod.TP_R * risk if direction == "BUY" else entry - mod.TP_R * risk
        outcome = "OPEN_OR_UNRESOLVED"
        r_value = None
        exit_time = None
        exit_price = None
        reason = "NO_SL_TP_HIT_IN_AVAILABLE_DATA"

        for j in range(i + 1, len(candles)):
            x = candles[j]
            hit_sl = x["low"] <= sl if direction == "BUY" else x["high"] >= sl
            hit_tp = x["high"] >= tp if direction == "BUY" else x["low"] <= tp

            if hit_sl and hit_tp:
                outcome = "AMBIGUOUS"
                r_value = None
                exit_time = x["time"]
                exit_price = None
                reason = "SL_AND_TP_SAME_BAR"
                break
            if hit_sl:
                outcome = "LOSS"
                r_value = -1.0
                exit_time = x["time"]
                exit_price = sl
                reason = "SL"
                break
            if hit_tp:
                outcome = "WIN"
                r_value = 1.0
                exit_time = x["time"]
                exit_price = tp
                reason = "TP"
                break

        signals.append({
            "signal_time_utc": utc(signal_time).isoformat(),
            "date_utc": utc(signal_time).date().isoformat(),
            "direction": direction,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "risk": risk,
            "outcome": outcome,
            "R": r_value,
            "exit_time_utc": utc(exit_time).isoformat() if exit_time else "",
            "exit_price": exit_price if exit_price is not None else "",
            "reason": reason,
        })

    wins = sum(x["outcome"] == "WIN" for x in signals)
    losses = sum(x["outcome"] == "LOSS" for x in signals)
    ambiguous = sum(x["outcome"] == "AMBIGUOUS" for x in signals)
    unresolved = sum(x["outcome"] == "OPEN_OR_UNRESOLVED" for x in signals)
    decisive = wins + losses
    total_r = wins - losses
    pf = wins / losses if losses else None

    daily = {}
    for row in signals:
        d = row["date_utc"]
        daily.setdefault(d, []).append(row)

    wb = Workbook()
    ws = wb.active
    ws.title = "Weekly Summary"
    summary = [
        ("Research status", "RESEARCH_ONLY"),
        ("Implementation", "Existing author-replica SP2L runner"),
        ("Symbol", SYMBOL),
        ("Timeframe", "M1"),
        ("Week start UTC", START.isoformat()),
        ("Week end UTC", END.isoformat()),
        ("Returned bars", len(candles)),
        ("First returned UTC", utc(candles[0]["time"]).isoformat()),
        ("Last returned UTC", utc(candles[-1]["time"]).isoformat()),
        ("Signals", len(signals)),
        ("Wins", wins),
        ("Losses", losses),
        ("Ambiguous", ambiguous),
        ("Open / unresolved", unresolved),
        ("Decisive win rate", wins / decisive if decisive else None),
        ("Total R", total_r),
        ("Profit factor", pf),
        ("P-Gap price", mod.P_GAP),
        ("Spike multiplier", mod.SPIKE_MULT),
        ("Max SL price", mod.MAX_SL),
        ("TP R", mod.TP_R),
        ("Important", "No unresolved outcome was guessed; week-end data availability limits late-week exits."),
    ]
    for row in summary:
        ws.append(row)

    ws2 = wb.create_sheet("Signals")
    headers = ["signal_time_utc","date_utc","direction","entry","sl","tp","risk","outcome","R","exit_time_utc","exit_price","reason"]
    ws2.append(headers)
    for row in signals:
        ws2.append([row[h] for h in headers])

    ws3 = wb.create_sheet("Daily Summary")
    ws3.append(["date_utc","signals","wins","losses","ambiguous","open_or_unresolved","decisive_win_rate","total_R","profit_factor"])
    for d in sorted(daily):
        rows = daily[d]
        w = sum(x["outcome"] == "WIN" for x in rows)
        l = sum(x["outcome"] == "LOSS" for x in rows)
        a = sum(x["outcome"] == "AMBIGUOUS" for x in rows)
        u = sum(x["outcome"] == "OPEN_OR_UNRESOLVED" for x in rows)
        dec = w + l
        ws3.append([d, len(rows), w, l, a, u, w / dec if dec else None, w-l, w/l if l else None])

    for sheet in wb.worksheets:
        sheet.freeze_panes = "A2"
        auto_width(sheet)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)

    json_out = OUT.with_suffix(".json")
    json_out.write_text(json.dumps({
        "research_only": True,
        "week_start_utc": START.isoformat(),
        "week_end_utc": END.isoformat(),
        "returned_bars": len(candles),
        "first_returned_utc": utc(candles[0]["time"]).isoformat(),
        "last_returned_utc": utc(candles[-1]["time"]).isoformat(),
        "signals": signals,
        "summary": {"wins": wins, "losses": losses, "ambiguous": ambiguous,
                    "open_or_unresolved": unresolved, "decisive_win_rate": wins/decisive if decisive else None,
                    "total_R": total_r, "profit_factor": pf},
        "config": {"pGapPrice": mod.P_GAP, "spikeMultiplier": mod.SPIKE_MULT,
                   "maxSlPrice": mod.MAX_SL, "tpR": mod.TP_R}
    }, indent=2), encoding="utf-8")

    print(json.dumps({
        "xlsx": str(OUT),
        "json": str(json_out),
        "returned_bars": len(candles),
        "first_returned_utc": utc(candles[0]["time"]).isoformat(),
        "last_returned_utc": utc(candles[-1]["time"]).isoformat(),
        "signals": len(signals), "wins": wins, "losses": losses,
        "ambiguous": ambiguous, "open_or_unresolved": unresolved,
        "decisive_win_rate": wins / decisive if decisive else None,
        "total_R": total_r, "profit_factor": pf
    }, indent=2))
finally:
    mt5.shutdown()
