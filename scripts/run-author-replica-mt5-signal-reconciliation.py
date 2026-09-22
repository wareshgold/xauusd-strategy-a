"""Research-only reconciliation of diagnostic conditions vs the exact mod.signal().

This script does not alter canonical geometry. It evaluates the exact same MT5 candles
through both the diagnostic predicate and the imported author-replica signal() and reports
any disagreement, including the first differing candle for each side.
"""
from __future__ import annotations
import importlib.util, json, os
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

SOURCE_SCRIPT = Path("scripts/run-author-replica-mt5-nonoverlap-stability.py")
SYMBOL = os.getenv("TRADING_SYMBOL", "XAUUSD.ecn")
N = int(os.getenv("BARS", "10000"))
START = datetime.fromisoformat(os.getenv("WEEK_START_UTC", "2026-09-14T00:00:00+00:00")).astimezone(timezone.utc)
END = datetime.fromisoformat(os.getenv("WEEK_END_UTC", "2026-09-18T23:59:59+00:00")).astimezone(timezone.utc)
PGAP = float(os.getenv("PGAP_PRICE", "1"))

spec = importlib.util.spec_from_file_location("sp2l_replica", SOURCE_SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit(f"Cannot load {SOURCE_SCRIPT}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def body(c):
    return abs(c["close"] - c["open"])

def diagnostic(c, i, side):
    a, s, corr, trig = c[i-4], c[i-3], c[i-2], c[i-1]
    if side == "BUY":
        return all([
            trig["low"] < corr["low"],
            corr["close"] > s["close"],
            corr["open"] > s["open"],
            s["open"] > a["open"],
            corr["close"] > corr["open"],
            s["close"] > s["open"],
            a["close"] > a["open"],
            corr["low"] > a["high"] + PGAP,
            body(s) > mod.SPIKE_MULT * body(corr),
            body(s) > mod.SPIKE_MULT * body(a),
            body(s) > mod.SPIKE_MULT * body(trig),
        ])
    return all([
        trig["high"] > corr["high"],
        corr["close"] < s["close"],
        corr["open"] < s["open"],
        s["close"] < a["close"],
        s["open"] < a["open"],
        corr["close"] < corr["open"],
        s["close"] < s["open"],
        a["close"] < a["open"],
        corr["high"] < a["low"] - PGAP,
        body(s) > mod.SPIKE_MULT * body(corr),
        body(s) > mod.SPIKE_MULT * body(a),
        body(s) > mod.SPIKE_MULT * body(trig),
    ])

def main():
    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL, True):
            raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        rates = mt5.copy_rates_from(SYMBOL, mt5.TIMEFRAME_M1, END, N)
        if rates is None or len(rates) == 0:
            raise SystemExit(f"No MT5 data: {mt5.last_error()}")
        c = [{"time": int(r[0]), "open": float(r[1]), "high": float(r[2]),
              "low": float(r[3]), "close": float(r[4])} for r in rates]
        lo, hi = START.timestamp(), END.timestamp()
        rows = []
        counts = {"BUY": {"diagnostic": 0, "exact_signal": 0, "both": 0, "diagnostic_only": 0, "signal_only": 0},
                  "SELL": {"diagnostic": 0, "exact_signal": 0, "both": 0, "diagnostic_only": 0, "signal_only": 0}}
        examples = {"BUY": [], "SELL": []}
        for i in range(4, len(c)):
            ts = c[i-1]["time"]
            if not (lo <= ts <= hi):
                continue
            exact = mod.signal(c, i)
            for side in ("BUY", "SELL"):
                d = diagnostic(c, i, side)
                e = exact is not None and exact[0] == side
                counts[side]["diagnostic"] += int(d)
                counts[side]["exact_signal"] += int(e)
                counts[side]["both"] += int(d and e)
                counts[side]["diagnostic_only"] += int(d and not e)
                counts[side]["signal_only"] += int(e and not d)
                if (d != e) and len(examples[side]) < 5:
                    examples[side].append({
                        "signal_time_utc": datetime.fromtimestamp(ts, timezone.utc).isoformat(),
                        "diagnostic": d,
                        "exact_signal": exact,
                        "candles": c[i-4:i]
                    })
        result = {
            "research_only": True,
            "symbol": SYMBOL,
            "timeframe": "M1",
            "week_start_utc": START.isoformat(),
            "week_end_utc": END.isoformat(),
            "returned_bars": len(c),
            "first_returned_utc": datetime.fromtimestamp(c[0]["time"], timezone.utc).isoformat(),
            "last_returned_utc": datetime.fromtimestamp(c[-1]["time"], timezone.utc).isoformat(),
            "config": {"pGapPrice": PGAP, "spikeMultiplier": mod.SPIKE_MULT,
                       "maxSlPrice": mod.MAX_SL, "tpR": mod.TP_R},
            "counts": counts,
            "first_disagreements": examples,
            "interpretation": "Diagnostic predicate is intended to mirror the exact signal() predicate condition-for-condition. Any disagreement is an engineering reconciliation issue and must be investigated before geometry changes."
        }
        print(json.dumps(result, indent=2))
        out = Path(os.getenv("RECONCILIATION_OUT", f"artifacts/SP2L_{SYMBOL.replace('.', '_')}_signal_reconciliation_2026-09-14_2026-09-18.json"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Wrote {out}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
