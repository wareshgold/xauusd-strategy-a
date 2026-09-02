import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PATH_DIR=resolve(ROOT,'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR=resolve(ROOT,'data/reports/strategy-a-baseline');
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-entry-trigger-immediate-failure');
const PRE=10000;

function metrics(rows){
  const rs=rows.map(x=>Number(x.r)).filter(Number.isFinite); const wins=rs.filter(x=>x>0), losses=rs.filter(x=>x<0);
  const gp=wins.reduce((a,b)=>a+b,0), gl=-losses.reduce((a,b)=>a+b,0);
  let dd=0,peak=0,eq=0,cl=0,maxCl=0; for(const r of rs){eq+=r;peak=Math.max(peak,eq);dd=Math.max(dd,peak-eq);cl=r<0?cl+1:0;maxCl=Math.max(maxCl,cl);}
  return {n:rs.length,wins:wins.length,losses:losses.length,winRate:rs.length?wins.length/rs.length:0,avgR:rs.length?eq/rs.length:0,totalR:eq,PF:gl?gp/gl:null,maxDD:dd,maxCL:maxCl};
}
function key(c){return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`}
function bucket(v, cuts){if(!Number.isFinite(v))return 'n/a'; for(const [name,max] of cuts) if(v<max)return name; return cuts[cuts.length-1][0]+'+';}
function q(v,p){const a=v.filter(Number.isFinite).sort((x,y)=>x-y);return a.length?a[Math.min(a.length-1,Math.floor((a.length-1)*p))]:null}
function pathStats(row,candles){
  const entry=Number(row.index), dir=row.direction, e=Number(row.entry), sl=Number(row.stopLoss), risk=Math.abs(e-sl), impulse=Math.max(Number(row.spikeSize),1e-9);
  const horizons=[1,2,3,5,10]; const out={};
  for(const n of horizons){let mae=0,mfe=0,inside=false,stopHit=false,tpHit=false; const end=Math.min(candles.length-1,entry+n); for(let j=entry+1;j<=end;j++){const c=candles[j]; const h=Number(c.high),l=Number(c.low); if(dir==='BUY'){mae=Math.max(mae,(e-l)/risk);mfe=Math.max(mfe,(h-e)/risk);if(l<=sl)stopHit=true;if(h>=Number(row.tp1))tpHit=true;}else{mae=Math.max(mae,(h-e)/risk);mfe=Math.max(mfe,(e-l)/risk);if(h>=sl)stopHit=true;if(l<=Number(row.tp1))tpHit=true;} if((dir==='BUY'&&Number(c.close)<Number(row.triggerLevel))||(dir==='SELL'&&Number(c.close)>Number(row.triggerLevel)))inside=true;} out[`h${n}`]={maeR:mae,mfeR:mfe,stopHit,tp1Hit:tpHit,reenteredTriggerZone:inside};}
  return out;
}
function aggregate(rows){
  const groups={}; const add=(name,subset)=>{groups[name]=metrics(subset);};
  add('all',rows);
  for(const h of [1,2,3,5,10]){
    add(`MAE_${h}bars_ge_0.25R`,rows.filter(r=>r.path[`h${h}`].maeR>=.25));
    add(`MAE_${h}bars_ge_0.5R`,rows.filter(r=>r.path[`h${h}`].maeR>=.5));
    add(`MAE_${h}bars_ge_1R`,rows.filter(r=>r.path[`h${h}`].maeR>=1));
    add(`MFE_${h}bars_ge_0.25R`,rows.filter(r=>r.path[`h${h}`].mfeR>=.25));
    add(`reentered_${h}bars`,rows.filter(r=>r.path[`h${h}`].reenteredTriggerZone));
  }
  add('delay_1',rows.filter(r=>Number(r.triggerDelay)===1)); add('delay_2plus',rows.filter(r=>Number(r.triggerDelay)>=2));
  return groups;
}
async function run(timeframe){
  const candles=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`),'utf8')).candles;
  const path=JSON.parse(await readFile(resolve(PATH_DIR,`${timeframe}.json`),'utf8'));
  const base=JSON.parse(await readFile(resolve(BASE_DIR,`${timeframe}.json`),'utf8'));
  const cutoff=candles[PRE]?.timestamp;
  const trades=(base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&new Date(t.entryTime)<new Date(cutoff));
  const map=new Map(trades.map(t=>[key({index:t.entryIndex,direction:t.direction,entry:t.entry,stopLoss:t.stopLoss,tp1:t.tp1}),t]));
  const rows=[];
  for(const c of (path.baselineSelected??[]).filter(c=>c.index<PRE)){const t=map.get(key(c));if(t)rows.push({...c,r:Number(t.rMultiple),result:t.result});}
  for(const r of rows) r.path=pathStats(r,candles);
  const by={};
  for(const h of [1,2,3,5,10]){
    by[`h${h}`]={all:metrics(rows),winners:metrics(rows.filter(r=>r.r>0)),losers:metrics(rows.filter(r=>r.r<0)),maeBuckets:{'<0.25R':metrics(rows.filter(r=>r.path[`h${h}`].maeR<.25)), '0.25-0.5R':metrics(rows.filter(r=>r.path[`h${h}`].maeR>=.25&&r.path[`h${h}`].maeR<.5)), '0.5-1R':metrics(rows.filter(r=>r.path[`h${h}`].maeR>=.5&&r.path[`h${h}`].maeR<1)), '1R+':metrics(rows.filter(r=>r.path[`h${h}`].maeR>=1))}, immediateFailure:{stopHit:metrics(rows.filter(r=>r.path[`h${h}`].stopHit)), reenteredTriggerZone:metrics(rows.filter(r=>r.path[`h${h}`].reenteredTriggerZone))}};
  }
  const report={strategy:'Strategy A',mode:'ENTRY_TRIGGER_IMMEDIATE_FAILURE_PREHOLDOUT',timeframe,candles:candles.length,scope:{preHoldoutCandles:PRE,freshHoldoutExcluded:true},methodology:{outcomeSource:'canonical baseline',pathSource:'visible candles strictly after baseline entry',horizons:[1,2,3,5,10],purpose:'diagnostic immediate post-entry failure attribution only; no threshold optimization; no production change'},baseline:metrics(rows),horizonBreakdown:by,delayGroups:{delay1:metrics(rows.filter(r=>Number(r.triggerDelay)===1)),delay2plus:metrics(rows.filter(r=>Number(r.triggerDelay)>=2))}};
  await mkdir(OUT_DIR,{recursive:true}); const out=resolve(OUT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: n=${rows.length} avgR=${report.baseline.avgR.toFixed(4)} PF=${report.baseline.PF?.toFixed(4)??'n/a'}`);
  for(const h of [1,2,3,5,10]){const x=by[`h${h}`]; console.log(`  h${h}: MAE<.25 n=${x.maeBuckets['<0.25R'].n} avgR=${x.maeBuckets['<0.25R'].avgR.toFixed(4)} | .25-.5 n=${x.maeBuckets['0.25-0.5R'].n} avgR=${x.maeBuckets['0.25-0.5R'].avgR.toFixed(4)} | .5-1 n=${x.maeBuckets['0.5-1R'].n} avgR=${x.maeBuckets['0.5-1R'].avgR.toFixed(4)} | 1R+ n=${x.maeBuckets['1R+'].n} avgR=${x.maeBuckets['1R+'].avgR.toFixed(4)} | reentered n=${x.immediateFailure.reenteredTriggerZone.n} avgR=${x.immediateFailure.reenteredTriggerZone.avgR.toFixed(4)}`);}
  console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
