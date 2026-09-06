import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT=resolve(process.cwd()),PRE=10000,DEV=6000;
const CFG={breakoutLookback:5,followThrough:{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true},spike:{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}};
const WINDOWS=[
  {name:'DEV_1',start:0,end:1999},
  {name:'DEV_2',start:2000,end:3999},
  {name:'DEV_3',start:4000,end:5999},
  {name:'VAL_1',start:6000,end:7999},
  {name:'VAL_2',start:8000,end:9999}
];
const round=n=>Number.isFinite(n)?Number(n.toFixed(6)):null;
const pct=n=>Number.isFinite(n)?Number((n*100).toFixed(4)):null;
const stats=rows=>{const r=rows.filter(x=>Number.isFinite(x.r)),w=r.filter(x=>x.r>0),l=r.filter(x=>x.r<=0),gw=w.reduce((s,x)=>s+x.r,0),gl=l.reduce((s,x)=>s+Math.abs(x.r),0);return{n:r.length,wins:w.length,losses:l.length,WR:r.length?w.length/r.length:null,avgR:r.length?r.reduce((s,x)=>s+x.r,0)/r.length:null,PF:gl?gw/gl:null,totalR:r.reduce((s,x)=>s+x.r,0)};};
const byR=(rows,desc=true)=>[...rows].sort((a,b)=>desc?b.r-a.r:a.r-b.r);
const withoutTop=(rows,k)=>{const drop=new Set(byR(rows).slice(0,k).map(x=>x.entryIndex));return rows.filter(x=>!drop.has(x.entryIndex));};
const concentration=(rows,k)=>{const s=stats(rows),top=byR(rows).slice(0,k).reduce((a,x)=>a+x.r,0);return{sTotal:s.totalR,topR:top,topShare:s.totalR?top/s.totalR:null};};
function replay(c,i){const v=c.slice(0,i+1);if(v.length<60)return null;const bo=detectBreakout(v,CFG.breakoutLookback),ft=detectFollowThrough(v,bo,CFG.followThrough),sp=detectSpikeCandidates(v,bo,ft,CFG.spike);for(const s of sp.candidates){if(s.endIndex>=i)continue;const co=detectFirstCorrection(v,s);if(!co||co.correctionExtremeIndex>=i)continue;const tr=detectEntryTrigger(v,co);if(!tr||tr.index!==i)continue;const b=bo.find(x=>x.index===s.breakoutIndex&&x.direction===s.direction),f=ft.find(x=>x.breakoutIndex===s.breakoutIndex&&x.direction===s.direction);if(b&&f)return{tr};}return null;}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();return m>=420&&m<960?'LONDON':m>=960&&m<1320?'NEW_YORK':'OUTSIDE';}
async function main(){
 const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
 const candles=(JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[]);
 const raw=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
 const rows=[];let mismatch=0;
 for(const t of raw){const i=Number(t.entryIndex),x=replay(candles,i);if(!x||x.tr.timestamp!==t.entryTime||x.tr.direction!==t.direction){mismatch++;continue;}rows.push({entryIndex:i,time:t.entryTime,split:i<DEV?'DEV':'VAL',window:WINDOWS.find(w=>i>=w.start&&i<=w.end)?.name??'UNKNOWN',direction:t.direction,session:session(t.entryTime),r:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5});}
 const sell=rows.filter(x=>x.direction==='SELL');
 const sellNoEx=sell.filter(x=>!x.exceptional);
 const london=sell.filter(x=>x.session==='LONDON'),ny=sell.filter(x=>x.session==='NEW_YORK');
 const londonNoEx=london.filter(x=>!x.exceptional),nyNoEx=ny.filter(x=>!x.exceptional);
 const windows=Object.fromEntries(WINDOWS.map(w=>{const all=sell.filter(x=>x.window===w.name),noEx=all.filter(x=>!x.exceptional);return[w.name,{outcome:stats(all),noExceptional:stats(noEx),top1Excluded:stats(withoutTop(all,1)),top2Excluded:stats(withoutTop(all,2)),top3Excluded:stats(withoutTop(all,3)),concentration:{k1:concentration(all,1),k2:concentration(all,2),k3:concentration(all,3)}}]}));
 const segments={SELL:stats(sell),SELL_NO_EXCEPTIONAL:stats(sellNoEx),SELL_LONDON:stats(london),SELL_LONDON_NO_EXCEPTIONAL:stats(londonNoEx),SELL_NEW_YORK:stats(ny),SELL_NEW_YORK_NO_EXCEPTIONAL:stats(nyNoEx)};
 const result={strategy:'Strategy A / SP2L',mode:'PHASE_16_SELL_EDGE_DEOUTLIER_STABILITY',timeframe:'5min',scope:{rawBaselinePre:raw.length,canonicalReplayed:rows.length,dev:rows.filter(x=>x.split==='DEV').length,val:rows.filter(x=>x.split==='VAL').length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:210,rawBaselinePre:raw.length,canonicalReplayed:rows.length,mismatch,deterministicRerunRequired:true},methodology:{purpose:'Descriptive stability audit of the existing SELL baseline edge across London/New York and fixed chronological windows, with exceptional-trade concentration removed diagnostically only.',fixedWindows:WINDOWS,noOptimization:true,noThresholdSearch:true,noNewTradingRules:true,noFreshHoldoutAccess:true,exceptionalDefinition:'rMultiple >= 5R',tests:['SELL vs SELL without exceptional','SELL London/NY','fixed chronological window outcomes','top-1/top-2/top-3 exclusion diagnostics','window concentration']},segments,windows,cases:sell};
 const out=resolve(ROOT,'data/reports/strategy-a-phase16-sell-edge-deoutlier-stability');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
 const fmt=s=>`N=${s.n} avgR=${round(s.avgR)} PF=${round(s.PF)} WR=${pct(s.WR)}% totalR=${round(s.totalR)}`;
 console.log(`PHASE_16_SELL_EDGE_DEOUTLIER_STABILITY 5min N=${rows.length} SELL=${sell.length} FRESH=LOCKED`);
 console.log(`INTEGRITY expected=${result.integrity.expectedCanonical} raw=${raw.length} actual=${rows.length} mismatch=${mismatch}`);
 console.log('=== SELL SEGMENTS ===');for(const[k,v]of Object.entries(segments))console.log(`${k}: ${fmt(v)}`);
 console.log('=== FIXED CHRONOLOGICAL WINDOWS ===');for(const[k,v]of Object.entries(windows))console.log(`${k}: ALL ${fmt(v.outcome)} | NO_EX ${fmt(v.noExceptional)} | -TOP1 ${fmt(v.top1Excluded)} | -TOP2 ${fmt(v.top2Excluded)} | -TOP3 ${fmt(v.top3Excluded)}`);
 console.log('=== WINDOW CONCENTRATION ===');for(const[k,v]of Object.entries(windows))console.log(`${k}: K1 share=${round(v.concentration.k1.topShare)} K2 share=${round(v.concentration.k2.topShare)} K3 share=${round(v.concentration.k3.topShare)}`);
 console.log(`REPORT=${resolve(out,'5min.json')}`);console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
main().catch(e=>{console.error(e);process.exit(1);});
