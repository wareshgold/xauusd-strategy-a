import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-opportunity-delayed-reentry-forensics');
const TIMEFRAMES = ['1min', '5min'];
const COMPRESSION_LOOKBACK = 5;
const MEDIAN_TR_LOOKBACK = 20;

function median(a){const x=a.filter(Number.isFinite).sort((u,v)=>u-v);if(!x.length)return null;const m=Math.floor(x.length/2);return x.length%2?x[m]:(x[m-1]+x[m])/2;}
function quantile(a,q){const x=a.filter(Number.isFinite).sort((u,v)=>u-v);if(!x.length)return null;const p=(x.length-1)*q,l=Math.floor(p),h=Math.ceil(p);return l===h?x[l]:x[l]+(x[h]-x[l])*(p-l);}
function tr(c){return Math.max(c.high-c.low,Math.abs(c.high-c.open),Math.abs(c.low-c.open));}
function sign(d){return d==='BUY'||d==='BULLISH'?1:-1;}
function summarize(rows){const a=rows.filter(r=>Number.isFinite(r.rMultiple));const gp=a.filter(r=>r.rMultiple>0).reduce((s,r)=>s+r.rMultiple,0);const gl=a.filter(r=>r.rMultiple<0).reduce((s,r)=>s-r.rMultiple,0);return{n:a.length,wins:a.filter(r=>r.rMultiple>0).length,losses:a.filter(r=>r.rMultiple<0).length,PF:gl?gp/gl:null,avgR:a.length?a.reduce((s,r)=>s+r.rMultiple,0)/a.length:0,totalR:a.reduce((s,r)=>s+r.rMultiple,0)};}
function dd(rows){let e=0,p=0,m=0;for(const r of rows.filter(x=>Number.isFinite(x.rMultiple))){e+=r.rMultiple;p=Math.max(p,e);m=Math.max(m,p-e);}return m;}
function medianTR(candles,i,n){if(i<n)return null;return median(candles.slice(i-n,i).map(tr));}
function band(v,bands){for(const [name,lo,hi] of bands)if(v>=lo&&v<hi)return name;return 'NA';}
const RETRACE_BANDS=[['LT_0.25',0,0.25],['0.25_0.50',0.25,0.50],['0.50_0.75',0.50,0.75],['0.75_1.00',0.75,1.00],['GE_1.00',1,Infinity]];
const COMP_BANDS=[['LT_0.75',0,0.75],['0.75_1.00',0.75,1.00],['1.00_1.25',1,1.25],['GE_1.25',1.25,Infinity]];

function enrich(candles,t){
  const ei=t.entryIndex, si=t.spikeIndex;
  if(!Number.isInteger(ei)||!Number.isInteger(si)||si>=ei||!candles[si]||!candles[ei])return null;
  const s=sign(t.direction), spike=candles[si];
  const base=medianTR(candles,si,MEDIAN_TR_LOOKBACK);
  const spikeTR=tr(spike);
  const start=si+1,end=ei-1, n=Math.max(0,end-start+1);
  const post=candles.slice(start,end+1);
  if(!post.length)return {...t,postSpikeBars:0,pullbackFraction:null,compressionRatio:null,entryDistanceFromSpikeExtreme:null,postSpikeMaxFavorableTR:null};
  const spikeExtreme=s>0?spike.high:spike.low;
  const spikeClose=spike.close;
  const postExtreme=s>0?Math.max(...post.map(c=>c.high)):Math.min(...post.map(c=>c.low));
  const favorableMove=Math.abs(spikeExtreme-spikeClose);
  const retraceNumerator=s>0?Math.max(0,spikeExtreme-Math.min(...post.map(c=>c.low))):Math.max(0,Math.max(...post.map(c=>c.high))-spikeExtreme);
  const pullbackFraction=favorableMove>0?retraceNumerator/favorableMove:null;
  const recent=post.slice(-Math.min(COMPRESSION_LOOKBACK,post.length));
  const recentTR=median(recent.map(tr));
  const preTR=medianTR(candles,start,MEDIAN_TR_LOOKBACK);
  const compressionRatio=recentTR!=null&&preTR?recentTR/preTR:null;
  const entry=candles[ei];
  const entryDistanceFromSpikeExtreme=Math.abs((s>0?entry.close-spikeExtreme:spikeExtreme-entry.close))/(base||spikeTR||1);
  const postSpikeMaxFavorableTR=base?Math.abs(postExtreme-spikeClose)/base:null;
  const postSpikeMaxAdverseTR=base?(s>0?Math.max(...post.map(c=>spikeClose-c.low)):Math.max(...post.map(c=>c.high-spikeClose)))/base:null;
  const hasPullback=pullbackFraction!=null&&pullbackFraction>=0.25;
  const hasDeepPullback=pullbackFraction!=null&&pullbackFraction>=0.50;
  const compressed=compressionRatio!=null&&compressionRatio<0.75;
  const delayedReentry=n>=3;
  return {...t,postSpikeBars:n,pullbackFraction, pullbackBand:pullbackFraction==null?'NA':band(pullbackFraction,RETRACE_BANDS),compressionRatio,compressionBand:compressionRatio==null?'NA':band(compressionRatio,COMP_BANDS),entryDistanceFromSpikeExtreme,postSpikeMaxFavorableTR,postSpikeMaxAdverseTR,hasPullback,hasDeepPullback,compressed,delayedReentry,delayedPullbackCompression:delayedReentry&&hasPullback&&compressed};
}

async function run(tf){
  const candles=(await load(resolve(ROOT,`data/historical/xauusd-${tf}.json`))).candles;
  const src=await load(resolve(ROOT,`data/reports/strategy-a-opportunity-window-structural-forensics/${tf}.json`));
  const trades=(src.tradeRows||[]).filter(t=>t.opportunityWindow!=='OTHER'&&Number.isFinite(t.rMultiple)).map(t=>enrich(candles,t)).filter(Boolean);
  const oos=trades.slice(Math.floor(trades.length*.5));
  const candidates=[
    ['DELAY_GE3',r=>r.delayedReentry],
    ['PULLBACK_GE25',r=>r.hasPullback],
    ['PULLBACK_GE50',r=>r.hasDeepPullback],
    ['COMPRESSION_LT75',r=>r.compressed],
    ['DELAY+PULLBACK',r=>r.delayedReentry&&r.hasPullback],
    ['DELAY+COMPRESSION',r=>r.delayedReentry&&r.compressed],
    ['DELAY+PULLBACK+COMPRESSION',r=>r.delayedPullbackCompression],
  ];
  const summarizeCandidate=(name,p)=>{const all=trades.filter(p),oo=oos.filter(p),no=oos.filter(r=>!p(r));return{name,all:{...summarize(all),maxDD:dd(all)},oos:{...summarize(oo),maxDD:dd(oo)},oosComplement:{...summarize(no),maxDD:dd(no)}};};
  const byCandidate=candidates.map(([n,p])=>summarizeCandidate(n,p));
  const byPullback=RETRACE_BANDS.map(([name])=>{const all=trades.filter(r=>r.pullbackBand===name),oo=oos.filter(r=>r.pullbackBand===name);return{name,all:summarize(all),oos:summarize(oo)};});
  const byCompression=COMP_BANDS.map(([name])=>{const all=trades.filter(r=>r.compressionBand===name),oo=oos.filter(r=>r.compressionBand===name);return{name,all:summarize(all),oos:summarize(oo)};});
  const byDirection=['BUY','SELL'].map(d=>{const a=trades.filter(r=>r.direction===d),oo=oos.filter(r=>r.direction===d);return{direction:d,all:summarize(a),oos:summarize(oo),delayedPullbackCompression:summarize(oo.filter(r=>r.delayedPullbackCompression))};});
  const byWindow=[...new Set(trades.map(r=>r.opportunityWindow))].map(w=>{const a=trades.filter(r=>r.opportunityWindow===w),oo=oos.filter(r=>r.opportunityWindow===w);return{window:w,all:summarize(a),oos:summarize(oo),delayedPullbackCompression:summarize(oo.filter(r=>r.delayedPullbackCompression))};});
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_OPPORTUNITY_DELAYED_REENTRY_FORENSICS',timeframe,methodology:{scope:'Opportunity Window trades that have a classified pre-entry spike',spike:'existing structural-forensics spikeIndex; no new spike threshold',pullback:'post-spike excursion against spike-direction extreme before entry',compression:'median TR of last up to 5 pre-entry bars divided by preceding 20-bar median TR',delayed:'at least 3 complete bars between spike and entry',lookahead:'all derived features use candles strictly before entry',oos:'chronological second half of Opportunity Window trades',decisionRule:'forensic only; no threshold or trading rule selected from these results',minimumSample:'candidates with very small OOS n are hypothesis-generating only'},coverage:{trades:trades.length,oos:oos.length,spikeKnown:trades.filter(r=>Number.isInteger(r.spikeIndex)).length},overall:{...summarize(trades),maxDD:dd(trades)},oos:{...summarize(oos),maxDD:dd(oos)},byCandidate,byPullback,byCompression,byDirection,byWindow,tradeRows:trades,nextResearchQuestion:'If any delayed re-entry pattern survives OOS with adequate n, validate it on a third untouched chronological holdout and test whether the edge is independent of direction/session.'};
  await mkdir(REPORT_DIR,{recursive:true});const out=resolve(REPORT_DIR,`${tf}.json`);await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: trades=${trades.length} OOS=${oos.length}`);
  for(const x of byCandidate)console.log(`  ${x.name}: all n=${x.all.n} PF=${x.all.PF?.toFixed(4)??'n/a'} | OOS n=${x.oos.n} PF=${x.oos.PF?.toFixed(4)??'n/a'} avgR=${x.oos.avgR.toFixed(4)} | complement PF=${x.oosComplement.PF?.toFixed(4)??'n/a'}`);
  console.log('  OOS direction/window candidates:');for(const x of byDirection)console.log(`    ${x.direction}: n=${x.oos.n} PF=${x.oos.PF?.toFixed(4)??'n/a'} delayedPullbackCompression n=${x.delayedPullbackCompression.n} PF=${x.delayedPullbackCompression.PF?.toFixed(4)??'n/a'}`);for(const x of byWindow)console.log(`    ${x.window}: n=${x.oos.n} PF=${x.oos.PF?.toFixed(4)??'n/a'} delayedPullbackCompression n=${x.delayedPullbackCompression.n} PF=${x.delayedPullbackCompression.PF?.toFixed(4)??'n/a'}`);
  console.log(`Report -> ${out}`);
}
async function load(path){return JSON.parse(await readFile(path,'utf8'));}
for(const tf of TIMEFRAMES)await run(tf);
