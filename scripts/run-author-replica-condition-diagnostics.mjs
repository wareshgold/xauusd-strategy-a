import fs from 'node:fs';

const DATA = 'data/historical/xauusd-1min.json';
const OUT = 'artifacts/sp2l-author-replica-condition-diagnostics.json';
const raw = JSON.parse(fs.readFileSync(DATA, 'utf8'));
const candles = (raw.candles ?? raw).map(c => ({
  time:c.timestamp ?? c.datetime ?? c.time,
  open:Number(c.open), high:Number(c.high), low:Number(c.low), close:Number(c.close),
})).filter(c => [c.open,c.high,c.low,c.close].every(Number.isFinite));
const spikeMultiplier = 1.5;
const thresholds = [0,0.25,0.5,1,1.5,2];

function conditions(i,pGap) {
  if(i<3) return null;
  const a=candles[i-3], s=candles[i-2], c=candles[i-1], t=candles[i];
  const buy=[
    t.low<c.low,
    c.close>s.close,
    c.open>s.open,
    s.close>a.close,
    s.open>a.open,
    c.close>c.open,
    s.close>s.open,
    a.close>a.open,
    c.low>a.high+pGap,
    (s.close-s.open)>spikeMultiplier*(c.close-c.open),
    (s.close-s.open)>spikeMultiplier*(a.close-a.open),
    (s.close-s.open)>spikeMultiplier*(t.close-t.open),
  ];
  const sell=[
    t.high>c.high,
    c.close<s.close,
    c.open<s.open,
    s.close<a.close,
    s.open<a.open,
    c.close<c.open,
    s.close<s.open,
    a.close<a.open,
    c.high<a.low-pGap,
    (s.open-s.close)>spikeMultiplier*(c.open-c.close),
    (s.open-s.close)>spikeMultiplier*(a.open-a.close),
    (s.open-s.close)>spikeMultiplier*(t.open-t.close),
  ];
  return {buy,sell};
}

const labels=['trigger breaks correction','correction close beyond spike','correction open beyond spike','spike close beyond A','spike open beyond A','correction bullish/bearish body','spike bullish/bearish body','A bullish/bearish body','P-Gap','spike > 1.5x correction','spike > 1.5x A','spike > 1.5x trigger'];
function summarize(side,pGap){
  const totals=Array(12).fill(0), survivors=Array(12).fill(0);
  let full=0;
  for(let i=3;i<candles.length;i++){
    const x=conditions(i,pGap)?.[side];
    if(!x) continue;
    for(let j=0;j<12;j++){ if(x[j]) totals[j]++; if(x.slice(0,j+1).every(Boolean)) survivors[j]++; }
    if(x.every(Boolean)) full++;
  }
  return {pGapPrice:pGap, side, full, conditions:labels.map((label,j)=>({index:j+1,label,pass:totals[j],prefixSurvivors:survivors[j]}))};
}
const result={methodology:'RESEARCH-ONLY condition-by-condition diagnostics of the author implementation candidate; no canonical inference.',data:{source:raw.source,symbol:raw.symbol,timeframe:raw.timeframe,timezone:raw.timezone,candles:candles.length,from:candles[0].time,to:candles.at(-1).time},spikeMultiplier,thresholds,diagnostics:thresholds.flatMap(p=>[summarize('buy',p),summarize('sell',p)])};
fs.mkdirSync('artifacts',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
