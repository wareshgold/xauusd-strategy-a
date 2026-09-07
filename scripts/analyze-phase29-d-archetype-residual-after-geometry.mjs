import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase29-d-archetype-residual-after-geometry');

const D_ARC = 'LOSS_D_PRE_GE_2R';
const ARCS = ['LOSS_A_NO_PRE_FAVORABLE','LOSS_B_PRE_0_5_TO_LT_1R','LOSS_C_PRE_1_TO_LT_2R',D_ARC];
const FEATURES = ['spikeSizeR','correctionSizeR','correctionEfficiency','entryTriggerBodyR','correctionToSpike','entryTriggerReclaimR'];
const finite = v => Number.isFinite(v);
// Discrete quantile, identical to Phase28 threshold derivation.
const discreteQ = (a,p)=>{const v=a.filter(finite).sort((x,y)=>x-y);if(!v.length)return null;return v[Math.floor((v.length-1)*p)]};
// Linear-interpolation quantile, identical to Phase27 feature stats.
const quantile = (a,p)=>{const v=a.filter(finite).sort((x,y)=>x-y);if(!v.length)return null;const i=(v.length-1)*p,l=Math.floor(i),h=Math.ceil(i);return l===h?v[l]:v[l]+(v[h]-v[l])*(i-l)};
const dRate = rows => ({n:rows.length,dCount:rows.filter(x=>x.archetype===D_ARC).length,dRate:rows.length?rows.filter(x=>x.archetype===D_ARC).length/rows.length:null});
const featureStats = rows => Object.fromEntries(FEATURES.map(f=>{const vals=rows.map(x=>x.features[f]);return [f,{median:quantile(vals,.5),q33:quantile(vals,.33),q66:quantile(vals,.66)}]}));
const slice = (rows, by, order) => {
  const keys = order ?? [...new Set(rows.map(by))];
  return Object.fromEntries(keys.map(k=>{const sub=rows.filter(r=>by(r)===k);return [k,{...dRate(sub),share:rows.length?sub.length/rows.length:null,features:featureStats(sub)}]}));
};

const source = JSON.parse(await readFile(SOURCE,'utf8'));
const integrity = source.integrity ?? {};
const expected = Number(integrity.expectedCanonical);
const actual = Number(integrity.canonicalReplayed);
if(expected!==actual || Number(integrity.replayMismatch)!==0 || Number(integrity.missingCanonicalTimestamp)!==0 || Number(integrity.exitMismatch)!==0) throw new Error('PHASE29 source integrity failure');
if(source.scope?.freshHoldoutExcluded!==true || source.scope?.productionUntouched!==true) throw new Error('PHASE29 source guard failure');

const rows=(source.cases??[]).filter(x=>ARCS.includes(x.archetype));
for(const r of rows) for(const f of FEATURES) if(!(f in (r.features??{}))) throw new Error(`Missing feature ${f}`);

// Inherit Phase28 Candidate C thresholds (q66 descriptive quantiles) and assert exact equality.
const spikeT=discreteQ(rows.map(x=>x.features.spikeSizeR),.66);
const corrEffT=discreteQ(rows.map(x=>x.features.correctionEfficiency),.66);
const PH28_SPIKE=15.81569621847631;
const PH28_CORR_EFF=0.8171813809520624;
if(spikeT!==PH28_SPIKE || corrEffT!==PH28_CORR_EFF) throw new Error('PHASE29 threshold inheritance mismatch vs Phase28');

const inCandidateC = r => r.features.spikeSizeR>=spikeT && r.features.correctionEfficiency>=corrEffT;
const candidateC = rows.filter(inCandidateC);
const residualD = rows.filter(r=>r.archetype===D_ARC && !inCandidateC(r));
const nonD = rows.filter(r=>r.archetype!==D_ARC);

const population = (rows,name,definition)=>({name,definition,n:rows.length,...dRate(rows),features:featureStats(rows)});

const result={
  strategy:'Strategy A / SP2L',
  mode:'PHASE_29_D_ARCHETYPE_RESIDUAL_AFTER_GEOMETRY',
  timeframe:'5min',
  source:'Phase24 loss-archetype report; same canonical universe as Phase27/28.',
  scope:{cases:rows.length,dCases:rows.filter(x=>x.archetype===D_ARC).length,nonDCases:nonD.length,freshHoldoutExcluded:true,productionUntouched:true},
  integrity:{expectedCanonical:expected,canonicalReplayed:actual,replayMismatch:Number(integrity.replayMismatch),missingCanonicalTimestamp:Number(integrity.missingCanonicalTimestamp),exitMismatch:Number(integrity.exitMismatch)},
  methodology:{
    purpose:'Analyze residual LOSS_D after explaining Candidate C geometry (Phase28).',
    noOptimization:true,
    noThresholdSearch:true,
    noTradingRules:true,
    thresholds:{spikeSizeR:spikeT,correctionEfficiency:corrEffT},
    thresholdOrigin:'Inherited from Phase28 Candidate C validation (q66 descriptive quantiles, recomputed and asserted equal).'
  },
  populations:{
    candidateC:population(candidateC,'Candidate C','All cases with spikeSizeR >= q66 AND correctionEfficiency >= q66 (Phase28 validated geometry; N=31, D=22, D rate=70.97%).'),
    residualD:population(residualD,'Residual D','LOSS_D cases NOT inside Candidate C geometry (D rate is 1.0 by construction).'),
    nonD:population(nonD,'NON_D','All non-D archetype cases.')
  },
  residualD:{
    byDirection:slice(residualD,r=>r.direction,['BUY','SELL']),
    bySession:slice(residualD,r=>r.session,['LONDON','NEW_YORK','OUT_OF_SESSION'])
  },
  notes:[
    'Descriptive only. No production rule inference.',
    'Candidate C population is defined on the full universe as in Phase28; its 9 non-D members are also counted in NON_D, so populations are not mutually exclusive.',
    'Residual D is the D-archetype subset not explained by Candidate C geometry; D rate is 1.0 by construction.'
  ]
};

await mkdir(OUT,{recursive:true});
await writeFile(resolve(OUT,'5min.json'),JSON.stringify(result,null,2));
const pct = v => v===null?null:(v*100).toFixed(2)+'%';
console.log(`PHASE_29_D_ARCHETYPE_RESIDUAL_AFTER_GEOMETRY 5min N=${rows.length} D=${result.scope.dCases} NON_D=${result.scope.nonDCases}`);
console.log(`CANDIDATE_C n=${candidateC.length} D=${result.populations.candidateC.dCount} D rate=${pct(result.populations.candidateC.dRate)}`);
console.log(`RESIDUAL_D n=${residualD.length} D=${result.populations.residualD.dCount} D rate=${pct(result.populations.residualD.dRate)}`);
console.log(`NON_D n=${nonD.length} D rate=${pct(result.populations.nonD.dRate)}`);
console.log(`RESIDUAL_D BUY=${result.residualD.byDirection.BUY.n} SELL=${result.residualD.byDirection.SELL.n} | LONDON=${result.residualD.bySession.LONDON.n} NEW_YORK=${result.residualD.bySession.NEW_YORK.n} OUT_OF_SESSION=${result.residualD.bySession.OUT_OF_SESSION.n}`);
console.log(`REPORT=${resolve(OUT,'5min.json')}`);