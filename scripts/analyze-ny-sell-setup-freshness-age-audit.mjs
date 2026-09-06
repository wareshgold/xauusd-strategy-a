import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-setup-freshness-age-audit');
const DEV = 6000;
const PRE = 10000;

function utcMinutes(ts) {
  const d = new Date(ts);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

function isNySell(ts) {
  const m = utcMinutes(ts);
  return m >= 16 * 60 && m < 22 * 60;
}

function replayAt(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;

  const breakouts = detectBreakout(visible, 5);
  const followThrough = detectFollowThrough(visible, breakouts, {
    maxBarsAfterBreakout: 2,
    requireCloseBeyondBrokenLevel: true,
  });
  const spikes = detectSpikeCandidates(visible, breakouts, followThrough, {
    maxCandles: 8,
    minDirectionalFraction: .5,
    maxOverlapFraction: .8,
  });

  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const breakout = breakouts.find((x) => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const ft = followThrough.find((x) => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !ft || ft.followThroughIndex >= index) continue;

    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;

    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index || trigger.direction !== 'SELL' || !isNySell(trigger.timestamp)) continue;

    return { spike, breakout, followThrough: ft, correction, trigger, visible };
  }
  return null;
}

function ageBars(startIndex, endIndex) {
  return endIndex - startIndex;
}

function ageMinutes(visible, startIndex, endIndex) {
  const start = new Date(visible[startIndex]?.timestamp ?? '').getTime();
  const end = new Date(visible[endIndex]?.timestamp ?? '').getTime();
  if (!Number.isFinite(start) || !Number.isFinite(end)) return null;
  return (end - start) / 60000;
}

function quantile(xs, q) {
  if (!xs.length) return null;
  const sorted = [...xs].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

function quantileBounds(xs) {
  return {
    q25: quantile(xs, .25),
    q50: quantile(xs, .5),
    q75: quantile(xs, .75),
  };
}

function bucket(value, bounds) {
  if (value <= bounds.q25) return 'Q1';
  if (value <= bounds.q50) return 'Q2';
  if (value <= bounds.q75) return 'Q3';
  return 'Q4';
}

function outcome(r) {
  if (r >= 5) return 'EXCEPTIONAL_WIN';
  if (r > 0) return 'NORMAL_WIN';
  return 'LOSS';
}

function stats(rows) {
  const wins = rows.filter((x) => x.r > 0);
  const losses = rows.filter((x) => x.r <= 0);
  const grossProfit = wins.reduce((s, x) => s + x.r, 0);
  const grossLoss = Math.abs(losses.reduce((s, x) => s + x.r, 0));
  return {
    n: rows.length,
    wins: wins.length,
    losses: losses.length,
    wr: rows.length ? wins.length / rows.length : null,
    avgR: rows.length ? rows.reduce((s, x) => s + x.r, 0) / rows.length : null,
    totalR: rows.reduce((s, x) => s + x.r, 0),
    pf: grossLoss > 0 ? grossProfit / grossLoss : null,
  };
}

function ageStats(rows, field, bucketField) {
  const out = {};
  for (const bucketName of ['Q1', 'Q2', 'Q3', 'Q4']) {
    const subset = rows.filter((x) => x[bucketField] === bucketName);
    out[bucketName] = {
      ageMedian: subset.length ? quantile(subset.map((x) => x[field]), .5) : null,
      ...stats(subset),
      outcomes: {
        LOSS: subset.filter((x) => x.outcome === 'LOSS').length,
        NORMAL_WIN: subset.filter((x) => x.outcome === 'NORMAL_WIN').length,
        EXCEPTIONAL_WIN: subset.filter((x) => x.outcome === 'EXCEPTIONAL_WIN').length,
      },
    };
  }
  return out;
}

function p(n) {
  return Number.isFinite(n) ? Number(n.toFixed(4)) : null;
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const targets = (base.trades ?? [])
    .map((t) => ({
      entryIndex: Number(t.entryIndex),
      entryTime: t.entryTime,
      r: Number(t.rMultiple),
      direction: t.direction,
      result: t.result,
    }))
    .filter((t) => Number.isInteger(t.entryIndex)
      && t.entryIndex >= 0
      && t.entryIndex < PRE
      && t.direction === 'SELL'
      && isNySell(t.entryTime)
      && t.result !== 'AMBIGUOUS'
      && Number.isFinite(t.r))
    .sort((a, b) => a.entryIndex - b.entryIndex);

  const rows = targets.map((target) => {
    const replay = replayAt(candles, target.entryIndex);
    if (!replay) throw new Error(`Could not rebuild canonical NY SELL at ${target.entryIndex}`);
    if (replay.trigger.timestamp !== target.entryTime) {
      throw new Error(`Lineage mismatch at ${target.entryIndex}: baseline=${target.entryTime} rebuilt=${replay.trigger.timestamp}`);
    }

    const { spike, breakout, followThrough, correction, trigger, visible } = replay;
    const correctionAgeBars = ageBars(correction.correctionStartIndex, target.entryIndex);
    const extremeAgeBars = ageBars(correction.correctionExtremeIndex, target.entryIndex);
    const setupAgeBars = ageBars(spike.startIndex, target.entryIndex);

    return {
      split: target.entryIndex < DEV ? 'DEV' : 'VAL',
      entryIndex: target.entryIndex,
      entryTime: target.entryTime,
      r: target.r,
      outcome: outcome(target.r),
      breakoutTime: breakout.timestamp,
      spikeStartTime: visible[spike.startIndex]?.timestamp ?? null,
      spikeEndTime: visible[spike.endIndex]?.timestamp ?? null,
      followThroughTime: visible[followThrough.followThroughIndex]?.timestamp ?? null,
      correctionStartTime: visible[correction.correctionStartIndex]?.timestamp ?? null,
      correctionExtremeTime: visible[correction.correctionExtremeIndex]?.timestamp ?? null,
      triggerTime: trigger.timestamp,
      correctionAgeBars,
      correctionAgeMinutes: ageMinutes(visible, correction.correctionStartIndex, target.entryIndex),
      extremeAgeBars,
      extremeAgeMinutes: ageMinutes(visible, correction.correctionExtremeIndex, target.entryIndex),
      setupAgeBars,
      setupAgeMinutes: ageMinutes(visible, spike.startIndex, target.entryIndex),
    };
  });

  const correctionBounds = quantileBounds(rows.map((x) => x.correctionAgeBars));
  const extremeBounds = quantileBounds(rows.map((x) => x.extremeAgeBars));
  const setupBounds = quantileBounds(rows.map((x) => x.setupAgeBars));

  for (const row of rows) {
    row.correctionAgeBucket = bucket(row.correctionAgeBars, correctionBounds);
    row.extremeAgeBucket = bucket(row.extremeAgeBars, extremeBounds);
    row.setupAgeBucket = bucket(row.setupAgeBars, setupBounds);
  }

  const byOutcome = Object.fromEntries(['LOSS', 'NORMAL_WIN', 'EXCEPTIONAL_WIN'].map((name) => {
    const subset = rows.filter((x) => x.outcome === name);
    return [name, {
      ...stats(subset),
      correctionAgeBarsMedian: subset.length ? quantile(subset.map((x) => x.correctionAgeBars), .5) : null,
      extremeAgeBarsMedian: subset.length ? quantile(subset.map((x) => x.extremeAgeBars), .5) : null,
      setupAgeBarsMedian: subset.length ? quantile(subset.map((x) => x.setupAgeBars), .5) : null,
    }];
  }));

  const splitStats = Object.fromEntries(['DEV', 'VAL'].map((split) => {
    const subset = rows.filter((x) => x.split === split);
    return [split, {
      ...stats(subset),
      byOutcome: Object.fromEntries(['LOSS', 'NORMAL_WIN', 'EXCEPTIONAL_WIN'].map((name) => [name, stats(subset.filter((x) => x.outcome === name))])),
      correctionAgeBuckets: ageStats(subset, 'correctionAgeBars', 'correctionAgeBucket'),
      extremeAgeBuckets: ageStats(subset, 'extremeAgeBars', 'extremeAgeBucket'),
      setupAgeBuckets: ageStats(subset, 'setupAgeBars', 'setupAgeBucket'),
    }];
  }));

  const summary = {
    total: rows.length,
    dev: rows.filter((x) => x.split === 'DEV').length,
    val: rows.filter((x) => x.split === 'VAL').length,
    byOutcome,
    allAgeQuantiles: {
      correctionAgeBars: correctionBounds,
      extremeAgeBars: extremeBounds,
      setupAgeBars: setupBounds,
    },
    splitStats,
  };

  const output = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_SETUP_FRESHNESS_AGE_AUDIT',
    timeframe: '5m',
    scope: {
      source: 'canonical baseline NY SELL trades before fresh holdout',
      ...summary,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    methodology: {
      purpose: 'Describe whether canonical NY SELL outcomes vary with setup age at trigger time.',
      metrics: {
        correctionAge: 'correction start index -> trigger index',
        extremeAge: 'correction extreme index -> trigger index',
        setupAge: 'spike start index -> trigger index',
      },
      bucketMethod: 'Natural Q1-Q4 quartiles computed from the 29-case DEV+VAL universe; descriptive only.',
      noOptimization: true,
      noNewTradingRules: true,
      noDetectorChanges: true,
      lineageCheck: 'rebuilt trigger timestamp must equal canonical baseline entry timestamp',
    },
    summary,
    cases: rows,
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(output, null, 2));

  console.log('');
  console.log('════════════════════════════════════════════════════════════');
  console.log('NY SELL — SETUP FRESHNESS / AGE ASSOCIATION AUDIT');
  console.log('════════════════════════════════════════════════════════════');
  console.log(`Universe: ${summary.total} canonical NY SELL | DEV=${summary.dev} | VAL=${summary.val} | Fresh=LOCKED`);
  console.log('');
  console.log('ALL AGE QUANTILES — 5m BARS');
  console.table({
    correctionAge: Object.fromEntries(Object.entries(correctionBounds).map(([k, v]) => [k, p(v)])),
    extremeAge: Object.fromEntries(Object.entries(extremeBounds).map(([k, v]) => [k, p(v)])),
    setupAge: Object.fromEntries(Object.entries(setupBounds).map(([k, v]) => [k, p(v)])),
  });
  console.log('');
  console.log('OUTCOME × AGE MEDIANS');
  console.table(Object.entries(byOutcome).map(([name, x]) => ({
    outcome: name,
    n: x.n,
    WR: p(x.wr),
    avgR: p(x.avgR),
    correctionAgeBarsMedian: p(x.correctionAgeBarsMedian),
    extremeAgeBarsMedian: p(x.extremeAgeBarsMedian),
    setupAgeBarsMedian: p(x.setupAgeBarsMedian),
  })));
  console.log('');

  for (const split of ['DEV', 'VAL']) {
    const s = splitStats[split];
    console.log(`${split} — CORRECTION AGE Q1-Q4`);
    console.table(Object.entries(s.correctionAgeBuckets).map(([bucketName, x]) => ({ bucket: bucketName, n: x.n, WR: p(x.wr), avgR: p(x.avgR), PF: p(x.pf), totalR: p(x.totalR), ageMedian: p(x.ageMedian), loss: x.outcomes.LOSS, normalWin: x.outcomes.NORMAL_WIN, exceptionalWin: x.outcomes.EXCEPTIONAL_WIN })));
    console.log(`${split} — EXTREME AGE Q1-Q4`);
    console.table(Object.entries(s.extremeAgeBuckets).map(([bucketName, x]) => ({ bucket: bucketName, n: x.n, WR: p(x.wr), avgR: p(x.avgR), PF: p(x.pf), totalR: p(x.totalR), ageMedian: p(x.ageMedian), loss: x.outcomes.LOSS, normalWin: x.outcomes.NORMAL_WIN, exceptionalWin: x.outcomes.EXCEPTIONAL_WIN })));
    console.log(`${split} — SETUP AGE Q1-Q4`);
    console.table(Object.entries(s.setupAgeBuckets).map(([bucketName, x]) => ({ bucket: bucketName, n: x.n, WR: p(x.wr), avgR: p(x.avgR), PF: p(x.pf), totalR: p(x.totalR), ageMedian: p(x.ageMedian), loss: x.outcomes.LOSS, normalWin: x.outcomes.NORMAL_WIN, exceptionalWin: x.outcomes.EXCEPTIONAL_WIN })));
    console.log('');
  }

  console.log('ALL CASES — AGE + OUTCOME');
  console.table(rows.map((x) => ({
    split: x.split,
    time: x.entryTime,
    R: p(x.r),
    outcome: x.outcome,
    corrAgeBars: x.correctionAgeBars,
    extremeAgeBars: x.extremeAgeBars,
    setupAgeBars: x.setupAgeBars,
    corrAgeQ: x.correctionAgeBucket,
    extremeAgeQ: x.extremeAgeBucket,
    setupAgeQ: x.setupAgeBucket,
  })));
  console.log('');
  console.log(`Full machine-readable report -> ${resolve(OUT, '5m.json')}`);
  console.log('No optimization, no new rules, no Fresh Holdout access.');
}

await main();
