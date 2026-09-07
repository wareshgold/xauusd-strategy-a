import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-phase24-preentry-loss-archetype-predictability/5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase26-d-archetype-feature-decomposition');

const FAMILIES = {
  impulse_quality: ['spikeSizeR', 'spikeStructureScore', 'spikeOverlapScore', 'spikeBars', 'breakoutToFollowThrough'],
  correction_quality: ['correctionSizeR', 'correctionToSpike', 'correctionBars', 'correctionDelay', 'correctionEfficiency'],
  trigger_quality: ['entryTriggerReclaimR', 'entryTriggerBodyR', 'entryTriggerCloseLocation', 'entryTriggerUpperWickShare', 'entryTriggerLowerWickShare'],
};
const ARCS = [
  'LOSS_A_NO_PRE_FAVORABLE',
  'LOSS_B_PRE_0_5_TO_LT_1R',
  'LOSS_C_PRE_1_TO_LT_2R',
  'LOSS_D_PRE_GE_2R',
];
const D_ARC = 'LOSS_D_PRE_GE_2R';
const GROUPS = {
  DEV: rows => rows.filter(x => x.split === 'DEV'),
  VAL: rows => rows.filter(x => x.split === 'VAL'),
  BUY: rows => rows.filter(x => x.direction === 'BUY'),
  SELL: rows => rows.filter(x => x.direction === 'SELL'),
  LONDON: rows => rows.filter(x => x.session === 'LONDON'),
  NEW_YORK: rows => rows.filter(x => x.session === 'NEW_YORK'),
  OUT_OF_SESSION: rows => rows.filter(x => x.session === 'OUT_OF_SESSION'),
};

const mean = values => { const v = values.filter(Number.isFinite); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
const sd = values => { const v = values.filter(Number.isFinite); if (v.length < 2) return null; const m = mean(v); return Math.sqrt(v.reduce((s, x) => s + (x - m) ** 2, 0) / (v.length - 1)); };
const median = values => { const v = values.filter(Number.isFinite).sort((a, b) => a - b); if (!v.length) return null; const m = Math.floor(v.length / 2); return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2; };
const auc = (a, b) => { const x = a.filter(Number.isFinite), y = b.filter(Number.isFinite); if (!x.length || !y.length) return null; let w = 0, ties = 0; for (const i of x) for (const j of y) { if (i > j) w++; else if (i === j) ties++; } return (w + 0.5 * ties) / (x.length * y.length); };
const pearson = (a, b) => { const pairs = a.map((x, i) => [x, b[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y)); if (pairs.length < 3) return null; const ax = mean(pairs.map(p => p[0])), ay = mean(pairs.map(p => p[1])); let n = 0, dx = 0, dy = 0; for (const [x, y] of pairs) { n += (x - ax) * (y - ay); dx += (x - ax) ** 2; dy += (y - ay) ** 2; } return dx && dy ? n / Math.sqrt(dx * dy) : null; };
const rankValues = values => { const pairs = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v); const out = Array(values.length).fill(null); let i = 0; while (i < pairs.length) { let j = i + 1; while (j < pairs.length && pairs[j].v === pairs[i].v) j++; const r = (i + 1 + j) / 2; for (let k = i; k < j; k++) out[pairs[k].i] = r; i = j; } return out; };
const spearman = (a, b) => pearson(rankValues(a), rankValues(b));
const finite = v => Number.isFinite(v);

function featureAudit(rows, feature) {
  const d = rows.filter(x => x.archetype === D_ARC);
  const nonD = rows.filter(x => x.archetype !== D_ARC);
  const dv = d.map(x => x.features[feature]);
  const nv = nonD.map(x => x.features[feature]);
  const dm = mean(dv), nm = mean(nv), ds = sd(dv), ns = sd(nv);
  const pooled = ds !== null && ns !== null && d.length + nonD.length > 2
    ? Math.sqrt(((d.length - 1) * ds ** 2 + (nonD.length - 1) * ns ** 2) / (d.length + nonD.length - 2))
    : null;
  const av = auc(dv, nv);
  return {
    nD: dv.filter(finite).length,
    nNonD: nv.filter(finite).length,
    dMean: dm,
    nonDMean: nm,
    dMedian: median(dv),
    nonDMedian: median(nv),
    meanDelta: dm !== null && nm !== null ? dm - nm : null,
    standardizedDelta: pooled ? (dm - nm) / pooled : null,
    aucDvsNonD: av,
    aucSeparation: av === null ? null : Math.abs(av - 0.5),
    direction: av === null ? null : av > 0.5 ? 'HIGHER_IN_D' : av < 0.5 ? 'LOWER_IN_D' : 'NONE',
  };
}

function groupedAudit(rows, feature) {
  const out = {};
  for (const [name, select] of Object.entries(GROUPS)) {
    const g = select(rows);
    out[name] = featureAudit(g, feature);
  }
  return out;
}

function archetypeMeans(rows, feature) {
  return Object.fromEntries(ARCS.map(a => {
    const vals = rows.filter(x => x.archetype === a).map(x => x.features[feature]);
    return [a, { n: vals.filter(finite).length, mean: mean(vals), median: median(vals) }];
  }));
}

function redundancy(rows, features) {
  const pairs = [];
  for (let i = 0; i < features.length; i++) {
    for (let j = i + 1; j < features.length; j++) {
      const a = rows.map(x => x.features[features[i]]);
      const b = rows.map(x => x.features[features[j]]);
      const r = spearman(a, b);
      if (r !== null) pairs.push({ a: features[i], b: features[j], spearman: r, absSpearman: Math.abs(r) });
    }
  }
  return pairs.sort((x, y) => y.absSpearman - x.absSpearman);
}

const source = JSON.parse(await readFile(SOURCE, 'utf8'));
const integrity = source.integrity ?? {};
const expected = Number(integrity.expectedCanonical);
const actual = Number(integrity.canonicalReplayed);
if (expected !== actual || Number(integrity.replayMismatch) !== 0 || Number(integrity.missingCanonicalTimestamp) !== 0 || Number(integrity.exitMismatch) !== 0) {
  throw new Error(`PHASE26 source integrity failure: expected=${expected} actual=${actual} replayMismatch=${integrity.replayMismatch} missingTimestamp=${integrity.missingCanonicalTimestamp} exitMismatch=${integrity.exitMismatch}`);
}
if (source.scope?.freshHoldoutExcluded !== true || source.scope?.productionUntouched !== true) {
  throw new Error('PHASE26 source guard failure: Fresh Holdout or production-untouched flag is not locked.');
}

const rows = (source.cases ?? []).filter(x => ARCS.includes(x.archetype));
const allFeatures = Object.values(FAMILIES).flat();
for (const row of rows) for (const feature of allFeatures) {
  if (!(feature in (row.features ?? {}))) throw new Error(`PHASE26 missing feature ${feature} at ${row.entryTime}`);
}

const overall = {};
for (const [family, features] of Object.entries(FAMILIES)) {
  overall[family] = {};
  for (const feature of features) {
    overall[family][feature] = {
      overall: featureAudit(rows, feature),
      grouped: groupedAudit(rows, feature),
      archetypeMeans: archetypeMeans(rows, feature),
    };
  }
}

const ranking = allFeatures.map(feature => {
  const family = Object.entries(FAMILIES).find(([, fs]) => fs.includes(feature))?.[0] ?? 'UNKNOWN';
  const o = featureAudit(rows, feature);
  const groups = groupedAudit(rows, feature);
  const dev = groups.DEV;
  const val = groups.VAL;
  const sameDirection = dev?.direction && val?.direction && dev.direction === val.direction && dev.direction !== 'NONE';
  return {
    family,
    feature,
    overallAUC: o.aucDvsNonD,
    overallSeparation: o.aucSeparation,
    overallDirection: o.direction,
    devAUC: dev?.aucDvsNonD ?? null,
    valAUC: val?.aucDvsNonD ?? null,
    devDirection: dev?.direction ?? null,
    valDirection: val?.direction ?? null,
    sameDEVVALDirection: Boolean(sameDirection),
  };
}).sort((a, b) => (b.overallSeparation ?? -1) - (a.overallSeparation ?? -1));

const redundancyAudit = Object.fromEntries(Object.entries(FAMILIES).map(([family, features]) => [family, redundancy(rows, features)]));
const stableDirectional = ranking.filter(x => x.sameDEVVALDirection);

const result = {
  strategy: 'Strategy A / SP2L',
  mode: 'PHASE_26_D_ARCHETYPE_FEATURE_DECOMPOSITION',
  timeframe: '5min',
  source: 'Phase24 loss-archetype report; no new replay or post-entry labeling performed here.',
  scope: {
    cases: rows.length,
    losses: rows.length,
    dCases: rows.filter(x => x.archetype === D_ARC).length,
    nonDCases: rows.filter(x => x.archetype !== D_ARC).length,
    freshHoldoutExcluded: true,
    productionUntouched: true,
  },
  integrity: {
    sourceExpectedCanonical: expected,
    sourceCanonicalReplayed: actual,
    sourceReplayMismatch: Number(integrity.replayMismatch),
    sourceMissingCanonicalTimestamp: Number(integrity.missingCanonicalTimestamp),
    sourceExitMismatch: Number(integrity.exitMismatch),
    sourceExactBaselineSelectionSemantics: source.integrity.exactBaselineSelectionSemantics === true,
    sourceExactBaselineExitSemantics: source.integrity.exactBaselineExitSemantics === true,
  },
  methodology: {
    purpose: 'Decompose the Phase25 D-vs-non-D family separation into individual pre-entry features.',
    target: `${D_ARC} versus all other losing archetypes.`,
    metric: 'One-vs-rest AUC where AUC > 0.5 means the feature is higher in D and AUC < 0.5 means lower in D.',
    validation: 'Each feature is audited overall and separately in DEV, VAL, BUY, SELL, LONDON, NEW_YORK and OUT_OF_SESSION. DEV/VAL direction agreement is reported descriptively.',
    redundancy: 'Within-family pairwise Spearman correlation is reported to identify features carrying overlapping information.',
    noOptimization: true,
    noThresholdSearch: true,
    noNewTradingRules: true,
    noFreshHoldoutAccess: true,
  },
  featureFamilies: FAMILIES,
  featureAudit: overall,
  rankedByOverallAUCSeparation: ranking,
  stableDirectionalDEVVAL: stableDirectional,
  withinFamilyRedundancy: redundancyAudit,
  interpretationGuard: {
    note: 'This is a descriptive decomposition, not a filter-selection study. A feature being separated does not authorize a threshold or production rule.',
  },
};

await mkdir(OUT, { recursive: true });
await writeFile(resolve(OUT, '5min.json'), JSON.stringify(result, null, 2));

console.log(`PHASE_26_D_ARCHETYPE_FEATURE_DECOMPOSITION 5min N=${rows.length} D=${result.scope.dCases} NON_D=${result.scope.nonDCases} FRESH=LOCKED`);
console.log(`INTEGRITY sourceExpected=${expected} sourceActual=${actual} replayMismatch=${integrity.replayMismatch} missingCanonicalTimestamp=${integrity.missingCanonicalTimestamp} exitMismatch=${integrity.exitMismatch}`);
for (const x of ranking) console.log(`FEATURE ${x.family}.${x.feature}: overallAUC=${x.overallAUC?.toFixed(4)} sep=${x.overallSeparation?.toFixed(4)} dir=${x.overallDirection} DEV=${x.devAUC?.toFixed(4)}(${x.devDirection}) VAL=${x.valAUC?.toFixed(4)}(${x.valDirection}) stableDEVVAL=${x.sameDEVVALDirection}`);
for (const [family, pairs] of Object.entries(redundancyAudit)) {
  const top = pairs.slice(0, 3).map(p => `${p.a}~${p.b}:${p.spearman?.toFixed(3)}`).join(' ');
  console.log(`REDUNDANCY ${family}: ${top || 'none'}`);
}
console.log(`STABLE_DIRECTIONAL_DEV_VAL count=${stableDirectional.length}`);
console.log(`REPORT=${resolve(OUT, '5min.json')}`);
console.log('STATUS=DESCRIPTIVE_ONLY FEATURE_DECOMPOSITION NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');