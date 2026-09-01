import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-weekly-reopen-impact');
const WINDOWS = [0, 5, 10, 15, 20, 30, 45, 60];
const TIMEFRAMES = [
  { name: '1min', minutes: 1 },
  { name: '5min', minutes: 5 }
];
const LOOKBACK = 60;

function median(a) { const v=a.filter(Number.isFinite).sort((x,y)=>x-y); if(!v.length)return null; const m=Math.floor(v.length/2); return v.length%2?v[m]:(v[m-1]+v[m])/2; }
function mean(a) { const v=a.filter(Number.isFinite); return v.length?v.reduce((s,x)=>s+x,0)/v.length:null; }
function quantile(a,q) { const v=a.filter(Number.isFinite).sort((x,y)=>x-y); if(!v.length)return null; const p=(v.length-1)*q,l=Math.floor(p),h=Math.ceil(p); return l===h?v[l]:v[l]+(v[h]-v[l])*(p-l); }
function parseTs(s){const d=new Date(s.replace(' ','T')+'Z'); return Number.isNaN(d.getTime())?null:d;}
function tr(c, prevClose){ return Math.max(c.high-c.low, Math.abs(c.high-prevClose), Math.abs(c.low-prevClose)); }

function analyse(candles, tfMinutes) {
  const idx = new Map(candles.map((c,i)=>[c.timestamp,i]));
  const events = [];
  for (let i=0;i<candles.length;i++) {
    const d=parseTs(candles[i].timestamp);
    if (!d || d.getUTCDay()!==0 || d.getUTCHours()!==22 || d.getUTCMinutes()!==0) continue;
    events.push(i);
  }
  const rows = [];
  for (const start of events) {
    const baseline=[];
    for(let j=Math.max(1,start-LOOKBACK);j<start;j++) baseline.push(tr(candles[j],candles[j-1].close));
    const base=median(baseline);
    const startTs=parseTs(candles[start].timestamp);
    const metrics={};
    for(const mins of WINDOWS){
      const end=startTs.getTime()+mins*60000;
      const slice=[];
      for(let j=start;j<candles.length;j++){
        const d=parseTs(candles[j].timestamp); if(!d)continue;
        if(d.getTime()>=startTs.getTime() && d.getTime()<end) slice.push(j); else if(d.getTime()>=end) break;
      }
      const trs=slice.map(j=>tr(candles[j],j?candles[j-1].close:null)).filter(Number.isFinite);
      const scores=base?trs.map(x=>x/base):[];
      metrics[String(mins)]={bars:slice.length,meanTR:mean(trs),p90TR:quantile(trs,.9),maxTR:trs.length?Math.max(...trs):null,meanScore:mean(scores),p90Score:quantile(scores,.9),maxScore:scores.length?Math.max(...scores):null};
    }
    rows.push({timestamp:candles[start].timestamp, baselineMedianTR:base, metrics});
  }
  const aggregate={};
  for(const mins of WINDOWS){const a=rows.map(r=>r.metrics[String(mins)]); aggregate[String(mins)]={events:rows.length,meanTR:mean(a.map(x=>x.meanTR)),p90TR:quantile(a.map(x=>x.p90TR),.9),meanScore:mean(a.map(x=>x.meanScore)),p90Score:quantile(a.map(x=>x.p90Score),.9),maxScore: a.reduce((m,x)=>Math.max(m,x.maxScore??-Infinity),-Infinity)};}
  return {weeklyReopenEvents:events.length,events:rows,aggregate};
}

await mkdir(OUT,{recursive:true});
const result={generatedAt:new Date().toISOString(),definition:'Sunday 22:00 UTC reopen; measure post-reopen volatility against the 60-bar pre-event median True Range. No candles are removed and no strategy threshold is changed.',timeframes:{}};
for(const tf of TIMEFRAMES){
 const d=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf.name}.json`),'utf8'));
 result.timeframes[tf.name]=analyse(d.candles,tf.minutes);
 await writeFile(resolve(OUT,`${tf.name}.json`),JSON.stringify(result.timeframes[tf.name],null,2)+'\n');
 const a=result.timeframes[tf.name].aggregate;
 console.log(`\n${tf.name}: weeklyReopenEvents=${result.timeframes[tf.name].weeklyReopenEvents}`);
 for(const mins of WINDOWS){const x=a[String(mins)]; console.log(`${mins}m meanTR=${x.meanTR?.toFixed(4)} p90TR=${x.p90TR?.toFixed(4)} meanScore=${x.meanScore?.toFixed(2)} p90Score=${x.p90Score?.toFixed(2)} maxScore=${x.maxScore?.toFixed(2)}`);}
}
await writeFile(resolve(OUT,'summary.json'),JSON.stringify(result,null,2)+'\n');
console.log(`Report -> ${resolve(OUT,'summary.json')}`);
