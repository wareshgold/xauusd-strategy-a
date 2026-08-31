import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-tp1-discrimination-global-holdout');
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [1, 2, 3, 5];
const MIN_N = 10;
const TOP_N = 25;

const finite = v => Number.isFinite(Number(v));
const num = (r, keys) => { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; };
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const w = rs.filter(x => x > 0), l = rs.filter(x => x < 0);
  const gp = w.reduce((a,b)=>a+b,0), gl = -l.reduce((a,b)=>a+b,0);
  return { n: rs.length, winRate: rs.length ? w.length/rs.length : 0, PF: gl ? gp/gl : (gp ? null : 0), avgR: rs.length ? rs.reduce((a,b)=>a+b,0)/rs.length : 0, totalR: rs.reduce((a,b)=>a+b,0) };
}
function split(rows) { const a=[...rows].sort((x,y)=>new Date(x.entryTime)-new Date(y.entryTime)); const c=Math.floor(a.length/3); return {dev:a.slice(0,c),validation:a.slice(c,2*c),holdout:a.slice(2*c)}; }
function session(ts) {
  const d = new Date(ts); const m = d.getUTCHours()*60+d.getUTCMinutes();
  if (m >= 7*60 && m < 13*60) return 'LONDON';
  if (m >= 13*60 && m < 22*60) return 'NEW_YORK';
  return 'OUTSIDE';
}
function path(trade,candles) {
  const ei=Number(trade.entryIndex), entry=num(trade,['entry','entryPrice','fillPrice','price']), sl=num(trade,['stopLoss','stop','sl']), tp=num(trade,['tp1','takeProfit','target']);
  if(!Number.isInteger(ei)||!finite(entry)||!finite(sl)||!finite(tp)) return null;
  const buy=String(trade.direction).toUpperCase()==='BUY', risk=Math.abs(entry-sl); if(!(risk>0)) return null;
  let tpIdx=null, slIdx=null;
  for(let i=ei+1;i<candles.length;i++){
    const c=candles[i], hi=Number(c.high), lo=Number(c.low); if(!finite(hi)||!finite(lo)) continue;
    if(tpIdx===null && (buy?hi>=tp:lo<=tp)) tpIdx=i;
    if(slIdx===null && (buy?lo<=sl:hi>=sl)) slIdx=i;
    if(tpIdx!==null && slIdx!==null) break;
  }
  const same=tpIdx!==null&&slIdx!==null&&tpIdx===slIdx;
  const winner=tpIdx!==null&&(slIdx===null||tpIdx<slIdx);
  const out={winner,same,tpIdx,slIdx, risk, features:{}};
  for(const h of HORIZONS){
    const end=Math.min(candles.length-1,ei+h); let mae=0,mfe=0;
    for(let i=ei+1;i<=end;i++){const c=candles[i],hi=Number(c.high),lo=Number(c.low);if(!finite(hi)||!finite(lo))continue;mae=Math.max(mae,buy?entry-lo:hi-entry);mfe=Math.max(mfe,buy?hi-entry:entry-lo);}
    out.features[`H${h}_MAE`] = mae/risk; out.features[`H${h}_MFE`] = mfe/risk;
  }
  return out;
}
function bucket(v) {
  if(!finite(v)) return null; v=Number(v);
  if(v<0.25) return 'LT_025'; if(v<0.5) return '025_050'; if(v<0.75) return '050_075'; if(v<1) return '075_100'; return 'GE_100';
}
function buildFeatures(rows) {
  return rows.map(r=>{const f={direction:String(r.direction).toUpperCase(),session:session(r.entryTime)}; for(const h of HORIZONS){f[`H${h}_MAE`]=bucket(r.path.features[`H${h}_MAE`]);f[`H${h}_MFE`]=bucket(r.path.features[`H${h}_MFE`]);} return {...r,f};});
}
function candidatePairs(rows) {
  const defs=[];
  for(const h of HORIZONS){ defs.push([`H${h}_MAE`,`LT_025`,r=>r.f[`H${h}_MAE`]==='LT_025']); defs.push([`H${h}_MAE`,`GE_100`,r=>r.f[`H${h}_MAE`]==='GE_100']); defs.push([`H${h}_MFE`,`GE_100`,r=>r.f[`H${h}_MFE`]==='GE_100']); defs.push([`H${h}_MFE`,`LT_025`,r=>r.f[`H${h}_MFE`]==='LT_025']); }
  defs.push(['direction','BUY',r=>r.f.direction==='BUY'],['direction','SELL',r=>r.f.direction==='SELL'],['session','LONDON',r=>r.f.session==='LONDON'],['session','NEW_YORK',r=>r.f.session==='NEW_YORK'],['session','OUTSIDE',r=>r.f.session==='OUTSIDE']);
  const out=[];
  for(let i=0;i<defs.length;i++) for(let j=i+1;j<defs.length;j++){
    if(defs[i][0]===defs[j][0]) continue;
    const subset=rows.filter(r=>defs[i][2](r)&&defs[j][2](r)); if(subset.length<MIN_N) continue;
    const s=split(subset), dev=stats(s.dev), val=stats(s.validation), hold=stats(s.holdout);
    const passes=dev.n>=MIN_N&&val.n>=MIN_N&&dev.PF>=1&&val.PF>=1&&dev.avgR>0&&val.avgR>0;
    out.push({featureA:defs[i][0],bucketA:defs[i][1],featureB:defs[j][0],bucketB:defs[j][1],dev,validation:val,holdout:hold,passesDevValidation:passes});
  }
  return out;
}
async function run(tf){
  const [raw,craw]=await Promise.all([readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf}.json`),'utf8'),readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8')]);
  const source=JSON.parse(raw), cd=JSON.parse(craw), candles=cd.candles??cd;
  const base=(source.trades??[]).filter(r=>finite(r.rMultiple));
  const rows=buildFeatures(base.map(r=>{const p=path(r,candles);return p?{...r,path:p}:null;}).filter(Boolean));
  const global=split(rows), pairs=candidatePairs(rows);
  const selected=pairs.filter(x=>x.passesDevValidation).sort((a,b)=>(b.validation.PF??-1)-(a.validation.PF??-1)||(b.validation.avgR-a.validation.avgR));
  const report={strategy:'Strategy A / SP2L',mode:'RESEARCH_TP1_DISCRIMINATION_GLOBAL_HOLDOUT_V1',timeframe:tf,scope:'Discrimination of trades that reach TP1 before SL versus SL-before-TP1 using only direction/session and first 1-5 post-entry candle excursion features. No TP1 or SL rule is changed.',methodology:{target:'TP1-before-SL',observableWindow:'Entry plus H1/H2/H3/H5 post-entry candles; these are diagnostic features, not an entry-time claim.',split:'global chronological thirds',selectionGate:`DEV and VALIDATION n >= ${MIN_N}, PF >= 1, avgR > 0`,holdout:'untouched during candidate selection',warning:'Small subgroups and multiple comparisons make positive holdout results exploratory until replicated on another period.'},counts:{trades:rows.length,dev:global.dev.length,validation:global.validation.length,holdout:global.holdout.length},outcomeRates:{all:stats(rows),tp1BeforeSl:stats(rows.filter(r=>r.path.winner)),slBeforeTp1:stats(rows.filter(r=>r.path.slIdx!==null&&!r.path.winner&&!r.path.same))},pairTests:pairs.length,devValidationCandidates:selected.length,robustHoldoutCandidates:selected.filter(x=>x.holdout.n>=MIN_N&&x.holdout.PF>=1&&x.holdout.avgR>0).length,topCandidates:selected.slice(0,TOP_N),robustHoldout:selected.filter(x=>x.holdout.n>=MIN_N&&x.holdout.PF>=1&&x.holdout.avgR>0).slice(0,TOP_N)};
  await mkdir(OUT,{recursive:true}); const out=resolve(OUT,`${tf}.json`); await writeFile(out,JSON.stringify(report,null,2));
  console.log(`${tf}: trades=${rows.length} tests=${pairs.length} devValidationCandidates=${selected.length} robustHoldoutCandidates=${report.robustHoldoutCandidates}`);
  for(const c of selected.slice(0,TOP_N)) console.log(`  ${c.featureA}=${c.bucketA} + ${c.featureB}=${c.bucketB}: DEV n=${c.dev.n} PF=${c.dev.PF?.toFixed(4)??'n/a'} avgR=${c.dev.avgR.toFixed(4)} | VAL n=${c.validation.n} PF=${c.validation.PF?.toFixed(4)??'n/a'} avgR=${c.validation.avgR.toFixed(4)} | HOLDOUT n=${c.holdout.n} PF=${c.holdout.PF?.toFixed(4)??'n/a'} avgR=${c.holdout.avgR.toFixed(4)} totalR=${c.holdout.totalR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}
for(const tf of TIMEFRAMES) await run(tf);
