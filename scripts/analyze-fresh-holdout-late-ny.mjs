import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-fresh-holdout-late-ny');
const HOLDOUT_CANDLES = Number(process.env.FRESH_HOLDOUT_CANDLES ?? '5000');
const MIN_TOTAL_CANDLES = HOLDOUT_CANDLES * 3;
const TIMEFRAMES = ['1min', '5min'];

function finite(v) { return Number.isFinite(Number(v)); }

function isLateNewYork(timestamp) {
  const d = new Date(`${timestamp.replace(' ', 'T')}Z`);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  return m >= 16 * 60 && m < 22 * 60;
}

function stats(rows) {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const grossProfit = wins.reduce((a, b) => a + b, 0);
  const grossLoss = -losses.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);
  let equity = 0;
  let peak = 0;
  let maxDD = 0;
  let currentCL = 0;
  let maxCL = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDD = Math.max(maxDD, peak - equity);
    if (r < 0) { currentCL += 1; maxCL = Math.max(maxCL, currentCL); }
    else if (r > 0) currentCL = 0;
  }
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    PF: grossLoss ? grossProfit / grossLoss : (grossProfit ? null : 0),
    avgR: rs.length ? totalR / rs.length : 0,
    totalR,
    maxDD,
    maxCL,
  };
}

function weekday(rows) {
  const names = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
  return Object.fromEntries(names.map((name, day) => [
    name,
    stats(rows.filter((r) => new Date(`${r.entryTime.replace(' ', 'T')}Z`).getUTCDay() === day)),
  ]));
}

async function run(timeframe) {
  const historical = JSON.parse(await readFile(
    resolve(ROOT, `data/historical/xauusd-${timeframe}.json`),
    'utf8',
  ));
  const baseline = JSON.parse(await readFile(
    resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`),
    'utf8',
  ));

  const candles = historical.candles ?? [];
  if (candles.length < MIN_TOTAL_CANDLES) {
    throw new Error(`${timeframe}: need at least ${MIN_TOTAL_CANDLES} candles for fresh holdout; found ${candles.length}. Run XAUUSD_OUTPUTSIZE=${MIN_TOTAL_CANDLES} npm run download:data first.`);
  }
  if (Number(baseline.candles) !== candles.length) {
    throw new Error(`${timeframe}: baseline report has ${baseline.candles} candles but historical dataset has ${candles.length}. Regenerate baseline before holdout.`);
  }

  const splitIndex = candles.length - HOLDOUT_CANDLES;
  const splitTimestamp = candles[splitIndex]?.timestamp ?? null;
  const resolved = (baseline.trades ?? []).filter((t) => finite(t.rMultiple) && t.result !== 'AMBIGUOUS');
  const lateNy = resolved
    .filter((t) => isLateNewYork(t.entryTime))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const train = lateNy.filter((t) => Number(t.entryIndex) < splitIndex);
  const holdout = lateNy.filter((t) => Number(t.entryIndex) >= splitIndex);
  const sellTrain = train.filter((t) => String(t.direction).toUpperCase() === 'SELL');
  const sellHoldout = holdout.filter((t) => String(t.direction).toUpperCase() === 'SELL');

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_FRESH_UNTOUCHED_HOLDOUT_LATE_NY_V1',
    timeframe,
    scope: 'Fixed candidate selected before this holdout: SELL + late New York (16:00-22:00 UTC). No parameter optimization or rule change.',
    data: {
      source: historical.source,
      candles: candles.length,
      from: candles[0]?.timestamp ?? null,
      to: candles.at(-1)?.timestamp ?? null,
      holdoutCandles: HOLDOUT_CANDLES,
      splitIndex,
      splitTimestamp,
    },
    candidate: {
      direction: 'SELL',
      session: 'NEW_YORK_LATE',
      sessionUTC: '16:00-22:00',
    },
    train: { allLateNY: stats(lateNy.filter((t) => Number(t.entryIndex) < splitIndex)), sellLateNY: stats(sellTrain) },
    holdout: { allLateNY: stats(holdout), sellLateNY: stats(sellHoldout), byWeekday: weekday(sellHoldout) },
    gate: {
      minimumHoldoutTrades: 15,
      positivePF: stats(sellHoldout).PF != null && stats(sellHoldout).PF >= 1,
      positiveAvgR: stats(sellHoldout).avgR > 0,
      finalDecision: 'DO_NOT_PROMOTE_AUTOMATICALLY',
    },
    warning: 'This holdout is only genuinely untouched if its candles occur after the data used to select the candidate. The script enforces a chronological final segment and does not optimize on it.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  const h = stats(sellHoldout);
  console.log(`${timeframe}: split=${splitTimestamp} SELL+NY_LATE holdout n=${h.n} PF=${h.PF?.toFixed(4) ?? 'n/a'} avgR=${h.avgR.toFixed(4)} totalR=${h.totalR.toFixed(4)} DD=${h.maxDD.toFixed(4)} CL=${h.maxCL}`);
  console.log(`Report -> ${out}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
