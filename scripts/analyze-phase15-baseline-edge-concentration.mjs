import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PRE=10000,DEV=6000;
const round=n=>Number.isFinite(n)?Number(n.toFixed(6)):null;
const pct=n=>Number.isFinite(n)?Number((n*100).toFixed(4)):null;
const stats=rows=>{const r=rows.filter(x=>Number.isFinite(x.r)),w=r.filter(x=>x.r>0),l=r.filter(x=>x.r<=0),gw=w.reduce((s,x)=>s+x.r,0),gl=l.reduce((s,x)=>s+Math.abs(x.r),0);return{n:r.length,wins:w.length,losses:l.length,WR:r.length?w.length/r.length:null,avgR:r.length?r.reduce((s,x)=>s+x.r,0)/r.length:null,PF:gl?gw/gl:null,totalR:r.reduce((s,x)=>s+x.r,0)};};
const byR=(rows,desc=true)=>[...rows].sort((a,b)=>desc?b.r-a.r:a.r-b.r);
const contribution=(rows,k)=>{const s=stats(rows),top=byR(rows).slice(0,k).reduce((a,x)=>a+x.r,0);return{sTotal:s.totalR,topR:top,topShare:s.totalR?top/s.totalR:null};};
const leaveOneOut=rows=>{const s=stats(rows);return rows.map((x,i)=>{const r=rows.filter((_,j)=>j!==i),q=stats(r);return{rank:i+1,entryIndex:x.entryIndex,direction:x.direction,session:x.session,r:x.r,totalRWithout:q.totalR,avgRWithout:q.avgR,PFWithout:q.PF,exceptional:x.exceptional};}).sort((a,b)=>b.r-a.r);};
const bucketStats=(rows,key)=>Object.fromEntries([...new Set(rows.map(x=>x[key]))].sort().map(k=>[k,stats(rows.filter(x=>x[key]===k))]));
function annotate(trades){return trades.map(t=>({entryIndex:Number(t.entryIndex),entryTime:t.entryTime,direction:t.direction,r:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,split:Number(t.entryIndex)<DEV?'DEV':'VAL',session:t.session??'UNKNOWN'})).filter(x=>Number.isInteger(x.entryIndex)&&x.entryIndex<PRE&&Number.isFinite(x.r)&&(x.direction==='BUY'||x.direction==='SELL'));}
async function main(){
 const base=JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8'));
 const rows=annotate(base.trades??[]);const dev=rows.filter(x=>x.split==='DEV'),val=rows.filter(x=>x.split==='VAL');
 const noEx=rows.filter(x=>!x.exceptional),devNoEx=dev.filter(x=>!x.exceptional),valNoEx=val.filter(x=>!x.exceptional);
 const topKs=[1,2,3,5,10].map(k=>({k,...contribution(rows,k),DEV:contribution(dev,Math.min(k,dev.length)),VAL:contribution(val,Math.min(k,val.length))}));
 const positiveWins=byR(rows).filter(x=>x.r>0),losses=byR(rows,false).filter(x=>x.r<=0);
 const maxWin=positiveWins[0]?.r??null,maxLoss=losses[0]?.r??null;
 const result={strategy:'Strategy A / SP2L',mode:'PHASE_15_BASELINE_EDGE_CONCENTRATION',timeframe:'5min',scope:{baselinePre:rows.length,dev:dev.length,val:val.length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedBaselinePre:210,actualBaselinePre:rows.length,entryIndexMissing:(base.trades??[]).filter(t=>!Number.isInteger(Number(t.entryIndex))&&Number(t.entryIndex)<PRE).length},methodology:{purpose:'Stability and concentration audit of the existing canonical baseline; no new features, filters, thresholds, optimization, or rule changes.',metrics:['top-k contribution to total R','exceptional-trade dependence','leave-one-out sensitivity','sign concentration','direction/session contribution','chronological DEV/VAL contribution'],noOptimization:true,noThresholdSearch:true,noNewTradingRules:true,noFreshHoldoutAccess:true},baseline:stats(rows),noExceptional:stats(noEx),dev:stats(dev),val:stats(val),devNoExceptional:stats(devNoEx),valNoExceptional:stats(valNoEx),topKContribution:topKs,maxSingleWinR:maxWin,maxSingleLossR:maxLoss,winSide:stats(positiveWins),lossSide:stats(losses),direction:bucketStats(rows,'direction'),session:bucketStats(rows,'session'),directionSession:Object.fromEntries([...new Set(rows.map(x=>`${x.direction}+${x.session}`))].sort().map(k=>[k,stats(rows.filter(x=>`${x.direction}+${x.session}`===k))])),leaveOneOut:leaveOneOut(rows),cases:rows};
 const out=resolve(ROOT,'data/reports/strategy-a-phase15-baseline-edge-concentration');await mkdir(out,{recursive:true});await writeFile(resolve(out,'5min.json'),JSON.stringify(result,null,2));
 const fmt=s=>`N=${s.n} avgR=${round(s.avgR)} PF=${round(s.PF)} WR=${pct(s.WR)}% totalR=${round(s.totalR)}`;
 console.log(`PHASE_15_BASELINE_EDGE_CONCENTRATION 5min N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
 console.log(`INTEGRITY expected=${result.integrity.expectedBaselinePre} actual=${rows.length} entryIndexMissing=${result.integrity.entryIndexMissing}`);
 console.log(`BASELINE ${fmt(result.baseline)} | NO_EX ${fmt(result.noExceptional)}`);
 console.log(`DEV ${fmt(result.dev)} | DEV_NO_EX ${fmt(result.devNoExceptional)}`);
 console.log(`VAL ${fmt(result.val)} | VAL_NO_EX ${fmt(result.valNoExceptional)}`);
 console.log('=== TOP-K TOTAL-R CONTRIBUTION ===');for(const x of topKs)console.log(`K=${x.k} ALL share=${round(x.topShare)} topR=${round(x.topR)} | DEV share=${round(x.DEV.topShare)} | VAL share=${round(x.VAL.topShare)}`);
 console.log(`MAX_WIN_R=${round(maxWin)} MAX_LOSS_R=${round(maxLoss)}`);
 console.log('=== DIRECTION ===');for(const[k,v]of Object.entries(result.direction))console.log(`${k}: ${fmt(v)}`);
 console.log('=== SESSION ===');for(const[k,v]of Object.entries(result.session))console.log(`${k}: ${fmt(v)}`);
 console.log('=== DIRECTION+SESSION ===');for(const[k,v]of Object.entries(result.directionSession))console.log(`${k}: ${fmt(v)}`);
 console.log('=== LEAVE-ONE-OUT TOP WIN INFLUENCE ===');for(const x of result.leaveOneOut.slice(0,5))console.log(`entry=${x.entryIndex} ${x.direction} r=${round(x.r)} totalR_without=${round(x.totalRWithout)} avgR_without=${round(x.avgRWithout)} PF_without=${round(x.PFWithout)}`);
 console.log(`REPORT=${resolve(out,'5min.json')}`);console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
main().catch(e=>{console.error(e);process.exit(1);});
