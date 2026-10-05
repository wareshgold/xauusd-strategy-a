"""SP2L missing-candidate forensic trace (read-only).

Targets the latest health-reconciliation gap and explains how the existing
V3 implementation sees candidates as the M1 window advances. No orders,
state, or runner processes are modified.

This is diagnostic only. It does not define canonical Strategy A geometry.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import MetaTrader5 as mt5
import sp2l_v3_config as cfg

EVENT_FILE = Path("artifacts/forward-test/SP2L_V3_XAUUSD_RR2_ACT10_TRAIL2_FORWARD_EVENTS.jsonl")
TARGET_TRIGGER = 1791201420  # 2026-10-05 11:57:00 UTC

def iso(ts):
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()

def detect_setup(candles, symbol):
    if len(candles) < 3:
        return None
    return cfg.detect(candles[-3:], symbol)

def causal_candidate_for_setup(candles, setup_end, setup):
    if not setup:
        return None
    direction = setup["direction"]
    if setup_end + 1 >= len(candles):
        return None
    prev, cur = candles[setup_end], candles[setup_end + 1]
    if direction == "BUY":
        if float(cur["low"]) >= float(prev["low"]):
            return None
        entry = float(cur["low"])
        sl = float(candles[setup_end - 2]["low"])
        risk = entry - sl
        if risk <= 0 or risk > cfg.MAX_SL_DISTANCE:
            return None
        return {"direction":"BUY","trigger_time":int(cur["time"]),
                "theoretical_entry":entry,"sl":sl,"risk":risk,
                "tp":entry + cfg.TP_R*risk}
    if float(cur["high"]) <= float(prev["high"]):
        return None
    entry = float(cur["high"])
    sl = float(candles[setup_end - 2]["high"])
    risk = sl - entry
    if risk <= 0 or risk > cfg.MAX_SL_DISTANCE:
        return None
    return {"direction":"SELL","trigger_time":int(cur["time"]),
            "theoretical_entry":entry,"sl":sl,"risk":risk,
            "tp":entry - cfg.TP_R*risk}

def load_events(path):
    out=[]
    if not path.exists(): return out
    for line in path.read_text(encoding="utf-8").splitlines():
        try: out.append(json.loads(line))
        except Exception: pass
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mt5-path",default=r"C:\Program Files\Otet Group MT5 Terminal\terminal64.exe")
    ap.add_argument("--symbol",default="XAUUSD.ecn")
    ap.add_argument("--target-trigger",type=int,default=TARGET_TRIGGER)
    ap.add_argument("--minutes",type=int,default=20)
    args=ap.parse_args()

    target_dt=datetime.fromtimestamp(args.target_trigger,tz=timezone.utc)
    start=target_dt-timedelta(minutes=args.minutes)
    end=target_dt+timedelta(minutes=args.minutes)

    if not mt5.initialize(path=args.mt5_path,timeout=60000):
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        rates=mt5.copy_rates_range(args.symbol,mt5.TIMEFRAME_M1,start-timedelta(minutes=10),end)
        if rates is None: raise SystemExit(f"M1 load failed: {mt5.last_error()}")
        rows=[{"time":int(r["time"]),"open":float(r["open"]),"high":float(r["high"]),
               "low":float(r["low"]),"close":float(r["close"])} for r in rates]

        print("SP2L V3 — MISSING CANDIDATE FORENSIC TRACE")
        print("READ-ONLY / RESEARCH ONLY / canonical=false")
        print(f"TARGET={iso(args.target_trigger)}")
        print(f"WINDOW={start.isoformat()} -> {end.isoformat()}")
        print(f"M1_BARS={len(rows)}")
        print()

        print("=== TARGET BAR ===")
        for r in rows:
            if r["time"]==args.target_trigger:
                print(r)
        print()

        print("=== CAUSAL SETUPS / ENTRIES ===")
        found=[]
        for i in range(2,len(rows)):
            prefix=rows[:i+1]
            setup=detect_setup(prefix,args.symbol)
            if not setup: continue
            c=causal_candidate_for_setup(prefix,i-2,setup)
            # detect() over prefix ends at i; setup_end is i-2? We report the
            # actual three-bar setup and its immediate next-bar trigger.
            if c and start.timestamp() <= c["trigger_time"] <= end.timestamp():
                found.append(c)
                print(f'{iso(c["trigger_time"])} {c["direction"]} entry={c["theoretical_entry"]:.2f} sl={c["sl"]:.2f} risk={c["risk"]:.2f} tp={c["tp"]:.2f}')

        print()
        print("=== EXISTING find_latest_candidate AT EACH CLOSED BAR ===")
        last=None
        for i in range(2,len(rows)):
            prefix=rows[:i+1]
            try: c=cfg.find_latest_candidate(prefix,args.symbol)
            except Exception as exc:
                print("ERROR",i,exc); continue
            if not c: continue
            key=(int(c["trigger_time"]),c["direction"])
            if key != last:
                last=key
                if start.timestamp() <= int(c["trigger_time"]) <= end.timestamp() or abs(int(c["trigger_time"])-args.target_trigger) <= 900:
                    print(f'prefix_last_bar={iso(rows[i]["time"])} -> {iso(c["trigger_time"])} {c["direction"]} entry={float(c["theoretical_entry"]):.2f} sl={float(c["sl"]):.2f} tp={float(c["tp"]):.2f}')

        print()
        print("=== EVENT EVIDENCE ===")
        events=load_events(EVENT_FILE)
        for e in events:
            if e.get("event") in {"START","CANDIDATE","ORDER_ATTEMPT","STALE_STARTUP_CANDIDATE_BLOCKED","SESSION_GATE"}:
                print(json.dumps(e,ensure_ascii=False))

        print()
        print("=== INTERPRETATION FLAGS ===")
        target_bar=next((r for r in rows if r["time"]==args.target_trigger),None)
        if target_bar:
            print("TARGET_BAR_PRESENT=true")
        target_c=[c for c in found if int(c["trigger_time"])==args.target_trigger]
        print(f"CAUSAL_TARGET_CANDIDATES={len(target_c)}")
        if target_c:
            print("CAUSAL_TARGET_EXISTS=true")
        else:
            print("CAUSAL_TARGET_EXISTS=false")
        print("NOTE=This trace does not change the live runner or any MT5 state.")
    finally:
        mt5.shutdown()

if __name__=="__main__":
    main()
