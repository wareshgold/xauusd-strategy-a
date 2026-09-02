import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-direction-session-h2-dev-val');
const TIMEFRAMES = ['1min', '5min'];
const HOLDOUT_CANDLES = 5000;
const DEV_FRACTION = 0.6;
const DIRECTIONS = ['BUY', 'SELL'];
const SESSIONS = ['LONDON', 'NEW_YORK', 'OUTSIDE'];

function session(entryTime) {
  const d = new Date(entryTime);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK';
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

function candidate(rows, direction, sess) {
  const subset = rows.filter((r) => r.direction === direction && r.session === sess);
  return { label: `${direction} + ${sess}`, ...summarize(subset) };
}

async function run(timeframe) {
  const source = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`), 'utf8'));
  const all = (source.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .map((t) => ({ ...t, rMultiple: Number(t.rMultiple), session: session(t.entryTime) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const holdoutStart = Math.max(0, all.length ? (source.trades ?? []).length - 0 : 0);
  // Baseline reports contain the full 15k-candle backtest trades. Identify the fresh holdout
  // by entry candle timestamp using the historical candle boundary, without reading/modifying data.
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
  const cutoffIndex = Math.max(0, candles.candles.length - HOLDOUT_CANDLES);
  const cutoffTime = candles.candles[cutoffIndex]?.timestamp ?? null;
  if (!cutoffTime) throw new Error(`Missing fresh holdout cutoff for ${timeframe}`);

  const preHoldout = all.filter((r) => new Date(r.entryTime) < new Date(cutoffTime));
  const split = Math.floor(preHoldout.length * DEV_FRACTION);
  const dev = preHoldout.slice(0, split);
  const val = preHoldout.slice(split);

  const devBase = summarize(dev);
  const valBase = summarize(val);
  const candidates = [];
  for (const direction of DIRECTIONS) {
    for (const sess of SESSIONS) {
      const d = candidate(dev, direction, sess);
      const v = candidate(val, direction, sess);
      const devDelta = d.avgR - devBase.avgR;
      const valDelta = v.avgR - valBase.avgR;
      const stablePositive = d.n >= 10 && v.n >= 10 && d.avgR > 0 && v.avgR > 0 && d.PF >= 1 && v.PF >= 1;
      candidates.push({ label: d.label, dev: d, val: v, devDeltaAvgR: devDelta, valDeltaAvgR: valDelta, stablePositive });
    }
  }

  // H2 is intentionally frozen as categorical direction × session attribution.
  // No threshold, hour, score, or subgroup was optimized here. This report only asks
  // whether the exact categories reproduce across DEV and VAL before any new holdout.
  const robustCandidates = candidates.filter((c) => c.stablePositive);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_H2_DIRECTION_SESSION_DEV_VAL',
    timeframe,
    scope: 'Pre-holdout trades only. Current 5k fresh holdout is excluded and remains untouched for H2 validation.',
    hypothesis: 'Frozen H2: Strategy A expectancy differs systematically by direction × trading session; any candidate regime must be positive on both chronological DEV and VAL without threshold optimization.',
    split: { preHoldoutTrades: preHoldout.length, devTrades: dev.length, valTrades: val.length, devFraction: DEV_FRACTION, freshHoldoutCandles: HOLDOUT_CANDLES, freshHoldoutCutoff: cutoffTime },
    baseline: { dev: devBase, val: valBase },
    candidates,
    gate: { minimumNPerSplit: 10, rule: 'candidate must have n>=10 in both DEV and VAL, avgR>0 and PF>=1 in both; no automatic production promotion', passed: robustCandidates.map((c) => c.label) },
    conclusion: robustCandidates.length ? 'H2 has at least one DEV/VAL-stable categorical regime and may proceed to a separate fresh holdout test.' : 'H2 fails the frozen DEV/VAL robustness gate; do not add a direction/session filter to Strategy A and revisit entry/trigger mechanics.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: preHoldout=${preHoldout.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${devBase.avgR.toFixed(4)} baselineVAL=${valBase.avgR.toFixed(4)}`);
  for (const c of candidates) console.log(`  ${c.label}: DEV n=${c.dev.n} avgR=${c.dev.avgR.toFixed(4)} PF=${c.dev.PF?.toFixed(4) ?? 'n/a'} | VAL n=${c.val.n} avgR=${c.val.avgR.toFixed(4)} PF=${c.val.PF?.toFixed(4) ?? 'n/a'} | pass=${c.stablePositive}`);
  console.log(`Report -> ${out}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
