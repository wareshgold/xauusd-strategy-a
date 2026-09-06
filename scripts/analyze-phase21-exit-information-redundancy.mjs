import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
const PRE = 10000;
const POST_HORIZON = 500;
const CFG = { breakoutLookback: 5, followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true }, spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 } };
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 }, { name: 'DEV_2', start: 2000, end: 3999 }, { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 }, { name: 'VAL_2', start: 8000, end: 9999 },
];
const DEV_END = 5999;
const FEATURE_NAMES = [
  'exitBars','exitRangeR','exitBodyR','exitCloseLocation','exitUpperWickShare','exitLowerWickShare',
  'exitSignedBodyToRange','previousRangeR','recentNetMoveR','recentPathEfficiency','recentRangeR',
  'exitVsEntryR','exitVsEntryAbsR'
];
const FEATURE_FAMILIES = {
  exit_timing: ['exitBars'],
  exit_candle_intensity: ['exitRangeR','exitBodyR','exitSignedBodyToRange','exitCloseLocation','exitUpperWickShare','exitLowerWickShare'],
  recent_path: ['previousRangeR','recentNetMoveR','recentPathEfficiency','recentRangeR'],
  displacement_from_entry: ['exitVsEntryR','exitVsEntryAbsR'],
};
const median = values => { const v=values.filter(Number.isFinite).sort((a,b)=>a-b); if(!v.length)return null; const m=Math.floor(v.length/2); return v.length%2?v[m]:(v[m-1]+v[m])/2; };
const mean = values => { const v=values.filter(Number.isFinite); return v.length?v.reduce((s,x)=>s+x,0)/v.length:null; };
const sd = values => { const v=values.filter(Number.isFinite); if(v.length<2)return null; const m=mean(v); return Math.sqrt(v.reduce((s,x)=>s+(x-m)**2,0)/(v.length-1)); };
const pct = rows => rows.length?rows.filter(Boolean).length/rows.length:null;
const stats = rows => { const n=rows.length,totalR=rows.reduce((s,x)=>s+x.r,0),wins=rows.filter(x=>x.r>0),losses=rows.filter(x=>x.r<=0),gw=wins.reduce((s,x)=>s+x.r,0),gl=-losses.reduce((s,x)=>s+x.r,0); return {n,avgR:n?totalR/n:null,PF:gl?gw/gl:null,WR:n?wins.length/n:null,totalR}; };
const rank = values => { const pairs=values.map((v,i)=>({v,i})).filter(x=>Number.isFinite(x.v)).sort((a,b)=>a.v-b.v); const out=Array(values.length).fill(null); let i=0; while(i<pairs.length){let j=i+1;while(j<pairs.length&&pairs[j].v===pairs[i].v)j++;const r=(i+1+j)/2;for(let k=i;k<j;k++)out[pairs[k].i]=r;i=j;}return out; };
function spearman(a,b){const pairs=[];for(let i=0;i<a.length;i++)if(Number.isFinite(a[i])&&Number.isFinite(b[i]))pairs.push([a[i],b[i]]);if(pairs.length<3)return null;const ra=rank(pairs.map(x=>x[0])),rb=rank(pairs.map(x=>x[1]));const ma=mean(ra),mb=mean(rb);let num=0,da=0,db=0;for(let i=0;i<ra.length;i++){const xa=ra[i]-ma,xb=rb[i]-mb;num+=xa*xb;da+=xa*xa;db+=xb*xb;}return da&&db?num/Math.sqrt(da*db):null;}
function auc(target,non){const a=target.filter(Number.isFinite),b=non.filter(Number.isFinite);if(!a.length||!b.length)return null;let wins=0,ties=0;for(const x of a)for(const y of b){if(x>y)wins++;else if(x===y)ties++;}return (wins+0.5*ties)/(a.length*b.length);}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=960&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION';}
function replay(entryIndex){const view=candles.slice(0,entryIndex+1);if(view.length<60)return null;const bo=detectBreakout(view,CFG.breakoutLookback),ft=detectFollowThrough(view,bo,CFG.followThrough),sp=detectSpikeCandidates(view,bo,ft,CFG.spike);for(const s of sp.candidates){if(s.endIndex>=entryIndex)continue;const co=detectFirstCorrection(view,s);if(!co||co.correctionExtremeIndex>=entryIndex)continue;const tr=detectEntryTrigger(view,co);if(!tr||tr.index!==entryIndex)continue;const b=bo.find(x=>x.index===s.breakoutIndex&&x.direction===s.direction),f=ft.find(x=>x.breakoutIndex===s.breakoutIndex&&x.direction===s.direction);if(b&&f)return{s,co,tr,b,f};}return null;}
function canonicalExit(entryIndex,entry,sl,tp,direction){const risk=Math.abs(entry-sl);if(!Number.isFinite(risk)||risk<=0)return null;for(let j=entryIndex+1;j<candles.length;j++){const c=candles[j],hitSL=direction==='BUY'?c.low<=sl:c.high>=sl,hitTP=direction==='BUY'?c.high>=tp:c.low<=tp;if(hitSL&&hitTP)return{index:j,reason:'AMBIGUOUS',risk};if(hitSL)return{index:j,reason:'SL',risk};if(hitTP)return{index:j,reason:'TP1',risk};}return null;}
function exitFeatures(entryIndex,exitIndex,entry,risk,direction){const c=candles[exitIndex],p=candles[Math.max(entryIndex,exitIndex-1)],range=Math.max(0,Number(c.high)-Number(c.low)),body=Math.abs(Number(c.close)-Number(c.open));const closeLoc=range?((Number(c.close)-Number(c.low))/range):null;const upper=range?((Number(c.high)-Math.max(Number(c.open),Number(c.close)))/range):null;const lower=range?((Math.min(Number(c.open),Number(c.close))-Number(c.low))/range):null;const signedBody=range?((Number(c.close)-Number(c.open))/range):null;const prevRange=Math.max(0,Number(p.high)-Number(p.low));const recentStart=Math.max(entryIndex,exitIndex-3);let netMove=0,pathRange=0,absMove=0;for(let j=recentStart+1;j<=exitIndex;j++){const a=candles[j-1],b=candles[j];const d=Number(b.close)-Number(a.close);netMove+=d;absMove+=Math.abs(d);pathRange+=Math.max(0,Number(b.high)-Number(b.low));}const exitVsEntry=(Number(c.close)-entry)/risk;return{exitBars:exitIndex-entryIndex,exitRangeR:range/risk,exitBodyR:body/risk,exitCloseLocation:closeLoc,exitUpperWickShare:upper,exitLowerWickShare:lower,exitSignedBodyToRange:signedBody,previousRangeR:prevRange/risk,recentNetMoveR:netMove/risk,recentPathEfficiency:absMove?Math.abs(netMove)/absMove:null,recentRangeR:pathRange/risk,exitVsEntryR:exitVsEntry,exitVsEntryAbsR:Math.abs(exitVsEntry)};}
function postContinuation(exitIndex,entry,risk,direction){let mfe=0;for(let j=exitIndex+1;j<=Math.min(candles.length-1,exitIndex+POST_HORIZON);j++){const c=candles[j],fav=direction==='BUY'?(c.high-entry)/risk:(entry-c.low)/risk;mfe=Math.max(mfe,fav);}return{mfeR:mfe,hasPost1:mfe>=1};}
const raw=(base.trades??[]).filter(t=>{const i=Number(t.entryIndex);return Number.isInteger(i)&&i<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL');});
let replayMismatch=0,exitMismatch=0;const rows=[];
for(const t of raw){const i=Number(t.entryIndex),r=replay(i);if(!r||r.tr.timestamp!==t.entryTime||r.tr.direction!==t.direction){replayMismatch++;continue;}const entry=Number(t.entry),sl=Number(t.stopLoss),tp=Number(t.tp1),ex=canonicalExit(i,entry,sl,tp,t.direction),expected=t.result==='TP1'?'TP1':'SL';if(!ex||ex.reason!==expected){exitMismatch++;continue;}const features=exitFeatures(i,ex.index,entry,ex.risk,t.direction),post=postContinuation(ex.index,entry,ex.risk,t.direction);rows.push({entryIndex:i,entryTime:t.entryTime,direction:t.direction,session:session(t.entryTime),split:i<=DEV_END?'DEV':'VAL',window:WINDOWS.find(w=>i>=w.start&&i<=w.end)?.name??'UNKNOWN',r:Number(t.rMultiple),outcome:Number(t.rMultiple)>0?'WIN':'LOSS',features,post});}
const losses=rows.filter(x=>x.outcome==='LOSS'),target=losses.filter(x=>x.post.hasPost1),nonTarget=losses.filter(x=>!x.post.hasPost1);
const featureTargetStats=Object.fromEntries(FEATURE_NAMES.map(k=>{const a=target.map(x=>x.features[k]),b=nonTarget.map(x=>x.features[k]);const am=mean(a),bm=mean(b),as=sd(a),bs=sd(b);const pooled=as!==null&&bs!==null?Math.sqrt(((a.filter(Number.isFinite).length-1)*as**2+(b.filter(Number.isFinite).length-1)*bs**2)/Math.max(1,a.filter(Number.isFinite).length+b.filter(Number.isFinite).length-2)):null;return[k,{targetMean:am,nonTargetMean:bm,delta:am!==null&&bm!==null?am-bm:null,targetMedian:median(a),nonTargetMedian:median(b),standardizedDelta:pooled?((am-bm)/pooled):null,aucTargetGreater:auc(a,b)}];}));
const pairwise=[];for(let i=0;i<FEATURE_NAMES.length;i++)for(let j=i+1;j<FEATURE_NAMES.length;j++){const a=rows.map(x=>x.features[FEATURE_NAMES[i]]),b=rows.map(x=>x.features[FEATURE_NAMES[j]]);const r=spearman(a,b);if(r!==null)pairwise.push({a:FEATURE_NAMES[i],b:FEATURE_NAMES[j],spearman:r});}
pairwise.sort((a,b)=>Math.abs(b.spearman)-Math.abs(a.spearman));
const familySummary=Object.fromEntries(Object.entries(FEATURE_FAMILIES).map(([family,features])=>{const relevant=pairwise.filter(p=>features.includes(p.a)&&features.includes(p.b));const targetEffects=features.map(f=>({feature:f,...featureTargetStats[f]}));return[family,{features,targetEffects,withinFamilyCorrelations:relevant.slice(0,10)}];}));
function breakdown(field,values){return Object.fromEntries(values.map(v=>{const a=losses.filter(x=>x[field]===v);return[v,{n:a.length,continuation1R:pct(a.map(x=>x.post.hasPost1))}]}));}
const result={strategy:'Strategy A / SP2L',mode:'PHASE_21_EXIT_INFORMATION_REDUNDANCY',timeframe:'5min',scope:{rawBaselinePre:raw.length,canonicalReplayed:rows.length,dev:rows.filter(x=>x.split==='DEV').length,val:rows.filter(x=>x.split==='VAL').length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:210,rawBaselinePre:raw.length,canonicalReplayed:rows.length,replayMismatch,exitMismatch,totalMismatch:replayMismatch+exitMismatch},methodology:{purpose:'Descriptive redundancy audit of information available at canonical exit. Tests whether Phase20 feature differences are largely measuring the same underlying exit-time movement rather than independent signals.',label:'Loss with post-exit MFE >=1R within 500 bars.',featuresUseOnlyExitTimeInformation:true,futureLeakageGuard:'Post-exit continuation is retrospective label only; no future candle enters any feature, correlation, or grouping input.',noOptimization:true,noThresholdSearch:true,noNewTradingRules:true,noFreshHoldoutAccess:true},overall:stats(rows),losses:{n:losses.length,continuation1R:target.length,continuation1RShare:target.length/losses.length,nonContinuation1R:nonTarget.length,featureTargetStats,pairwiseFeatureCorrelations:pairwise,familySummary},direction:breakdown('direction',['BUY','SELL']),session:breakdown('session',['LONDON','NEW_YORK','OUT_OF_SESSION']),window:breakdown('window',WINDOWS.map(x=>x.name))};
const out=resolve(ROOT,'data/reports/strategy-a-phase21-exit-information-redundancy');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE_21_EXIT_INFORMATION_REDUNDANCY 5min N=${rows.length} DEV=${rows.filter(x=>x.split==='DEV').length} VAL=${rows.filter(x=>x.split==='VAL').length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch} exitMismatch=${exitMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR*100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`LOSSES N=${losses.length} CONT_GE_1R=${target.length} share=${(result.losses.continuation1RShare*100).toFixed(4)}% NO_CONT=${nonTarget.length}`);
for(const k of FEATURE_NAMES){const s=featureTargetStats[k];console.log(`FEATURE ${k}: stdDelta=${s.standardizedDelta?.toFixed(4)} auc=${s.aucTargetGreater?.toFixed(4)} delta=${s.delta?.toFixed(6)}`);}
console.log('TOP_FEATURE_CORRELATIONS');for(const p of pairwise.slice(0,12))console.log(`CORR ${p.a} ~ ${p.b}: spearman=${p.spearman.toFixed(4)}`);
for(const [k,v] of Object.entries(result.direction))console.log(`DIRECTION ${k}: N=${v.n} continuation1R=${(v.continuation1R*100).toFixed(2)}%`);
for(const [k,v] of Object.entries(result.session))console.log(`SESSION ${k}: N=${v.n} continuation1R=${(v.continuation1R*100).toFixed(2)}%`);
for(const [k,v] of Object.entries(result.window))console.log(`WINDOW ${k}: N=${v.n} continuation1R=${(v.continuation1R*100).toFixed(2)}%`);
console.log(`REPORT=${resolve(out,'5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
