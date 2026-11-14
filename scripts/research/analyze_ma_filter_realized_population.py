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

def inspect_m1_timestamps(times):
    """Require source order and report gaps; never sort or synthesize missing bars."""
    gaps = []
    for i in range(1, len(times)):
        delta = times[i] - times[i - 1]
        if delta <= 0:
            raise ValueError("M1 timestamps must be strictly increasing (no duplicates or out-of-order bars)")
        if delta > 60:
            gaps.append({"index": i, "previous": times[i - 1], "current": times[i], "seconds": delta})
    return gaps

def last_completed_m1_index(times, timestamp):
    """Index of the last bar whose 60-second interval ended at/before timestamp."""
    completed = [t + 60 for t in times]
    index = bisect.bisect_right(completed, timestamp) - 1
    return index if index >= 0 else None

def moving_average(values, period, exponential=False, gap_indices=()):
    """Calculate MA independently inside contiguous M1 segments.

    A gap index identifies the first observed bar after a missing interval.
    Both SMA and EMA remain unavailable until a full period of contiguous
    observations has accumulated. EMA is reseeded from that segment's first
    full-period SMA; no pre-gap recursive state is carried across the gap.
    """
    if period <= 0:
        raise ValueError("period must be positive")
    out = [None] * len(values)
    boundaries = sorted(set(int(i) for i in gap_indices))
    if any(i <= 0 or i >= len(values) for i in boundaries):
        raise ValueError("gap index must identify a non-initial bar within values")
    starts = [0, *boundaries]
    ends = [*boundaries, len(values)]
    for start, end in zip(starts, ends):
        segment = values[start:end]
        if len(segment) < period:
            continue
        seed = sum(segment[:period]) / period
        out[start + period - 1] = seed
        if not exponential:
            running = sum(segment[:period])
            for offset in range(period, len(segment)):
                running += segment[offset] - segment[offset-period]
                out[start + offset] = running / period
            continue
        alpha, previous = 2.0 / (period + 1.0), seed
        for offset in range(period, len(segment)):
            previous = alpha * segment[offset] + (1.0-alpha) * previous
            out[start + offset] = previous
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
    """Return True/False per filter; None means that filter lacks MA history."""
    def side(key):
        x = ma[key]
        if x is None: return None
        if close == x: return 0
        return 1 if (close > x if direction == "BUY" else close < x) else -1

    s = {k:side(k) for k in ma}
    def available(*keys):
        return all(s[k] is not None for k in keys)

    result = {"F00": True}
    simple = {
        "F01":"SMA50", "F02":"SMA100", "F03":"EMA50", "F04":"EMA100",
        "F05":"SMA20", "F06":"SMA200", "F07":"EMA20", "F08":"EMA200",
    }
    for fid, key in simple.items():
        result[fid] = None if s[key] is None else s[key] == 1

    result["F09"] = None if not available("SMA50", "SMA100") else s["SMA50"] == 1 and s["SMA100"] == 1
    result["F10"] = None if not available("EMA50", "EMA100") else s["EMA50"] == 1 and s["EMA100"] == 1
    result["F11"] = None if not available("SMA50", "SMA100") else (
        s["SMA50"] == 1 and s["SMA100"] == 1 and
        (ma["SMA50"] > ma["SMA100"] if direction == "BUY" else ma["SMA50"] < ma["SMA100"])
    )
    result["F12"] = None if not available("EMA50", "EMA100") else (
        s["EMA50"] == 1 and s["EMA100"] == 1 and
        (ma["EMA50"] > ma["EMA100"] if direction == "BUY" else ma["EMA50"] < ma["EMA100"])
    )
    keys = ("SMA50", "SMA100", "EMA50", "EMA100")
    if any(s[k] == 1 for k in keys):
        result["F13"] = True
    elif available(*keys):
        result["F13"] = False
    else:
        result["F13"] = None
    return result

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
    times = [integer(r,"time") for r in bars]
    gaps = inspect_m1_timestamps(times)
    closes = [num(r,"close") for r in bars]
    gap_indices = [g["index"] for g in gaps]
    ma = {}
    for p in PERIODS:
        ma[f"SMA{p}"] = moving_average(closes,p,gap_indices=gap_indices)
        ma[f"EMA{p}"] = moving_average(closes,p,True,gap_indices=gap_indices)
    aligned, unaligned = [], 0
    for pos in positions:
        i = last_completed_m1_index(times, pos["entry_time"])
        if i is None:
            unaligned += 1
            continue
        values = {k:v[i] for k,v in ma.items()}
        states = classify(pos["direction"],closes[i],values)
        aligned.append({**pos,"states":states})
    out = [
        "# MA Filter — realized-runner diagnostic",
        "",
        "Research-only. Filter state is measured on the last completed M1 bar at/before the actual entry DEAL time. This is a fill-time proxy, not the Runner decision timestamp and not an executable counterfactual.",
        "",
        f"- Deals SHA-256: {dh}", f"- M1 SHA-256: {bh}",
        f"- Raw deal rows: {len(deals)}; M1 bars: {len(bars)}",
        f"- M1 gaps >60s: {len(gaps)}; largest gap: {max((g['seconds'] for g in gaps), default=0)}s",
        f"- Closed positions: {len(positions)}; open positions: {open_count}; ambiguous groups: {unresolved}",
        f"- Aligned closed positions: {len(aligned)}; unaligned: {unaligned}",
        "",
        "| Filter | Definition | N passed | Unavailable | Win % | Net USD | PF | Avg USD | Max DD USD | Excluded winners | Excluded losers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for fid,name in FILTERS.items():
        passed = [r for r in aligned if r["states"][fid] is True]
        rejected = [r for r in aligned if r["states"][fid] is False]
        unavailable = [r for r in aligned if r["states"][fid] is None]
        m = stats(passed)
        ew,el = sum(r["net"]>0 for r in rejected),sum(r["net"]<0 for r in rejected)
        out.append(f"| {fid} | {name} | {m['n']} | {len(unavailable)} | {fmt(m['win'])} | {fmt(m['net'])} | {fmt(m['pf'],3)} | {fmt(m['avg'],3)} | {fmt(m['dd'])} | {ew} | {el} |")
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
