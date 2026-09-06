import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-discriminative-anatomy/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-conditional-anatomy-replication');
const FEATURES = ['triggerReclaimToRange', 'triggerReclaimToCorrection'];
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function median(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = (a.length - 1) / 2;
  return p((a[Math.floor(m)] + a[Math.ceil(m)]) / 2);
}

function stats(rows) {
  const r = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter(x => x > 0), losses = r.filter(x => x < 0);
  const grossWin = wins.reduce((s,x)=>s+x,0);
  const grossLoss = -losses.reduce((s,x)=>s+x,0);
  return { n:r.length, WR:r.length ? p(wins.length/r.length) : null, avgR:r.length ? p(r.reduce((s,x)=>s+x,0)/r.length) : null, PF:grossLoss ? p(grossWin/grossLoss) : null };
}

function delta(rows, feature) {
  const normal = rows.filter(x=>x.classification==='NORMAL_WIN');
  const loss = rows.filter(x=>x.classification==='LOSS');
  const a=median(normal.map(x=>Number(x[feature]))), b=median(loss.map(x=>Number(x[feature])));
  return { normalN:normal.length, lossN:loss.length, normalMedian:a, lossMedian:b, delta:Number.isFinite(a)&&Number.isFinite(b)?p(a-b):null };
}

function spearman(rows, feature) {
  const pairs=rows.map(x=>({x:Number(x[feature]),y:Number(x.r)})).filter(z=>Number.isFinite(z.x)&&Number.isFinite(z.y));
  if(pairs.length<3) return null;
  const rank=a=>{const s=[...a].sort((u,v)=>u-v); return a.map(v=>{let lo=0;while(lo<s.length&&s[lo]<v)lo++;let hi=lo;while(hi<s.length&&s[hi]===v)hi++;return (lo+hi-1)/2;});};
  const rx=rank(pairs.map(z=>z.x)), ry=rank(pairs.map(z=>z.y));
  const mx=rx.reduce((s,v)=>s+v,0)/rx.length, my=ry.reduce((s,v)=>s+v,0)/ry.length;
  let num=0,dx=0,dy=0; for(let i=0;i<rx.length;i++){const a=rx[i]-mx,b=ry[i]-my;num+=a*b;dx+=a*a;dy+=b*b;}
  return dx&&dy?p(num/Math.sqrt(dx*dy)):null;
}

function windows(rows){
  const out=[];
  for(const split of ['DEV','VAL']){
    const scoped=rows.filter(x=>x.split===split).sort((a,b)=>new Date(a.time)-new Date(b.time));
    const mid=Math.ceil(scoped.length/2);
    for(const [i,w] of [scoped.slice(0,mid),scoped.slice(mid)].entries()){
      const nonExceptional=w.filter(x=>Number(x.r)<5);
      out.push({id:`${split}_H${i+1}`, n:w.length, outcome:stats(w), nonExceptionalOutcome:stats(nonExceptional), features:Object.fromEntries(FEATURES.map(f=>[f,{delta:delta(w,f),deltaNoExceptional:delta(nonExceptional,f),spearman:spearman(w,f),spearmanNoExceptional:spearman(nonExceptional,f)}]))});
    }
  }
  return out;
}

async function main(){
  const source=JSON.parse(await readFile(SOURCE,'utf8'));
  const rows=(source.cases??[]).filter(x=>x.split==='DEV'||x.split==='VAL');
  if(!rows.length) throw new Error('No DEV/VAL cases found');
  const ws=windows(rows);
  const result={strategy:'Strategy A / SP2L',mode:'RESEARCH_NY_SELL_PREENTRY_CONDITIONAL_ANATOMY_REPLICATION',timeframe:'5m',scope:{n:rows.length,dev:rows.filter(x=>x.split==='DEV').length,val:rows.filter(x=>x.split==='VAL').length,freshHoldoutExcluded:true,productionUntouched:true},methodology:{features:FEATURES,purpose:'Replication and sensitivity analysis of the two strongest remaining pre-entry descriptors after exceptional-winner attribution.',exceptionalDefinition:'r >= 5R',temporalWindows:'DEV and VAL chronological halves',comparisons:'NORMAL_WIN median minus LOSS median; Spearman feature vs R',noOptimization:true,noThresholdSearch:true,noNewTradingRules:true,holdoutLocked:true},windows:ws};
  await mkdir(OUT,{recursive:true}); await writeFile(resolve(OUT,'5m.json'),JSON.stringify(result,null,2));
  console.log(`PREENTRY_CONDITIONAL_ANATOMY_REPLICATION N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  for(const w of ws) console.log(`${w.id}: N=${w.n} avgR=${w.outcome.avgR??'-'} PF=${w.outcome.PF??'-'} | noExceptionalAvgR=${w.nonExceptionalOutcome.avgR??'-'} PF=${w.nonExceptionalOutcome.PF??'-'}`);
  for(const f of FEATURES){console.log(`${f}:`); for(const w of ws){const z=w.features[f]; console.log(`  ${w.id} delta=${z.delta.delta??'-'} deltaNoExceptional=${z.deltaNoExceptional.delta??'-'} spearman=${z.spearman??'-'} spearmanNoExceptional=${z.spearmanNoExceptional??'-'}`);}}
  console.log(`REPORT=${resolve(OUT,'5m.json')}`); console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}
await main();
