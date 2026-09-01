import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = process.cwd();
const OUT = resolve(ROOT, 'data/reports/strategy-a-spike-fixed-holdout');
const TF = ['1min', '5min'];
const HOLDOUT_CANDLES = Number(process.env.FRESH_HOLDOUT_CANDLES ?? 5000);
const SPIKE_LOOKBACK = 60;
const SPIKE_THRESHOLD = 2.0;
const REOPEN_MINUTES = [0, 15, 30, 45, 60];

const finite = x => Number.isFinite(Number(x));
const median = xs => { const a = xs.filter(finite).map(Number).sort((a,b)=>a-b); if (!a.length) return null; const m=Math.floor(a.length/2); return a.length%2?a[m]:(a[m-1]+a[m])/2; };
const mean = xs => { const a=xs.filter(finite).map(Number); return a.length?a.reduce((s,x)=>s+x,0)/a.length:null; };
const pf = xs => { const a=xs.filter(finite).map(Number); const g=a.filter(x=>x>0).reduce((s,x)=>s+x,0); const l=-a.filter(x=>x<0).reduce((s,x)=>s+x,0); return l?g/l:(g?Infinity:null); };
const maxDD = xs => { let eq=0, peak=0, dd=0; for(const x of xs.filter(finite).map(Number)){ eq+=x; peak=Math.max(peak,eq); dd=Math.max(dd,peak-eq); } return dd; };
const bootstrapDelta = (spike, non, iterations=5000) => {
  if (spike.length<2 || non.length<2) return null;
  let seed=0x9e3779b9;
  const rnd=()=>{ seed|=0; seed=(seed+0x6D2B79F5)|0; let t=Math.imul(seed^(seed>>>15),1|seed); t^=t+Math.imul(t^(t>>>7),61|t); return ((t^(t>>>14))>>>0)/4294967296; };
  const sampleMean=a=>{let s=0;for(let i=0;i<a.length;i++)s+=a[Math.floor(rnd()*a.length)];return s/a.length;};
  const d=[]; for(let i=0;i<iterations;i++) d.push(sampleMean(spike)-sampleMean(non));
  d.sort((a,b)=>a-b); return { lo:d[Math.floor(iterations*.025)], hi:d[Math.floor(iterations*.975)] };
};
const resolved = b => (b.trades ?? []).filter(t => finite(t.rMultiple));
const load = async tf => JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${tf}.json`), 'utf8'));
const loadCandles = async tf => {
  const candidates=[`data/${tf}.json`,`data/candles/${tf}.json`,`data/market/${tf}.json`,`data/raw/${tf}.json`];
  for(const p of candidates){try{return JSON.parse(await readFile(resolve(ROOT,p),'utf8'));}catch{}}
  throw new Error(`${tf}: candle dataset not found in standard paths`);
};
const run = async tf => {
  const baseline=await load(tf); const trades=resolved(baseline);
  const candles=await loadCandles(tf);
  if (!Array.isArray(candles) || candles.length < HOLDOUT_CANDLES) throw new Error(`${tf}: insufficient candles for ${HOLDOUT_CANDLES}-candle holdout`);
  const split=candles.length-HOLDOUT_CANDLES;
  const holdoutStart=candles[split]?.timestamp;
  const holdoutEnd=candles[candles.length-1]?.timestamp;
  const holdoutTrades=trades.filter(t => String(t.entryTimestamp ?? t.entryTime ?? t.timestamp ?? '') >= String(holdoutStart));
  const priorTR=[]; const spikeByTs=new Map();
  for(let i=0;i<candles.length;i++){
    const c=candles[i]; const tr=Math.max(Number(c.high)-Number(c.low), Math.abs(Number(c.high)-Number(c.open)), Math.abs(Number(c.low)-Number(c.open)));
    const base=median(priorTR.slice(-SPIKE_LOOKBACK));
    if(base) spikeByTs.set(String(c.timestamp), tr/base>=SPIKE_THRESHOLD);
    priorTR.push(tr);
  }
  const eligible=holdoutTrades.filter(t=>t.entryTimestamp ?? t.entryTime ?? t.timestamp).filter(t=>{const ts=String(t.entryTimestamp ?? t.entryTime ?? t.timestamp); return ts>=String(holdoutStart)&&ts<=String(holdoutEnd);});
  const priorSpike=(t, mins)=>{const ts=String(t.entryTimestamp ?? t.entryTime ?? t.timestamp); const idx=candles.findIndex(c=>String(c.timestamp)===ts); if(idx<0)return null; for(let j=idx-1;j>=0;j--){const a=new Date(candles[j].timestamp).getTime(), b=new Date(candles[idx].timestamp).getTime(); if((b-a)/60000>=mins)return spikeByTs.get(String(candles[j].timestamp))??false;} return false;};
  const overall=eligible.map(t=>Number(t.rMultiple)).filter(Number.isFinite);
  const scenarios={};
  for(const mins of REOPEN_MINUTES){
    const ex=eligible.filter(t=>{const ts=String(t.entryTimestamp ?? t.entryTime ?? t.timestamp); const d=new Date(ts); return d.getUTCDay()===0 && d.getUTCHours()===22 && d.getUTCMinutes()<=mins;});
    const pool=eligible.filter(t=>!ex.includes(t));
    const spike=pool.filter(t=>priorSpike(t,0)===true).map(t=>Number(t.rMultiple)).filter(Number.isFinite);
    const non=pool.filter(t=>priorSpike(t,0)===false).map(t=>Number(t.rMultiple)).filter(Number.isFinite);
    scenarios[mins]={excluded:ex.length,n:pool.length,spike:{n:spike.length,avgR:mean(spike),pf:pf(spike),totalR:spike.reduce((s,x)=>s+x,0)},nonSpike:{n:non.length,avgR:mean(non),pf:pf(non),totalR:non.reduce((s,x)=>s+x,0)},deltaR:mean(spike)-mean(non),bootstrap95:bootstrapDelta(spike,non)};
  }
  const report={timeframe:tf,rule:{threshold:SPIKE_THRESHOLD,lookbackBars:SPIKE_LOOKBACK,holdoutCandles:HOLDOUT_CANDLES},holdout:{start:holdoutStart,end:holdoutEnd,candles:HOLDOUT_CANDLES,baselineResolvedTrades:trades.length,holdoutTrades:eligible.length,overall:{n:overall.length,avgR:mean(overall),pf:pf(overall),totalR:overall.reduce((s,x)=>s+x,0),maxDD:maxDD(overall)}},scenarios};
  await mkdir(OUT,{recursive:true}); const out=resolve(OUT,`${tf}.json`); await writeFile(out,JSON.stringify(report,null,2)+'\n');
  console.log(`\n${tf}: holdout=${holdoutStart} -> ${holdoutEnd} trades=${eligible.length} overallAvgR=${mean(overall)?.toFixed(4)??'n/a'}`);
  for(const [m,x] of Object.entries(scenarios)){const ci=x.bootstrap95; console.log(`${m}m excluded=${x.excluded} spikeN=${x.spike.n} spikeAvgR=${x.spike.avgR?.toFixed(4)??'n/a'} nonN=${x.nonSpike.n} nonAvgR=${x.nonSpike.avgR?.toFixed(4)??'n/a'} deltaR=${x.deltaR?.toFixed(4)??'n/a'} CI=[${ci?ci.lo.toFixed(4):'n/a'},${ci?ci.hi.toFixed(4):'n/a'}]`)}
  console.log(`Report -> ${out}`);
};
for(const tf of TF) await run(tf);
