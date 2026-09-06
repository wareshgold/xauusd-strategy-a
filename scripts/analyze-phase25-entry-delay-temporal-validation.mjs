import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT=resolve(fileURLToPath(new URL('..',import.meta.url)));
const candles=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[];
const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
const PRE=10000, DEV_END=5999;
const WINDOWS=[['DEV_1',0,1999],['DEV_2',2000,3999],['DEV_3',4000,5999],['VAL_1',6000,7999],['VAL_2',8000,9999]];
const CFG={breakoutLookback:5,followThrough:{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true},spike:{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}};
const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
function stats(rows){const n=rows.length,w=rows.filter(x=>x.r>0),l=rows.filter(x=>x.r<=0),gw=w.reduce((s,x)=>s+x.r,0),gl=-l.reduce((s,x)=>s+x.r,0),tr=rows.reduce((s,x)=>s+x.r,0);return{n,avgR:n?tr/n:null,PF:gl?gw/gl:null,WR:n?w.length/n:null,totalR:tr};}
function replay(i){const v=candles.slice(0,i+1);if(v.length<60)return null;const bo=detectBreakout(v,CFG.breakoutLookback),ft=detectFollowThrough(v,bo,CFG.followThrough),sp=detectSpikeCandidates(v,bo,ft,CFG.spike);for(const s of sp.candidates){if(s.endIndex>=i)continue;const co=detectFirstCorrection(v,s);if(!co||co.correctionExtremeIndex>=i)continue;const tr=detectEntryTrigger(v,co);if(!tr||tr.index!==i)continue;const b=bo.find(x=>x.index===s.breakoutIndex&&x.direction===s.direction),f=ft.find(x=>x.breakoutIndex===s.breakoutIndex&&x.direction===s.direction);if(b&&f)return{tr,co,s,b,f};}return null;}
function row(t,r){const delay=Number(t.entryIndex)-Number(r.co.correctionExtremeIndex);return{r:Number(t.rMultiple),delay,direction:t.direction,entryIndex:Number(t.entryIndex),window:WINDOWS.find(w=>Number(t.entryIndex)>=w[1]&&Number(t.entryIndex)<=w[2])?.[0]??'UNKNOWN'};}
const raw=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
let replayMismatch=0,rows=[];for(const t of raw){const r=replay(Number(t.entryIndex));if(!r||r.tr.timestamp!==t.entryTime||r.tr.direction!==t.direction){replayMismatch++;continue;}rows.push(row(t,r));}
const candidate=rows.filter(x=>x.delay===1),nonCandidate=rows.filter(x=>x.delay!==1);
function groupAudit(rows){const all=stats(rows), noOut=rows.length>1?(()=>{const sorted=[...rows].sort((a,b)=>b.r-a.r);return stats(sorted.slice(1));})():stats(rows);return{all,noExceptionalTop1:noOut};}
function audit(label,subset){const c=subset.filter(x=>x.delay===1),n=subset.filter(x=>x.delay!==1);return{label,all:stats(subset),delay1:groupAudit(c),notDelay1:groupAudit(n),deltaAvgR:c.length&&n.length?c.reduce((s,x)=>s+x.r,0)/c.length-n.reduce((s,x)=>s+x.r,0)/n.length:null};}
const windows=Object.fromEntries(WINDOWS.map(w=>[w[0],audit(w[0],rows.filter(x=>x.window===w[0]))]));
const directions=Object.fromEntries(['BUY','SELL'].map(d=>[d,audit(d,rows.filter(x=>x.direction===d))]));
const result={strategy:'Strategy A / SP2L',mode:'PHASE_25_ENTRY_DELAY_TEMPORAL_VALIDATION',timeframe:'5min',scope:{rawBaselinePre:raw.length,canonicalReplayed:rows.length,dev:rows.filter(x=>x.window?.startsWith('DEV')).length,val:rows.filter(x=>x.window?.startsWith('VAL')).length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:210,rawBaselinePre:raw.length,canonicalReplayed:rows.length,replayMismatch},overall:stats(rows),hypothesis:{name:'ENTRY_DELAY_EQ_1',candidate:'entryDelay = 1',contrast:'entryDelay != 1',preRegistered:true,source:'Phase24 descriptive observation; no threshold search in Phase25',freshHoldoutLocked:true},candidate:groupAudit(candidate),contrast:groupAudit(nonCandidate),windows,directions,methodology:{canonicalReplay:true,entryDelayDefinition:'entryIndex - correctionExtremeIndex',fixedChronologicalWindows:WINDOWS,top1OutlierSensitivity:true,noThresholdSearch:true,noOptimization:true,noNewFeatures:true,noFreshHoldoutAccess:true,decisionRule:'Do not promote the candidate to a trading rule from this descriptive validation alone. Candidate must show positive and reasonably stable behavior across multiple fixed windows and not depend on the single largest winner before any separate pre-registered validation stage.'}};
const out=resolve(ROOT,'data/reports/strategy-a-phase25-entry-delay-temporal-validation');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE_25_ENTRY_DELAY_TEMPORAL_VALIDATION 5min N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} replayMismatch=${replayMismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR*100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)}`);
console.log(`CANDIDATE entryDelay=1 N=${candidate.length} avgR=${result.candidate.all.avgR?.toFixed(6)} PF=${result.candidate.all.PF?.toFixed(6)} WR=${(result.candidate.all.WR*100)?.toFixed(4)}% totalR=${result.candidate.all.totalR?.toFixed(6)} | NO_TOP1 avgR=${result.candidate.noExceptionalTop1.avgR?.toFixed(6)} PF=${result.candidate.noExceptionalTop1.PF?.toFixed(6)} totalR=${result.candidate.noExceptionalTop1.totalR?.toFixed(6)}`);
console.log(`CONTRAST entryDelay!=1 N=${nonCandidate.length} avgR=${result.contrast.all.avgR?.toFixed(6)} PF=${result.contrast.all.PF?.toFixed(6)} WR=${(result.contrast.all.WR*100)?.toFixed(4)}% totalR=${result.contrast.all.totalR?.toFixed(6)} | NO_TOP1 avgR=${result.contrast.noExceptionalTop1.avgR?.toFixed(6)} PF=${result.contrast.noExceptionalTop1.PF?.toFixed(6)} totalR=${result.contrast.noExceptionalTop1.totalR?.toFixed(6)}`);
for(const [k,v] of Object.entries(windows))console.log(`WINDOW ${k}: ALL N=${v.all.n} avgR=${v.all.avgR?.toFixed(4)} | DELAY1 N=${v.delay1.all.n} avgR=${v.delay1.all.avgR?.toFixed(4)} PF=${v.delay1.all.PF?.toFixed(4)} | NOT1 N=${v.notDelay1.all.n} avgR=${v.notDelay1.all.avgR?.toFixed(4)} PF=${v.notDelay1.all.PF?.toFixed(4)} delta=${v.deltaAvgR?.toFixed(4)}`);
for(const [k,v] of Object.entries(directions))console.log(`DIRECTION ${k}: DELAY1 N=${v.delay1.all.n} avgR=${v.delay1.all.avgR?.toFixed(4)} PF=${v.delay1.all.PF?.toFixed(4)} | NOT1 N=${v.notDelay1.all.n} avgR=${v.notDelay1.all.avgR?.toFixed(4)} PF=${v.notDelay1.all.PF?.toFixed(4)} delta=${v.deltaAvgR?.toFixed(4)}`);
console.log(`REPORT=${resolve(out,'5min.json')}`);
console.log('STATUS=DESCRIPTIVE_VALIDATION NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');