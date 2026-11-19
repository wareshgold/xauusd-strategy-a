"""Build a gap-isolated V3.1 frozen entry population from the audited M1 CSV.GZ.

Offline research only. No MT5 imports, runner imports, network calls, or order APIs.
Every timestamp discontinuity >60 seconds splits the input into independent segments;
neither setup detection nor entry search can cross a gap.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, importlib.util, json, math, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG_PATH = HERE / "vendor" / "sp2l_v3_1_rr4_act40_config.py"
EXPECTED_SOURCE_SHA256 = "daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402"
EXPECTED_ROWS = 89866
EXPECTED_FIRST_UTC = "2026-08-10T01:00:00Z"
EXPECTED_LAST_UTC = "2026-11-09T07:43:00Z"
INPUT_FIELDS = ["time", "time_utc", "open", "high", "low", "close", "tick_volume", "spread_points", "real_volume"]
OUTPUT_FIELDS = ["strategy","variant","direction","setup_time_utc","entry_time_utc","entry_proxy","sl_initial","target","risk_price","exit_time_utc","exit_price","exit_reason","status","r_multiple"]

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def iso_utc(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")

def load_config():
    spec = importlib.util.spec_from_file_location("pinned_sp2l_v3_1_config", CFG_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned config: {CFG_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def load_bars(path: Path, expected_sha: str):
    raw = path.read_bytes()
    actual_sha = sha256_bytes(raw)
    if actual_sha != expected_sha:
        raise ValueError(f"source SHA mismatch: expected={expected_sha} actual={actual_sha}")
    bars = []
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != INPUT_FIELDS:
            raise ValueError(f"unexpected M1 header: {reader.fieldnames}")
        prev = None
        for line, row in enumerate(reader, 2):
            ts = int(row["time"])
            parsed = datetime.fromisoformat(row["time_utc"].replace("Z", "+00:00"))
            if parsed.tzinfo is None or int(parsed.timestamp()) != ts or ts % 60:
                raise ValueError(f"invalid UTC/epoch timestamp at line {line}")
            if prev is not None and ts <= prev:
                raise ValueError(f"duplicate/out-of-order timestamp at line {line}")
            o,h,l,c = (float(row[k]) for k in ("open","high","low","close"))
            if not all(math.isfinite(x) and x > 0 for x in (o,h,l,c)) or h < max(o,l,c) or l > min(o,h,c):
                raise ValueError(f"invalid OHLC at line {line}")
            bars.append({"time":ts,"open":o,"high":h,"low":l,"close":c,
                         "tick_volume":int(row["tick_volume"]),
                         "spread":int(row["spread_points"]),
                         "real_volume":int(row["real_volume"])})
            prev = ts
    if len(bars) != EXPECTED_ROWS:
        raise ValueError(f"row count mismatch: expected={EXPECTED_ROWS} actual={len(bars)}")
    if iso_utc(bars[0]["time"]) != EXPECTED_FIRST_UTC or iso_utc(bars[-1]["time"]) != EXPECTED_LAST_UTC:
        raise ValueError("source first/last timestamp mismatch")
    return bars, actual_sha, len(raw)

def split_segments(bars):
    segments, gaps, start = [], [], 0
    for i in range(1, len(bars)):
        delta = bars[i]["time"] - bars[i-1]["time"]
        if delta != 60:
            gaps.append({"previous_utc":iso_utc(bars[i-1]["time"]),
                         "next_utc":iso_utc(bars[i]["time"]),
                         "delta_seconds":delta,
                         "missing_minute_slots":max(0, delta//60-1)})
            segments.append(bars[start:i])
            start = i
    segments.append(bars[start:])
    return [s for s in segments if s], gaps

def build_population(segments, cfg, symbol):
    out, seen = [], set()
    for segment in segments:
        for i in range(2, len(segment)-2):
            setup = cfg.detect(segment[i-2:i+1], symbol)
            if not setup:
                continue
            candidate = cfg.find_first_entry(segment, i, setup)
            if not candidate:
                continue
            key = (int(candidate["trigger_time"]), candidate["direction"])
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "strategy":"SP2L","variant":cfg.VERSION,"direction":candidate["direction"],
                "setup_time_utc":iso_utc(int(segment[i]["time"])),
                "entry_time_utc":iso_utc(int(candidate["trigger_time"])),
                "entry_proxy":f'{float(candidate["theoretical_entry"]):.10g}',
                "sl_initial":f'{float(candidate["sl"]):.10g}',
                "target":f'{float(candidate["tp"]):.10g}',
                "risk_price":f'{float(candidate["risk"]):.10g}',
                "exit_time_utc":"","exit_price":"","exit_reason":"","status":"","r_multiple":"",
            })
    out.sort(key=lambda x:(x["entry_time_utc"],x["direction"]))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--m1-csv-gz",required=True)
    ap.add_argument("--m1-sha256",default=EXPECTED_SOURCE_SHA256)
    ap.add_argument("--symbol",default="XAUUSD.ecn")
    ap.add_argument("--output-dir",required=True)
    args=ap.parse_args()
    if args.m1_sha256.lower()!=EXPECTED_SOURCE_SHA256:
        raise ValueError("only the audited three-month M1 SHA is accepted")
    source=Path(args.m1_csv_gz).resolve()
    outdir=Path(args.output_dir).resolve()
    if outdir.exists() and (not outdir.is_dir() or any(outdir.iterdir())):
        raise FileExistsError(f"output directory is not empty or is not a directory: {outdir}")
    outdir.mkdir(parents=True,exist_ok=True)
    bars,source_sha,source_bytes=load_bars(source,args.m1_sha256)
    segments,gaps=split_segments(bars)
    cfg=load_config()
    population=build_population(segments,cfg,args.symbol)
    if not population:
        raise RuntimeError("empty population; no output accepted")
    csv_path=outdir/"SP2L_V31_THREE_MONTH_FROZEN_ENTRIES.csv"
    with csv_path.open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=OUTPUT_FIELDS); w.writeheader(); w.writerows(population)
    csv_sha=sha256_bytes(csv_path.read_bytes())
    cfg_sha=sha256_bytes(CFG_PATH.read_bytes())
    month_counts={}
    for row in population:
        key=f'{row["entry_time_utc"][:7]}:{row["direction"]}'
        month_counts[key]=month_counts.get(key,0)+1
    manifest={
        "research_only":True,"canonical":False,"symbol":args.symbol,"timeframe":"M1",
        "source_path":str(source),"source_sha256":source_sha,"source_bytes":source_bytes,
        "source_rows":len(bars),"source_first_utc":iso_utc(bars[0]["time"]),
        "source_last_utc":iso_utc(bars[-1]["time"]),
        "source_header_mapping":{"time":"epoch_seconds","time_utc":"UTC_ISO8601","spread_points":"spread"},
        "gap_policy":"SPLIT_ON_EVERY_TIMESTAMP_DELTA_NOT_EQUAL_TO_60_SECONDS; NO_SETUP_OR_ENTRY_SEARCH_CROSSES_SEGMENTS",
        "gap_count":len(gaps),"gaps":gaps,"segment_count":len(segments),
        "entry_config_version":cfg.VERSION,"entry_config_source_branch":"feat/v31-monitor-control-center-20261116",
        "entry_config_source_path":"scripts/sp2l_v3_1_rr4_act40_config.py",
        "entry_config_sha256":cfg_sha,"population_rows":len(population),
        "population_sha256":csv_sha,"population_month_direction_counts":month_counts,
        "population_policy":"ONE_FIXED_V31_ENTRY_POPULATION_SHARED_BY_ALL_EXIT_VARIANTS",
        "exit_fields":"BLANK; EXIT MANAGEMENT MUST BE REPLAYED SEPARATELY",
        "limitations":["All timestamp gaps, including expected market closures, split the signal search.",
                       "No gap is filled or bridged; trades do not carry through a gap during entry discovery.",
                       "Tick-level fills, spread, commission, slippage, and historical contract metadata are not inferred here.",
                       "This pinned config is a research replica, not canonical Strategy A source confirmation."],
        "mt5_accessed":False,"runner_accessed":False,"orders_possible":False
    }
    manifest_path=outdir/"SP2L_V31_THREE_MONTH_FROZEN_ENTRIES_MANIFEST.json"
    with manifest_path.open("x",encoding="utf-8") as f:
        json.dump(manifest,f,indent=2,ensure_ascii=False); f.write("\\n")
    print(json.dumps({"status":"COMPLETE","rows":len(population),"csv":str(csv_path),
      "csv_sha256":csv_sha,"manifest":str(manifest_path),"source_sha256":source_sha,
      "source_rows":len(bars),"gap_count":len(gaps),"segments":len(segments),
      "config":cfg.VERSION,"config_sha256":cfg_sha,"mt5_accessed":False},indent=2))

if __name__=="__main__": main()
