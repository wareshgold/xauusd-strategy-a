import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const PRE = 10000;
const DEV_END = 5999;
const CFG = { breakoutLookback: 5, followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true }, spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 } };
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 }, { name: 'DEV_2', start: 2000, end: 3999 }, { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 }, { name: 'VAL_2', start: 8000, end: 9999 },
];
const round = x => Number.isFinite(x) ? Number(x.toFixed(6)) : null;
const pct = x => Number.isFinite(x) ? Number((x * 100).toFixed(4)) : null;
const median = values => { const v = values.filter(Number.isFinite).sort((a,b)=>a-b); if(!v.length)return null; const m=Math.floor(v.length/2); return v.length%2?v[m]:(v[m-1]+v[m])/2; };
const stats = rows => { const n=rows.length,totalR=rows.reduce((s,x)=>s+x.r,0),wins=rows.filter(x=>x.r>0),losses=rows.filter(x=>x.r<=0),gw=wins.reduce((s,x)=>s+x.r,0),gl=-losses.reduce((s,x)=>s+x.r,0); return {n,avgR:n?totalR/n:null,PF:gl?gw/gl:null,WR:n?wins.length/n:null,totalR}; };
const bucket=(rows,key)=>Object.fromEntries([...new Set(rows.map(x=>x[key]))].sort().map(v=>[v,stats(rows.filter(x=>x[key]===v))]));
const consecutiveLosses=rows=>{let c=0,m=0;for(const x of rows){if(x.r<=0){c++;m=Math.max(m,c)}else c=0}return m};
const session=timestamp=>{const d=new Date(timestamp),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=960&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION'};

function replay(candles, entryIndex) {
  const view=candles.slice(0,entryIndex+1); if(view.length<60)return null;
  const breakouts=detectBreakout(view,CFG.breakoutLookback),followThrough=detectFollowThrough(view,breakouts,CFG.followThrough),spikes=detectSpikeCandidates(view,breakouts,followThrough,CFG.spike);
  for(const spike of spikes.candidates){
    if(spike.endIndex>=entryIndex)continue;
    const correction=detectFirstCorrection(view,spike); if(!correction||correction.correctionExtremeIndex>=entryIndex)continue;
    const trigger=detectEntryTrigger(view,correction); if(!trigger||trigger.index!==entryIndex)continue;
    const breakout=breakouts.find(x=>x.index===spike.breakoutIndex&&x.direction===spike.direction),follow=followThrough.find(x=>x.breakoutIndex===spike.breakoutIndex&&x.direction===spike.direction);
    if(breakout&&follow)return{spike,correction,trigger,breakout,follow};
  }
  return null;
}
function path(candles,entryIndex,entryPrice,stopLoss,takeProfit,direction){
  const risk=Math.abs(entryPrice-stopLoss); if(!Number.isFinite(risk)||risk<=0)return{maeR:null,mfeR:null,firstHalfAdverse:null,firstHalfFavorable:null,first1R:null,hitSL:null,hitTP:null};
  let maeR=0,mfeR=0,firstHalfAdverse=null,firstHalfFavorable=null,first1R=null,hitSL=null,hitTP=null;
  for(let j=entryIndex+1;j<=Math.min(candles.length-1,entryIndex+500);j++){
    const c=candles[j],adverse=direction==='BUY'?(entryPrice-c.low)/risk:(c.high-entryPrice)/risk,favorable=direction==='BUY'?(c.high-entryPrice)/risk:(entryPrice-c.low)/risk;
    maeR=Math.max(maeR,adverse);mfeR=Math.max(mfeR,favorable);
    if(firstHalfAdverse===null&&adverse>=.5)firstHalfAdverse=j-entryIndex;if(firstHalfFavorable===null&&favorable>=.5)firstHalfFavorable=j-entryIndex;if(first1R===null&&favorable>=1)first1R=j-entryIndex;
    if(hitSL===null&&(direction==='BUY'?c.low<=stopLoss:c.high>=stopLoss))hitSL=j-entryIndex;if(hitTP===null&&(direction==='BUY'?c.high>=takeProfit:c.low<=takeProfit))hitTP=j-entryIndex;if(hitSL!==null&&hitTP!==null)break;
  }
  return{maeR,mfeR,firstHalfAdverse,firstHalfFavorable,first1R,hitSL,hitTP};
}

async function main(){
  const [base,candleData]=await Promise.all([readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'),readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')]);
  const baseline=JSON.parse(base),candles=JSON.parse(candleData).candles??[];
  const raw=(baseline.trades??[]).filter(t=>{const i=Number(t.entryIndex);return Number.isInteger(i)&&i<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL')});
  const rows=[];let mismatch=0,missingCanonicalTimestamp=0;
  for(const t of raw){
    const i=Number(t.entryIndex),r=replay(candles,i); if(!r){mismatch++;continue;}
    if(r.trigger.timestamp!==t.entryTime||r.trigger.direction!==t.direction){mismatch++;continue;}
    const p=path(candles,i,Number(t.entry),Number(t.stopLoss),Number(t.tp1),t.direction),rr=Number(t.rMultiple);
    rows.push({entryIndex:i,entryTime:t.entryTime,direction:t.direction,session:session(t.entryTime),split:i<=DEV_END?'DEV':'VAL',window:WINDOWS.find(w=>i>=w.start&&i<=w.end)?.name??'UNKNOWN',r:rr,exceptional:rr>=5,maeR:p.maeR,mfeR:p.mfeR,firstHalfAdverse:p.firstHalfAdverse,firstHalfFavorable:p.firstHalfFavorable,first1R:p.first1R,hitSL:p.hitSL,hitTP:p.hitTP,outcome:rr>0?'WIN':'LOSS'});
  }
  if(mismatch!==0||rows.length!==raw.length)throw new Error(`canonical replay integrity failure: raw=${raw.length} actual=${rows.length} mismatch=${mismatch}`);
  const losses=rows.filter(x=>x.r<=0),wins=rows.filter(x=>x.r>0);
  const buckets={direction:bucket(rows,'direction'),session:bucket(rows,'session'),outcome:bucket(rows,'outcome'),window:bucket(rows,'window'),split:bucket(rows,'split')};
  const failureModes={losses:stats(losses),wins:stats(wins),lossMAE:{medianR:median(losses.map(x=>x.maeR)),p50:losses.filter(x=>x.maeR>=.5).length/losses.length,p75:losses.filter(x=>x.maeR>=.75).length/losses.length,p90:losses.filter(x=>x.maeR>=.9).length/losses.length},lossMFE:{medianR:median(losses.map(x=>x.mfeR)),reachedHalf:losses.filter(x=>x.mfeR>=.5).length/losses.length,reached1R:losses.filter(x=>x.mfeR>=1).length/losses.length,reached2R:losses.filter(x=>x.mfeR>=2).length/losses.length},winsMAE:{medianR:median(wins.map(x=>x.maeR))},winsMFE:{medianR:median(wins.map(x=>x.mfeR))},pathTiming:{lossReachedHalfAdverse:losses.filter(x=>x.firstHalfAdverse!==null).length/losses.length,lossReachedHalfFavorable:losses.filter(x=>x.firstHalfFavorable!==null).length/losses.length,lossReached1R:losses.filter(x=>x.first1R!==null).length/losses.length,winReached1R:wins.filter(x=>x.first1R!==null).length/wins.length,winHitSL:wins.filter(x=>x.hitSL!==null).length/wins.length,winHitTP:wins.filter(x=>x.hitTP!==null).length/wins.length},consecutiveLosses:consecutiveLosses(rows)};
  const windowFailure=Object.fromEntries(WINDOWS.map(w=>{const wr=rows.filter(x=>x.window===w.name),wl=wr.filter(x=>x.r<=0);return[w.name,{overall:stats(wr),losses:stats(wl),wins:stats(wr.filter(x=>x.r>0)),lossMAEmedianR:median(wl.map(x=>x.maeR)),lossMFEmedianR:median(wl.map(x=>x.mfeR)),lossReachedHalfAdverse:wl.length?wl.filter(x=>x.firstHalfAdverse!==null).length/wl.length:null,lossReachedHalfFavorable:wl.length?wl.filter(x=>x.firstHalfFavorable!==null).length/wl.length:null,lossReached1R:wl.length?wl.filter(x=>x.first1R!==null).length/wl.length:null,maxConsecutiveLosses:consecutiveLosses(wr)}]}));
  const result={strategy:'Strategy A / SP2L',mode:'PHASE_17_BASELINE_FAILURE_DECOMPOSITION',timeframe:'5min',scope:{rawBaselinePre:raw.length,canonicalReplayed:rows.length,dev:rows.filter(x=>x.split==='DEV').length,val:rows.filter(x=>x.split==='VAL').length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:221,rawBaselinePre:raw.length,canonicalReplayed:rows.length,mismatch,missingCanonicalTimestamp,deterministicRerunRequired:true},methodology:{purpose:'Descriptive decomposition of baseline trade failures and path behavior; identify common mechanical failure modes without optimizing or selecting thresholds.',pathHorizonBars:500,metrics:['MAE in R','MFE in R','time-to-0.5R adverse','time-to-0.5R favorable','time-to-1R favorable','SL/TP path hits','fixed chronological windows','direction/session splits','maximum consecutive losses'],noOptimization:true,noThresholdSearch:true,noNewTradingRules:true,noFreshHoldoutAccess:true},overall:stats(rows),buckets,failureModes,windowFailure,cases:rows};
  const out=resolve(ROOT,'data/reports/strategy-a-phase17-baseline-failure-decomposition');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
  const fmt=s=>`N=${s.n} avgR=${round(s.avgR)} PF=${round(s.PF)} WR=${pct(s.WR)}% totalR=${round(s.totalR)}`;
  console.log(`PHASE_17_BASELINE_FAILURE_DECOMPOSITION 5min N=${rows.length} DEV=${rows.filter(x=>x.split==='DEV').length} VAL=${rows.filter(x=>x.split==='VAL').length} FRESH=LOCKED`);
  console.log(`INTEGRITY expected=${result.integrity.expectedCanonical} raw=${raw.length} actual=${rows.length} mismatch=${mismatch} noReplay=0 missingCanonicalTimestamp=${missingCanonicalTimestamp}`);
  console.log(`OVERALL ${fmt(result.overall)}`);console.log(`LOSSES ${fmt(failureModes.losses)} | WINS ${fmt(failureModes.wins)}`);
  console.log(`MAE losses median=${round(failureModes.lossMAE.medianR)}R >=0.5R=${pct(failureModes.lossMAE.p50)}% >=0.75R=${pct(failureModes.lossMAE.p75)}% >=0.9R=${pct(failureModes.lossMAE.p90)}%`);
  console.log(`MFE losses median=${round(failureModes.lossMFE.medianR)}R reached0.5R=${pct(failureModes.lossMFE.reachedHalf)}% reached1R=${pct(failureModes.lossMFE.reached1R)}% reached2R=${pct(failureModes.lossMFE.reached2R)}%`);
  console.log(`PATH losses: halfAdv=${pct(failureModes.pathTiming.lossReachedHalfAdverse)}% halfFav=${pct(failureModes.pathTiming.lossReachedHalfFavorable)}% 1R=${pct(failureModes.pathTiming.lossReached1R)}% | wins: 1R=${pct(failureModes.pathTiming.winReached1R)}%`);
  console.log(`MAX_CONSECUTIVE_LOSSES=${failureModes.consecutiveLosses}`);console.log('=== WINDOWS ===');for(const[k,v]of Object.entries(windowFailure))console.log(`${k}: ${fmt(v.overall)} lossMAE=${round(v.lossMAEmedianR)}R lossMFE=${round(v.lossMFEmedianR)}R lossHalfAdv=${pct(v.lossReachedHalfAdverse)}% lossHalfFav=${pct(v.lossReachedHalfFavorable)}% loss1R=${pct(v.lossReached1R)}% maxLossStreak=${v.maxConsecutiveLosses}`);
  console.log(`REPORT=${resolve(out,'5min.json')}`);console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
main().catch(e=>{console.error(e);process.exit(1)});
