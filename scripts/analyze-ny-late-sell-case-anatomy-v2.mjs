import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const ANATOMY = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-case-anatomy/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-case-anatomy-v2');
const GROUPS = ['EXCEPTIONAL_WIN', 'NORMAL_WIN', 'LOSS'];
const FEATURES = [
  'breakoutExtension',
  'breakoutExtensionToPreRange',
  'breakoutToFollowThroughBars',
  'followThroughDistance',
  'followThroughFromLevel',
  'followThroughDistanceToPreRange',
  'spikeSize',
  'spikeSizeToMedianRange',
  'spikeSizeToPreRange',
  'spikeDurationBars',
  'correctionBars',
  'correctionDepth',
  'entryDelayFromCorrection',
  'entryDistanceFromStructuralHigh',
  'entryDistanceFromStructuralHighPct',
  'entryDistanceFromSpikeEnd',
  'entryDistanceFromSpikeEndPct',
  'stopDistance',
  'rewardDistance',
  'plannedRR',
];
const HORIZONS = [12, 24, 48];

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return {
    n: a.length,
    min: p(a[0]),
    p25: q(0.25),
    median: q(0.5),
    p75: q(0.75),
    max: p(a[a.length - 1]),
    mean: p(a.reduce((s, x) => s + x, 0) / a.length),
  };
}

function rowsFor(cases, group) {
  return cases.filter((x) => x.classification === group);
}

function featureValue(row, feature) {
  return Number(row.geometry?.[feature]);
}

function featureTable(cases) {
  const out = {};
  for (const feature of FEATURES) {
    out[feature] = Object.fromEntries(GROUPS.map((group) => [
      group,
      quantiles(rowsFor(cases, group).map((row) => featureValue(row, feature))),
    ]));
  }
  return out;
}

function pathTable(cases) {
  const out = {};
  for (const horizon of HORIZONS) {
    const key = String(horizon);
    out[key] = {};
    for (const group of GROUPS) {
      const rows = rowsFor(cases, group);
      out[key][group] = {
        mfeR: quantiles(rows.map((x) => Number(x.fixedHorizonExcursion?.[key]?.mfeR))),
        maeR: quantiles(rows.map((x) => Number(x.fixedHorizonExcursion?.[key]?.maeR))),
        barsObserved: quantiles(rows.map((x) => Number(x.fixedHorizonExcursion?.[key]?.bars))),
      };
    }
  }
  return out;
}

function outcomePathTable(cases) {
  return Object.fromEntries(GROUPS.map((group) => {
    const rows = rowsFor(cases, group);
    return [group, {
      barsToOutcome: quantiles(rows.map((x) => Number(x.outcomeExcursion?.barsToOutcome))),
      mfeR: quantiles(rows.map((x) => Number(x.outcomeExcursion?.mfeR))),
      maeR: quantiles(rows.map((x) => Number(x.outcomeExcursion?.maeR))),
      plannedRR: quantiles(rows.map((x) => Number(x.geometry?.plannedRR))),
      outcomeMfeOverPlannedRR: quantiles(rows.map((x) => {
        const rr = Number(x.geometry?.plannedRR);
        const mfe = Number(x.outcomeExcursion?.mfeR);
        return rr > 0 && Number.isFinite(mfe) ? mfe / rr : NaN;
      })),
    }];
  }));
}

function casePathRows(cases) {
  return cases.map((x) => ({
    split: x.split,
    time: x.entryTime,
    class: x.classification,
    r: x.r,
    plannedRR: x.geometry?.plannedRR,
    entryDelay: x.geometry?.entryDelayFromCorrection,
    correctionBars: x.geometry?.correctionBars,
    correctionDepth: x.geometry?.correctionDepth,
    spikeSizeToPreRange: x.geometry?.spikeSizeToPreRange,
    breakoutExtensionToPreRange: x.geometry?.breakoutExtensionToPreRange,
    entryDistanceFromStructuralHighPct: x.geometry?.entryDistanceFromStructuralHighPct,
    entryDistanceFromSpikeEndPct: x.geometry?.entryDistanceFromSpikeEndPct,
    barsToOutcome: x.outcomeExcursion?.barsToOutcome ?? null,
    outcomeMfeR: x.outcomeExcursion?.mfeR ?? null,
    outcomeMaeR: x.outcomeExcursion?.maeR ?? null,
    h12MfeR: x.fixedHorizonExcursion?.['12']?.mfeR ?? null,
    h12MaeR: x.fixedHorizonExcursion?.['12']?.maeR ?? null,
    h24MfeR: x.fixedHorizonExcursion?.['24']?.mfeR ?? null,
    h24MaeR: x.fixedHorizonExcursion?.['24']?.maeR ?? null,
    h48MfeR: x.fixedHorizonExcursion?.['48']?.mfeR ?? null,
    h48MaeR: x.fixedHorizonExcursion?.['48']?.maeR ?? null,
  }));
}

function devValTable(cases) {
  return Object.fromEntries([...GROUPS, 'ALL'].map((group) => {
    const rows = group === 'ALL' ? cases : rowsFor(cases, group);
    return [group, {
      DEV: rows.filter((x) => x.split === 'DEV').length,
      VAL: rows.filter((x) => x.split === 'VAL').length,
    }];
  }));
}

async function main() {
  const report = JSON.parse(await readFile(ANATOMY, 'utf8'));
  const cases = report.cases ?? [];
  if (cases.length !== 15) throw new Error(`Expected 15 anatomy cases, got ${cases.length}`);

  const result = {
    strategy: report.strategy,
    mode: 'RESEARCH_NY_LATE_SELL_CASE_ANATOMY_V2',
    timeframe: '5m',
    scope: {
      source: 'NY late sell case anatomy',
      n: cases.length,
      dev: cases.filter((x) => x.split === 'DEV').length,
      val: cases.filter((x) => x.split === 'VAL').length,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    methodology: {
      purpose: 'Descriptive comparison of pre-entry geometry and post-entry path dynamics across exceptional wins, normal wins, and losses.',
      preEntryOnlyForFeatures: true,
      postEntryMetricsAreOutcomeDiagnostics: true,
      noOptimization: true,
      noNewTradingRules: true,
      noThresholdSearch: true,
      holdoutLocked: true,
      note: 'Group separation is exploratory only because n=15. Any apparent difference must be tested on a larger unseen sample before becoming a hypothesis or rule.',
    },
    devValCounts: devValTable(cases),
    preEntryGeometry: featureTable(cases),
    postEntryFixedHorizon: pathTable(cases),
    outcomePath: outcomePathTable(cases),
    cases: casePathRows(cases),
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));

  console.log(`5m anatomy v2: cases=${cases.length}`);
  console.log('DEV/VAL by class:');
  console.table(result.devValCounts);
  console.log('Pre-entry geometry — medians:');
  console.table(Object.fromEntries(FEATURES.map((feature) => [
    feature,
    Object.fromEntries(GROUPS.map((group) => [group, result.preEntryGeometry[feature][group].median])),
  ])));
  console.log('Outcome path:');
  console.table(Object.fromEntries(GROUPS.map((group) => [group, {
    n: rowsFor(cases, group).length,
    plannedRR_median: result.outcomePath[group].plannedRR.median,
    barsToOutcome_median: result.outcomePath[group].barsToOutcome.median,
    outcomeMfeR_median: result.outcomePath[group].mfeR.median,
    outcomeMaeR_median: result.outcomePath[group].maeR.median,
    outcomeMfeOverPlannedRR_median: result.outcomePath[group].outcomeMfeOverPlannedRR.median,
  }])));
  for (const horizon of HORIZONS) {
    console.log(`Fixed horizon ${horizon} bars:`);
    console.table(Object.fromEntries(GROUPS.map((group) => [group, {
      mfeR_median: result.postEntryFixedHorizon[String(horizon)][group].mfeR.median,
      maeR_median: result.postEntryFixedHorizon[String(horizon)][group].maeR.median,
    }])));
  }
  console.log('Case path rows:');
  console.table(result.cases);
}

await main();
