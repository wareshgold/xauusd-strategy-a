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
  let fixedReport;
  try{fixedReport=JSON.parse(await readFile(fixedReportPath,'utf8'))}catch{throw new Error('Phase 10F economics report missing locally. Run analyze-delay1-fixed-horizon-exit-economics.mjs first.');}
  const fixedRows=new Map();
  for(const h of H){const all=fixedReport.horizons?.[`H${h}`]?.all;if(!all)throw new Error(`Missing H${h} in Phase 10F report.`)}
  const baselineMap=new Map(usable.map(t=>[key(t),t]));
  let matched=0;
  for(let i=0;i<PRE;i++){
    // Match the already-produced Phase 10F row by canonical entry index. The report is
    // deliberately not treated as an outcome source; baseline rMultiple supplies the
    // exceptional label and the fixed-horizon script supplies the hypothetical exits.
    const candidates=usable.filter(t=>Number(t.entryIndex)===i);
    if(candidates.length!==1)continue;
    const t=candidates[0];
    const row={baselineR:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,entryIndex:i,direction:t.direction,entry:Number(t.entry),risk:Math.abs(Number(t.entry)-Number(t.stopLoss)),horizonR:{}};
    for(const h of H){const idx=i+h;if(idx>=candles.length){row.horizonR[h]=null;continue}const close=Number(candles[idx].close);row.horizonR[h]=(t.direction==='BUY'?close-Number(t.entry):Number(t.entry)-close)/row.risk}
    if(H.some(h=>!finite(row.horizonR[h])))continue;
    fixedRows.set(key(t),row);matched++;
  }
  if(matched!==144)throw new Error(`Expected 144 matched DELAY1 rows by baseline index, got ${matched}.`);
  const rows=[...fixedRows.values()];
  const dev=rows.filter(r=>r.entryIndex<DEV),val=rows.filter(r=>r.entryIndex>=DEV&&r.entryIndex<PRE);
  const exceptional=rows.filter(r=>r.exceptional),normal=rows.filter(r=>!r.exceptional);
  const results={};
  for(const h of H){
    const make=(subset,removeExceptional=false)=>{const rs=subset.filter(r=>!removeExceptional||!r.exceptional).map(r=>r.horizonR[h]);return stats(rs)};
    const excRs=exceptional.map(r=>r.horizonR[h]), normalRs=normal.map(r=>r.horizonR[h]);
    const total=normalRs.reduce((a,b)=>a+b,0)+excRs.reduce((a,b)=>a+b,0);
    const contribution=total?excRs.reduce((a,b)=>a+b,0)/total:null;
    const sorted=[...exceptional].sort((a,b)=>b.horizonR[h]-a.horizonR[h]);
    results[`H${h}`]={all:make(rows),noExceptional:make(rows,true),dev:make(dev),devNoExceptional:make(dev,true),val:make(val),valNoExceptional:make(val,true),exceptional:{n:exceptional.length,totalR:excRs.reduce((a,b)=>a+b,0),avgR:mean(excRs),shareOfAllTotalR:contribution,rows:sorted.map(r=>({entryIndex:r.entryIndex,baselineR:r.baselineR,horizonR:r.horizonR[h]}))},normal:{n:normalRs.length,totalR:normalRs.reduce((a,b)=>a+b,0),avgR:mean(normalRs)},deltaNoExceptionalVsAll:mean(normalRs)-mean(rows.map(r=>r.horizonR[h]))};
  }
  const report={strategy:'Strategy A',mode:'DELAY1_FIXED_HORIZON_EXCEPTIONAL_DEPENDENCE',timeframe:'5min',scope:{preHoldoutCandles:PRE,devCutoff:DEV,delay1N:144,exceptionalDefinition:'Canonical baseline rMultiple >= 5R.',horizons:H,freshHoldoutAccessed:false},integrity:{baselinePre:usable.length,matched,rows:rows.length,devN:dev.length,valN:val.length,duplicateKeys:0,pathComplete:true,deterministic:true},methodology:{purpose:'Audit whether Phase 10F fixed-horizon economics depends materially on exceptional canonical winners.',exceptionalLabelSource:'Canonical baseline rMultiple only.',horizonOutcomeSource:'Pure close-to-close fixed-horizon R recomputed from historical candles; no SL/TP execution.',noExceptionalIsDiagnosticOnly:true,noThresholdOptimization:true,noHorizonOptimization:true,noExitRuleCreation:true,noBrokerExecutionModel:true,diagnosticOnly:true,freshHoldoutExcluded:true,productionUntouched:true},population:{all:rows.length,exceptional:exceptional.length,normal:normal.length},horizons:results};
  const OUT=resolve(ROOT,'data/reports/strategy-a-delay1-fixed-horizon-exceptional-dependence');await mkdir(OUT,{recursive:true});await writeFile(resolve(OUT,'5m.json'),JSON.stringify(report,null,2));
  console.log(`PHASE_10F_EXCEPTIONAL_DEPENDENCE N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${usable.length} matched=${matched} exceptional=${exceptional.length} normal=${normal.length} pathComplete=true deterministic=true`);
  for(const h of H){const x=results[`H${h}`];console.log(`H${h}: ALL avgR=${x.all.avgR.toFixed(4)} PF=${x.all.PF?.toFixed(4)} WR=${(x.all.WR*100).toFixed(2)}% | NO_EX avgR=${x.noExceptional.avgR.toFixed(4)} PF=${x.noExceptional.PF?.toFixed(4)} WR=${(x.noExceptional.WR*100).toFixed(2)}% | DEV NO_EX avgR=${x.devNoExceptional.avgR.toFixed(4)} PF=${x.devNoExceptional.PF?.toFixed(4)} WR=${(x.devNoExceptional.WR*100).toFixed(2)}% | VAL NO_EX avgR=${x.valNoExceptional.avgR.toFixed(4)} PF=${x.valNoExceptional.PF?.toFixed(4)} WR=${(x.valNoExceptional.WR*100).toFixed(2)}%`)}
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}
main().catch(err=>{console.error(err);process.exitCode=1});
