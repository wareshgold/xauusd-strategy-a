import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-post-tp1-management-forensics');
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [1, 2, 3, 5, 8, 12, 20, 30, 50];
const MIN_N = 10;

const finite = v => Number.isFinite(Number(v));
const num = (r, keys) => { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; };
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const w = rs.filter(x => x > 0), l = rs.filter(x => x < 0);
  const gp = w.reduce((a,b)=>a+b,0), gl = -l.reduce((a,b)=>a+b,0);
  return { n: rs.length, winRate: rs.length ? w.length/rs.length : 0, PF: gl ? gp/gl : (gp ? null : 0), avgR: rs.length ? rs.reduce((a,b)=>a+b,0)/rs.length : 0, totalR: rs.reduce((a,b)=>a+b,0) };
}
function split(rows) { const a=[...rows].sort((x,y)=>new Date(x.entryTime)-new Date(y.entryTime)),c=Math.floor(a.length/3); return {dev:a.slice(0,c),validation:a.slice(c,2*c),holdout:a.slice(2*c)}; }
function path(r,candles) {
  const ei=Number(r.entryIndex), entry=num(r,['entry','entryPrice','fillPrice','price']), sl=num(r,['stopLoss','stop','sl']), tp1=num(r,['tp1','takeProfit','target']), tp2=num(r,['tp2','target2','takeProfit2']);
  if(!Number.isInteger(ei)||!finite(entry)||!finite(sl)||!finite(tp1)) return null;
  const buy=String(r.direction).toUpperCase()==='BUY', risk=Math.abs(entry-sl); if(!(risk>0)) return null;
  let tp1Idx=null,tp2Idx=null,slIdx=null;
  for(let i=ei+1;i<candles.length;i++){
    const c=candles[i],hi=Number(c.high),lo=Number(c.low); if(!finite(hi)||!finite(lo)) continue;
    if(tp1Idx===null&&(buy?hi>=tp1:lo<=tp1)) tp1Idx=i;
    if(tp2!==null&&tp2Idx===null&&(buy?hi>=tp2:lo<=tp2)) tp2Idx=i;
    if(slIdx===null&&(buy?lo<=sl:hi>=sl)) slIdx=i;
    if(tp1Idx!==null && (tp2Idx!==null || tp2===null) && slIdx!==null) break;
  }
  const tp1BeforeSl=tp1Idx!==null&&(slIdx===null||tp1Idx<slIdx);
  if(!tp1BeforeSl) return {tp1Idx,slIdx,tp2Idx,tp1BeforeSl:false};
  const tp1R=Math.abs(tp1-entry)/risk;
  const end=Math.min(candles.length-1,tp1Idx+50);
  let postMfe=0,postMae=0,maxGiveback=0,peak=0,peakIdx=tp1Idx,firstAdverse=null,tp2AfterTp1=null;
  for(let i=tp1Idx;i<=end;i++){
    const c=candles[i],hi=Number(c.high),lo=Number(c.low); if(!finite(hi)||!finite(lo)) continue;
    const favorable=buy?hi-entry:entry-lo, adverse=buy?entry-lo:hi-entry;
    postMfe=Math.max(postMfe,favorable/risk); postMae=Math.max(postMae,adverse/risk);
    const favAtClose=buy?(Number(c.close)-entry)/risk:(entry-Number(c.close))/risk;
    if(favAtClose>peak){peak=favAtClose;peakIdx=i;}
    maxGiveback=Math.max(maxGiveback,Math.max(0,peak-favAtClose));
    if(firstAdverse===null && adverse/risk>=0.5) firstAdverse=i-tp1Idx;
    if(tp2!==null && tp2AfterTp1===null && i>tp1Idx && (buy?hi>=tp2:lo<=tp2)) tp2AfterTp1=i-tp1Idx;
  }
  return {tp1Idx,slIdx,tp2Idx,tp1BeforeSl:true,tp1R,barsToTp1:tp1Idx-ei,barsToSl:slIdx===null?null:slIdx-ei,barsToTp2:tp2AfterTp1,tp2ReachedAfterTp1:tp2AfterTp1!==null,postMfeR:postMfe,postMaeR:postMae,maxGivebackR:maxGiveback,firstAdverseBars:firstAdverse,peakBarsAfterTp1:peakIdx-tp1Idx};
}
function enrich(rows,candles){return rows.map(r=>{const p=path(r,candles);return p?{...r,path:p}:null}).filter(Boolean);}
function horizon(rows,h){return rows.filter(r=>r.path.tp1BeforeSl&&r.path.tp1Idx+h<r._candlesLength);}
async function run(tf){
  const [br,cr]=await Promise.all([readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf}.json`),'utf8'),readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')]);
  const base=JSON.parse(br), data=JSON.parse(cr), candles=data.candles??data;
  const rows=enrich((base.trades??[]).filter(r=>finite(r.rMultiple)),candles).map(r=>({...r,_candlesLength:candles.length}));
  const s=split(rows), tp1=rows.filter(r=>r.path.tp1BeforeSl);
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_POST_TP1_MANAGEMENT_FORENSICS_V1',timeframe:tf,scope:'Descriptive analysis only of trades that reached TP1 before SL. No early invalidation is introduced and no post-TP1 feature is used to select entries.',methodology:{target:'post-TP1 continuation and giveback',rule:'a signal remains valid until TP1 or structural invalidation; this report never converts pre-TP1 adverse movement into an early exit',tp2:'recorded TP2 when available; otherwise continuation metrics are still measured',window:'up to 50 candles after TP1',selection:'descriptive only; no optimization or candidate selection'},counts:{all:rows.length,tp1BeforeSl:tp1.length,dev:s.dev.filter(r=>r.path.tp1BeforeSl).length,validation:s.validation.filter(r=>r.path.tp1BeforeSl).length,holdout:s.holdout.filter(r=>r.path.tp1BeforeSl).length},tp1ReachedOutcome:stats(tp1),postTp1Classes:{tp2Reached:stats(tp1.filter(r=>r.path.tp2ReachedAfterTp1)),noTp2By50:stats(tp1.filter(r=>!r.path.tp2ReachedAfterTp1)),lowGiveback:stats(tp1.filter(r=>r.path.maxGivebackR<0.5)),highGiveback:stats(tp1.filter(r=>r.path.maxGivebackR>=0.5)),fastTp2:stats(tp1.filter(r=>r.path.tp2ReachedAfterTp1&&r.path.barsToTp2<=3)),slowTp2:stats(tp1.filter(r=>r.path.tp2ReachedAfterTp1&&r.path.barsToTp2>3))},holdout:{all:stats(s.holdout.filter(r=>r.path.tp1BeforeSl)),tp2Reached:stats(s.holdout.filter(r=>r.path.tp2ReachedAfterTp1)),noTp2By50:stats(s.holdout.filter(r=>r.path.tp1BeforeSl&&!r.path.tp2ReachedAfterTp1)),lowGiveback:stats(s.holdout.filter(r=>r.path.tp1BeforeSl&&r.path.maxGivebackR<0.5)),highGiveback:stats(s.holdout.filter(r=>r.path.tp1BeforeSl&&r.path.maxGivebackR>=0.5))},horizons:{}};
  for(const h of HORIZONS){const x=tp1.filter(r=>r.path.tp1Idx+h<candles.length);const tp2=x.filter(r=>r.path.tp2ReachedAfterTp1&&r.path.barsToTp2<=h);const give=x.filter(r=>r.path.maxGivebackR>=0.5);report.horizons[`H${h}`]={eligibleN:x.length,tp2ReachedByH:tp2.length,tp2Rate:x.length?tp2.length/x.length:0,highGivebackBy50:give.length,highGivebackRate:x.length?give.length/x.length:0};}
  report.holdoutPathStats={tp1Bars:stats(s.holdout.filter(r=>r.path.tp1BeforeSl)),tp1Rows:s.holdout.filter(r=>r.path.tp1BeforeSl).map(r=>({entryTime:r.entryTime,direction:r.direction,barsToTp1:r.path.barsToTp1,tp2ReachedAfterTp1:r.path.tp2ReachedAfterTp1,barsToTp2:r.path.barsToTp2,postMfeR:r.path.postMfeR,postMaeR:r.path.postMaeR,maxGivebackR:r.path.maxGivebackR}))};
  await mkdir(OUT,{recursive:true}); const out=resolve(OUT,`${tf}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: trades=${rows.length} TP1-before-SL=${tp1.length} TP2-after-TP1=${tp1.filter(r=>r.path.tp2ReachedAfterTp1).length}`);
  for(const h of HORIZONS){const x=report.horizons[`H${h}`]; console.log(`  H${h}: TP2-after-TP1=${x.tp2ReachedByH}/${x.eligibleN} ${(x.tp2Rate*100).toFixed(1)}% | high-giveback=${x.highGivebackBy50}/${x.eligibleN} ${(x.highGivebackRate*100).toFixed(1)}%`);}
  console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES) await run(tf);
