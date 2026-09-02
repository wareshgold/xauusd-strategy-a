import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-direction-session-h2-dev-val');
const TIMEFRAMES = ['1min', '5min'];
const TOTAL_CANDLES = 15000;
const FRESH_HOLDOUT_CANDLES = 5000;
const PRE_HOLDOUT_CANDLES = TOTAL_CANDLES - FRESH_HOLDOUT_CANDLES;
const DEV_CANDLES = 6000;
const MIN_N_PER_SPLIT = 10;
const DIRECTIONS = ['BUY', 'SELL'];
const SESSIONS = ['LONDON', 'NEW_YORK', 'OUTSIDE'];

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

function byRegime(rows, direction, session) {
  return rows.filter((r) => r.direction === direction && r.session === session);
}

async function run(timeframe) {
  const source = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`), 'utf8'));
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles ?? [];

  if (candles.length < TOTAL_CANDLES) {
    throw new Error(`${timeframe}: expected at least ${TOTAL_CANDLES} candles, found ${candles.length}`);
  }

  const freshHoldoutCutoff = candles[PRE_HOLDOUT_CANDLES]?.timestamp;
  const devValCutoff = candles[DEV_CANDLES]?.timestamp;
  if (!freshHoldoutCutoff || !devValCutoff) throw new Error(`${timeframe}: missing deterministic split timestamps`);

  const allTrades = (source.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .map((t) => ({ ...t, rMultiple: Number(t.rMultiple) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const preHoldout = allTrades.filter((t) => new Date(t.entryTime) < new Date(freshHoldoutCutoff));
  const dev = preHoldout.filter((t) => new Date(t.entryTime) < new Date(devValCutoff));
  const val = preHoldout.filter((t) => new Date(t.entryTime) >= new Date(devValCutoff));

  const baseline = { dev: summarize(dev), val: summarize(val) };
  const candidates = [];

  for (const direction of DIRECTIONS) {
    for (const session of SESSIONS) {
      const devRows = byRegime(dev, direction, session);
      const valRows = byRegime(val, direction, session);
      const devStats = { label: `${direction} + ${session}`, ...summarize(devRows) };
      const valStats = { label: `${direction} + ${session}`, ...summarize(valRows) };
      const devDeltaAvgR = devStats.avgR - baseline.dev.avgR;
      const valDeltaAvgR = valStats.avgR - baseline.val.avgR;
      const stablePositive =
        devStats.n >= MIN_N_PER_SPLIT &&
        valStats.n >= MIN_N_PER_SPLIT &&
        devStats.avgR > 0 &&
        valStats.avgR > 0 &&
        devStats.PF >= 1 &&
        valStats.PF >= 1;
      candidates.push({ label: devStats.label, dev: devStats, val: valStats, devDeltaAvgR, valDeltaAvgR, stablePositive });
    }
  }

  const frozenH2 = candidates.find((c) => c.label === 'SELL + NEW_YORK');
  const gatePassed = Boolean(frozenH2?.stablePositive);

  const report = {
    strategy: 'Strategy A',
    mode: 'RESEARCH_H2_DIRECTION_SESSION_DEV_VAL',
    timeframe,
    scope: 'Pre-holdout only. The final 5,000 candles are excluded and remain reserved for a separate fresh H2 holdout test.',
    hypothesis: 'Frozen H2: Strategy A expectancy differs systematically by direction × trading session; the pre-registered candidate is SELL + NEW_YORK because it was identified before this DEV/VAL test from baseline attribution.',
    methodology: {
      sourceBaseline: 'data/reports/strategy-a-baseline',
      totalCandlesRequired: TOTAL_CANDLES,
      freshHoldoutCandles: FRESH_HOLDOUT_CANDLES,
      preHoldoutCandles: PRE_HOLDOUT_CANDLES,
      devCandles: DEV_CANDLES,
      valCandles: PRE_HOLDOUT_CANDLES - DEV_CANDLES,
      splitMethod: 'Chronological candle split; trades are assigned by entryTime. No threshold, hour boundary, score, or subgroup optimization is performed.',
      minimumNPerSplit: MIN_N_PER_SPLIT,
      promotionRule: 'Frozen SELL + NEW_YORK must have n>=10, avgR>0, and PF>=1 in both DEV and VAL. Passing does not modify Strategy A; it only authorizes a separate fresh holdout test.',
    },
    split: {
      devCutoff: devValCutoff,
      freshHoldoutCutoff: freshHoldoutCutoff,
      preHoldoutTrades: preHoldout.length,
      devTrades: dev.length,
      valTrades: val.length,
    },
    baseline,
    frozenCandidate: frozenH2,
    allDirectionSessionCells: candidates,
    gate: {
      passed: gatePassed,
      candidate: 'SELL + NEW_YORK',
      rule: 'n>=10, avgR>0, PF>=1 in both DEV and VAL',
    },
    conclusion: gatePassed
      ? 'H2 passes the frozen DEV/VAL gate. Do not change production Strategy A. The next step is a single fresh holdout test of SELL + NEW_YORK on the reserved 5,000 candles.'
      : 'H2 fails the frozen DEV/VAL gate. Do not add a direction/session filter to Strategy A; the hypothesis should be rejected and research should return to entry/trigger mechanics.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: preHoldout=${preHoldout.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${baseline.dev.avgR.toFixed(4)} baselineVAL=${baseline.val.avgR.toFixed(4)}`);
  for (const c of candidates) {
    console.log(`  ${c.label}: DEV n=${c.dev.n} avgR=${c.dev.avgR.toFixed(4)} PF=${c.dev.PF?.toFixed(4) ?? 'n/a'} | VAL n=${c.val.n} avgR=${c.val.avgR.toFixed(4)} PF=${c.val.PF?.toFixed(4) ?? 'n/a'} | pass=${c.stablePositive}`);
  }
  console.log(`  FROZEN H2 SELL + NEW_YORK: ${gatePassed ? 'PASS' : 'FAIL'}`);
  console.log(`Report -> ${out}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
