"""Offline read-only comparison of a supplied MT5 tick dump and M1 OHLC CSV."""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ENTRY_DEFAULT = "2026-10-27T12:56:05.552Z"
EXIT_DEFAULT = "2026-10-27T13:01:49Z"
TICK_RE = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)).*?\bBID\s*=\s*(?P<bid>-?\d+(?:\.\d+)?).*?\bASK\s*=\s*(?P<ask>-?\d+(?:\.\d+)?)", re.I)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def parse_utc(value):
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None: raise ValueError(f"Timestamp must include UTC offset: {value}")
    return dt.astimezone(timezone.utc)

def parse_ticks(path):
    ticks = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        m = TICK_RE.search(line)
        if not m: continue
        dt = parse_utc(m["ts"])
        ticks.append({"epoch": dt.timestamp(), "time_utc": dt.isoformat(timespec="milliseconds").replace("+00:00","Z"),
                      "bid": float(m["bid"]), "ask": float(m["ask"]), "line": line_no})
    if not ticks: raise ValueError("No timestamp/BID/ASK rows found in tick file")
    return sorted(ticks, key=lambda x:(x["epoch"],x["line"]))

def parse_bar_epoch(raw):
    value = raw.strip()
    try: return int(float(value))
    except ValueError: return int(parse_utc(value).timestamp())

def parse_m1(path):
    bars=[]
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(4096); f.seek(0)
        try: dialect=csv.Sniffer().sniff(sample,delimiters=",;\t|")
        except csv.Error: dialect=csv.excel
        reader=csv.DictReader(f,dialect=dialect)
        if not reader.fieldnames: raise ValueError("M1 CSV has no header")
        cols={n.strip().lower():n for n in reader.fieldnames if n}
        aliases={"time":("time","datetime","timestamp","date"),"open":("open","o"),"high":("high","h"),"low":("low","l"),"close":("close","c")}
        chosen={}
        for key,names in aliases.items():
            found=next((cols[n] for n in names if n in cols),None)
            if found is None: raise ValueError(f"M1 CSV missing {key}; headers={reader.fieldnames}")
            chosen[key]=found
        for n,row in enumerate(reader,2):
            try:
                t=parse_bar_epoch(row[chosen["time"]])
                bars.append({"epoch":t,"time_utc":datetime.fromtimestamp(t,timezone.utc).isoformat().replace("+00:00","Z"),
                             **{k:float(row[chosen[k]]) for k in ("open","high","low","close")},"source_row":n})
            except (TypeError,ValueError) as e: raise ValueError(f"Invalid M1 CSV row {n}: {e}") from e
    return sorted(bars,key=lambda x:x["epoch"])

def audit(ticks,bars,entry_text,exit_text):
    entry=parse_utc(entry_text); entry_epoch=entry.timestamp()
    exit_dt=parse_utc(exit_text) if exit_text else None
    exit_epoch=exit_dt.timestamp() if exit_dt else ticks[-1]["epoch"]
    post=[t for t in ticks if t["epoch"]>=entry_epoch]
    if not post: raise ValueError("No ticks at/after entry in supplied tick file")
    min_bid=min(post,key=lambda x:x["bid"]); min_ask=min(post,key=lambda x:x["ask"])
    tick_minutes=defaultdict(list)
    for t in ticks: tick_minutes[int(t["epoch"]//60)*60].append(t)
    start=int(entry_epoch//60)*60-60; end=int(exit_epoch//60)*60+60
    nearby=[b for b in bars if start<=b["epoch"]<=end]
    rows=[]
    for b in nearby:
        ts=tick_minutes.get(b["epoch"],[])
        rows.append({**b,"tick_count_in_minute":len(ts),
          "first_tick_utc":ts[0]["time_utc"] if ts else None,
          "first_tick_bid":ts[0]["bid"] if ts else None,
          "last_tick_before_minute_end_utc":ts[-1]["time_utc"] if ts else None,
          "last_tick_before_minute_end_bid":ts[-1]["bid"] if ts else None,
          "last_tick_before_minute_end_ask":ts[-1]["ask"] if ts else None,
          "tick_coverage":"PRESENT" if ts else "NO_TICKS_IN_SUPPLIED_FILE"})
    return {"status":"COMPLETE","research_only":True,"read_only":True,"position_id":64500649,"direction":"SELL",
      "entry_time_utc":entry.isoformat(timespec="milliseconds").replace("+00:00","Z"),
      "exit_time_utc":exit_dt.isoformat(timespec="seconds").replace("+00:00","Z") if exit_dt else None,
      "reported_entry_price":4006.11,"trail_activation_distance_price":0.40,
      "tick_rows":len(ticks),"tick_coverage_start_utc":ticks[0]["time_utc"],"tick_coverage_end_utc":ticks[-1]["time_utc"],
      "post_entry_tick_rows":len(post),"minimum_post_entry_bid":{"time_utc":min_bid["time_utc"],"bid":min_bid["bid"],"favorable_move_price":round(4006.11-min_bid["bid"],8)},
      "minimum_post_entry_ask":{"time_utc":min_ask["time_utc"],"ask":min_ask["ask"]},
      "m1_total_rows":len(bars),"m1_rows_near_position":len(rows),"m1_bars":rows,
      "limitations":["Offline only; no MT5 connection or order actions.","No ticks in a minute means absent from the supplied tick file, not no market ticks.","M1 OHLC cannot establish intrabar ordering relative to entry.","SELL favorable movement uses Bid as a diagnostic only; verify execution and stop handling from runner events and broker history.","The 0.40 threshold is a supplied case parameter, not a canonical rule."]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ticks",required=True,type=Path); p.add_argument("--m1",required=True,type=Path)
    p.add_argument("--entry-time",default=ENTRY_DEFAULT); p.add_argument("--exit-time",default=EXIT_DEFAULT)
    p.add_argument("--output",type=Path,help="Optional separate JSON report; inputs are never modified")
    a=p.parse_args()
    for path in (a.ticks,a.m1):
        if not path.is_file(): raise FileNotFoundError(path)
    result=audit(parse_ticks(a.ticks),parse_m1(a.m1),a.entry_time,a.exit_time or None)
    result["inputs"]={"ticks_path":str(a.ticks.resolve()),"ticks_sha256":sha256(a.ticks),
                      "m1_path":str(a.m1.resolve()),"m1_sha256":sha256(a.m1)}
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"position_id":result["position_id"],"tick_rows":result["tick_rows"],
      "tick_coverage_start_utc":result["tick_coverage_start_utc"],"tick_coverage_end_utc":result["tick_coverage_end_utc"],
      "minimum_post_entry_bid":result["minimum_post_entry_bid"],"m1_total_rows":result["m1_total_rows"],
      "m1_rows_near_position":result["m1_rows_near_position"],"m1_bars":result["m1_bars"],
      "output":str(a.output.resolve()) if a.output else None,"research_only":True,"read_only":True},indent=2,ensure_ascii=False))

if __name__=="__main__": main()
