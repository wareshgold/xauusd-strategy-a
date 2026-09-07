import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase28-d-archetype-conditional-validation');

const D_ARC = 'LOSS_D_PRE_GE_2R';
const ARCS = ['LOSS_A_NO_PRE_FAVORABLE','LOSS_B_PRE_0_5_TO_LT_1R','LOSS_C_PRE_1_TO_LT_2R',D_ARC];
const finite = v => Number.isFinite(v);
const rate = rows => ({n: rows.length, dCount: rows.filter(x=>x.archetype===D_ARC).length, dRate: rows.length ? rows.filter(x=>x.archetype===D_ARC).length / rows.length : null});
const q = (rows, f, p=.66) => { const a=rows.map(x=>x.features[f]).filter(finite).sort((a,b)=>a-b); if(!a.length)return null; return a[Math.floor((a.length-1)*p)]; };

const source = JSON.parse(await readFile(SOURCE,'utf8'));
const integrity = source.integrity ?? {};
if(Number(integrity.expectedCanonical)!==Number(integrity.canonicalReplayed) || Number(integrity.replayMismatch)!==0 || Number(integrity.missingCanonicalTimestamp)!==0 || Number(integrity.exitMismatch)!==0) throw new Error('PHASE28 source integrity failure');
if(source.scope?.freshHoldoutExcluded!==true || source.scope?.productionUntouched!==true) throw new Error('PHASE28 source guard failure');

const rows=(source.cases??[]).filter(x=>ARCS.includes(x.archetype));
const candidates=[
 {name:'A_spikeSizeR_HIGH',feature:'spikeSizeR'},
 {name:'B_correctionSizeR_HIGH',feature:'correctionSizeR'},
 {name:'C_spikeSizeR_HIGH_plus_correctionEfficiency_HIGH',features:['spikeSizeR','correctionEfficiency']}
];

const validate=(c)=>{
 if(c.feature){const t=q(rows,c.feature);return {candidate:c.name,threshold:{[c.feature]:t},result:rate(rows.filter(x=>x.features[c.feature]>=t))};}
 const [a,b]=c.features;const at=q(rows,a),bt=q(rows,b);return {candidate:c.name,threshold:{[a]:at,[b]:bt},result:rate(rows.filter(x=>x.features[a]>=at&&x.features[b]>=bt))};
};

const result={strategy:'Strategy A / SP2L',mode:'PHASE_28_D_ARCHETYPE_CONDITIONAL_VALIDATION',timeframe:'5min',scope:{cases:rows.length,freshHoldoutExcluded:true,productionUntouched:true},integrity:{expectedCanonical:Number(integrity.expectedCanonical),canonicalReplayed:Number(integrity.canonicalReplayed),replayMismatch:Number(integrity.replayMismatch)},methodology:{purpose:'Validate Phase27 descriptive candidates.',noOptimization:true,noTradingRuleChange:true,noEntryModification:true,candidates:candidates.map(validate)},notes:['Validation only.','Thresholds are inherited descriptive quantiles, not optimized.','Session and direction slices remain required for interpretation.']};
await mkdir(OUT,{recursive:true});
await writeFile(resolve(OUT,'5min.json'),JSON.stringify(result,null,2));
console.log(`PHASE_28_D_ARCHETYPE_CONDITIONAL_VALIDATION 5min N=${rows.length}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);
