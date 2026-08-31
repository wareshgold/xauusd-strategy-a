import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const configs = [
  { tf: '1min', baseline: 'data/reports/strategy-a-baseline/1min.json' },
  { tf: '5min', baseline: 'data/reports/strategy-a-baseline/5min.json' },
];
const horizons = [2, 3, 5];
const thresholds = [0.25, 0.5, 0.75, 1];

function load(p) { return JSON.parse(fs.readFileSync(path.join(root, p), 'utf8')); }
function finite(n) { return Number.isFinite(n) ? n : 0; }
function pf(rs) {
  const wins = rs.filter(r => r > 0).reduce((a,b)=>a+b,0);
  const losses = -rs.filter(r => r < 0).reduce((a,b)=>a+b,0);
  return losses === 0 ? Infinity : wins / losses;
}
function dd(rs) {
  let eq=0, peak=0, max=0;
  for (const r of rs) { eq += r; peak=Math.max(peak,eq); max=Math.max(max,peak-eq); }
  return max;
}
function med(a) { const x=[...a].sort((a,b)=>a-b); if(!x.length)return 0; const m=Math.floor(x.length/2); return x.length%2?x[m]:(x[m-1]+x[m])/2; }

// The baseline report schema is intentionally consumed generically: trade objects must
// contain entryIndex, rMultiple, result, riskDistance and enough path data to infer
// adverse excursion. The forensic reports provide per-trade path samples.
for (const c of configs) {
  const baseline = load(c.baseline);
  const forensicPath = `data/reports/strategy-a-trade-forensics/${c.tf}.json`;
  const forensic = fs.existsSync(path.join(root, forensicPath)) ? load(forensicPath) : null;
  if (!forensic) throw new Error(`Missing ${forensicPath}; run analyze-trade-forensics first.`);

  const trades = forensic.trades ?? forensic;
  if (!Array.isArray(trades)) throw new Error(`Unsupported forensic schema for ${c.tf}`);

  const baseRs = trades.map(t => finite(t.rMultiple)).filter((_,i)=>i < baseline.metrics?.trades ?? Infinity);
  const results = [];
  for (const h of horizons) for (const threshold of thresholds) {
    const simulated = [];
    let earlyExits=0, earlyWins=0, earlyLosses=0;
    for (const t of trades) {
      const pathSamples = t.path ?? t.earlyPath ?? t.candles ?? [];
      let exit = null;
      for (const s of pathSamples) {
        const idx = s.horizon ?? s.offset ?? s.candleOffset;
        const adverse = Math.abs(Math.min(0, finite(s.closeR ?? s.adverseR ?? s.maeR)));
        if (idx <= h && adverse >= threshold) { exit = -threshold; break; }
      }
      const r = exit === null ? finite(t.rMultiple) : exit;
      simulated.push(r);
      if (exit !== null) { earlyExits++; if (finite(t.rMultiple)>0) earlyWins++; else earlyLosses++; }
    }
    const totalR = simulated.reduce((a,b)=>a+b,0);
    results.push({ horizon:h, thresholdR:threshold, trades:simulated.length, earlyExits, earlyWins, earlyLosses,
      winRate: simulated.filter(r=>r>0).length/simulated.length, averageR:totalR/simulated.length,
      profitFactor:pf(simulated), totalR, maxDrawdownR:dd(simulated), medianR:med(simulated) });
  }
  const out = { timeframe:c.tf, baseline: { trades:baseRs.length, totalR:baseRs.reduce((a,b)=>a+b,0), averageR:baseRs.reduce((a,b)=>a+b,0)/baseRs.length, profitFactor:pf(baseRs), maxDrawdownR:dd(baseRs) }, simulations:results,
    researchNote:'Diagnostic only. This simulation closes a trade at -thresholdR when adverse path reaches the threshold within the selected early horizon; otherwise the original terminal result is retained. No strategy rule changed.' };
  const outDir=path.join(root,`data/reports/strategy-a-early-exit-simulation`); fs.mkdirSync(outDir,{recursive:true});
  fs.writeFileSync(path.join(outDir,`${c.tf}.json`),JSON.stringify(out,null,2)+'\n');
  console.log(`${c.tf}: baseline trades=${baseRs.length}`);
  for(const r of results) console.log(`  h+${r.horizon} adverse>=${r.thresholdR}R: exits=${r.earlyExits} earlyW/L=${r.earlyWins}/${r.earlyLosses} PF=${Number.isFinite(r.profitFactor)?r.profitFactor.toFixed(4):'Infinity'} avgR=${r.averageR.toFixed(4)} totalR=${r.totalR.toFixed(4)} DD=${r.maxDrawdownR.toFixed(4)}`);
  console.log(`Report -> ${path.join(outDir,`${c.tf}.json`)}`);
}
