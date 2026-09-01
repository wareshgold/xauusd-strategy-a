import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-normal-regime-spike-opportunity');
const TIMEFRAMES = ['1min', '5min'];
const LOOKBACK = 60;
const HORIZONS = [5, 10, 15, 30, 60];
const SPIKE_QUANTILES = [0.80, 0.90, 0.95];

function median(a){const v=a.filter(Number.isFinite).sort((x,y)=>x-y);if(!v.length)return null;const m=Math.floor(v.length/2);return v.length%2?v[m]:(v[m-1]+v[m])/2}
function q(a,p){const v=a.filter(Number.isFinite).sort((x,y)=>x-y);if(!v.length)return null;const x=(v.length-1)*p,l=Math.floor(x),h=Math.ceil(x);return l===h?v[l]:v[l]+(v[h]-v[l])*(x-l)}
function mean(a){const v=a.filter(Number.isFinite);return v.length?v.reduce((s,x)=>s+x,0)/v.length:null}
function parse(s){const d=new Date(s.includes('T')?s:s.replace(' ','T')+'Z');return Number.isNaN(d.getTime())?null:d}
function tr(c,p){return Math.max(c.high-c.low,Math.abs(c.high-p),Math.abs(c.low-p))}
function isSundayReopen(d){return d?.getUTCDay()===0&&d.getUTCHours()===22}
function summarize(a){return {n:a.length,mean:mean(a),p50:q(a,.5),p90:q(a,.9),p95:q(a,.95)}}

async function run(tf){
 const data=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8'));
 const candles=data.candles;
 const trv=candles.map((c,i)=>i?tr(c,candles[i-1].close):null);
 const score=candles.map((c,i)=>{if(i<LOOKBACK||!Number.isFinite(trv[i]))return null;const base=median(trv.slice(i-LOOKBACK,i));return base>0?trv[i]/base:null});
 const eligible=[];
 for(let i=LOOKBACK;i<candles.length;i++){const d=parse(candles[i].timestamp);if(!d||!Number.isFinite(score[i])||isSundayReopen(d))continue;eligible.push(i)}
 const cuts=Object.fromEntries(SPIKE_QUANTILES.map(p=>[String(p),q(eligible.map(i=>score[i]),p)]));
 const horizons={};
 for(const p of SPIKE_QUANTILES){const cut=cuts[String(p)];horizons[String(p)]={};for(const h of HORIZONS){const rows=[];for(const i of eligible){if(score[i]<cut)continue;const bars=Math.max(1,Math.round(h/(tf==='1min'?1:5)));const end=Math.min(candles.length,i+bars+1);const entry=candles[i].close;let maxUp=0,maxDown=0;for(let j=i+1;j<end;j++){maxUp=Math.max(maxUp,(candles[j].high-entry)/entry);maxDown=Math.max(maxDown,(entry-candles[j].low)/entry)}rows.push({maxUp,maxDown});}horizons[String(p)][String(h)]={events:rows.length,up:summarize(rows.map(x=>x.maxUp)),down:summarize(rows.map(x=>x.maxDown))}}}
 const eventRows=eligible.filter(i=>score[i]>=cuts['0.9']).map(i=>({index:i,timestamp:candles[i].timestamp,score:score[i],tr:trv[i],hourUTC:parse(candles[i].timestamp)?.getUTCHours(),close:candles[i].close}));
 const report={generatedAt:new Date().toISOString(),timeframe:tf,data:{symbol:data.symbol,source:data.source,candles:candles.length,from:candles[0]?.timestamp,to:candles.at(-1)?.timestamp},definition:'Normal-regime spike opportunity diagnostic. Sunday 22:00 UTC weekly reopen bars are excluded from the opportunity population but remain in the raw dataset. No production threshold is selected.',eligibleBars:eligible.length,spikeCuts:cuts,horizons,topP90Events:eventRows.slice(0,200),decision:{status:'RESEARCH_ONLY',nextGate:'Join spike events to existing Strategy A structural setup outcomes and compare conditional expectancy against matched non-spike opportunities.',warning:'This report measures volatility continuation only; it does not claim profitability or create BUY/SELL signals.'}};
 await mkdir(OUT,{recursive:true});const out=resolve(OUT,`${tf}.json`);await writeFile(out,JSON.stringify(report,null,2)+'\n');console.log(`${tf}: eligible=${eligible.length} p80=${cuts['0.8']?.toFixed(4)} p90=${cuts['0.9']?.toFixed(4)} p95=${cuts['0.95']?.toFixed(4)} p90events=${eventRows.length}`);for(const h of HORIZONS){const x=horizons['0.9'][String(h)];console.log(`  P90 ${h}m events=${x.events} upP90=${(x.up.p90*100).toFixed(3)}% downP90=${(x.down.p90*100).toFixed(3)}%`)}console.log(`Report -> ${out}`)
}
for(const tf of TIMEFRAMES)await run(tf);