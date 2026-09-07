import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-phase12-preentry-geometry-robustness/5m.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-phase12b-geometry-quantile-robustness');
const OUT = resolve(OUT_DIR, '5m.json');

// Fixed descriptive bins. These are ranks, not optimized trading thresholds.
const BIN_COUNT = 5;
const BOOTSTRAP_ITERATIONS = 4000;
const PERMUTATION_ITERATIONS = 4000;
const SEED = 1207;
const FEATURES = [
  'triggerReclaimToRange',
  'triggerBodyToRange',
  'triggerCloseLocation',
  'pathEfficiency',
  'lowerWickShare',
  'bodyParticipation',
  'secondHalfProgress',
];

const finite = (v) => Number.isFinite(v);
const round = (v, d = 6) => finite(v) ? Number(v.toFixed(d)) : null;

function outcome(rows) {
  const x = rows.filter((r) => finite(r.r));
  if (!x.length) return { n: 0, wins: 0, WR: null, avgR: null, PF: null, totalR: 0 };
  const wins = x.filter((r) => r.r > 0);
  const losses = x.filter((r) => r.r <= 0);
  const grossWin = wins.reduce((s, r) => s + r.r, 0);
  const grossLoss = losses.reduce((s, r) => s + Math.abs(r.r), 0);
  return {
    n: x.length,
    wins: wins.length,
    WR: wins.length / x.length,
    avgR: x.reduce((s, r) => s + r.r, 0) / x.length,
    PF: grossLoss > 0 ? grossWin / grossLoss : null,
    totalR: x.reduce((s, r) => s + r.r, 0),
  };
}

function sortedFinite(rows, feature) {
  return rows.filter((r) => finite(r[feature]) && finite(r.r)).sort((a, b) => a[feature] - b[feature]);
}

function quantileBins(rows, feature, bins = BIN_COUNT) {
  const sorted = sortedFinite(rows, feature);
  if (!sorted.length) return [];
  const out = [];
  for (let i = 0; i < bins; i++) {
    const start = Math.floor(i * sorted.length / bins);
    const end = Math.floor((i + 1) * sorted.length / bins);
    const group = sorted.slice(start, Math.max(start + 1, end));
    if (!group.length) continue;
    out.push({
      bin: i + 1,
      n: group.length,
      min: group[0][feature],
      max: group[group.length - 1][feature],
      median: group[Math.floor(group.length / 2)][feature],
      outcome: outcome(group),
    });
  }
  return out;
}

function slope(bins) {
  const usable = bins.filter((b) => finite(b.outcome.avgR));
  if (usable.length < 3) return null;
  const mx = usable.reduce((s, b) => s + b.bin, 0) / usable.length;
  const my = usable.reduce((s, b) => s + b.outcome.avgR, 0) / usable.length;
  let num = 0, den = 0;
  for (const b of usable) { num += (b.bin - mx) * (b.outcome.avgR - my); den += (b.bin - mx) ** 2; }
  return den ? num / den : null;
}

function lcg(seed) {
  let state = seed >>> 0;
  return () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

function bootstrapMeanDifference(rows, feature, rng) {
  const usable = rows.filter((r) => finite(r[feature]) && finite(r.r) && r.r < 5);
  if (usable.length < 20) return null;
  const sorted = [...usable].sort((a, b) => a[feature] - b[feature]);
  const cut = Math.floor(sorted.length / 2);
  const low = sorted.slice(0, cut);
  const high = sorted.slice(cut);
  const observed = outcome(high).avgR - outcome(low).avgR;
  const diffs = new Array(BOOTSTRAP_ITERATIONS);
  for (let b = 0; b < BOOTSTRAP_ITERATIONS; b++) {
    const sample = Array.from({ length: usable.length }, () => usable[Math.floor(rng() * usable.length)]);
    sample.sort((a, c) => a[feature] - c[feature]);
    const m = Math.floor(sample.length / 2);
    diffs[b] = outcome(sample.slice(m)).avgR - outcome(sample.slice(0, m)).avgR;
  }
  diffs.sort((a, b) => a - b);
  const lo = diffs[Math.floor(0.025 * diffs.length)];
  const hi = diffs[Math.floor(0.975 * diffs.length)];
  return { n: usable.length, observedMedianSplitAvgRDiff: observed, bootstrap95CI: [lo, hi] };
}

function permutationPValue(rows, feature, rng) {
  const usable = rows.filter((r) => finite(r[feature]) && finite(r.r) && r.r < 5);
  if (usable.length < 20) return null;
  const ordered = [...usable].sort((a, b) => a[feature] - b[feature]);
  const cut = Math.floor(ordered.length / 2);
  const labels = Array.from({ length: ordered.length }, (_, i) => i >= cut);
  const observed = outcome(ordered.filter((_, i) => labels[i])).avgR - outcome(ordered.filter((_, i) => !labels[i])).avgR;
  const values = usable.map((r) => r.r);
  let extreme = 0;
  for (let p = 0; p < PERMUTATION_ITERATIONS; p++) {
    for (let i = values.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [values[i], values[j]] = [values[j], values[i]];
    }
    let hiSum = 0, loSum = 0;
    for (let i = 0; i < values.length; i++) {
      if (labels[i]) hiSum += values[i]; else loSum += values[i];
    }
    const diff = hiSum / (values.length - cut) - loSum / cut;
    if (Math.abs(diff) >= Math.abs(observed)) extreme++;
  }
  return { n: usable.length, observedMedianSplitAvgRDiff: observed, permutationPValueTwoSided: (extreme + 1) / (PERMUTATION_ITERATIONS + 1) };
}

function directionalSession(rows) {
  const groups = {};
  for (const r of rows) {
    const key = `${r.direction}+${r.session}`;
    (groups[key] ??= []).push(r);
  }
  return Object.fromEntries(Object.entries(groups).sort().map(([k, v]) => [k, outcome(v)]));
}

function stability(rows, feature) {
  const dev = rows.filter((r) => r.split === 'DEV');
  const val = rows.filter((r) => r.split === 'VAL');
  const result = {};
  for (const [name, group] of [['ALL', rows], ['DEV', dev], ['VAL', val]]) {
    const bins = quantileBins(group, feature);
    const s = slope(bins);
    result[name] = { bins, avgRByBinSlope: s, monotonicNonDecreasing: bins.length >= 3 ? bins.every((b, i) => i === 0 || b.outcome.avgR >= bins[i - 1].outcome.avgR) : null };
  }
  return result;
}

async function main() {
  const report = JSON.parse(await readFile(INPUT, 'utf8'));
  const rows = report.cases ?? [];
  if (!rows.length) throw new Error('PHASE12B: Phase 12 report contains no cases');
  const rng = lcg(SEED);
  const featureResults = {};
  for (const feature of FEATURES) {
    featureResults[feature] = {
      stability: stability(rows, feature),
      medianSplitRobustness: {
        ALL: bootstrapMeanDifference(rows, feature, rng),
        DEV: bootstrapMeanDifference(rows.filter((r) => r.split === 'DEV'), feature, rng),
        VAL: bootstrapMeanDifference(rows.filter((r) => r.split === 'VAL'), feature, rng),
      },
      permutationAudit: {
        ALL: permutationPValue(rows, feature, rng),
        DEV: permutationPValue(rows.filter((r) => r.split === 'DEV'), feature, rng),
        VAL: permutationPValue(rows.filter((r) => r.split === 'VAL'), feature, rng),
      },
      directionSessionOutcome: directionalSession(rows),
    };
  }

  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'PHASE_12B_GEOMETRY_QUANTILE_ROBUSTNESS',
    timeframe: '5m',
    inputReport: 'strategy-a-phase12-preentry-geometry-robustness/5m.json',
    scope: {
      n: rows.length,
      dev: rows.filter((r) => r.split === 'DEV').length,
      val: rows.filter((r) => r.split === 'VAL').length,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    methodology: {
      purpose: 'Descriptive robustness decomposition of pre-entry geometry features already audited in Phase 12.',
      fixedBinCount: BIN_COUNT,
      binning: 'Empirical quintiles within each reported sample; bins are descriptive ranks, not trading thresholds.',
      bootstrapIterations: BOOTSTRAP_ITERATIONS,
      permutationIterations: PERMUTATION_ITERATIONS,
      seed: SEED,
      exceptionalExcludedFromRobustnessTests: 'rMultiple >= 5 excluded only from median-split bootstrap/permutation audits.',
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      noFreshHoldoutAccess: true,
      note: 'No threshold, filter, direction rule, session rule, or execution rule is proposed or changed by this audit.',
    },
    features: featureResults,
  };

  await mkdir(OUT_DIR, { recursive: true });
  await writeFile(OUT, JSON.stringify(result, null, 2));
  console.log(`PHASE_12B_GEOMETRY_QUANTILE_ROBUSTNESS N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  for (const feature of FEATURES) {
    const s = featureResults[feature].stability;
    console.log(`${feature}: ALL slope=${round(s.ALL.avgRByBinSlope)} DEV slope=${round(s.DEV.avgRByBinSlope)} VAL slope=${round(s.VAL.avgRByBinSlope)} | ALL mono=${s.ALL.monotonicNonDecreasing} DEV mono=${s.DEV.monotonicNonDecreasing} VAL mono=${s.VAL.monotonicNonDecreasing}`);
  }
  console.log(`REPORT=${OUT}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}

await main();
