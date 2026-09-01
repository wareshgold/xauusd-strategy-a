import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const OUT=resolve(ROOT,'data/reports/strategy-a-weekly-reopen-vs-normal');
const WINDOWS=[5,10,15,20,30,45,60];
const TF=[{name:'1min',minutes:1},{name:'5min',minutes:5}];
const LOOKBACK=60;
const BINS=[0,5,10,15,20,30,45,60];
const mean=a=>{a=a.filter(Number.isFinite);return a.length?a.reduce((s,x)=>s+x,0)/a.length:null};
const median=a=>{a=a.filter(Number.isFinite).sort((x,y)=>x-y);if(!a.length)return null;const m=Math.floor(a.length/2);return a.length%2?a[m]:(a[m-1]+a[m])/2};
const q=(a,p)=>{a=a.filter(Number.isFinite).sort((x,y)=>x-y);if(!a.length)return null;const x=(a.length-1)*p,l=Math.floor(x),h=Math.ceil(x);return l===h?a[l]:a[l]+(a[h]-a[l])*(x-l)};
const parse=s=>{const d=new Date(s.replace(' ','T')+'Z');return Number.isNaN(d.getTime())?null:d};
const tr=(c,p)=>Math.max(c.high-c.low,Math.abs(c.high-p),Math.abs(c.low-p));
function profile(candles, start, end){
 const base=median(candles.slice(Math.max(1,start-LOOKBACK),start).map((c,i)=>tr(c,candles[Math.max(0,start-LOOKBACK)+i-1]?.close)).filter(Number.isFinite));
 const rows=[];
 for(let i=start;i<end;i++){const p=i?candles[i-1].close:null;if(!p)continue;const t=tr(candles[i],p);rows.push({tr:t,score:base?t/base:null});}
 return {meanTR:mean(rows.map(x=>x.tr)),p90TR:q(rows.map(x=>x.tr),.9),meanScore:mean(rows.map(x=>x.score)),p90Score:q(rows.map(x=>x.score),.9)};
}
function run(candles,minutes){
 const events=[]; for(let i=0;i<candles.length;i++){const d=parse(candles[i].timestamp);if(d?.getUTCDay()===0&&d.getUTCHours()===22&&d.getUTCMinutes()===0)events.push(i);}
 const reopen=WINDOWS.map(w=>{const vals=[];for(const i of events){const end=Math.min(candles.length,i+Math.ceil(w/minutes));vals.push(profile(candles,i,end));}return {minutes:w,events:vals.length,meanTR:mean(vals.map(x=>x.meanTR)),p90TR:q(vals.map(x=>x.p90TR),.9),meanScore:mean(vals.map(x=>x.meanScore)),p90Score:q(vals.map(x=>x.p90Score),.9)};});
 const normalByHour={};
 for(let h=0;h<24;h++){const vals=[];for(let i=0;i<candles.length;i++){const d=parse(candles[i].timestamp);if(!d||d.getUTCHours()!==h||d.getUTCDay()===0)continue;if(i<LOOKBACK)continue;const base=median(candles.slice(i-LOOKBACK,i).map((c,j)=>j?tr(c,candles[i-LOOKBACK+j-1].close):null));const t=tr(candles[i],candles[i-1].close);if(base)vals.push(t/base);}normalByHour[String(h)]={bars:vals.length,meanScore:mean(vals),p90Score:q(vals,.9)};}
 const reopenScores=events.map(i=>{const end=Math.min(candles.length,i+Math.ceil(60/minutes));return profile(candles,i,end).meanScore}).filter(Number.isFinite);
 const normalScores=[];for(let i=LOOKBACK;i<candles.length;i++){const d=parse(candles[i].timestamp);if(!d||d.getUTCDay()===0&&d.getUTCHours()===22)continue;const base=median(candles.slice(i-LOOKBACK,i).map((c,j)=>j?tr(c,candles[i-LOOKBACK+j-1].close):null));if(base)normalScores.push(tr(candles[i],candles[i-1].close)/base);}
 return {weeklyReopenEvents:events.length,reopenWindows:reopen,reopen60mMeanScore:mean(reopenScores),normalBarMeanScore:mean(normalScores),normalBarP90Score:q(normalScores,.9),normalByHourUTC:normalByHour};
}
await mkdir(OUT,{recursive:true});const result={generatedAt:new Date().toISOString(),definition:'Sunday 22:00 UTC weekly reopen compared with non-Sunday bars. Reopen impact measured without deleting candles or changing strategy thresholds.',timeframes:{}};
for(const tf of TF){const d=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf.name}.json`),'utf8'));result.timeframes[tf.name]=run(d.candles,tf.minutes);console.log(`\n${tf.name} events=${result.timeframes[tf.name].weeklyReopenEvents}`);for(const x of result.timeframes[tf.name].reopenWindows)console.log(`${x.minutes}m meanScore=${x.meanScore?.toFixed(2)} p90=${x.p90Score?.toFixed(2)}`);console.log(`normal bar mean=${result.timeframes[tf.name].normalBarMeanScore?.toFixed(2)} p90=${result.timeframes[tf.name].normalBarP90Score?.toFixed(2)}`);}
await writeFile(resolve(OUT,'summary.json'),JSON.stringify(result,null,2)+'\n');console.log(`Report -> ${resolve(OUT,'summary.json')}`);
