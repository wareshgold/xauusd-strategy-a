import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase27-d-archetype-conditional-residual-decomposition');

const D_ARC = 'LOSS_D_PRE_GE_2R';
const FEATURES = ['spikeSizeR','correctionSizeR','correctionEfficiency','entryTriggerBodyR','correctionToSpike','entryTriggerReclaimR'];
const PAIRS = [['spikeSizeR','correctionSizeR'],['spikeSizeR','correctionEfficiency'],['correctionSizeR','correctionEfficiency'],['spikeSizeR','entryTriggerBodyR'],['correctionSizeR','entryTriggerBodyR']];
const ARCS = ['LOSS_A_NO_PRE_FAVORABLE','LOSS_B_PRE_0_5_TO_LT_1R','LOSS_C_PRE_1_TO_LT_2R',D_ARC];
const finite = v => Number.isFinite(v);
const quantile = (a,q)=>{const v=a.filter(finite).sort((x,y)=>x-y);if(!v.length)return null;const i=(v.length-1)*q,l=Math.floor(i),h=Math.ceil(i);return l===h?v[l]:v[l]+(v[h]-v[l])*(i-l)};
const dRate = rows => ({n:rows.length,dCount:rows.filter(x=>x.archetype===D_ARC).length,dRate:rows.length?rows.filter(x=>x.archetype===D_ARC).length/rows.length:null});

const source = JSON.parse(await readFile(SOURCE,'utf8'));
const integrity = source.integrity ?? {};
const expected = Number(integrity.expectedCanonical);
const actual = Number(integrity.canonicalReplayed);
if(expected!==actual || Number(integrity.replayMismatch)!==0 || Number(integrity.missingCanonicalTimestamp)!==0 || Number(integrity.exitMismatch)!==0) throw new Error('PHASE27 source integrity failure');
if(source.scope?.freshHoldoutExcluded!==true || source.scope?.productionUntouched!==true) throw new Error('PHASE27 source guard failure');

const rows=(source.cases??[]).filter(x=>ARCS.includes(x.archetype));
for(const r of rows) for(const f of FEATURES) if(!(f in (r.features??{}))) throw new Error(`Missing feature ${f}`);

function bucket(rows,f){const vals=rows.map(x=>x.features[f]);const q33=quantile(vals,.33),q66=quantile(vals,.66);return {feature:f,q33,q66,buckets:{LOW:dRate(rows.filter(x=>x.features[f]<=q33)),MID:dRate(rows.filter(x=>x.features[f]>q33&&x.features[f]<q66)),HIGH:dRate(rows.filter(x=>x.features[f]>=q66))}}}
function interaction(rows,a,b){const aq=quantile(rows.map(x=>x.features[a]),.66),bq=quantile(rows.map(x=>x.features[b]),.66);return {features:[a,b],thresholds:{[a]:aq,[b]:bq},HIGH_HIGH:dRate(rows.filter(x=>x.features[a]>=aq&&x.features[b]>=bq))}}

const result={strategy:'Strategy A / SP2L',mode:'PHASE_27_D_ARCHETYPE_CONDITIONAL_RESIDUAL_DECOMPOSITION',timeframe:'5min',source:'Phase24 loss-archetype report; same canonical universe as Phase26.',scope:{cases:rows.length,dCases:rows.filter(x=>x.archetype===D_ARC).length,nonDCases:rows.filter(x=>x.archetype!==D_ARC).length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{sourceExpectedCanonical:expected,sourceCanonicalReplayed:actual,replayMismatch:Number(integrity.replayMismatch),missingCanonicalTimestamp:Number(integrity.missingCanonicalTimestamp),exitMismatch:Number(integrity.exitMismatch)},methodology:{purpose:'Conditional decomposition of D archetype geometry.',noOptimization:true,noThresholdSearch:true,noTradingRules:true},baseline:dRate(rows),singleFeatureConditioning:FEATURES.map(f=>bucket(rows,f)),interactionConditioning:PAIRS.map(([a,b])=>interaction(rows,a,b)),interpretation:'Descriptive only. No production rule inference.'};

await mkdir(OUT,{recursive:true});
await writeFile(resolve(OUT,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE_27_D_ARCHETYPE_CONDITIONAL_RESIDUAL_DECOMPOSITION 5min N=${rows.length} D=${result.scope.dCases} NON_D=${result.scope.nonDCases}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);
