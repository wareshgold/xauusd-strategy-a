import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT=resolve(process.cwd()),PRE=10000,DEV=6000;
const CFG={breakoutLookback:5,followThrough:{maxBarsAfterBreakout:2,requireCloseBeyondBrokenLevel:true},spike:{maxCandles:8,minDirectionalFraction:.5,maxOverlapFraction:.8}};
const round=n=>Number.isFinite(n)?Number(n.toFixed(6)):null;
const pct=n=>Number.isFinite(n)?Number((n*100).toFixed(4)):null;
const stats=rows=>{const r=rows.filter(x=>Number.isFinite(x.r)),w=r.filter(x=>x.r>0),l=r.filter(x=>x.r<=0),gw=w.reduce((s,x)=>s+x.r,0),gl=l.reduce((s,x)=>s+Math.abs(x.r),0);return{n:r.length,wins:w.length,losses:l.length,WR:r.length?w.length/r.length:null,avgR:r.length?r.reduce((s,x)=>s+x.r,0)/r.length:null,PF:gl?gw/gl:null,totalR:r.reduce((s,x)=>s+x.r,0)};};
const byR=(rows,desc=true)=>[...rows].sort((a,b)=>desc?b.r-a.r:a.r-b.r);
const contribution=(rows,k)=>{const s=stats(rows),top=byR(rows).slice(0,k).reduce((a,x)=>a+x.r,0);return{sTotal:s.totalR,topR:top,topShare:s.totalR?top/s.totalR:null};};
const leaveOneOut=rows=>rows.map((x,i)=>{const q=stats(rows.filter((_,j)=>j!==i));return{rank:i+1,entryIndex:x.entryIndex,direction:x.direction,session:x.session,r:x.r,totalRWithout:q.totalR,avgRWithout:q.avgR,PFWithout:q.PF,exceptional:x.exceptional};}).sort((a,b)=>b.r-a.r);
const bucketStats=(rows,key)=>Object.fromEntries([...new Set(rows.map(x=>x[key]))].sort().map(k=>[k,stats(rows.filter(x=>x[key]===k))]));
function session(ts){const d=new Date(ts),m=d.getUTCHours()*60+d.getUTCMinutes();return m>=420&&m<960?'LONDON':m>=960&&m<1320?'NEW_YORK':'OUTSIDE';}
function replay(c,i){const v=c.slice(0,i+1);if(v.length<60)return null;const bo=detectBreakout(v,CFG.breakoutLookback),ft=detectFollowThrough(v,bo,CFG.followThrough),sp=detectSpikeCandidates(v,bo,ft,CFG.spike);for(const s of sp.candidates){if(s.endIndex>=i)continue;const co=detectFirstCorrection(v,s);if(!co||co.correctionExtremeIndex>=i)continue;const tr=detectEntryTrigger(v,co);if(!tr||tr.index!==i)continue;const b=bo.find(x=>x.index===s.breakoutIndex&&x.direction===s.direction),f=ft.find(x=>x.breakoutIndex===s.breakoutIndex&&x.direction===s.direction);if(b&&f)return{tr,s,co,b,f};}return null;}
async function main(){
 const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
 const candles=(JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8')).candles??[]);
 const targets=(base.trades??[]).filter(t=>Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE&&t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))&&(t.direction==='BUY'||t.direction==='SELL'));
 const rows=[];let mismatch=0;
 for(const t of targets){const i=Number(t.entryIndex),x=replay(candles,i);if(!x||x.tr.timestamp!==t.entryTime||x.tr.direction!==t.direction){mismatch++;continue;}rows.push({entryIndex:i,entryTime:t.entryTime,direction:t.direction,r:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,split:i<DEV?'DEV':'VAL',session:session(t.entryTime)});}
 const dev=rows.filter(x=>x.split==='DEV'),val=rows.filter(x=>x.split==='VAL');
 const noEx=rows.filter(x=>!x.exceptional),devNoEx=dev.filter(x=>!x.exceptional),valNoEx=val.filter(x=>!x.exceptional);
 const topKs=[1,2,3,5,10].map(k=>({k,...contribution(rows,Math.min(k,rows.length)),DEV:contribution(dev,Math.min(k,dev.length)),VAL:contribution(val,Math.min(k,val.length))}));
 const wins=byR(rows).filter(x=>x.r>0),losses=byR(rows,false).filter(x=>x.r<=0);
 const result={strategy:'Strategy A / SP2L',mode:'PHASE_15_BASELINE_EDGE_CONCENTRATION',timeframe:'5min',scope:{baselineRawPre:targets.length,replayed:rows.length,dev:dev.length,val:val.length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonicalPre:210,baselineRawPre:targets.length,replayed:rows.length,mismatch,canonicalPopulationMatch:rows.length===210&&mismatch===0},methodology:{purpose:'Stability and concentration audit of the existing canonical baseline population.',population:'Exact Phase14 replay semantics: canonical baseline trade must be reproducible from historical candles through Breakout -> FollowThrough -> Spike -> Correction -> Trigger, with matching trigger timestamp and direction.',metrics:['top-k contribution to total R','exceptional-trade dependence','leave-one-out sensitivity','sign concentration','direction/session contribution','chronological DEV/VAL contribution'],noOptimization:true,noThresholdSearch:true,noNewTradingRules:true,noFreshHoldoutAccess:true},baseline:stats(rows),noExceptional:stats(noEx),dev:stats(dev),val:stats(val),devNoExceptional:stats(devNoEx),valNoExceptional:stats(valNoEx),topKContribution:topKs,maxSingleWinR:wins[0]?.r??null,maxSingleLossR:losses[0]?.r??null,winSide:stats(wins),lossSide:stats(losses),direction:bucketStats(rows,'direction'),session:bucketStats(rows,'session'),directionSession:Object.fromEntries([...new Set(rows.map(x=>`${x.direction}+${x.session}`))].sort().map(k=>[k,stats(rows.filter(x=>`${x.direction}+${x.session}`===k))])),leaveOneOut:leaveOneOut(rows),cases:rows};
 const out=resolve(ROOT,'data/reports/strategy-a-phase15-baseline-edge-concentration');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
 const fmt=s=>`N=${s.n} avgR=${round(s.avgR)} PF=${round(s.PF)} WR=${pct(s.WR)}% totalR=${round(s.totalR)}`;
 console.log(`PHASE_15_BASELINE_EDGE_CONCENTRATION 5min N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
 console.log(`INTEGRITY expected=210 raw=${targets.length} actual=${rows.length} mismatch=${mismatch}`);
 console.log(`BASELINE ${fmt(result.baseline)} | NO_EX ${fmt(result.noExceptional)}`);
 console.log(`DEV ${fmt(result.dev)} | DEV_NO_EX ${fmt(result.devNoExceptional)}`);
 console.log(`VAL ${fmt(result.val)} | VAL_NO_EX ${fmt(result.valNoExceptional)}`);
 console.log('=== TOP-K TOTAL-R CONTRIBUTION ===');for(const x of topKs)console.log(`K=${x.k} ALL share=${round(x.topShare)} topR=${round(x.topR)} | DEV share=${round(x.DEV.topShare)} | VAL share=${round(x.VAL.topShare)}`);
 console.log(`MAX_WIN_R=${round(result.maxSingleWinR)} MAX_LOSS_R=${round(result.maxSingleLossR)}`);
 console.log('=== DIRECTION ===');for(const[k,v]of Object.entries(result.direction))console.log(`${k}: ${fmt(v)}`);
 console.log('=== SESSION ===');for(const[k,v]of Object.entries(result.session))console.log(`${k}: ${fmt(v)}`);
 console.log('=== DIRECTION+SESSION ===');for(const[k,v]of Object.entries(result.directionSession))console.log(`${k}: ${fmt(v)}`);
 console.log('=== LEAVE-ONE-OUT TOP WIN INFLUENCE ===');for(const x of result.leaveOneOut.slice(0,5))console.log(`entry=${x.entryIndex} ${x.direction} r=${round(x.r)} totalR_without=${round(x.totalRWithout)} avgR_without=${round(x.avgRWithout)} PF_without=${round(x.PFWithout)}`);
 console.log(`REPORT=${resolve(out,'5min.json')}`);console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
main().catch(e=>{console.error(e);process.exit(1);});
