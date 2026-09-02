import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-frozen-5m-sell-ny-robustness');
const TIMEFRAME = '5min';
const TOTAL_CANDLES = 15000;
const FRESH_HOLDOUT_CANDLES = 5000;
const PRE_HOLDOUT_CANDLES = TOTAL_CANDLES - FRESH_HOLDOUT_CANDLES;
const WINDOW_COUNT = 6;
const MIN_WINDOW_N = 3;
const DIRECTION = 'SELL';
const SESSION = 'NEW_YORK';

function session(entryTime) {
  const d = new Date(entryTime);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 780 && m < 1320) return 'NEW_YORK';
  return 'OUTSIDE';
}

function summarize(rows) {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const grossProfit = wins.reduce((a, b) => a + b, 0);
  const grossLoss = -losses.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    PF: grossLoss ? grossProfit / grossLoss : (grossProfit ? null : 0),
    avgR: rs.length ? totalR / rs.length : 0,
    totalR,
  };
}

function maxDrawdown(rows) {
  let equity = 0;
  let peak = 0;
  let maxDD = 0;
  for (const r of [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime))) {
    equity += Number(r.rMultiple);
    peak = Math.max(peak, equity);
    maxDD = Math.max(maxDD, peak - equity);
  }
  return maxDD;
}

function maxConsecutiveLosses(rows) {
  let current = 0;
  let max = 0;
  for (const r of [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime))) {
    if (Number(r.rMultiple) < 0) {
      current += 1;
      max = Math.max(max, current);
    } else if (Number(r.rMultiple) > 0) {
      current = 0;
    }
  }
  return max;
}

function splitRolling(rows) {
  const sorted = [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const base = Math.floor(sorted.length / WINDOW_COUNT);
  return Array.from({ length: WINDOW_COUNT }, (_, i) => sorted.slice(
    i * base,
    i === WINDOW_COUNT - 1 ? sorted.length : (i + 1) * base,
  ));
}

function stability(windows) {
  const eligible = windows.filter((w) => w.n >= MIN_WINDOW_N);
  const positive = eligible.filter((w) => w.avgR > 0 && w.PF >= 1).length;
  const nonNegative = eligible.filter((w) => w.avgR >= 0).length;
  const final = windows.at(-1);
  return {
    eligibleWindows: eligible.length,
    positiveWindows: positive,
    positiveWindowRate: eligible.length ? positive / eligible.length : 0,
    nonNegativeWindows: nonNegative,
    nonNegativeWindowRate: eligible.length ? nonNegative / eligible.length : 0,
    finalWindowPositive: Boolean(final && final.n >= MIN_WINDOW_N && final.avgR > 0 && final.PF >= 1),
    allEligibleWindowsPositive: eligible.length > 0 && positive === eligible.length,
  };
}

async function run() {
  const source = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${TIMEFRAME}.json`), 'utf8'));
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${TIMEFRAME}.json`), 'utf8')).candles ?? [];
  if (candles.length < TOTAL_CANDLES) throw new Error(`${TIMEFRAME}: expected at least ${TOTAL_CANDLES} candles, found ${candles.length}`);

  const freshHoldoutCutoff = candles[PRE_HOLDOUT_CANDLES]?.timestamp;
  if (!freshHoldoutCutoff) throw new Error(`${TIMEFRAME}: missing fresh holdout cutoff timestamp`);

  const rows = (source.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .map((t) => ({ ...t, rMultiple: Number(t.rMultiple), session: session(t.entryTime) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const preHoldout = rows.filter((t) => new Date(t.entryTime) < new Date(freshHoldoutCutoff));
  const candidateRows = preHoldout.filter((r) => r.direction === DIRECTION && r.session === SESSION);
  const windows = splitRolling(candidateRows).map((w, i) => ({ window: i + 1, from: w[0]?.entryTime ?? null, to: w.at(-1)?.entryTime ?? null, ...summarize(w) }));
  const baselineWindows = splitRolling(preHoldout).map((w, i) => ({ window: i + 1, from: w[0]?.entryTime ?? null, to: w.at(-1)?.entryTime ?? null, ...summarize(w) }));

  const overall = summarize(candidateRows);
  const baseline = summarize(preHoldout);
  const s = stability(windows);
  const verdict = s.eligibleWindows >= 4 && s.positiveWindowRate >= 0.67 && s.finalWindowPositive
    ? 'ROBUST'
    : s.positiveWindowRate >= 0.5 && s.finalWindowPositive
      ? 'PROMISING_INCONCLUSIVE'
      : 'FRAGILE_REJECT';

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_FROZEN_5M_SELL_NEW_YORK_ROBUSTNESS_V1',
    timeframe: TIMEFRAME,
    candidate: `${DIRECTION} + ${SESSION}`,
    scope: 'Frozen robustness review of the already-qualified 5m candidate using pre-holdout data only. Diagnostic only; no production rule changes.',
    methodology: {
      totalCandles: TOTAL_CANDLES,
      freshHoldoutCandles: FRESH_HOLDOUT_CANDLES,
      preHoldoutCandles: PRE_HOLDOUT_CANDLES,
      freshHoldoutCutoff,
      rollingWindows: WINDOW_COUNT,
      minimumWindowN: MIN_WINDOW_N,
      sessionDefinition: 'UTC entryTime; NEW_YORK 13:00-22:00, matching the H2 candidate definition.',
      ordering: 'chronological entryTime',
      tradeSplit: 'Trades are assigned to pre-holdout by entryTime against the deterministic candle timestamp cutoff; no row-count approximation is used.',
      holdoutExcluded: true,
      optimization: false,
      note: 'The candidate was previously observed in fresh-holdout attribution, so the later holdout confirmation is not equivalent to a blinded discovery-free test. This report therefore emphasizes pre-holdout temporal stability.',
    },
    preHoldout: {
      baseline: { ...baseline, maxDD: maxDrawdown(preHoldout), maxConsecutiveLosses: maxConsecutiveLosses(preHoldout) },
      candidate: { ...overall, maxDD: maxDrawdown(candidateRows), maxConsecutiveLosses: maxConsecutiveLosses(candidateRows) },
      deltaAvgR: overall.avgR - baseline.avgR,
      deltaPF: (overall.PF ?? 0) - (baseline.PF ?? 0),
    },
    rolling: { candidate: windows, baseline: baselineWindows, stability: s },
    verdict,
    verdictRationale: 'ROBUST requires at least 4 eligible chronological candidate windows, at least two-thirds positive by both AvgR and PF, and a positive final window. PROMISING_INCONCLUSIVE requires at least half positive and a positive final window. These are research gates, not production promotion rules.',
    nextStep: 'Do not alter Strategy A from this report. If ROBUST or PROMISING_INCONCLUSIVE, proceed to independent day-of-week/regime stress tests and prospective paper-signal validation before any production filter change.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${TIMEFRAME}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${TIMEFRAME}: preHoldout baseline n=${baseline.n} avgR=${baseline.avgR.toFixed(4)} PF=${baseline.PF?.toFixed(4) ?? 'n/a'} | frozen SELL+NEW_YORK n=${overall.n} avgR=${overall.avgR.toFixed(4)} PF=${overall.PF?.toFixed(4) ?? 'n/a'}`);
  console.log(`  stability: positiveWindows=${s.positiveWindows}/${s.eligibleWindows} (${(s.positiveWindowRate * 100).toFixed(1)}%) finalPositive=${s.finalWindowPositive} | maxDD=${maxDrawdown(candidateRows).toFixed(4)}R maxCL=${maxConsecutiveLosses(candidateRows)}`);
  for (const w of windows) console.log(`  W${w.window} n=${w.n} PF=${w.PF?.toFixed(4) ?? 'n/a'} avgR=${w.avgR.toFixed(4)} totalR=${w.totalR.toFixed(4)}`);
  console.log(`  VERDICT=${verdict}`);
  console.log(`Report -> ${out}`);
}

await run();
