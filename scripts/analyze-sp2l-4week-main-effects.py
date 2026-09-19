"""Research-only S4 main-effect analysis for the archived 4-week 81-point matrix.

Reads the local 81-combination matrix produced by analyze-sp2l-4week-parameter-stability.py.
No parameter selection/promotion.
"""
from __future__ import annotations
import json, statistics
from pathlib import Path

src=Path("artifacts/SP2L_parameter_stability_4week_81_matrix_2026-09-19.json")
out=Path("artifacts/SP2L_parameter_main_effects_4week_2026-09-19.json")
data=json.loads(src.read_text(encoding="utf-8"))
rows=data["combinations"]

params={"pGap":[0.8,1.0,1.2],"spikeMultiplier":[1.3,1.5,1.7],"maxSL":[8.0,10.0,12.0],"tpR":[0.8,1.0,1.2]}
effects={}
for p,levels in params.items():
    effects[p]={}
    for level in levels:
        r=[x for x in rows if x[p]==level]
        wr=[x["decisive_wr"] for x in r if x["decisive_wr"] is not None]
        rr=[x["total_R"] for x in r]
        pf=[x["profit_factor"] for x in r if x["profit_factor"] is not None]
        effects[p][str(level)]={
            "combinations":len(r),
            "mean_decisive_wr":statistics.mean(wr),
            "median_decisive_wr":statistics.median(wr),
            "min_decisive_wr":min(wr),
            "max_decisive_wr":max(wr),
            "mean_total_R":statistics.mean(rr),
            "median_total_R":statistics.median(rr),
            "min_total_R":min(rr),
            "max_total_R":max(rr),
            "mean_profit_factor":statistics.mean(pf),
            "median_profit_factor":statistics.median(pf),
            "positive_total_R_count":sum(v>0 for v in rr),
            "above_60pct_wr_count":sum(v>0.60 for v in wr)
        }

payload={
 "research_only":True,
 "source":str(src),
 "purpose":"S4 parameter main-effect sensitivity; descriptive only",
 "effects":effects,
 "guard":"No causal interpretation and no parameter promotion."
}
out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
print(json.dumps(payload,indent=2))
print(f"\nWrote {out}")
