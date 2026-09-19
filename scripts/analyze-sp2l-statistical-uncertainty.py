import json, math, random
from pathlib import Path
from statistics import mean

INPUT = Path("artifacts/SP2L_pl_pip_accounting_2026-09-14_2026-09-18.json")
OUTPUT = Path("artifacts/SP2L_statistical_uncertainty_2026-09-14_2026-09-18.json")
B = 20000
SEED = 20260919

data = json.loads(INPUT.read_text(encoding="utf-8"))
rows = [r for r in data["signals"] if r["realized_pips"] is not None]
outcomes = [r["outcome"] for r in rows]
pips = [float(r["realized_pips"]) for r in rows]
pl = [float(r["realized_pl_account_currency"]) for r in rows]

def percentile(xs, q):
    ys = sorted(xs)
    if not ys: return None
    pos = (len(ys)-1)*q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi: return ys[lo]
    return ys[lo] + (ys[hi]-ys[lo])*(pos-lo)

def bootstrap(metric, n=B):
    rng = random.Random(SEED)
    vals=[]
    m=len(rows)
    for _ in range(n):
        idx=[rng.randrange(m) for _ in range(m)]
        vals.append(metric(idx))
    return {
        "bootstrap_samples": n,
        "ci_95_percentile": [percentile(vals,0.025), percentile(vals,0.975)],
        "median_bootstrap": percentile(vals,0.5),
        "mean_bootstrap": mean(vals),
    }

def wr(idx):
    return sum(outcomes[i]=="WIN" for i in idx)/len(idx)*100

def net_pips(idx):
    return sum(pips[i] for i in idx)

def net_pl(idx):
    return sum(pl[i] for i in idx)

def pf(idx):
    gp=sum(pl[i] for i in idx if pl[i]>0)
    gl=abs(sum(pl[i] for i in idx if pl[i]<0))
    return gp/gl if gl else None

def avg_win_loss(idx):
    w=[pips[i] for i in idx if pips[i]>0]
    l=[abs(pips[i]) for i in idx if pips[i]<0]
    return (mean(w)/mean(l)) if w and l else None

# Wilson score interval for observed decisive win rate.
wins=sum(x=="WIN" for x in outcomes)
n=len(outcomes)
z=1.959963984540054
phat=wins/n
den=1+z*z/n
center=(phat+z*z/(2*n))/den
half=z*math.sqrt((phat*(1-phat)/n)+(z*z/(4*n*n)))/den
wilson=[center-half, center+half]

# Leave-k-largest-wins-out sensitivity: descriptive, not optimization.
win_pip_rows=sorted([(pips[i],i) for i in range(n) if pips[i]>0], reverse=True)
sensitivity={}
for k in [1,2,3,5]:
    drop=set(i for _,i in win_pip_rows[:k])
    kept=[i for i in range(n) if i not in drop]
    sensitivity[str(k)] = {
        "removed_winning_trades": k,
        "removed_pips": sum(pips[i] for _,i in win_pip_rows[:k]),
        "remaining_n": len(kept),
        "remaining_wins": sum(outcomes[i]=="WIN" for i in kept),
        "remaining_losses": sum(outcomes[i]=="LOSS" for i in kept),
        "remaining_win_rate_pct": wr(kept),
        "remaining_net_pips": net_pips(kept),
        "remaining_net_pl_0_01_lot": net_pl(kept),
        "remaining_profit_factor": pf(kept),
    }

result={
    "research_only": True,
    "artifact_type":"SP2L_STATISTICAL_UNCERTAINTY",
    "input_artifact":str(INPUT),
    "input_artifact_sha256":data.get("source_artifact_sha256"),
    "sample":{"decisive_n":n,"wins":wins,"losses":sum(x=="LOSS" for x in outcomes),"ambiguous_excluded":sum(x["outcome"]=="AMBIGUOUS" for x in data["signals"])},
    "observed":{"win_rate_pct":phat*100,"wilson_95_ci_pct":[wilson[0]*100,wilson[1]*100],"net_pips":sum(pips),"net_pl_0_01_lot":sum(pl),"profit_factor":pf(list(range(n))),"avg_win_loss_pip_ratio":avg_win_loss(list(range(n)))},
    "bootstrap": {
        "win_rate_pct":bootstrap(wr),
        "net_pips":bootstrap(net_pips),
        "net_pl_0_01_lot":bootstrap(net_pl),
        "profit_factor":bootstrap(pf),
        "avg_win_loss_pip_ratio":bootstrap(avg_win_loss),
    },
    "largest_winner_sensitivity":sensitivity,
    "methodology":{"bootstrap_replicates":B,"seed":SEED,"ci_method":"percentile_95","win_rate_interval":"Wilson_score_95"},
    "guard":"RESEARCH_STATISTICS_ONLY; NO_RULE_OR_PARAMETER_PROMOTION",
    "limitations":[
        "37 decisive observations is a small sample.",
        "Bootstrap resamples trades as if independently exchangeable; temporal dependence is not modeled.",
        "The observed window is historical and not a fresh post-boundary holdout.",
        "Ambiguous outcome is excluded rather than resolved.",
        "Costs and broker execution effects are not reconstructed.",
        "Sensitivity removes largest winning trades descriptively; it is not a selection procedure."
    ]
}
OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({
    "status":"ANALYZED","output":str(OUTPUT),
    "observed":result["observed"],
    "bootstrap":result["bootstrap"],
    "largest_winner_sensitivity":result["largest_winner_sensitivity"]
},ensure_ascii=False,indent=2))
