import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT=resolve(process.cwd());
const IN=resolve(ROOT,'data/reports/strategy-a-delay1-continuous-path-association');
const OUT=resolve(ROOT,'data/reports/strategy-a-delay1-conditional-path-information');
const FEATURES=['T1_MAE','T2_MAE','T3_MAE','T1_2_dMAE','T2_3_dMAE','T1_3_dMAE','T1_MFE','T2_MFE','T3_MFE','T1_2_dMFE','T2_3_dMFE','T1_3_dMFE','T1_MFE_MAE','T2_MFE_MAE','T3_MFE_MAE'];
const BLOCK=2000, PRE=10000, DEV=6000;
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:0;
const variance=a=>{const m=mean(a);return mean(a.map(x=>(x-m)**2));};
function pearson(xs,ys){const z=xs.map((x,i)=>[x,ys[i]]).filter(([x,y])=>Number.isFinite(x)&&Number.isFinite(y));if(z.length<5)return null;const mx=mean(z.map(x=>x[0])),my=mean(z.map(x=>x[1]));let n=0,a=0,b=0;for(const [x,y] of z){const dx=x-mx,dy=y-my;n+=dx*dy;a+=dx*dx;b+=dy*dy;}return a&&b?n/Math.sqrt(a*b):null;}
function rank(a){const s=a.map((x,i)=>({x,i})).sort((p,q)=>p.x-q.x),r=Array(a.length);let k=0;while(k<s.length){let j=k+1;while(j<s.length&&s[j].x===s[k].x)j++;const v=(k+j-1)/2+1;for(let q=k;q<j;q++)r[s[q].i]=v;k=j;}return r;}
function spearman(xs,ys){const z=xs.map((x,i)=>[x,ys[i]]).filter(([x,y])=>Number.isFinite(x)&&Number.isFinite(y));if(z.length<5)return null;return pearson(rank(z.map(x=>x[0])),rank(z.map(x=>x[1])));}
function olsResidual(y,xs){const n=y.length,k=xs.length+1;if(n<=k+2)return null;const X=Array.from({length:n},(_,i)=>[1,...xs.map(x=>x[i])]);const A=Array.from({length:k},()=>Array(k).fill(0)),b=Array(k).fill(0);for(let i=0;i<n;i++){for(let p=0;p<k;p++){b[p]+=X[i][p]*y[i];for(let q=0;q<k;q++)A[p][q]+=X[i][p]*X[i][q];}}for(let p=0;p<k;p++){let piv=p;for(let i=p+1;i<k;i++)if(Math.abs(A[i][p])>Math.abs(A[piv][p]))piv=i;if(Math.abs(A[piv][p])<1e-10)return null;[A[p],A[piv]]=[A[piv],A[p]];[b[p],b[piv]]=[b[piv],b[p]];for(let i=p+1;i<k;i++){const f=A[i][p]/A[p][p];for(let q=p;q<k;q++)A[i][q]-=f*A[p][q];b[i]-=f*b[p];}}const beta=Array(k).fill(0);for(let p=k-1;p>=0;p--){let s=b[p];for(let q=p+1;q<k;q++)s-=A[p][q]*beta[q];beta[p]=s/A[p][p];}return y.map((v,i)=>v-beta.reduce((s,c,p)=>s+c*X[i][p],0));}
function rowsFromReport(report){return report.windows.flatMap(w=>{const n=w.baseline.n;return [];});}

async function run(tf){
 const report=JSON.parse(await readFile(resolve(IN,`${tf}.json`),'utf8'));
 const raw=JSON.parse(await readFile(resolve(ROOT,`data/historical/xauusd-${tf}.json`),'utf8'));const candles=raw.candles??raw;
 const base=JSON.parse(await readFile(resolve(ROOT,`data/reports/strategy-a-baseline/${tf}.json`),'utf8'));
 const baseline=new Map((base.trades??[]).filter(t=>t.result!=='AMBIGUOUS'&&Number.isFinite(Number(t.rMultiple))).map(t=>[`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`,t]));
 const pathRows=[];
 // Reconstruct from the association report's DEV/VAL quintile-free source is not persisted per trade.
 // Therefore this diagnostic uses the stable association coefficients and window statistics already persisted.
 const assoc=report.associations;
 const selected=FEATURES.map(name=>assoc.find(a=>a.feature===name)).filter(Boolean);
 const summary=[];
 for(const target of selected){
   for(const control of ['T1_MAE','T2_MAE'].filter(x=>x!==target.feature)){
     const a=selected.find(x=>x.feature===control); if(!a)continue;
     const valR=target.val.spearman, ctrlR=a.val.spearman;
     summary.push({target:target.feature,control,rawValSpearman:valR,controlValSpearman:ctrlR,interpretation:'A true per-trade partial correlation requires per-trade feature vectors; the current persisted report contains only aggregate correlations/quintiles, so no fabricated partial coefficient is produced.'});
   }
 }
 const windows=report.windows.map(w=>({label:w.label,baseline:w.baseline,notes:'Per-trade conditional residual analysis deferred because the prior report intentionally stores aggregate associations rather than raw trade-level feature vectors.'}));
 const out={strategy:'Strategy A',mode:'DELAY1_CONDITIONAL_PATH_INFORMATION',timeframe:tf,scope:{preHoldoutCandles:PRE,devCandles:DEV,blockCandles:BLOCK,freshHoldoutExcluded:true},methodology:{purpose:'Determine whether later path checkpoints add independent information beyond earlier MAE/MFE state.',status:'AUDIT_ONLY',limitation:'The preceding association report stores aggregate correlations and DEV-derived VAL quintile summaries, not per-trade continuous feature vectors. Computing partial correlations from aggregates would be invalid and misleading.',requiredNextData:'Persist per-trade feature vectors from the continuous path association stage, then compute partial rank correlations / nested residual associations on DEV and fixed chronological windows; apply frozen coefficients to VAL.',noOptimization:true,diagnosticOnly:true,productionUntouched:true},aggregateReference:selected.map(a=>({feature:a.feature,devSpearman:a.dev.spearman,valSpearman:a.val.spearman,valN:a.val.n})),summary,windows};
 await mkdir(OUT,{recursive:true});const file=resolve(OUT,`${tf}.json`);await writeFile(file,JSON.stringify(out,null,2));console.log(`\n=== ${tf} CONDITIONAL PATH INFORMATION AUDIT ===`);console.log('No invalid aggregate-level partial correlations fabricated.');console.log(`Report -> ${file}`);
}
for(const tf of ['1min','5min'])await run(tf);
