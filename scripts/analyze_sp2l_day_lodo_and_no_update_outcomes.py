#!/usr/bin/env python
"""Follow-up QC: explain RR3-RR6 no-update equality and leave-one-day-out.

Uses only the existing anonymized paired CSV and relative-day joined CSV.
Aggregate-only output; no MT5, raw archive, dates, timestamps, or trade IDs.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np

RRS=range(1,7)

def read(p):
    with Path(p).expanduser().resolve().open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def vals(rows,rr):
    return [float(r[f"actual_minus_rr{rr}_usd"]) for r in rows if r.get(f"actual_minus_rr{rr}_usd") not in ("",None)]

def stats(x):
    return {"n":len(x),"mean_delta_usd":round(float(np.mean(x)),4) if x else None,
            "sum_delta_usd":round(float(np.sum(x)),4) if x else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("paired_csv")
    ap.add_argument("day_bucket_csv")
    ap.add_argument("--output-dir",default="")
    a=ap.parse_args()
    rows=read(a.paired_csv); dayrows=read(a.day_bucket_csv)
    if len(rows)!=66 or len(dayrows)!=66: raise SystemExit("POPULATION_GATE_FAILED")
    if [r.get("trade_key") for r in rows]!=[f"T{i:03d}" for i in range(1,67)]:
        raise SystemExit("PAIRED_ORDER_GATE_FAILED")
    if [r.get("trade_key") for r in dayrows]!=[f"T{i:03d}" for i in range(1,67)]:
        raise SystemExit("DAY_JOIN_ORDER_GATE_FAILED")
    if any(rows[i]["trade_key"]!=dayrows[i]["trade_key"] for i in range(66)):
        raise SystemExit("JOIN_KEY_MISMATCH")
    no_update=[r for r in rows if int(r.get("successful_trail_updates") or 0)==0]
    equality={}
    for rr in range(3,7):
        outcomes=[r.get(f"rr{rr}_outcome","") for r in no_update]
        nets=[r.get(f"rr{rr}_net_usd","") for r in no_update]
        equality[f"RR{rr}"]={"outcome_counts":{x:outcomes.count(x) for x in sorted(set(outcomes))},
            "net_nonblank":sum(x not in ("",None) for x in nets),
            "unique_net_values":len(set(x for x in nets if x not in ("",None)))}
    same_outcome_rows=sum(
        len({r.get(f"rr{rr}_outcome","") for rr in range(3,7)})==1 for r in no_update)
    same_net_rows=sum(
        all(r.get(f"rr{rr}_net_usd","") not in ("",None) for rr in range(3,7)) and
        len({r.get(f"rr{rr}_net_usd") for rr in range(3,7)})==1 for r in no_update)
    byday={}
    for r in dayrows: byday.setdefault(r["day_bucket"],[]).append(r)
    lodo={}
    for omitted in sorted(byday):
        kept=[r for r in dayrows if r["day_bucket"]!=omitted]
        lodo[omitted]={"remaining_n":len(kept)}
        for rr in RRS: lodo[omitted][f"RR{rr}"]=stats(vals(kept,rr))
    full={}
    for rr in RRS: full[f"RR{rr}"]=stats(vals(dayrows,rr))
    out=Path(a.output_dir).expanduser().resolve() if a.output_dir else Path(a.paired_csv).expanduser().resolve().parent/"SP2L_DAY_STABILITY_QC"
    out.mkdir(parents=True,exist_ok=True)
    report={"status":"NO_UPDATE_OUTCOME_AND_LEAVE_ONE_DAY_OUT_QC_COMPLETE",
      "population":66,"no_successful_update_n":len(no_update),
      "no_update_rr3_to_rr6":{"per_rr":equality,"rows_same_outcome_rr3_to_rr6":same_outcome_rows,
                              "rows_same_nonblank_net_rr3_to_rr6":same_net_rows},
      "full_sample_paired_delta":full,"leave_one_relative_day_out":lodo,
      "limitations":["In-sample diagnostic only; not a holdout.",
        "Four day buckets are too few for robust time-series inference.",
        "Leave-one-day-out is sensitivity analysis, not an independent validation.",
        "No causal interpretation of successful trailing update status.",
        "No strategy, geometry, execution rule, or live configuration is changed."]}
    p=out/"day_lodo_and_no_update_outcome_qc.json"
    p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    print("NO_UPDATE_OUTCOME_AND_LEAVE_ONE_DAY_OUT_QC_COMPLETE")
    print("TRADES=66 NO_UPDATE_N=",len(no_update))
    print("RR3_RR6_SAME_OUTCOME_ROWS=",same_outcome_rows,"SAME_NET_ROWS=",same_net_rows)
    for rr,v in equality.items(): print(rr,"OUTCOMES=",v["outcome_counts"],"UNIQUE_NET=",v["unique_net_values"])
    print("LEAVE_ONE_DAY_OUT")
    for d,v in lodo.items():
        print("OMIT",d,"N=",v["remaining_n"]," ".join(f"RR{rr}={v[f'RR{rr}']['mean_delta_usd']}" for rr in RRS))
    print("REPORT=",p)
    print("REPORT_SHA256=",digest)

if __name__=="__main__": main()
