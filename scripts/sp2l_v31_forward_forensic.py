#!/usr/bin/env python3
"""Read-only forensic summary for an archived SP2L V3.1 MT5 forward capture.

Reads only the supplied ZIP. Never imports MetaTrader5, connects to a terminal,
changes runner state, or emits trading decisions.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, statistics, sys, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED = {
    "raw/capture_metadata.json", "raw/mt5_history_deals.json",
    "raw/mt5_history_orders.json", "raw/runner_files/forward_events.jsonl",
}
ENTRY_IN, ENTRY_OUT = {0}, {1, 2, 3}
REASON_NAMES = {0:"CLIENT", 1:"MOBILE", 2:"WEB", 3:"EXPERT", 4:"SL", 5:"TP", 6:"SO"}

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _records(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        for key in ("data", "items", "records", "orders", "deals", "result"):
            if isinstance(value.get(key), list):
                return [x for x in value[key] if isinstance(x, dict)]
        if value and all(isinstance(v, dict) for v in value.values()):
            return list(value.values())
    raise ValueError("Expected JSON array or recognized object wrapper")

def _json(zf, name):
    return json.loads(zf.read(name).decode("utf-8-sig"))

def _i(row, key, default=0):
    value = row.get(key, default)
    if value is None or value == "":
        return default
    try: return int(value)
    except (TypeError, ValueError): return default

def _f(row, key):
    try: return float(row.get(key, 0.0) or 0.0)
    except (TypeError, ValueError): return 0.0

def _utc(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat() if epoch > 0 else None

def _events(raw):
    result = []
    for n, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        if not line.strip(): continue
        try: value = json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError(f"Invalid JSONL line {n}: {exc}") from exc
        if isinstance(value, dict): result.append(value)
    return result

def _manifest_checks(zf):
    name = "raw/SHA256_MANIFEST.json"
    if name not in zf.namelist():
        return {"present":False, "verified":0, "mismatches":[], "unparsed":True}
    obj = _json(zf, name)
    pairs = []
    def walk(value):
        if isinstance(value, dict):
            path = value.get("path") or value.get("file") or value.get("name")
            digest = value.get("sha256") or value.get("SHA256") or value.get("hash")
            if isinstance(path, str) and isinstance(digest, str):
                pairs.append((path, digest.lower()))
            else:
                for k, v in value.items():
                    if isinstance(k, str) and isinstance(v, str) and len(v) == 64:
                        pairs.append((k, v.lower()))
                    else: walk(v)
        elif isinstance(value, list):
            for item in value: walk(item)
    walk(obj)
    names, verified, mismatches = set(zf.namelist()), 0, []
    for path, expected in pairs:
        path = path.lstrip("./")
        if path not in names and f"raw/{path}" in names: path = f"raw/{path}"
        if path not in names: continue
        actual = _sha(zf.read(path))
        if actual == expected: verified += 1
        else: mismatches.append({"path":path, "expected":expected, "actual":actual})
    return {"present":True, "verified":verified, "mismatches":mismatches, "unparsed":not bool(pairs)}

def analyze_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        if bad: raise ValueError(f"ZIP CRC failure: {bad}")
        names = set(zf.namelist())
        missing = sorted(REQUIRED - names)
        if missing: raise ValueError("Missing ZIP members: " + ", ".join(missing))
        metadata = _json(zf, "raw/capture_metadata.json")
        deals = _records(_json(zf, "raw/mt5_history_deals.json"))
        orders = _records(_json(zf, "raw/mt5_history_orders.json"))
        events = _events(zf.read("raw/runner_files/forward_events.jsonl"))
        manifest = _manifest_checks(zf)
        member_hashes = {n:_sha(zf.read(n)) for n in sorted(REQUIRED)}

    grouped, trails = defaultdict(list), defaultdict(list)
    event_counts, trail_counts, failure_targets = Counter(), Counter(), set()
    for deal in deals:
        pid = _i(deal, "position_id")
        if pid > 0: grouped[pid].append(deal)
    for event in events:
        kind = str(event.get("event", "UNKNOWN"))
        event_counts[kind] += 1
        if kind == "TRAIL_UPDATE":
            pid = _i(event, "position")
            if pid: trails[pid].append(event)
            trail_counts["updates"] += 1
            trail_counts["success"] += int(bool(event.get("success")))
            trail_counts["failed"] += int(not bool(event.get("success")))
        elif kind == "MT5_DEAL_HISTORY_QUERY_FAILED":
            target = _i(event, "target")
            if target: failure_targets.add(target)

    trade_rows, closed_nets, reasons = [], [], Counter()
    for pid, rows in sorted(grouped.items()):
        rows.sort(key=lambda x: (_i(x, "time_msc") or _i(x, "time"), _i(x, "ticket")))
        entries = [x for x in rows if _i(x, "entry", -1) in ENTRY_IN]
        exits = [x for x in rows if _i(x, "entry", -1) in ENTRY_OUT]
        net = sum(_f(x,"profit")+_f(x,"commission")+_f(x,"swap")+_f(x,"fee") for x in rows)
        if exits: closed_nets.append(net)
        exit_codes = sorted({_i(x, "reason", -1) for x in exits})
        for code in exit_codes: reasons[REASON_NAMES.get(code, f"UNKNOWN_{code}")] += 1
        first, last = (entries[0] if entries else {}), (exits[-1] if exits else {})
        vin, vout = sum(_f(x,"volume") for x in entries), sum(_f(x,"volume") for x in exits)
        ep = sum(_f(x,"price")*_f(x,"volume") for x in entries)/vin if vin else None
        xp = sum(_f(x,"price")*_f(x,"volume") for x in exits)/vout if vout else None
        tr = trails.get(pid, [])
        ok = sum(bool(x.get("success")) for x in tr)
        trade_rows.append({
            "position_id":pid, "status":"CLOSED" if exits else "OPEN_OR_INCOMPLETE",
            "side":("BUY" if _i(first,"type",-1)==0 else "SELL" if entries else "UNKNOWN"),
            "entry_time_utc":_utc(_i(first,"time")), "exit_time_utc":_utc(_i(last,"time")),
            "entry_price_volume_weighted":round(ep,5) if ep is not None else None,
            "exit_price_volume_weighted":round(xp,5) if xp is not None else None,
            "volume_in":round(vin,4), "volume_out":round(vout,4), "deal_count":len(rows),
            "net_account_currency":round(net,2),
            "exit_reasons":"|".join(REASON_NAMES.get(x,f"UNKNOWN_{x}") for x in exit_codes),
            "trail_update_count":len(tr), "trail_success_count":ok,
            "trail_failed_count":len(tr)-ok,
            "trail_last_sl":_f(tr[-1],"new_sl") if tr else None,
        })

    n = len(closed_nets)
    wins, losses = sum(x>0 for x in closed_nets), sum(x<0 for x in closed_nets)
    gp, gl = sum(x for x in closed_nets if x>0), -sum(x for x in closed_nets if x<0)
    pf = gp/gl if gl else (None if not gp else "infinity")
    ticket_set = {_i(x,"ticket") for x in orders if _i(x,"ticket")>0}
    summary = {
        "report_version":1, "input_zip":zip_path.name, "input_zip_sha256":_sha(zip_path.read_bytes()),
        "zip_crc":"PASS",
        "metadata":{
            "captured_at":metadata.get("captured_at") or metadata.get("captured_at_utc"),
            "expected_version":metadata.get("expected_version") or metadata.get("version"),
            "symbol":metadata.get("symbol") or metadata.get("expected_symbol"),
            "magic":metadata.get("magic") or metadata.get("expected_magic"),
            "git_commit":metadata.get("commit") or metadata.get("git_commit"),
            "git_branch":metadata.get("branch") or metadata.get("git_branch"),
        },
        "integrity":{"manifest":manifest,"required_member_sha256":member_hashes},
        "raw_counts":{"deals":len(deals),"orders":len(orders),"events":len(events),"positions_with_deals":len(grouped)},
        "realized_closed_positions":{
            "count":n,"wins":wins,"losses":losses,"breakeven":n-wins-losses,
            "win_rate_pct":round(100*wins/n,2) if n else None,
            "net_account_currency":round(sum(closed_nets),2),
            "gross_profit":round(gp,2),"gross_loss_abs":round(gl,2),
            "profit_factor":round(pf,4) if isinstance(pf,float) else pf,
            "average_net_per_closed_position":round(sum(closed_nets)/n,2) if n else None,
            "median_net_per_closed_position":round(statistics.median(closed_nets),2) if closed_nets else None,
        },
        "exit_reasons":dict(reasons),
        "trailing":{"updates":trail_counts["updates"],"success":trail_counts["success"],
                    "failed":trail_counts["failed"],"positions_with_trail_events":len(trails)},
        "history_query_failures":{
            "events":event_counts["MT5_DEAL_HISTORY_QUERY_FAILED"],
            "unique_targets":len(failure_targets),
            "targets_found_in_final_order_history":len(failure_targets & ticket_set),
        },
        "event_counts":dict(sorted(event_counts.items())),
        "limitations":[
            "MFE/MAE needs synchronized price bars/ticks; it is not derivable from deals and runner events alone.",
            "V3-versus-V3.1 counterfactual needs frozen identical entries and separately validated replay/fill assumptions.",
            "Net sums broker deal profit, commission, swap and fee fields when present; currency is the MT5 account currency.",
            "Broker exit reason is an observed code, not proof of which software component caused the exit.",
        ],
    }
    return summary, trade_rows, events

def write_outputs(summary, trades, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    jp, cp = out_dir/"v31_forward_forensic_report.json", out_dir/"v31_closed_positions.csv"
    jp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    columns = list(trades[0]) if trades else ["position_id","status","side","entry_time_utc","exit_time_utc",
        "entry_price_volume_weighted","exit_price_volume_weighted","volume_in","volume_out","deal_count",
        "net_account_currency","exit_reasons","trail_update_count","trail_success_count","trail_failed_count","trail_last_sl"]
    with cp.open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=columns); writer.writeheader(); writer.writerows(trades)
    return jp,cp

def compact_text(s):
    p,t,h=s["realized_closed_positions"],s["trailing"],s["history_query_failures"]
    return "\n".join([
        "SP2L V3.1 LOCAL FORENSIC SUMMARY",f"ZIP_SHA256={s['input_zip_sha256']}",f"ZIP_CRC={s['zip_crc']}",
        f"DEALS={s['raw_counts']['deals']} ORDERS={s['raw_counts']['orders']} EVENTS={s['raw_counts']['events']}",
        f"CLOSED_POSITIONS={p['count']} WINS={p['wins']} LOSSES={p['losses']} WIN_RATE={p['win_rate_pct']}%",
        f"NET_ACCOUNT_CURRENCY={p['net_account_currency']} PF={p['profit_factor']} AVG_NET={p['average_net_per_closed_position']}",
        f"EXIT_REASONS={json.dumps(s['exit_reasons'],ensure_ascii=False,sort_keys=True)}",
        f"TRAIL_UPDATES={t['updates']} SUCCESS={t['success']} FAILED={t['failed']}",
        f"HISTORY_QUERY_FAILURES={h['events']} UNIQUE_TARGETS={h['unique_targets']} FOUND_IN_FINAL_ORDERS={h['targets_found_in_final_order_history']}",
        f"MANIFEST_VERIFIED={s['integrity']['manifest']['verified']} MANIFEST_MISMATCHES={len(s['integrity']['manifest']['mismatches'])}",
        "LIMITATION=MFE/MAE and same-entry V3 counterfactual need additional validated price/replay evidence.",
    ])

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip",required=True,type=Path,help="Private forensic ZIP path")
    parser.add_argument("--out",type=Path,default=Path("artifacts/forensic/v31-local-20261108"))
    args=parser.parse_args(argv)
    if not args.zip.is_file(): parser.error(f"ZIP not found: {args.zip}")
    try:
        summary,trades,_=analyze_zip(args.zip)
        jp,cp=write_outputs(summary,trades,args.out)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print(f"FORENSIC_ERROR={type(exc).__name__}: {exc}",file=sys.stderr); return 2
    print(compact_text(summary)); print(f"REPORT_JSON={jp.resolve()}"); print(f"POSITIONS_CSV={cp.resolve()}")
    print("READ_ONLY=True MT5_CONNECTION=False RUNNER_MODIFIED=False")
    return 0

if __name__=="__main__": raise SystemExit(main())
