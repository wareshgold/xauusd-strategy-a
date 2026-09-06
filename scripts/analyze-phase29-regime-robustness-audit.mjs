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
const PRE=10000;
const WINDOWS=[['DEV_1',0,1999],['DEV_2',2000,3999],['DEV_3',4000,5999],['VAL_1',6000,7999],['VAL_2',8000,9999]];
const REGIMES=['BUY+LONDON','BUY+NEW_YORK','BUY+OUT_OF_SESSION','SELL+LONDON','SELL+NEW_YORK','SELL+OUT_OF_SESSION'];
const CFG={breakoutLookback:5,followThrough:{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true},spike:{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}};
function maxConsecutiveLosses(rows){let max=0,cur=0;for(const x of [...rows].sort((a,b)=>a.entryIndex-b.entryIndex)){if(x.r<=0){cur++;max=Math.max(max,cur);}else cur=0;}return max;}
function stats(rows){const n=rows.length,w=rows.filter(x=>x.r>0),l=rows.filter(x=>x.r<=0),grossWin=w.reduce((s,x)=>s+x.r,0),grossLoss=-l.reduce((s,x)=>s+x.r,0),total=rows.reduce((s,x)=>s+x.r,0);return{n,avgR:n?total/n:null,PF:grossLoss?grossWin/grossLoss:null,WR:n?w.length/n:null,totalR:total,maxConsecLoss:maxConsecutiveLosses(rows)};}
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();if(m>=420&&m<960)return'LONDON';if(m>=960&&m<1320)return'NEW_YORK';return'OUT_OF_SESSION';}
function regime(x){return `${x.direction}+${x.session}`;}
function replay(i){const v=candles.slice(0,i+1);if(v.length<60)return null;const bo=detectBreakout(v,CFG.breakoutLookback),ft=detectFollowThrough(v,bo,CFG.followThrough),sp=detectSpikeCandidates(v,bo,ft,CFG.spike);for(const s of sp.candidates){if(s.endIndex>=i)continue;const co=detectFirstCorrection(v,s);if(!co||co.correctionExtremeIndex>=i)continue;const tr=detectEntryTrigger(v,co);if(!tr||tr.index!==i)continue;const b=bo.find(x=>x.index===s.breakoutIndex&&x.direction===s.direction),f=ft.find(x=>x.breakoutIndex===s.breakoutIndex&&x.direction===s.direction);if(b&&f)return{tr,b,f,s,co};}return null;}
const raw=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
let mismatch=0,rows=[];
for(const t of raw){const r=replay(Number(t.entryIndex));if(!r||r.tr.timestamp!==t.entryTime||r.tr.direction!==t.direction){mismatch++;continue;}rows.push({r:Number(t.rMultiple),entryIndex:Number(t.entryIndex),direction:t.direction,session:session(t.entryTime),window:WINDOWS.find(w=>Number(t.entryIndex)>=w[1]&&Number(t.entryIndex)<=w[2])?.[0]??'UNKNOWN'});}
function regimeAudit(rs,name){const a=rs.filter(x=>regime(x)===name);const perWindow=WINDOWS.map(([w,s,e])=>{const q=a.filter(x=>x.window===w);return{window:w,...stats(q)}});const positiveWindows=perWindow.filter(x=>x.n>0&&x.avgR>0).length;const negativeWindows=perWindow.filter(x=>x.n>0&&x.avgR<0).length;const observed=perWindow.filter(x=>x.n>0).length;return{overall:stats(a),perWindow,observedWindows:observed,positiveWindows,negativeWindows,signConsistency:observed?Math.max(positiveWindows,negativeWindows)/observed:null};}
function familyAudit(rs){const direction={BUY:stats(rs.filter(x=>x.direction==='BUY')),SELL:stats(rs.filter(x=>x.direction==='SELL'))};const sessionStats=Object.fromEntries(['LONDON','NEW_YORK','OUT_OF_SESSION'].map(s=>[s,stats(rs.filter(x=>x.session===s))]));return{direction,session:sessionStats};}
function contribution(rs){const total=stats(rs).totalR;return Object.fromEntries(REGIMES.map(g=>{const r=stats(rs.filter(x=>regime(x)===g));return[g,{n:r.n,totalR:r.totalR,shareAbsTotal:Math.abs(total)>0?Math.abs(r.totalR)/Math.abs(total):null,shareSignedTotal:Math.abs(total)>0?r.totalR/total:null}]}));}
const result={strategy:'Strategy A / SP2L',mode:'PHASE_29_REGIME_ROBUSTNESS_AUDIT',timeframe:'5min',scope:{rawBaselinePre:raw.length,canonicalReplayed:rows.length,dev:rows.filter(x=>x.window.startsWith('DEV')).length,val:rows.filter(x=>x.window.startsWith('VAL')).length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:210,rawBaselinePre:raw.length,canonicalReplayed:rows.length,replayMismatch:mismatch},overall:stats(rows),regimes:Object.fromEntries(REGIMES.map(g=>[g,regimeAudit(rows,g)])),families:familyAudit(rows),contribution:contribution(rows),temporalWindows:Object.fromEntries(WINDOWS.map(([w])=>[w,stats(rows.filter(x=>x.window===w))])),methodology:{purpose:'Robustness audit of already-observed categorical regime families. No new thresholds or candidate trading rules are introduced. The audit asks whether the existing direction/session regimes recur with the same sign across fixed chronological windows and whether baseline PnL is broadly distributed across regimes.',fixedRegimes:REGIMES,fixedChronologicalWindows:WINDOWS,metrics:['N','avgR','PF','WR','totalR','maxConsecLoss','signConsistency'],noThresholdSearch:true,noOptimization:true,noNewFeatures:true,noNewTradingRule:true,noFreshHoldoutAccess:true,productionUntouched:true}};
const out=resolve(ROOT,'data/reports/strategy-a-phase29-regime-robustness-audit');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE_29_REGIME_ROBUSTNESS_AUDIT 5min N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
console.log(`INTEGRITY expected=210 raw=${raw.length} actual=${rows.length} replayMismatch=${mismatch}`);
console.log(`OVERALL N=${rows.length} avgR=${result.overall.avgR?.toFixed(6)} PF=${result.overall.PF?.toFixed(6)} WR=${(result.overall.WR*100)?.toFixed(4)}% totalR=${result.overall.totalR?.toFixed(6)} maxConsecLoss=${result.overall.maxConsecLoss}`);
for(const g of REGIMES){const v=result.regimes[g];console.log(`REGIME ${g}: N=${v.overall.n} avgR=${v.overall.avgR?.toFixed(4)} PF=${v.overall.PF?.toFixed(4)} WR=${(v.overall.WR*100)?.toFixed(2)}% totalR=${v.overall.totalR?.toFixed(4)} maxConsecLoss=${v.overall.maxConsecLoss} | windows=${v.observedWindows} positive=${v.positiveWindows} negative=${v.negativeWindows} signConsistency=${v.signConsistency?.toFixed(3)}`);}
for(const [w,v] of Object.entries(result.temporalWindows))console.log(`WINDOW ${w}: N=${v.n} avgR=${v.avgR?.toFixed(4)} PF=${v.PF?.toFixed(4)} WR=${(v.WR*100)?.toFixed(2)}% totalR=${v.totalR?.toFixed(4)} maxConsecLoss=${v.maxConsecLoss}`);
console.log(`CONTRIBUTION ${Object.entries(result.contribution).map(([g,v])=>`${g}[N=${v.n},totalR=${v.totalR.toFixed(3)},absShare=${(v.shareAbsTotal*100).toFixed(1)}%]`).join(' ')}`);
console.log(`REPORT=${resolve(out,'5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
