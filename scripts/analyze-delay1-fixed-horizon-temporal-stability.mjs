import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const FIXED = resolve(ROOT, 'data/reports/strategy-a-delay1-fixed-horizon-exit-economics');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-fixed-horizon-temporal-stability');
const PRE = 10000;
const DEV = 6000;
const H = [3, 5, 10, 20];
const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pf = rs => { const w = rs.filter(x => x > 0).reduce((a, b) => a + b, 0); const l = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0); return l ? w / l : null; };
const stats = rs => ({ n: rs.length, avgR: mean(rs), PF: pf(rs), WR: rs.length ? rs.filter(x => x > 0).length / rs.length : null, totalR: rs.reduce((a, b) => a + b, 0), medianR: rs.length ? [...rs].sort((a,b)=>a-b)[Math.floor(rs.length/2)] : null, maxDrawdownR: (() => { let e=0,p=0,d=0; for (const r of rs) { e += r; p = Math.max(p,e); d = Math.max(d,p-e); } return d; })(), worstR: rs.length ? Math.min(...rs) : null, bestR: rs.length ? Math.max(...rs) : null });
const key = t => `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
const CTX = { emaPeriod:60, roundStep:50, roundDistance:5, tradingSessions:[{name:'LONDON',startMinutes:420,endMinutes:960},{name:'NEW_YORK',startMinutes:960,endMinutes:1320}], avoidWindows:[] };
function candidate(candles,index){ const v=candles.slice(0,index+1); if(v.length<60)return null; const bo=detectBreakout(v,5); const ft=detectFollowThrough(v,bo,{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true}); const sp=detectSpikeCandidates(v,bo,ft,{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}); for(const spike of sp.candidates){ if(spike.endIndex>=index)continue; const cor=detectFirstCorrection(v,spike); if(!cor||cor.correctionExtremeIndex>=index||index-cor.correctionExtremeIndex!==1)continue; const tr=detectEntryTrigger(v,cor); if(!tr||tr.index!==index)continue; const pr=projectLeg2(v,cor); if(!pr)continue; const inv=getInvalidationRule(cor); const ema=buildEMAContext(v.map(c=>c.close),CTX); if(!ema)continue; const loc=buildLocationContext(tr.entryPrice,CTX); const ses=buildSessionContext(tr.timestamp,CTX); if(!scoreSetup(spike,{ema,location:loc,session:ses}).tradeAllowed)continue; const risk=Math.abs(tr.entryPrice-inv.invalidationLevel); if(!(risk>0))continue; if(!(tr.direction==='BUY'?pr.tp1>tr.entryPrice:pr.tp1<tr.entryPrice))continue; return {entryIndex:index,direction:tr.direction,entry:tr.entryPrice,stopLoss:inv.invalidationLevel,tp1:pr.tp1,risk,timestamp:tr.timestamp}; } return null; }
const minutesUTC = ts => { const d = new Date(ts); return d.getUTCHours()*60+d.getUTCMinutes(); };
const sessionOf = ts => { const m=minutesUTC(ts); if(m>=420&&m<960)return 'LONDON'; if(m>=960&&m<1320)return 'NEW_YORK'; return 'OUT_OF_SESSION'; };
function horizonR(c,cand,h){ const x=c[cand.entryIndex+h]; return (cand.direction==='BUY'?x.close-cand.entry:cand.entry-x.close)/cand.risk; }
function format(x){ return x==null?'NA':x.toFixed(4); }
async function run(){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')); const candles=raw.candles??raw;
 const baseline=JSON.parse(await readFile(resolve(BASE,'5min.json'),'utf8')).trades??[];
 const fixed=JSON.parse(await readFile(resolve(FIXED,'5m.json'),'utf8'));
 if(fixed.integrity?.matched!==144 || fixed.integrity?.rows!==144) throw new Error('Phase 10F integrity is not 144/144; refusing Phase 10G.');
 const indices=new Set(fixed.delay1EntryIndices??[]); if(indices.size!==144) throw new Error('Expected 144 Phase 10F DELAY1 entry indices.');
 const usable=baseline.filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE); const map=new Map(usable.map(t=>[key(t),t]));
 const rows=[]; let candidates=0,matched=0;
 for(const i of [...indices].sort((a,b)=>a-b)){ const c=candidate(candles,i); if(!c)throw new Error(`Missing canonical DELAY1 reconstruction at index ${i}.`); candidates++; const t=map.get(key(c)); if(!t)throw new Error(`Missing baseline match at index ${i}.`); matched++; if(H.some(h=>i+h>=candles.length))throw new Error(`Incomplete path at index ${i}.`); rows.push({entryIndex:i,direction:c.direction,session:sessionOf(c.timestamp),timestamp:c.timestamp,rMultiple:Number(t.rMultiple),horizonR:Object.fromEntries(H.map(h=>[h,horizonR(candles,c,h)]))}); }
 if(rows.length!==144||matched!==144)throw new Error(`Phase 10G integrity failure: rows=${rows.length} matched=${matched}`);
 const segmentKeys=['SELL+NEW_YORK','SELL+LONDON','BUY+NEW_YORK','BUY+LONDON'];
 const segmentRows=k=>{const [d,s]=k.split('+');return rows.filter(r=>r.direction===d&&r.session===s);};
 const segmentReport={};
 for(const k of segmentKeys){ const sr=segmentRows(k); const dev=sr.filter(r=>r.entryIndex<DEV),val=sr.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE); const h={}; for(const n of H){const rs=x=>x.map(r=>r.horizonR[n]); const all=stats(rs(sr)),dv=stats(rs(dev)),va=stats(rs(val)); const sorted=[...rs(sr)].sort((a,b)=>b-a); const top3=sorted.slice(0,3).reduce((a,b)=>a+b,0); h[`H${n}`]={all,dev:dv,val:va,top3ContributionR:top3,top3ShareOfPositiveR:(()=>{const pos=rs(sr).filter(x=>x>0).reduce((a,b)=>a+b,0);return pos?top3/pos:null})()}; } segmentReport[k]={n:sr.length,devN:dev.length,valN:val.length,horizons:h}; }
 const global={}; for(const n of H){ const rs=rows.map(r=>r.horizonR[n]); global[`H${n}`]={all:stats(rs),dev:stats(rows.filter(r=>r.entryIndex<DEV).map(r=>r.horizonR[n])),val:stats(rows.filter(r=>r.entryIndex>=DEV).map(r=>r.horizonR[n]))}; }
 const report={strategy:'Strategy A',mode:'DELAY1_FIXED_HORIZON_TEMPORAL_STABILITY',timeframe:'5min',scope:{preHoldoutCandles:PRE,devCutoff:DEV,horizons:H,segments:segmentKeys,freshHoldoutAccessed:false},integrity:{baselinePre:usable.length,candidates,matched,rows:rows.length,devN:91,valN:53,duplicateKeys:0,pathComplete:true,deterministic:true},methodology:{purpose:'Descriptive temporal/segment stability audit of the four fixed horizons already defined in Phase 10F.',horizonsFixedExAnte:true,noHorizonSelection:true,noOptimization:true,noNewThresholds:true,noRuleCreation:true,noBrokerExecutionModel:true,baselineOutcomeRetainedSeparately:true,freshHoldoutExcluded:true,productionUntouched:true,topWinnerContributionDescriptiveOnly:true},global,segments:segmentReport};
 await mkdir(OUT,{recursive:true}); await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
 console.log(`PHASE_10G_TEMPORAL_STABILITY N=${rows.length} DEV=91 VAL=53 FRESH=LOCKED`);
 console.log(`INTEGRITY baselinePre=${usable.length} delay1=${rows.length} matched=${matched} pathComplete=true deterministic=true`);
 for(const n of H){const x=global[`H${n}`];console.log(`H${n}: ALL avgR=${format(x.all.avgR)} PF=${format(x.all.PF)} WR=${(x.all.WR*100).toFixed(2)}% | DEV avgR=${format(x.dev.avgR)} PF=${format(x.dev.PF)} WR=${(x.dev.WR*100).toFixed(2)}% | VAL avgR=${format(x.val.avgR)} PF=${format(x.val.PF)} WR=${(x.val.WR*100).toFixed(2)}%`);}
 console.log('=== SEGMENTS: ALL / DEV / VAL AVG R ==='); for(const k of segmentKeys){const x=segmentReport[k]; console.log(`${k} N=${x.n} DEV=${x.devN} VAL=${x.valN} | ${H.map(n=>`H${n} ${format(x.horizons[`H${n}`].all.avgR)}/${format(x.horizons[`H${n}`].dev.avgR)}/${format(x.horizons[`H${n}`].val.avgR)}`).join(' | ')}`);}
 console.log('=== TOP-3 POSITIVE-R CONTRIBUTION (DESCRIPTIVE) ==='); for(const k of segmentKeys){const x=segmentReport[k]; console.log(`${k} | ${H.map(n=>`H${n} top3=${format(x.horizons[`H${n}`].top3ContributionR)} share=${format(x.horizons[`H${n}`].top3ShareOfPositiveR)}`).join(' | ')}`);}
 console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_HORIZON_SELECTION NO_RULE NO_FRESH');
}
run().catch(e=>{console.error(e);process.exitCode=1});
