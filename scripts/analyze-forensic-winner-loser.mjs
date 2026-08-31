import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const inputDir = path.join(root, 'data', 'reports', 'strategy-a-trade-forensics');
const outputDir = path.join(root, 'data', 'reports', 'strategy-a-winner-loser-analysis');
fs.mkdirSync(outputDir, { recursive: true });

function load(tf) {
  return JSON.parse(fs.readFileSync(path.join(inputDir, `${tf}.json`), 'utf8'));
}
function median(a) { if (!a.length) return null; const b=[...a].sort((x,y)=>x-y); const m=Math.floor(b.length/2); return b.length%2?b[m]:(b[m-1]+b[m])/2; }
function stats(rows) {
  if (!rows.length) return { n:0 };
  const wins=rows.filter(r=>r.rMultiple>0), losses=rows.filter(r=>r.rMultiple<0);
  const gp=wins.reduce((s,r)=>s+r.rMultiple,0), gl=-losses.reduce((s,r)=>s+r.rMultiple,0);
  return { n:rows.length, wins:wins.length, losses:losses.length, winRate:wins.length/rows.length, avgR:rows.reduce((s,r)=>s+r.rMultiple,0)/rows.length, pf:gl?gp/gl:(gp?null:0), medianR:median(rows.map(r=>r.rMultiple)), medianMFE:median(rows.map(r=>r.mfeR)), medianMAE:median(rows.map(r=>r.maeR)) };
}
function bucket(v, edges) { for (const e of edges) if (v<e) return `<${e}`; return `>=${edges.at(-1)}`; }
function group(rows, fn) { const m={}; for(const r of rows){const k=fn(r);(m[k]??=[]).push(r);} return Object.fromEntries(Object.entries(m).sort()); }
function featureComparison(rows) {
  const winners=rows.filter(r=>r.rMultiple>0), losers=rows.filter(r=>r.rMultiple<0);
  const fields=['qualityScore','targetR','riskDistance','mfeR','maeR'];
  return Object.fromEntries(fields.map(f=>[f,{winnerMedian:median(winners.map(r=>r[f]).filter(Number.isFinite)),loserMedian:median(losers.map(r=>r[f]).filter(Number.isFinite))}]));
}
for (const tf of ['1min','5min']) {
  const data=load(tf), rows=data.trades;
  const report={timeframe:tf,total:stats(rows),winnerVsLoser:featureComparison(rows),byQuality:group(rows,r=>`Q${r.qualityScore}`),byMFE:group(rows,r=>bucket(r.mfeR,[0.25,0.5,1,2,3,5,10])),byMAE:group(rows,r=>bucket(r.maeR,[0.25,0.5,1,1.5,2,3,5])),byTargetR:group(rows,r=>bucket(r.targetR,[1,2,3,5,10,20])),byRisk:group(rows,r=>bucket(r.riskDistance,[0.05,0.1,0.25,0.5,1,2,5])),bySessionDirection:group(rows,r=>`${r.direction}__${r.session}`),winnerProfile:stats(rows.filter(r=>r.rMultiple>0)),loserProfile:stats(rows.filter(r=>r.rMultiple<0))};
  fs.writeFileSync(path.join(outputDir,`${tf}.json`),JSON.stringify(report,null,2));
  console.log(`${tf}: winners=${report.winnerProfile.n} losers=${report.loserProfile.n}`);
  console.log(`  quality median W/L=${report.winnerVsLoser.qualityScore.winnerMedian}/${report.winnerVsLoser.qualityScore.loserMedian}`);
  console.log(`  MFE median W/L=${report.winnerVsLoser.mfeR.winnerMedian}/${report.winnerVsLoser.mfeR.loserMedian}`);
  console.log(`  MAE median W/L=${report.winnerVsLoser.maeR.winnerMedian}/${report.winnerVsLoser.maeR.loserMedian}`);
}
