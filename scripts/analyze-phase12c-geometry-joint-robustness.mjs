import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-phase12b-geometry-quantile-robustness/5m.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-phase12c-geometry-joint-robustness');
const OUT = resolve(OUT_DIR, '5m.json');

// Pre-declared feature pairs. This is an information/redundancy audit only.
// Median splits are descriptive partitions, not proposed trading thresholds.
const FEATURES = [
  'triggerReclaimToRange',
  'triggerBodyToRange',
  'pathEfficiency',
  'lowerWickShare',
  'bodyParticipation',
];
const PAIRS = [
  ['triggerReclaimToRange', 'triggerBodyToRange'],
  ['triggerReclaimToRange', 'pathEfficiency'],
  ['triggerBodyToRange', 'pathEfficiency'],
  ['triggerBodyToRange', 'bodyParticipation'],
  ['lowerWickShare', 'bodyParticipation'],
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

function median(rows, feature) {
  const values = rows.map((r) => r[feature]).filter(finite).sort((a, b) => a - b);
  if (!values.length) return null;
  const mid = Math.floor(values.length / 2);
  return values.length % 2 ? values[mid] : (values[mid - 1] + values[mid]) / 2;
}

function jointMatrix(rows, a, b) {
  const usable = rows.filter((r) => finite(r[a]) && finite(r[b]) && finite(r.r));
  if (usable.length < 20) return { n: usable.length, medianA: null, medianB: null, cells: {} };
  const medianA = median(usable, a);
  const medianB = median(usable, b);
  const cells = {};
  for (const aSide of ['LOW', 'HIGH']) {
    for (const bSide of ['LOW', 'HIGH']) {
      const group = usable.filter((r) =>
        (aSide === 'HIGH' ? r[a] >= medianA : r[a] < medianA) &&
        (bSide === 'HIGH' ? r[b] >= medianB : r[b] < medianB)
      );
      cells[`${aSide}_${bSide}`] = outcome(group);
    }
  }
  return { n: usable.length, medianA, medianB, cells };
}

function compareGroups(rows, a, b) {
  const usable = rows.filter((r) => finite(r[a]) && finite(r[b]) && finite(r.r) && r.r < 5);
  if (usable.length < 20) return null;
  const ma = median(usable, a);
  const mb = median(usable, b);
  const highHigh = usable.filter((r) => r[a] >= ma && r[b] >= mb);
  const lowLow = usable.filter((r) => r[a] < ma && r[b] < mb);
  const highLow = usable.filter((r) => r[a] >= ma && r[b] < mb);
  const lowHigh = usable.filter((r) => r[a] < ma && r[b] >= mb);
  return {
    n: usable.length,
    exceptionalExcluded: true,
    highHighMinusLowLowAvgR: outcome(highHigh).avgR - outcome(lowLow).avgR,
    highLowMinusLowHighAvgR: outcome(highLow).avgR - outcome(lowHigh).avgR,
    cellCounts: {
      HIGH_HIGH: highHigh.length,
      HIGH_LOW: highLow.length,
      LOW_HIGH: lowHigh.length,
      LOW_LOW: lowLow.length,
    },
  };
}

function featureDirectionSummary(report, feature) {
  const s = report.features?.[feature]?.stability;
  if (!s) return null;
  return {
    ALL: { slope: round(s.ALL.avgRByBinSlope), monotonic: s.ALL.monotonicNonDecreasing },
    DEV: { slope: round(s.DEV.avgRByBinSlope), monotonic: s.DEV.monotonicNonDecreasing },
    VAL: { slope: round(s.VAL.avgRByBinSlope), monotonic: s.VAL.monotonicNonDecreasing },
  };
}

async function main() {
  const report = JSON.parse(await readFile(INPUT, 'utf8'));
  const rows = report?.scope?.n ? null : null;
  // Phase 12B intentionally stores its analysis results, not raw cases. Reload Phase 12 for exact case rows.
  const phase12 = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-phase12-preentry-geometry-robustness/5m.json'), 'utf8'));
  const cases = phase12.cases ?? [];
  if (!cases.length) throw new Error('PHASE12C: Phase 12 report contains no cases');

  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'PHASE_12C_GEOMETRY_JOINT_ROBUSTNESS',
    timeframe: '5m',
    inputReports: [
      'strategy-a-phase12-preentry-geometry-robustness/5m.json',
      'strategy-a-phase12b-geometry-quantile-robustness/5m.json',
    ],
    scope: {
      n: cases.length,
      dev: cases.filter((r) => r.split === 'DEV').length,
      val: cases.filter((r) => r.split === 'VAL').length,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    methodology: {
      purpose: 'Descriptive joint-state and redundancy audit for pre-entry geometry features already identified in Phases 12 and 12B.',
      partition: 'Within each sample, each feature is split at its sample median; this is a descriptive state partition, not a trading threshold.',
      pairs: PAIRS,
      exceptionalExcludedFromContrast: 'rMultiple >= 5 excluded only from the contrast summary; raw cell outcomes retain all cases.',
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      noFreshHoldoutAccess: true,
      note: 'Pairs were pre-declared from Phase 12B stability evidence. No pair is selected or promoted to a trading rule by this audit.',
    },
    featureDirections: Object.fromEntries(FEATURES.map((f) => [f, featureDirectionSummary(report, f)])),
    pairs: {},
  };

  for (const [a, b] of PAIRS) {
    result.pairs[`${a}__${b}`] = {
      ALL: jointMatrix(cases, a, b),
      DEV: jointMatrix(cases.filter((r) => r.split === 'DEV'), a, b),
      VAL: jointMatrix(cases.filter((r) => r.split === 'VAL'), a, b),
      contrast: {
        ALL: compareGroups(cases, a, b),
        DEV: compareGroups(cases.filter((r) => r.split === 'DEV'), a, b),
        VAL: compareGroups(cases.filter((r) => r.split === 'VAL'), a, b),
      },
    };
  }

  await mkdir(OUT_DIR, { recursive: true });
  await writeFile(OUT, JSON.stringify(result, null, 2));
  console.log(`PHASE_12C_GEOMETRY_JOINT_ROBUSTNESS N=${cases.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  for (const [pair, value] of Object.entries(result.pairs)) {
    console.log(`${pair}: ALL HH-LL=${round(value.contrast.ALL?.highHighMinusLowLowAvgR)} DEV HH-LL=${round(value.contrast.DEV?.highHighMinusLowLowAvgR)} VAL HH-LL=${round(value.contrast.VAL?.highHighMinusLowLowAvgR)}`);
  }
  console.log(`REPORT=${OUT}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}

await main();
