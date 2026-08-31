import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const inputDir = path.join(root, 'data', 'reports', 'strategy-a-trade-forensics');
const outputDir = path.join(root, 'data', 'reports', 'strategy-a-forensic-segments');
fs.mkdirSync(outputDir, { recursive: true });

function load(tf) {
  const p = path.join(inputDir, `${tf}.json`);
  return JSON.parse(JSON.parse(fs.readFileSync(p, 'utf8')).content ?? fs.readFileSync(p, 'utf8'));
}

function pf(rows) {
  const grossWin = rows.filter(x => x.rMultiple > 0).reduce((s,x) => s+x.rMultiple,0);
  const grossLoss = -rows.filter(x => x.rMultiple < 0).reduce((s,x) => s+x.rMultiple,0);
  return grossLoss === 0 ? (grossWin ? Infinity : 0) : grossWin/grossLoss;
}
function summary(rows) {
  if (!rows.length) return { n:0 };
  return { n:rows.length, wins:rows.filter(x=>x.rMultiple>0).length, winRate:rows.filter(x=>x.rMultiple>0).length/rows.length, avgR:rows.reduce((s,x)=>s+x.rMultiple,0)/rows.length, pf:pf(rows), medianMFE:median(rows.map(x=>x.mfeR)), medianMAE:median(rows.map(x=>x.maeR)) };
}
function median(a) { if(!a.length)return null; const b=[...a].sort((x,y)=>x-y); const m=Math.floor(b.length/2); return b.length%2?b[m]:(b[m-1]+b[m])/2; }
function bucket(v, edges) { for (let i=0;i<edges.length;i++) if(v < edges[i]) return `<${edges[i]}`; return `>=${edges.at(-1)}`; }
function segment(rows, keyFn) { const m={}; for(const r of rows){const k=keyFn(r);(m[k]??=[]).push(r);} return Object.fromEntries(Object.entries(m).sort()); }

for (const tf of ['1min','5min']) {
  const data=load(tf); const rows=data.trades;
  const report={timeframe:tf,total:summary(rows),byQuality:segment(rows,r=>`Q${r.qualityScore}`),byTargetR:segment(rows,r=>bucket(r.targetR,[1,2,3,5,10])),byRisk:segment(rows,r=>bucket(r.riskDistance,[0.05,0.1,0.25,0.5,1,2,5])),byMFE:segment(rows,r=>bucket(r.mfeR,[0,0.5,1,2,3,5,10])),byMAE:segment(rows,r=>bucket(r.maeR,[0.25,0.5,1,1.5,2,3,5])),bySessionDirection:segment(rows,r=>`${r.direction}__${r.session}`),largeWinners:{gt5:summary(rows.filter(r=>r.rMultiple>5)),gt10:summary(rows.filter(r=>r.rMultiple>10)),tinyRisk:summary(rows.filter(r=>r.riskDistance<0.1)),gt5NonTiny:summary(rows.filter(r=>r.rMultiple>5&&r.riskDistance>=0.1)),gt10NonTiny:summary(rows.filter(r=>r.rMultiple>10&&r.riskDistance>=0.1))}};
  fs.writeFileSync(path.join(outputDir,`${tf}.json`),JSON.stringify(report,null,2));
  console.log(`${tf}: total=${rows.length} >5R=${rows.filter(r=>r.rMultiple>5).length} >10R=${rows.filter(r=>r.rMultiple>10).length} tinyRisk<0.1=${rows.filter(r=>r.riskDistance<0.1).length}`);
  console.log(`  >5R nonTiny=${report.largeWinners.gt5NonTiny.n} avgR=${report.largeWinners.gt5NonTiny.avgR?.toFixed(4)} PF=${report.largeWinners.gt5NonTiny.pf?.toFixed(4)}`);
  console.log(`  >10R nonTiny=${report.largeWinners.gt10NonTiny.n} avgR=${report.largeWinners.gt10NonTiny.avgR?.toFixed(4)} PF=${report.largeWinners.gt10NonTiny.pf?.toFixed(4)}`);
}
