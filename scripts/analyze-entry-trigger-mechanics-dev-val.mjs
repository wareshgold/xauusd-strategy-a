import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PATH_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-trigger-mechanics-dev-val');
const TOTAL_CANDLES = 15000;
const FRESH_HOLDOUT_CANDLES = 5000;
const PRE_HOLDOUT_CANDLES = 10000;
const DEV_CANDLES = 6000;
const MIN_N = 10;

function stats(rows) {
  const rs = rows.map(r => Number(r.r)).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0), losses = rs.filter(r => r < 0);
  const gp = wins.reduce((a,b)=>a+b,0), gl = -losses.reduce((a,b)=>a+b,0);
  let eq=0, peak=0, dd=0, streak=0, maxCL=0;
  for (const r of rs) { eq += r; peak=Math.max(peak,eq); dd=Math.max(dd,peak-eq); streak=r<0?streak+1:0; maxCL=Math.max(maxCL,streak); }
  return { n:rs.length, wins:wins.length, losses:losses.length, winRate:rs.length?wins.length/rs.length:0, avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0, totalR:rs.reduce((a,b)=>a+b,0), PF:gl?gp/gl:null, maxDD:dd, maxCL };
}
function key(c) { return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`; }
function summarizeHypothesis(name, dev, val, baselineDev, baselineVal) {
  const d=stats(dev), v=stats(val);
  return { name, DEV:d, VAL:v, devDeltaAvgR:d.avgR-baselineDev.avgR, valDeltaAvgR:v.avgR-baselineVal.avgR,
    eligible:d.n>=MIN_N&&v.n>=MIN_N,
    devPositive:d.avgR>0&&d.PF!==null&&d.PF>=1,
    valPositive:v.avgR>0&&v.PF!==null&&v.PF>=1,
    pass:d.n>=MIN_N&&v.n>=MIN_N&&d.avgR>0&&v.avgR>0&&d.PF>=1&&v.PF>=1 };
}
function cells(rows, predicate) { return rows.filter(predicate); }

async function run(timeframe) {
  const candles=(JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles??[]);
  if(candles.length<TOTAL_CANDLES) throw new Error(`${timeframe}: expected ${TOTAL_CANDLES} candles, found ${candles.length}`);
  const path=JSON.parse(await readFile(resolve(PATH_DIR,`${timeframe}.json`),'utf8'));
  const base=JSON.parse(await readFile(resolve(BASE_DIR,`${timeframe}.json`),'utf8'));
  const freshCut=candles[PRE_HOLDOUT_CANDLES]?.timestamp, devCut=candles[DEV_CANDLES]?.timestamp;
  if(!freshCut||!devCut) throw new Error(`${timeframe}: missing split timestamps`);
  const baseTrades=(base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<new Date(freshCut));
  const baseMap=new Map(baseTrades.map(t=>[`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`,t]));
  const selected=(path.baselineSelected??[]).filter(c=>c.index<PRE_HOLDOUT_CANDLES);
  const joined=[];
  for(const c of selected){const t=baseMap.get(key(c));if(t)joined.push({...c,r:Number(t.rMultiple),result:t.result,entryTime:t.entryTime});}
  const dev=joined.filter(r=>new Date(r.entryTime)<new Date(devCut));
  const val=joined.filter(r=>new Date(r.entryTime)>=new Date(devCut)&&new Date(r.entryTime)<new Date(freshCut));
  const baselineDev=stats(dev), baselineVal=stats(val);
  const hypotheses=[];
  const add=(name,p)=>hypotheses.push(summarizeHypothesis(name,cells(dev,p),cells(val,p),baselineDev,baselineVal));
  add('triggerDelay <= 1',r=>r.triggerDelay<=1);
  add('triggerDelay >= 2',r=>r.triggerDelay>=2);
  add('triggerExtension < 10%',r=>r.triggerExtension<0.10);
  add('triggerExtension >= 10%',r=>r.triggerExtension>=0.10);
  add('correctionDepth < 25%',r=>r.correctionDepth<0.25);
  add('correctionDepth >= 25%',r=>r.correctionDepth>=0.25);
  add('stopToImpulse < 25%',r=>r.stopToImpulse<0.25);
  add('stopToImpulse 25-50%',r=>r.stopToImpulse>=0.25&&r.stopToImpulse<0.50);
  add('stopToImpulse >= 50%',r=>r.stopToImpulse>=0.50);
  const report={strategy:'Strategy A',mode:'ENTRY_TRIGGER_MECHANICS_DEV_VAL',timeframe,scope:{totalCandles:candles.length,preHoldoutCandles:PRE_HOLDOUT_CANDLES,freshHoldoutCandles:FRESH_HOLDOUT_CANDLES,devCandles:DEV_CANDLES,valCandles:PRE_HOLDOUT_CANDLES-DEV_CANDLES},methodology:{outcomeSource:'canonical baseline backtest; no outcome recomputation',featureSource:'direct baseline-path forensic',split:'chronological by entryTime',minN:MIN_N,hypothesesFrozen:true,valNotUsedForThresholdSelection:true,productionUntouched:true},parity:{baselineResolvedPreHoldout:baseTrades.length,joinedForensics:joined.length,baselineMissing:baseTrades.filter(t=>!joined.some(r=>key(r)===`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`)).length},baseline:{DEV:baselineDev,VAL:baselineVal},hypotheses,decision:'Research attribution only. No hypothesis is promoted automatically; any candidate passing both DEV and VAL requires a separately pre-registered single fresh-holdout confirmation.'};
  await mkdir(OUT_DIR,{recursive:true}); const out=resolve(OUT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: joined=${joined.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${baselineDev.avgR.toFixed(4)} baselineVAL=${baselineVal.avgR.toFixed(4)}`);
  for(const h of hypotheses) console.log(`  ${h.name}: DEV n=${h.DEV.n} avgR=${h.DEV.avgR.toFixed(4)} PF=${h.DEV.PF?.toFixed(3)??'n/a'} | VAL n=${h.VAL.n} avgR=${h.VAL.avgR.toFixed(4)} PF=${h.VAL.PF?.toFixed(3)??'n/a'} | pass=${h.pass}`);
  console.log(`Report -> ${out}`);
}
for(const tf of ['1min','5min']) await run(tf);
