import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const BASE=resolve(ROOT,'data/reports/strategy-a-baseline/5min.json');
const PRE=10000, DEV=6000, H=[3,5,10,20];
const finite=Number.isFinite;
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
const pf=rs=>{const w=rs.filter(x=>x>0).reduce((a,b)=>a+b,0),l=-rs.filter(x=>x<0).reduce((a,b)=>a+b,0);return l?w/l:null};
const maxDD=rs=>{let eq=0,peak=0,dd=0;for(const r of rs){eq+=r;peak=Math.max(peak,eq);dd=Math.max(dd,peak-eq)}return dd};
const stats=rs=>({n:rs.length,avgR:mean(rs),PF:pf(rs),WR:rs.length?rs.filter(x=>x>0).length/rs.length:null,totalR:rs.reduce((a,b)=>a+b,0),maxDrawdownR:maxDD(rs)});
const key=t=>`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;

async function main(){
  const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8'));
  const candles=raw.candles??raw;
  const baseline=JSON.parse(await readFile(BASE,'utf8')).trades??[];
  const usable=baseline.filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE);
  const fixedReportPath=resolve(ROOT,'data/reports/strategy-a-delay1-fixed-horizon-exit-economics/5m.json');
  try{await readFile(fixedReportPath,'utf8')}catch{throw new Error('Phase 10F economics report missing locally. Run analyze-delay1-fixed-horizon-exit-economics.mjs first.');}

  // The baseline contains 210 pre-holdout trades, of which 144 are DELAY1.
  // Phase 10F is explicitly DELAY1-only. Reuse the canonical baseline index
  // partition used by the existing DELAY1 analyzers rather than treating all
  // 210 baseline rows as DELAY1.
  // A baseline trade is DELAY1 iff its entry candle is immediately after the
  // correction extreme. The authoritative flag is reconstructed from the
  // existing Phase 10F candidate population stored in its report integrity.
  const fixedReport=JSON.parse(await readFile(fixedReportPath,'utf8'));
  if(fixedReport.integrity?.matched!==144)throw new Error(`Phase 10F integrity expected 144 matched rows, got ${fixedReport.integrity?.matched}.`);

  // The fixed-horizon report contains only aggregate rows, so derive the same
  // DELAY1 population by matching each baseline trade to the historical path
  // and applying the exact Phase 10F geometric condition: entryIndex is one
  // candle after its correction extreme. We intentionally do not create a new
  // detector; instead use the canonical delay1 index list from the report if
  // present, otherwise fail closed rather than guessing.
  const delay1Indices=fixedReport.delay1EntryIndices;
  if(!Array.isArray(delay1Indices)||delay1Indices.length!==144){
    throw new Error('Phase 10F report does not expose the canonical 144 DELAY1 entry indices. Regenerate Phase 10F after updating the reporter.');
  }
  const delay1Set=new Set(delay1Indices.map(Number));
  const delay1=usable.filter(t=>delay1Set.has(Number(t.entryIndex)));
  if(delay1.length!==144)throw new Error(`Expected 144 canonical DELAY1 baseline rows, got ${delay1.length}.`);
  const counts=new Map();for(const t of delay1)counts.set(key(t),(counts.get(key(t))??0)+1);const duplicateKeys=[...counts.values()].filter(n=>n>1).length;if(duplicateKeys)throw new Error(`duplicateKeys=${duplicateKeys}`);

  const rows=delay1.filter(t=>H.every(h=>Number(t.entryIndex)+h<candles.length)).map(t=>({entryIndex:Number(t.entryIndex),baselineR:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,entry:Number(t.entry),risk:Math.abs(Number(t.entry)-Number(t.stopLoss)),horizonR:Object.fromEntries(H.map(h=>{const close=Number(candles[Number(t.entryIndex)+h].close);return[h,(t.direction==='BUY'?close-Number(t.entry):Number(t.entry)-close)/Math.abs(Number(t.entry)-Number(t.stopLoss))]}))}));
  const dev=rows.filter(r=>r.entryIndex<DEV),val=rows.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE),exceptional=rows.filter(r=>r.exceptional),normal=rows.filter(r=>!r.exceptional);
  const results={};
  for(const h of H){const make=(subset,removeExceptional=false)=>stats(subset.filter(r=>!removeExceptional||!r.exceptional).map(r=>r.horizonR[h]));const excRs=exceptional.map(r=>r.horizonR[h]),normalRs=normal.map(r=>r.horizonR[h]);const total=normalRs.reduce((a,b)=>a+b,0)+excRs.reduce((a,b)=>a+b,0);results[`H${h}`]={all:make(rows),noExceptional:make(rows,true),dev:make(dev),devNoExceptional:make(dev,true),val:make(val),valNoExceptional:make(val,true),exceptional:{n:exceptional.length,totalR:excRs.reduce((a,b)=>a+b,0),avgR:mean(excRs),shareOfAllTotalR:total?excRs.reduce((a,b)=>a+b,0)/total:null,rows:[...exceptional].sort((a,b)=>b.horizonR[h]-a.horizonR[h]).map(r=>({entryIndex:r.entryIndex,baselineR:r.baselineR,horizonR:r.horizonR[h]}))},normal:{n:normalRs.length,totalR:normalRs.reduce((a,b)=>a+b,0),avgR:mean(normalRs)},deltaNoExceptionalVsAll:mean(normalRs)-mean(rows.map(r=>r.horizonR[h]))}};
  }
  const report={strategy:'Strategy A',mode:'DELAY1_FIXED_HORIZON_EXCEPTIONAL_DEPENDENCE',timeframe:'5min',scope:{preHoldoutCandles:PRE,devCutoff:DEV,delay1N:144,exceptionalDefinition:'Canonical baseline rMultiple >= 5R.',horizons:H,freshHoldoutAccessed:false},integrity:{baselinePre:usable.length,delay1Baseline:delay1.length,rows:rows.length,devN:dev.length,valN:val.length,duplicateKeys, pathComplete:rows.length===144,deterministic:true},methodology:{purpose:'Audit whether Phase 10F fixed-horizon economics depends materially on exceptional canonical winners.',exceptionalLabelSource:'Canonical baseline rMultiple only.',horizonOutcomeSource:'Pure close-to-close fixed-horizon R recomputed from historical candles; no SL/TP execution.',noExceptionalIsDiagnosticOnly:true,noThresholdOptimization:true,noHorizonOptimization:true,noExitRuleCreation:true,noBrokerExecutionModel:true,diagnosticOnly:true,freshHoldoutExcluded:true,productionUntouched:true},population:{all:rows.length,exceptional:exceptional.length,normal:normal.length},horizons:results};
  const OUT=resolve(ROOT,'data/reports/strategy-a-delay1-fixed-horizon-exceptional-dependence');await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
  console.log(`PHASE_10F_EXCEPTIONAL_DEPENDENCE N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);console.log(`INTEGRITY baselinePre=${usable.length} delay1=${delay1.length} exceptional=${exceptional.length} normal=${normal.length} pathComplete=${rows.length===144} deterministic=true`);for(const h of H){const x=results[`H${h}`];console.log(`H${h}: ALL avgR=${x.all.avgR.toFixed(4)} PF=${x.all.PF?.toFixed(4)} WR=${(x.all.WR*100).toFixed(2)}% | NO_EX avgR=${x.noExceptional.avgR.toFixed(4)} PF=${x.noExceptional.PF?.toFixed(4)} WR=${(x.noExceptional.WR*100).toFixed(2)}% | DEV NO_EX avgR=${x.devNoExceptional.avgR.toFixed(4)} PF=${x.devNoExceptional.PF?.toFixed(4)} WR=${(x.devNoExceptional.WR*100).toFixed(2)}% | VAL NO_EX avgR=${x.valNoExceptional.avgR.toFixed(4)} PF=${x.valNoExceptional.PF?.toFixed(4)} WR=${(x.valNoExceptional.WR*100).toFixed(2)}%`)}console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}
main().catch(err=>{console.error(err);process.exitCode=1});
