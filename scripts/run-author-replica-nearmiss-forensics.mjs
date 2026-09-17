import fs from 'node:fs';

const DATA = 'data/historical/xauusd-1min.json';
const OUT = 'artifacts/sp2l-author-replica-nearmiss-forensics.json';
const raw = JSON.parse(fs.readFileSync(DATA, 'utf8'));
const candles = (raw.candles ?? raw).map(c => ({
  time:c.timestamp ?? c.datetime ?? c.time,
  open:Number(c.open), high:Number(c.high), low:Number(c.low), close:Number(c.close),
})).filter(c => [c.open,c.high,c.low,c.close].every(Number.isFinite));
const spikeMultiplier = 1.5;
const pGap = 1.0;
const maxSlPrice = 10.0;
const labels = ['trigger_break','correction_close_vs_spike','correction_open_vs_spike','spike_close_vs_A','spike_open_vs_A','correction_body_direction','spike_body_direction','A_body_direction','p_gap','spike_gt_1_5x_correction','spike_gt_1_5x_A','spike_gt_1_5x_trigger'];

function inspect(i, side) {
  const a=candles[i-3], s=candles[i-2], c=candles[i-1], t=candles[i];
  const spikeBody=Math.abs(s.close-s.open), correctionBody=Math.abs(c.close-c.open), aBody=Math.abs(a.close-a.open), triggerBody=Math.abs(t.close-t.open);
  const buy = [
    t.low<c.low, c.close>s.close, c.open>s.open, s.close>a.close, s.open>a.open,
    c.close>c.open, s.close>s.open, a.close>a.open, c.low>a.high+pGap,
    spikeBody>spikeMultiplier*correctionBody, spikeBody>spikeMultiplier*aBody, spikeBody>spikeMultiplier*triggerBody,
  ];
  const sell = [
    t.high>c.high, c.close<s.close, s.open>c.open, s.close<a.close, s.open<a.open,
    c.close<c.open, s.close<s.open, a.close<a.open, c.high<a.low-pGap,
    spikeBody>spikeMultiplier*correctionBody, spikeBody>spikeMultiplier*aBody, spikeBody>spikeMultiplier*triggerBody,
  ];
  const x=side==='BUY'?buy:sell;
  const entry=side==='BUY'?t.low:t.high, stop=side==='BUY'?a.low:a.high;
  const risk=side==='BUY'?entry-stop:stop-entry;
  const margins = side==='BUY' ? {
    pGap:c.low-a.high,
    spikeVsCorrection:spikeBody/(correctionBody||Number.MIN_VALUE),
    spikeVsA:spikeBody/(aBody||Number.MIN_VALUE),
    spikeVsTrigger:spikeBody/(triggerBody||Number.MIN_VALUE),
  } : {
    pGap:a.low-c.high,
    spikeVsCorrection:spikeBody/(correctionBody||Number.MIN_VALUE),
    spikeVsA:spikeBody/(aBody||Number.MIN_VALUE),
    spikeVsTrigger:spikeBody/(triggerBody||Number.MIN_VALUE),
  };
  const failed=labels.map((label,j)=>({index:j+1,label,pass:x[j]})).filter(z=>!z.pass).map(z=>z.index);
  return {index:i,time:t.time,side,failedCount:failed.length,failed,entry,stopLoss:stop,risk,spikeBody,correctionBody,aBody,triggerBody,...margins,ohlc:{a,s,c,t}};
}

function collect(side) {
  const rows=[];
  for(let i=3;i<candles.length;i++) {
    const r=inspect(i,side);
    if(r.failedCount<=2) rows.push(r);
  }
  rows.sort((a,b)=>a.failedCount-b.failedCount || a.index-b.index);
  return rows.slice(0,50);
}

function exactPgapNearMisses(side) {
  const rows=[];
  for(let i=3;i<candles.length;i++) {
    const r=inspect(i,side);
    const pg=r.pGap;
    if(pg>0 && pg<=2) rows.push(r);
  }
  rows.sort((a,b)=>b.pGap-a.pGap);
  return rows.slice(0,50);
}

const result={
  methodology:'RESEARCH-ONLY near-miss forensic analysis of the author implementation candidate. Does not modify or infer canonical geometry.',
  data:{source:raw.source,symbol:raw.symbol,timeframe:raw.timeframe,timezone:raw.timezone,candles:candles.length,from:candles[0].time,to:candles.at(-1).time},
  config:{pGapPrice:pGap,spikeMultiplier,maxSlPrice},
  nearMisses:{BUY:collect('BUY'),SELL:collect('SELL')},
  positivePGapWindow:{BUY:exactPgapNearMisses('BUY'),SELL:exactPgapNearMisses('SELL')},
};
fs.mkdirSync('artifacts',{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
