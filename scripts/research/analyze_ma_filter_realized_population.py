"""Research-only comparison of realized V3.1 positions against M1 MA filters.

Alignment is the last completed M1 bar at/before entry DEAL time (fill-time
proxy), not the unresolved Runner candidate-decision timestamp. This script
does not replay orders or alternative management rules.
"""
from __future__ import annotations
import argparse, bisect, csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path

PERIODS = (20, 50, 100, 200)
FILTERS = {
    "F00": "Baseline (no MA)", "F01": "SMA50 price-side",
    "F02": "SMA100 price-side", "F03": "EMA50 price-side",
    "F04": "EMA100 price-side", "F05": "SMA20 price-side",
    "F06": "SMA200 price-side", "F07": "EMA20 price-side",
    "F08": "EMA200 price-side", "F09": "SMA50+SMA100 price-side",
    "F10": "EMA50+EMA100 price-side", "F11": "SMA stack + price-side",
    "F12": "EMA stack + price-side", "F13": "OR: SMA/EMA50/100 price-side",
}

def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def num(row, key):
    value = row.get(key, "")
    return float(value) if value not in ("", None) else 0.0

def integer(row, key):
    return int(num(row, key))

def moving_average(values, period, exponential=False):
    out = [None] * len(values)
    if len(values) < period:
        return out
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    if not exponential:
        running = sum(values[:period])
        for i in range(period, len(values)):
            running += values[i] - values[i-period]
            out[i] = running / period
        return out
    alpha, previous = 2.0 / (period + 1.0), seed
    for i in range(period, len(values)):
        previous = alpha * values[i] + (1.0-alpha) * previous
        out[i] = previous
    return out

def position_groups(deals):
    groups = defaultdict(list)
    for d in deals:
        if d.get("position_id"):
            groups[str(d["position_id"])].append(d)
    closed, open_count, unresolved = [], 0, 0
    for pid, rows in groups.items():
        rows.sort(key=lambda d: (integer(d, "time_msc"), integer(d, "ticket")))
        entries = [d for d in rows if integer(d, "entry") == 0]
        if not entries or any(integer(d, "entry") == 2 for d in rows):
            unresolved += 1
            continue
        entry = entries[0]
        side = integer(entry, "type")
        if side not in (0, 1):
            unresolved += 1
            continue
        exits = [d for d in rows if integer(d, "entry") in (1, 3)]
        if not exits:
            open_count += 1
            continue
        entry_ms = integer(entry, "time_msc")
        exit_ms = max(integer(d, "time_msc") for d in exits)
        entry_time = entry_ms/1000 if entry_ms else integer(entry, "time")
        exit_time = exit_ms/1000 if exit_ms else max(integer(d, "time") for d in exits)
        net = sum(num(d, "profit")+num(d, "commission")+num(d, "swap")+num(d, "fee") for d in rows)
        closed.append({"id":pid, "direction":"BUY" if side == 0 else "SELL",
                       "entry_time":entry_time, "exit_time":exit_time, "net":net})
    return closed, open_count, unresolved

def stats(rows):
    rows = sorted(rows, key=lambda r:r["exit_time"])
    vals = [r["net"] for r in rows]
    wins, losses = sum(v > 0 for v in vals), sum(v < 0 for v in vals)
    gp, gl = sum(v for v in vals if v > 0), -sum(v for v in vals if v < 0)
    equity = peak = dd = 0.0
    for v in vals:
        equity += v
        peak = max(peak, equity)
        dd = max(dd, peak-equity)
    return {"n":len(vals), "wins":wins, "losses":losses,
            "win":100*wins/len(vals) if vals else None, "net":sum(vals),
            "pf":gp/gl if gl else (math.inf if gp else None),
            "avg":sum(vals)/len(vals) if vals else None, "dd":dd}

def fmt(v, digits=2):
    if v is None: return "—"
    if isinstance(v, float) and math.isinf(v): return "∞"
    return f"{v:.{digits}f}"

def classify(direction, close, ma):
    def side(key):
        x = ma[key]
        if x is None or close == x: return 0
        return 1 if (close > x if direction == "BUY" else close < x) else -1
    s = {k:side(k) for k in ma}
    if any(v is None for v in ma.values()): return None
    return {
        "F00":True, "F01":s["SMA50"]==1, "F02":s["SMA100"]==1,
        "F03":s["EMA50"]==1, "F04":s["EMA100"]==1,
        "F05":s["SMA20"]==1, "F06":s["SMA200"]==1,
        "F07":s["EMA20"]==1, "F08":s["EMA200"]==1,
        "F09":s["SMA50"]==1 and s["SMA100"]==1,
        "F10":s["EMA50"]==1 and s["EMA100"]==1,
        "F11":s["SMA50"]==1 and s["SMA100"]==1 and
              (ma["SMA50"] > ma["SMA100"] if direction=="BUY" else ma["SMA50"] < ma["SMA100"]),
        "F12":s["EMA50"]==1 and s["EMA100"]==1 and
              (ma["EMA50"] > ma["EMA100"] if direction=="BUY" else ma["EMA50"] < ma["EMA100"]),
        "F13":any(s[k]==1 for k in ("SMA50","SMA100","EMA50","EMA100")),
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-dir", default="artifacts/ma_filter_week_20261109")
    ap.add_argument("--output", default="artifacts/ma_filter_week_20261109/ma_filter_comparison.md")
    args = ap.parse_args()
    root = Path(args.input_dir)
    dp, bp, mp = root/"runner_deals.csv", root/"xauusd_m1.csv", root/"manifest.json"
    if not all(p.is_file() for p in (dp,bp,mp)):
        raise SystemExit("Required local exports or manifest are missing")
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    dh, bh = sha256(dp), sha256(bp)
    if manifest.get("deals_sha256") != dh or manifest.get("m1_sha256") != bh:
        raise SystemExit("INPUT_HASH_MISMATCH: raw exports differ from manifest")
    deals, bars = read_csv(dp), read_csv(bp)
    positions, open_count, unresolved = position_groups(deals)
    bars.sort(key=lambda r:integer(r,"time"))
    times = [integer(r,"time") for r in bars]
    closes = [num(r,"close") for r in bars]
    completed = [t+60 for t in times]
    ma = {}
    for p in PERIODS:
        ma[f"SMA{p}"] = moving_average(closes,p)
        ma[f"EMA{p}"] = moving_average(closes,p,True)
    aligned, unaligned = [], 0
    for pos in positions:
        i = bisect.bisect_right(completed,pos["entry_time"])-1
        if i < 0:
            unaligned += 1
            continue
        values = {k:v[i] for k,v in ma.items()}
        states = classify(pos["direction"],closes[i],values)
        if states is None:
            unaligned += 1
            continue
        aligned.append({**pos,"states":states})
    out = [
        "# MA Filter — realized-runner diagnostic",
        "",
        "Research-only. Filter state is measured on the last completed M1 bar at/before the actual entry DEAL time. This is a fill-time proxy, not the Runner decision timestamp and not an executable counterfactual.",
        "",
        f"- Deals SHA-256: {dh}", f"- M1 SHA-256: {bh}",
        f"- Raw deal rows: {len(deals)}; M1 bars: {len(bars)}",
        f"- Closed positions: {len(positions)}; open positions: {open_count}; ambiguous groups: {unresolved}",
        f"- Aligned closed positions: {len(aligned)}; unaligned: {unaligned}",
        "",
        "| Filter | Definition | N passed | Win % | Net USD | PF | Avg USD | Max DD USD | Excluded winners | Excluded losers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for fid,name in FILTERS.items():
        passed = [r for r in aligned if r["states"][fid]]
        rejected = [r for r in aligned if not r["states"][fid]]
        m = stats(passed)
        ew,el = sum(r["net"]>0 for r in rejected),sum(r["net"]<0 for r in rejected)
        out.append(f"| {fid} | {name} | {m['n']} | {fmt(m['win'])} | {fmt(m['net'])} | {fmt(m['pf'],3)} | {fmt(m['avg'],3)} | {fmt(m['dd'])} | {ew} | {el} |")
    out += [
        "", "## Blocked definitions and replays", "",
        "| Item | Status | Reason |", "|---|---|---|",
        "| F14–F18 | BLOCKED | Slope lookback/horizon is unspecified; no arbitrary slope convention is introduced. |",
        "| M0 ACT40+TRAIL40 | BLOCKED | Exact activation, broker stop-distance, update timing and fill semantics require source pinning. |",
        "| M1–M4 fixed RR1–RR4 | BLOCKED | Entry/fill, initial SL, costs, intrabar ordering and same-bar ambiguity are not frozen. |",
        "", "## Decision use", "",
        "F00 is the realized baseline. F01–F13 are descriptive subsets of trades actually taken under the existing management. Excluded winners/losers expose selection effects. These results cannot identify the best executable Runner or rank Top 3/Top 5 management variants. Use them only for exploratory screening; long-horizon replay and untouched validation remain mandatory.",
        "",
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text("\n".join(out),encoding="utf-8")
    print(f"REPORT={output.resolve()}")
    print(f"ALIGNED_CLOSED={len(aligned)} OPEN={open_count} AMBIGUOUS={unresolved} UNALIGNED={unaligned}")
    print("COMPUTED_FILTERS=14 BLOCKED_FILTERS=5 BLOCKED_MANAGEMENT_VARIANTS=5")

if __name__ == "__main__":
    main()
