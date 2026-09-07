import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase25-d-archetype-robustness');

const source = JSON.parse(await readFile(SOURCE, 'utf8'));
const rows = Array.isArray(source.cases) ? source.cases : [];
const D = 'LOSS_D_PRE_GE_2R';
const FEATURES = {
  impulse_quality: ['spikeSizeR', 'spikeStructureScore', 'spikeOverlapScore', 'spikeBars', 'breakoutToFollowThrough'],
  correction_quality: ['correctionSizeR', 'correctionToSpike', 'correctionBars', 'correctionDelay', 'correctionEfficiency'],
  trigger_quality: ['entryTriggerReclaimR', 'entryTriggerBodyR', 'entryTriggerCloseLocation', 'entryTriggerUpperWickShare', 'entryTriggerLowerWickShare'],
};
const DIMENSIONS = {
  split: ['DEV', 'VAL'],
  direction: ['BUY', 'SELL'],
  session: ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION'],
};

const mean = a => { const v = a.filter(Number.isFinite); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
const sd = a => { const v = a.filter(Number.isFinite); if (v.length < 2) return null; const m = mean(v); return Math.sqrt(v.reduce((s, x) => s + (x - m) ** 2, 0) / (v.length - 1)); };
const median = a => { const v = a.filter(Number.isFinite).sort((x, y) => x - y); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const rank = values => {
  const pairs = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v);
  const out = Array(values.length).fill(null);
  let i = 0;
  while (i < pairs.length) {
    let j = i + 1;
    while (j < pairs.length && pairs[j].v === pairs[i].v) j++;
    const r = (i + 1 + j) / 2;
    for (let k = i; k < j; k++) out[pairs[k].i] = r;
    i = j;
  }
  return out;
};
const auc = (target, rest) => {
  const x = target.filter(Number.isFinite), y = rest.filter(Number.isFinite);
  if (!x.length || !y.length) return null;
  let wins = 0, ties = 0;
  for (const a of x) for (const b of y) { if (a > b) wins++; else if (a === b) ties++; }
  return (wins + ties * 0.5) / (x.length * y.length);
};

function validateSource() {
  const i = source.integrity ?? {};
  if (i.replayMismatch !== 0 || i.missingCanonicalTimestamp !== 0 || i.exitMismatch !== 0) {
    throw new Error(`PHASE25 source integrity is not clean: replayMismatch=${i.replayMismatch} missingCanonicalTimestamp=${i.missingCanonicalTimestamp} exitMismatch=${i.exitMismatch}`);
  }
  if (Number(i.canonicalReplayed) !== Number(i.expectedCanonical)) {
    throw new Error(`PHASE25 source canonical count mismatch: expected=${i.expectedCanonical} actual=${i.canonicalReplayed}`);
  }
}

validateSource();
if (!rows.length) throw new Error('PHASE25 no Phase24 cases found');

const losses = rows.filter(r => r.outcome === 'LOSS');
const dRows = losses.filter(r => r.archetype === D);
const nonD = losses.filter(r => r.archetype !== D);

const familyScores = Object.fromEntries(Object.entries(FEATURES).map(([family, keys]) => {
  const ranks = Object.fromEntries(keys.map(k => [k, rank(losses.map(r => r.features?.[k]))]));
  const scores = new Map();
  for (let i = 0; i < losses.length; i++) {
    const vals = keys.map(k => ranks[k][i]).filter(Number.isFinite);
    scores.set(losses[i], vals.length > 1 ? mean(vals.map(v => (v - 1) / (losses.length - 1))) : null);
  }
  return [family, scores];
}));

function auditGroup(group, rest) {
  const out = {};
  for (const [family] of Object.entries(FEATURES)) {
    const target = group.map(r => familyScores[family].get(r)).filter(Number.isFinite);
    const other = rest.map(r => familyScores[family].get(r)).filter(Number.isFinite);
    const tm = mean(target), rm = mean(other), ts = sd(target), rs = sd(other);
    const pooled = ts !== null && rs !== null && target.length + other.length > 2
      ? Math.sqrt(((target.length - 1) * ts ** 2 + (other.length - 1) * rs ** 2) / (target.length + other.length - 2))
      : null;
    out[family] = {
      n: target.length,
      meanRank: tm,
      medianRank: median(target),
      restMeanRank: rm,
      deltaVsRest: tm !== null && rm !== null ? tm - rm : null,
      standardizedDeltaVsRest: pooled ? (tm - rm) / pooled : null,
      aucVsRest: auc(target, other),
    };
  }
  return out;
}

function dimensionAudit(field, values) {
  return Object.fromEntries(values.map(value => {
    const group = dRows.filter(r => r[field] === value);
    const rest = nonD.filter(r => r[field] === value);
    return [value, { nD: group.length, nNonD: rest.length, audit: auditGroup(group, rest) }];
  }));
}

function dShare(group) {
  const total = group.length;
  return total ? dRows.filter(r => group.includes(r)).length / total : null;
}

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_25_D_ARCHETYPE_ROBUSTNESS',
  timeframe: '5min',
  scope: {
    sourceMode: 'Phase24 canonical loss cases',
    totalBaselineTrades: source.scope?.canonicalReplayed ?? null,
    totalLosses: losses.length,
    dLosses: dRows.length,
    freshHoldoutExcluded: true,
    productionUntouched: true,
  },
  integrity: source.integrity,
  methodology: {
    purpose: 'Descriptive robustness audit of the Phase24 LOSS_D pre-entry separation finding.',
    target: 'LOSS_D_PRE_GE_2R versus all other loss archetypes.',
    targetDefinition: 'A losing trade whose pre-exit MFE reaches at least 2R before the eventual SL.',
    featureGuard: 'Only Phase24 pre-entry feature families are used as predictors; the post-entry MFE/archetype label is never used as a predictor.',
    compression: 'Feature percentile ranks are computed once across the complete loss population, then family scores are unweighted means of member ranks. This global ranking is retained across every subgroup to avoid subgroup-local rank inflation.',
    dimensions: ['DEV/VAL', 'BUY/SELL', 'LONDON/NEW_YORK/OUT_OF_SESSION'],
    interpretation: 'AUC, standardized deltas and sample counts are descriptive only. No threshold, cutoff, filter or production rule is selected.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  overall: {
    dN: dRows.length,
    nonDN: nonD.length,
    dShareOfLosses: losses.length ? dRows.length / losses.length : null,
    familyAudit: auditGroup(dRows, nonD),
  },
  dimensions: {
    split: dimensionAudit('split', DIMENSIONS.split),
    direction: dimensionAudit('direction', DIMENSIONS.direction),
    session: dimensionAudit('session', DIMENSIONS.session),
  },
  dCounts: {
    split: Object.fromEntries(DIMENSIONS.split.map(v => [v, dRows.filter(r => r.split === v).length])),
    direction: Object.fromEntries(DIMENSIONS.direction.map(v => [v, dRows.filter(r => r.direction === v).length])),
    session: Object.fromEntries(DIMENSIONS.session.map(v => [v, dRows.filter(r => r.session === v).length])),
  },
};

await mkdir(OUT, { recursive: true });
await writeFile(resolve(OUT, '5min.json'), JSON.stringify(result, null, 2));

console.log(`PHASE_25_D_ARCHETYPE_ROBUSTNESS 5min LOSSES=${losses.length} D=${dRows.length} NON_D=${nonD.length} FRESH=LOCKED`);
console.log(`INTEGRITY expected=${source.integrity.expectedCanonical} actual=${source.integrity.canonicalReplayed} replayMismatch=${source.integrity.replayMismatch} missingCanonicalTimestamp=${source.integrity.missingCanonicalTimestamp} exitMismatch=${source.integrity.exitMismatch}`);
console.log(`OVERALL D_SHARE=${(result.overall.dShareOfLosses * 100).toFixed(2)}%`);
for (const [family, a] of Object.entries(result.overall.familyAudit)) console.log(`OVERALL ${family}: D_N=${a.n} mean=${a.meanRank?.toFixed(4)} vsRest=${a.standardizedDeltaVsRest?.toFixed(4)} auc=${a.aucVsRest?.toFixed(4)}`);
for (const [dimension, values] of Object.entries(result.dimensions)) {
  for (const [value, a] of Object.entries(values)) {
    console.log(`${dimension.toUpperCase()} ${value}: D=${a.nD} NON_D=${a.nNonD} ${Object.entries(a.audit).map(([f, x]) => `${f}[delta=${x.standardizedDeltaVsRest?.toFixed(4)},auc=${x.aucVsRest?.toFixed(4)}]`).join(' ')}`);
  }
}
console.log(`REPORT=${resolve(OUT, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY ROBUSTNESS_AUDIT NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
