import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PATH_DIR=resolve(ROOT,'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR=resolve(ROOT,'data/reports/strategy-a-baseline');
const OUT_DIR=resolve(ROOT,'data/reports/strategy-a-entry-trigger-reclaim-mechanics');
const PRE=10000;

function metrics(rows){
  const rs=rows.map(x=>Number(x.r)).filter(Number.isFinite);
  const wins=rs.filter(x=>x>0), losses=rs.filter(x=>x<0);
  const gp=wins.reduce((a,b)=>a+b,0), gl=-losses.reduce((a,b)=>a+b,0);
  return {n:rs.length,wins:wins.length,losses:losses.length,winRate:rs.length?wins.length/rs.length:0,avgR:rs.length?rs.reduce((a,b)=>a+b,0)/rs.length:0,totalR:rs.reduce((a,b)=>a+b,0),PF:gl?gp/gl:null};
}
function key(c){return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`}
function q(v,p){const a=v.filter(Number.isFinite).sort((x,y)=>x-y);return a.length?a[Math.min(a.length-1,Math.floor((a.length-1)*p))]:null}
function describe(rows,candles){
  for(const r of rows){
    const i=Number(r.index), c=candles[i]; if(!c) continue;
    const o=Number(c.open),h=Number(c.high),l=Number(c.low),cl=Number(c.close),range=h-l;
    const body=Math.abs(cl-o);
    const upper=h-Math.max(o,cl),lower=Math.min(o,cl)-l;
    const dir=r.direction;
    const impulse=Math.max(Number(r.spikeSize),1e-9);
    const adjustedClose=dir==='BUY'?(cl-l)/Math.max(range,1e-9):(h-cl)/Math.max(range,1e-9);
    const adjustedBody=dir==='BUY'?(cl-o)/Math.max(range,1e-9):(o-cl)/Math.max(range,1e-9);
    const oppositeWick=dir==='BUY'?lower/Math.max(range,1e-9):upper/Math.max(range,1e-9);
    const correctionStart=Number(r.spikeEndIndex)+1;
    const extreme=Number(r.correctionExtremeIndex);
    const delay=Number(r.triggerDelay);
    let maxPostExtremeAdverse=0;
    if(extreme<=i){
      for(let j=extreme;j<=i;j++){
        const cj=candles[j];
        const adverse=dir==='BUY'?Math.max(0,Number(r.extremePrice??cj.low)-Number(cj.low)):Math.max(0,Number(cj.high)-Number(r.extremePrice??cj.high));
        maxPostExtremeAdverse=Math.max(maxPostExtremeAdverse,adverse/impulse);
      }
    }
    const reclaimDistance=dir==='BUY'?(Number(r.entry)-Number(r.triggerLevel))/impulse:(Number(r.triggerLevel)-Number(r.entry))/impulse;
    const triggerVsExtreme=dir==='BUY'?(Number(r.entry)-(Number(r.spikeStartIndex)>=0?Number(r.entry)-Number(r.correctionDepth)*impulse:Number(r.entry))):0;
    const prior=[];
    for(let j=Math.max(0,i-5);j<i;j++){const pc=candles[j];const pr=Number(pc.high)-Number(pc.low);if(pr>0)prior.push(pr);}
    const medianPriorRange=q(prior,0.5);
    const priorBody=[];
    for(let j=Math.max(0,i-5);j<i;j++){const pc=candles[j];priorBody.push(Math.abs(Number(pc.close)-Number(pc.open)));}
    const medianPriorBody=q(priorBody,0.5);
    Object.assign(r,{
      correctionBars:Math.max(0,extreme-correctionStart+1),
      postExtremeDelay:delay,
      triggerBodyFraction:body/Math.max(range,1e-9),
      directionAdjustedCloseLocation:adjustedClose,
      directionAdjustedBody:adjustedBody,
      oppositeWickFraction:oppositeWick,
      triggerRangeToImpulse:range/impulse,
      triggerBodyToImpulse:body/impulse,
      triggerRangeToPrior5Median:medianPriorRange?range/medianPriorRange:null,
      triggerBodyToPrior5Median:medianPriorBody?body/medianPriorBody:null,
      maxPostExtremeAdverseExtension:maxPostExtremeAdverse,
      reclaimDistanceFromLevel:reclaimDistance,
      sameDirectionTrigger:adjustedBody>0,
      correctionStartIndex:correctionStart,
      triggerVsExtreme
    });
  }
}
function summary(rows,fields){
  const winners=rows.filter(r=>r.r>0),losers=rows.filter(r=>r.r<0);
  const out={};
  for(const f of fields){
    const vals=a=>a.map(r=>Number(r[f])).filter(Number.isFinite);
    const stat=a=>{const v=vals(a);return {n:v.length,p10:q(v,.1),p25:q(v,.25),p50:q(v,.5),p75:q(v,.75),p90:q(v,.9),mean:v.length?v.reduce((x,y)=>x+y,0)/v.length:null};};
    out[f]={all:stat(rows),winners:stat(winners),losers:stat(losers)};
  }
  return out;
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
  describe(rows,candles);
  const fields=['triggerDelay','correctionBars','correctionDepth','directionAdjustedCloseLocation','directionAdjustedBody','oppositeWickFraction','triggerBodyFraction','triggerRangeToImpulse','triggerBodyToImpulse','triggerRangeToPrior5Median','triggerBodyToPrior5Median','maxPostExtremeAdverseExtension','reclaimDistanceFromLevel','triggerExtension','stopToImpulse'];
  const report={strategy:'Strategy A',mode:'ENTRY_TRIGGER_RECLAIM_MECHANICS_PREHOLDOUT',timeframe,candles:candles.length,scope:{preHoldoutCandles:PRE,freshHoldoutExcluded:true},methodology:{outcomeSource:'canonical baseline',featureSource:'baseline path + trigger candle OHLC + post-extreme visible path',purpose:'diagnostic mechanism attribution only; no threshold optimization; no production change'},baseline:metrics(rows),featureSummary:summary(rows,fields),directionNormalizedDefinitions:{closeLocation:'BUY=(close-low)/range; SELL=(high-close)/range',directionalBody:'BUY=(close-open)/range; SELL=(open-close)/range',oppositeWick:'BUY=lower wick/range; SELL=upper wick/range'},notes:['correctionBars counts candles from spikeEnd+1 through first correction extreme','postExtremeDelay equals triggerDelay','maxPostExtremeAdverseExtension measures further adverse excursion after the first correction extreme before the trigger','triggerRange/body-to-prior5 use only candles strictly before the trigger; no future leakage']};
  await mkdir(OUT_DIR,{recursive:true}); const out=resolve(OUT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: n=${rows.length} avgR=${report.baseline.avgR.toFixed(4)} PF=${report.baseline.PF?.toFixed(4)??'n/a'}`);
  for(const f of fields){const s=report.featureSummary[f];console.log(`  ${f}: all_p50=${s.all.p50??'n/a'} win_p50=${s.winners.p50??'n/a'} lose_p50=${s.losers.p50??'n/a'} win_mean=${s.winners.mean??'n/a'} lose_mean=${s.losers.mean??'n/a'}`);}
  console.log(`Report -> ${out}`);
}
await run('1min'); await run('5min');
