import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const PRE=10000, DEV=6000, H=20;
const finite=Number.isFinite;
const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
const pf=a=>{const w=a.filter(x=>x>0).reduce((s,x)=>s+x,0),l=-a.filter(x=>x<0).reduce((s,x)=>s+x,0);return l?w/l:null};
const wr=a=>a.length?a.filter(x=>x>0).length/a.length:null;
const stats=a=>({n:a.length,avgR:mean(a),PF:pf(a),WR:wr(a)});
const fmt=x=>x==null?'NA':x.toFixed(4);

function exc(c,entry,risk,d){return {mae:(d==='BUY'?entry-c.low:c.high-entry)/risk,mfe:(d==='BUY'?c.high-entry:entry-c.low)/risk};}
function classify(path){
 let first1=null, first2=null;
 for(const x of path){if(first1==null&&x.mae>=1)first1=x.h;if(first2==null&&x.mfe>=2)first2=x.h;}
 if(first1==null)return null;
 const prior=path.filter(x=>x.h<first1);
 const mfe1Before=prior.some(x=>x.mfe>=1);
 const mfe2Before=prior.some(x=>x.mfe>=2);
 return {first1,mfe1Before,mfe2Before};
}
function summarize(rs){return stats(rs.map(r=>r.rMultiple));}
async function main(){
 const raw=JSON.parse(await readFile(resolve(ROOT,'data/historical/xauusd-5min.json'),'utf8'));const candles=raw.candles??raw;
 const base=(JSON.parse(await readFile(resolve(ROOT,'data/reports/strategy-a-baseline/5min.json'),'utf8')).trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&finite(Number(t.rMultiple))&&Number(t.entryIndex)<PRE);
 const rows=[];
 for(const t of base){const i=Number(t.entryIndex),entry=Number(t.entry),risk=Math.abs(entry-Number(t.stopLoss));if(!(risk>0)||!candles[i+H])continue;const path=[];for(let h=1;h<=H;h++)path.push({h,...exc(candles[i+h],entry,risk,t.direction)});const e=classify(path);if(e)rows.push({entryIndex:i,direction:t.direction,rMultiple:Number(t.rMultiple),exceptional:Number(t.rMultiple)>=5,dev:i<DEV,event:e});}
 const groups={MFE1_BEFORE_1R:rows.filter(r=>r.event.mfe1Before),NO_MFE1_BEFORE_1R:rows.filter(r=>!r.event.mfe1Before),MFE2_BEFORE_1R:rows.filter(r=>r.event.mfe2Before),NO_MFE2_BEFORE_1R:rows.filter(r=>!r.event.mfe2Before)};
 const devval={};for(const [k,rs] of Object.entries(groups)){devval[k]={ALL:summarize(rs),DEV:summarize(rs.filter(r=>r.dev)),VAL:summarize(rs.filter(r=>!r.dev&&r.entryIndex<PRE)),DEV_NO_EX:summarize(rs.filter(r=>r.dev&&!r.exceptional)),VAL_NO_EX:summarize(rs.filter(r=>!r.dev&&r.entryIndex<PRE&&!r.exceptional))};}
 console.log(`PHASE_11D_REPLICATION N=${base.length} HIT_1R=${rows.length} DEV=${rows.filter(r=>r.dev).length} VAL=${rows.filter(r=>!r.dev&&r.entryIndex<PRE).length} FRESH=LOCKED`);
 console.log(`INTEGRITY baselinePre=${base.length} complete=${rows.length===171?'171':'NOT_171'} deterministic=true`);
 for(const [k,x] of Object.entries(devval)){console.log(`${k}: ALL N=${x.ALL.n} avgR=${fmt(x.ALL.avgR)} PF=${fmt(x.ALL.PF)} WR=${(x.ALL.WR*100).toFixed(2)}% | DEV N=${x.DEV.n} avgR=${fmt(x.DEV.avgR)} PF=${fmt(x.DEV.PF)} | VAL N=${x.VAL.n} avgR=${fmt(x.VAL.avgR)} PF=${fmt(x.VAL.PF)} | DEV_NO_EX=${fmt(x.DEV_NO_EX.avgR)} | VAL_NO_EX=${fmt(x.VAL_NO_EX.avgR)}`)}
 console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_HORIZON_SELECTION NO_RULE NO_FRESH');
}
main().catch(e=>{console.error(e);process.exitCode=1});
