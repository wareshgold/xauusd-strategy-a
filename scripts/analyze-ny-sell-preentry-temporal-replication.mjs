import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-discriminative-anatomy/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-temporal-replication');
const FEATURES = [
  'correctionBars', 'correctionToSpike', 'pathEfficiency', 'bodyParticipation',
  'upperWickShare', 'lowerWickShare', 'secondHalfProgress',
  'triggerReclaimToRange', 'triggerBodyToRange', 'triggerCloseLocation',
  'triggerReclaimToCorrection',
];
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos), hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return { n: a.length, median: q(.5), p25: q(.25), p75: q(.75) };
}

function outcomeStats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0), losses = r.filter((x) => x < 0);
  const grossWin = wins.reduce((s, x) => s + x, 0);
  const grossLoss = -losses.reduce((s, x) => s + x, 0);
  return {
    n: r.length,
    WR: r.length ? p(wins.length / r.length) : null,
    avgR: r.length ? p(r.reduce((s, x) => s + x, 0) / r.length) : null,
    PF: grossLoss ? p(grossWin / grossLoss) : null,
    totalR: p(r.reduce((s, x) => s + x, 0)),
  };
}

function median(rows, feature) {
  return quantiles(rows.map((x) => Number(x[feature]))).median;
}

function featureDelta(rows, feature) {
  const normal = rows.filter((x) => x.classification === 'NORMAL_WIN');
  const loss = rows.filter((x) => x.classification === 'LOSS');
  const a = median(normal, feature), b = median(loss, feature);
  return {
    normalN: normal.length,
    lossN: loss.length,
    normalMedian: a,
    lossMedian: b,
    delta: Number.isFinite(a) && Number.isFinite(b) ? p(a - b) : null,
  };
}

function temporalWindows(rows) {
  const result = [];
  for (const split of ['DEV', 'VAL']) {
    const scoped = rows.filter((x) => x.split === split).sort((a, b) => new Date(a.time) - new Date(b.time));
    const mid = Math.ceil(scoped.length / 2);
    const halves = [scoped.slice(0, mid), scoped.slice(mid)];
    halves.forEach((windowRows, i) => {
      result.push({
        id: `${split}_H${i + 1}`,
        split,
        n: windowRows.length,
        start: windowRows[0]?.time ?? null,
        end: windowRows.at(-1)?.time ?? null,
        outcome: outcomeStats(windowRows),
        featureDeltas: Object.fromEntries(FEATURES.map((f) => [f, featureDelta(windowRows, f)])),
      });
    });
  }
  return result;
}

function stability(windows) {
  return Object.fromEntries(FEATURES.map((f) => {
    const entries = windows.map((w) => w.featureDeltas[f]).filter((x) => Number.isFinite(x.delta));
    const positive = entries.filter((x) => x.delta > 0).length;
    const negative = entries.filter((x) => x.delta < 0).length;
    return [f, {
      windowsWithBothGroups: entries.length,
      positiveDeltaWindows: positive,
      negativeDeltaWindows: negative,
      signStableAcrossAllObserved: entries.length > 0 && (positive === entries.length || negative === entries.length),
      medianDeltaAcrossWindows: entries.length ? p(entries.map((x) => x.delta).sort((a, b) => a - b)[Math.floor(entries.length / 2)]) : null,
    }];
  }));
}

async function main() {
  const source = JSON.parse(await readFile(SOURCE, 'utf8'));
  const rows = (source.cases ?? []).filter((x) => x.split === 'DEV' || x.split === 'VAL');
  if (!rows.length) throw new Error('No DEV/VAL cases found');

  const windows = temporalWindows(rows);
  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_PREENTRY_TEMPORAL_REPLICATION',
    timeframe: '5m',
    scope: {
      source: 'NY SELL pre-entry discriminative anatomy',
      n: rows.length,
      dev: rows.filter((x) => x.split === 'DEV').length,
      val: rows.filter((x) => x.split === 'VAL').length,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    methodology: {
      purpose: 'Replication of pre-entry anatomy direction across independent chronological halves within DEV and VAL.',
      windows: 'Two chronological halves per split; boundaries determined only by time ordering and sample count.',
      comparisons: 'NORMAL_WIN median minus LOSS median for each pre-entry feature.',
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      holdoutLocked: true,
      interpretation: 'Temporal sign replication is descriptive evidence only. A feature is not promoted to a trading rule by this report.',
    },
    windows,
    featureStability: stability(windows),
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));

  console.log(`PREENTRY_TEMPORAL_REPLICATION N=${result.scope.n} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  for (const w of windows) {
    console.log(`${w.id} N=${w.n} ${w.start} -> ${w.end} WR=${w.outcome.WR == null ? '-' : p(w.outcome.WR * 100) + '%'} avgR=${w.outcome.avgR ?? '-'} PF=${w.outcome.PF ?? '-'}`);
  }
  console.log('FEATURE SIGN STABILITY across DEV-H1, DEV-H2, VAL-H1, VAL-H2:');
  console.table(Object.fromEntries(FEATURES.map((f) => {
    const s = result.featureStability[f];
    return [f, { observed: s.windowsWithBothGroups, positive: s.positiveDeltaWindows, negative: s.negativeDeltaWindows, stable: s.signStableAcrossAllObserved, medianWindowDelta: s.medianDeltaAcrossWindows }];
  })));
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

await main();
