import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-opportunity-window-structural-forensics');
const TIMEFRAMES = ['1min', '5min'];
const LOOKBACK = 60;
const STRUCTURE_LOOKBACK = 5;
const MEDIAN_TR_LOOKBACK = 20;
const MAX_SEQUENCE_BARS = 12;
const MAX_RETEST_BARS = 8;
const OOS_SPLIT = 0.5;

function median(values) { const a = values.filter(Number.isFinite).sort((x,y)=>x-y); if (!a.length) return null; const m=Math.floor(a.length/2); return a.length%2?a[m]:(a[m-1]+a[m])/2; }
function quantile(values,q) { const a=values.filter(Number.isFinite).sort((x,y)=>x-y); if(!a.length)return null; const p=(a.length-1)*q,lo=Math.floor(p),hi=Math.ceil(p); return lo===hi?a[lo]:a[lo]+(a[hi]-a[lo])*(p-lo); }
function parseTime(value) { const d=new Date(value.includes('T')?value:`${value.replace(' ','T')}Z`); return Number.isNaN(d.getTime())?null:d; }
function minuteOfDay(value) { const d=parseTime(value); return d?d.getUTCHours()*60+d.getUTCMinutes():null; }
function opportunityWindow(m) { if(m==null)return'UNKNOWN'; if(m>=660&&m<780)return'PRE_NY_BUILD'; if(m>=780&&m<840)return'NY_OPEN_WINDOW'; if(m>=840&&m<960)return'LONDON_NY_OVERLAP'; if(m>=420&&m<540)return'LONDON_OPEN_WINDOW'; return'OTHER'; }
function sign(direction) { return direction==='BUY'||direction==='BULLISH'?1:-1; }
function tr(c) { return Math.max(c.high-c.low,Math.abs(c.high-c.open),Math.abs(c.low-c.open)); }
function bodyFraction(c) { const r=c.high-c.low; return r>0?Math.abs(c.close-c.open)/r:0; }
function medianTR(candles,i,n) { if(i<n)return null; return median(candles.slice(i-n,i).map(tr)); }
function priorRange(candles,i,n) { if(i<n)return null; const s=candles.slice(i-n,i); return {high:Math.max(...s.map(c=>c.high)),low:Math.min(...s.map(c=>c.low))}; }
function sweep(candles,i,s) { const p=priorRange(candles,i,STRUCTURE_LOOKBACK),c=candles[i]; if(!p||!c)return false; return s>0?(c.low<p.low&&c.close>p.low):(c.high>p.high&&c.close<p.high); }
function bos(candles,i,s) { const p=priorRange(candles,i,STRUCTURE_LOOKBACK),c=candles[i]; if(!p||!c)return false; return s>0?c.close>p.high:c.close<p.low; }
function displacement(candles,i,s) { const c=candles[i],base=medianTR(candles,i,MEDIAN_TR_LOOKBACK); if(!c||!base)return false; return (s>0?c.close>c.open:c.close<c.open)&&tr(c)/base>=1.5&&bodyFraction(c)>=0.6; }
function expansion(candles,i) { const c=candles[i],base=medianTR(candles,i,MEDIAN_TR_LOOKBACK); return Boolean(c&&base&&tr(c)/base>=1.25); }
function fvg(candles,i,s) { if(i<2)return null; const a=candles[i-2],c=candles[i]; if(s>0&&c.low>a.high)return{low:a.high,high:c.low,index:i}; if(s<0&&c.high<a.low)return{low:c.high,high:a.low,index:i}; return null; }
function retest(candles,gap,s,entry) { if(!gap)return false; const end=Math.min(entry-1,gap.index+MAX_RETEST_BARS); for(let i=gap.index+1;i<=end;i++){const c=candles[i]; if(!c)continue; const touched=c.low<=gap.high&&c.high>=gap.low; const close=s>0?c.close>=gap.high:c.close<=gap.low; if(touched&&close)return true;} return false; }
function summarize(rows) { const u=rows.filter(x=>Number.isFinite(x.rMultiple)); const win=u.filter(x=>x.rMultiple>0).reduce((s,x)=>s+x.rMultiple,0); const loss=u.filter(x=>x.rMultiple<0).reduce((s,x)=>s+Math.abs(x.rMultiple),0); return {n:u.length,wins:u.filter(x=>x.rMultiple>0).length,losses:u.filter(x=>x.rMultiple<0).length,PF:loss?win/loss:null,avgR:u.length?u.reduce((s,x)=>s+x.rMultiple,0)/u.length:0,totalR:u.reduce((s,x)=>s+x.rMultiple,0)}; }
function dd(rows) { let eq=0,peak=0,max=0; for(const x of rows.filter(r=>Number.isFinite(r.rMultiple))){eq+=x.rMultiple;peak=Math.max(peak,eq);max=Math.max(max,peak-eq);} return max; }

function classify(candles, trade, spikeCut) {
  const ei=trade.entryIndex; if(!Number.isInteger(ei)||!candles[ei])return null; const s=sign(trade.direction); const window=opportunityWindow(minuteOfDay(trade.entryTime));
  const start=Math.max(LOOKBACK,ei-MAX_SEQUENCE_BARS), end=ei-1;
  let spikeIndex=null,sweepIndex=null,bosIndex=null,displacementIndex=null,expansionIndex=null,gap=null;
  for(let i=start;i<=end;i++){
    const base=medianTR(candles,i,LOOKBACK); const score=base?tr(candles[i])/base:null;
    if(spikeIndex==null&&Number.isFinite(score)&&score>=spikeCut)spikeIndex=i;
    if(sweepIndex==null&&sweep(candles,i,s))sweepIndex=i;
    if(bosIndex==null&&bos(candles,i,s))bosIndex=i;
    if(displacementIndex==null&&displacement(candles,i,s))displacementIndex=i;
    if(expansionIndex==null&&expansion(candles,i))expansionIndex=i;
    if(!gap){const g=fvg(candles,i,s);if(g)gap=g;}
  }
  const fvgIndex=gap?.index??null; const fvgRetest=retest(candles,gap,s,ei);
  const ordered=[spikeIndex,sweepIndex,bosIndex,displacementIndex,expansionIndex,fvgIndex]; let prev=-1,sequenceLength=0;
  for(const idx of ordered)if(idx!=null&&idx>prev){sequenceLength++;prev=idx;}
  const sequenceComplete=spikeIndex!=null&&sweepIndex!=null&&bosIndex!=null&&displacementIndex!=null&&fvgIndex!=null&&fvgRetest;
  return {...trade,opportunityWindow:window,opportunitySpike:window!=='OTHER'&&spikeIndex!=null,spikeIndex,sweepIndex,bosIndex,displacementIndex,expansionIndex,fvgIndex,fvgRetest,sequenceLength,sequenceComplete,structuralCount:[sweepIndex,bosIndex,displacementIndex,expansionIndex,fvgIndex].filter(x=>x!=null).length};
}
async function load(path){return JSON.parse(await readFile(path,'utf8'));}

async function run(timeframe){
  const candles=(await load(resolve(ROOT,`data/historical/xauusd-${timeframe}.json`))).candles;
  const baseline=await load(resolve(ROOT,`data/reports/strategy-a-baseline/${timeframe}.json`));
  const scores=[]; for(let i=LOOKBACK;i<candles.length;i++){const b=medianTR(candles,i,LOOKBACK);if(b)scores.push(tr(candles[i])/b);} const spikeCut=quantile(scores,.9);
  const trades=baseline.trades.filter(t=>Number.isFinite(t.rMultiple)&&Number.isInteger(t.entryIndex)).map(t=>classify(candles,t,spikeCut)).filter(Boolean);
  const opportunity=trades.filter(t=>t.opportunityWindow!=='OTHER'), complete=trades.filter(t=>t.sequenceComplete);
  const names=['LONDON_OPEN_WINDOW','PRE_NY_BUILD','NY_OPEN_WINDOW','LONDON_NY_OVERLAP','OTHER'];
  const byWindow=names.map(name=>{const rows=trades.filter(t=>t.opportunityWindow===name),sp=rows.filter(t=>t.opportunitySpike);return{name,...summarize(rows),maxDD:dd(rows),spikeN:sp.length,spikePF:summarize(sp).PF,spikeAvgR:summarize(sp).avgR};});
  const features=['opportunitySpike','sweepIndex','bosIndex','displacementIndex','expansionIndex','fvgIndex','fvgRetest','sequenceComplete'];
  const byFeature=features.map(feature=>{const yes=trades.filter(t=>Boolean(t[feature])),no=trades.filter(t=>!Boolean(t[feature]));return{feature,YES:{...summarize(yes),maxDD:dd(yes)},NO:{...summarize(no),maxDD:dd(no)}};});
  const bySequenceLength=[...new Set(trades.map(t=>t.sequenceLength))].sort((a,b)=>a-b).map(n=>({minimumSequenceLength:n,...summarize(trades.filter(t=>t.sequenceLength>=n))}));
  const mid=Math.floor(trades.length*.5),oos=trades.slice(mid),oosOpportunity=oos.filter(t=>t.opportunityWindow!=='OTHER'),oosComplete=oos.filter(t=>t.sequenceComplete);
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_OPPORTUNITY_WINDOW_STRUCTURAL_FORENSICS',timeframe,data:{candles:candles.length,from:candles[0]?.timestamp??null,to:candles.at(-1)?.timestamp??null},methodology:{windowsUTC:{LONDON_OPEN_WINDOW:'07:00-09:00',PRE_NY_BUILD:'11:00-13:00',NY_OPEN_WINDOW:'13:00-14:00',LONDON_NY_OVERLAP:'14:00-16:00'},spike:'top 10% normalized true-range score vs preceding 60 bars',sweep:'preceding 5-bar extreme taken and close returned inside',bos:'close beyond preceding 5-bar extreme',displacement:'directional range >=1.5x preceding 20-bar median TR and body fraction >=0.60',expansion:'range >=1.25x preceding 20-bar median TR',fvg:'classic 3-candle directional imbalance',retest:'gap touched and directionally closed within 8 bars',lookahead:'features use candles strictly before entry; descriptive only'},thresholds:{spikeP90:spikeCut},overall:{...summarize(trades),maxDD:dd(trades)},opportunityOnly:{...summarize(opportunity),maxDD:dd(opportunity)},sequenceComplete:{...summarize(complete),maxDD:dd(complete)},byWindow,byFeature,bySequenceLength,oos:{overall:{...summarize(oos),maxDD:dd(oos)},opportunityOnly:{...summarize(oosOpportunity),maxDD:dd(oosOpportunity)},sequenceComplete:{...summarize(oosComplete),maxDD:dd(oosComplete)}},tradeRows:trades,nextResearchQuestion:'Find a compact ordered subset of spike + sweep + BOS/MSS + displacement + FVG/retest that remains positive OOS inside opportunity windows without forcing a daily signal quota.'};
  await mkdir(REPORT_DIR,{recursive:true}); const out=resolve(REPORT_DIR,`${timeframe}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${timeframe}: trades=${trades.length} spikeP90=${spikeCut?.toFixed(4)??'n/a'}`); console.log(`  opportunity-only: n=${opportunity.length} PF=${summarize(opportunity).PF?.toFixed(4)??'n/a'} avgR=${summarize(opportunity).avgR.toFixed(4)}`); console.log(`  sequence-complete: n=${complete.length} PF=${summarize(complete).PF?.toFixed(4)??'n/a'} avgR=${summarize(complete).avgR.toFixed(4)}`); for(const r of byWindow)console.log(`  ${r.name}: n=${r.n} PF=${r.PF?.toFixed(4)??'n/a'} avgR=${r.avgR.toFixed(4)} spikeN=${r.spikeN} spikePF=${r.spikePF?.toFixed(4)??'n/a'}`); console.log(`  OOS opportunity: n=${oosOpportunity.length} PF=${summarize(oosOpportunity).PF?.toFixed(4)??'n/a'} avgR=${summarize(oosOpportunity).avgR.toFixed(4)}`); console.log(`  OOS sequence-complete: n=${oosComplete.length} PF=${summarize(oosComplete).PF?.toFixed(4)??'n/a'} avgR=${summarize(oosComplete).avgR.toFixed(4)}`); console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES)await run(tf);
