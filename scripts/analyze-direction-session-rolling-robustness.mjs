import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-direction-session-rolling-robustness');
const TIMEFRAMES = ['1min', '5min'];
const WINDOW_COUNT = 6;
const MIN_WINDOW_N = 5;
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

function splitRolling(rows) {
  const sorted = [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const base = Math.floor(sorted.length / WINDOW_COUNT);
  return Array.from({ length: WINDOW_COUNT }, (_, i) => sorted.slice(
    i * base,
    i === WINDOW_COUNT - 1 ? sorted.length : (i + 1) * base,
  ));
}

function weekday(rows) {
  const names = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
  return Object.fromEntries(names.map((name, day) => [
    name,
    summarize(rows.filter((r) => new Date(r.entryTime).getUTCDay() === day)),
  ]));
}

function candidate(rows, label) {
  const windows = splitRolling(rows);
  const stats = windows.map((w, i) => ({
    window: i + 1,
    from: w[0]?.entryTime ?? null,
    to: w.at(-1)?.entryTime ?? null,
    ...summarize(w),
  }));
  const eligible = stats.filter((w) => w.n >= MIN_WINDOW_N);
  const positiveWindows = eligible.filter((w) => w.PF != null && w.PF >= 1 && w.avgR > 0).length;
  const last = stats.at(-1);
  return {
    label,
    overall: summarize(rows),
    windows: stats,
    stability: {
      eligibleWindows: eligible.length,
      positiveWindows,
      positiveWindowRate: eligible.length ? positiveWindows / eligible.length : 0,
      finalWindowPositive: Boolean(last && last.n >= MIN_WINDOW_N && last.PF != null && last.PF >= 1 && last.avgR > 0),
      allEligibleWindowsPositive: eligible.length > 0 && positiveWindows === eligible.length,
    },
    byWeekday: weekday(rows),
  };
}

async function run(timeframe) {
  const source = JSON.parse(await readFile(
    resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`),
    'utf8',
  ));
  const rows = (source.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .map((t) => ({ ...t, rMultiple: Number(t.rMultiple), session: session(t.entryTime) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const candidates = [];
  for (const direction of DIRECTIONS) {
    for (const sess of SESSIONS) {
      const subset = rows.filter((r) => r.direction === direction && r.session === sess);
      candidates.push(candidate(subset, `${direction} + ${sess}`));
    }
  }

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_DIRECTION_SESSION_ROLLING_ROBUSTNESS_V1',
    timeframe,
    scope: 'Baseline resolved trades only; diagnostic stability analysis; no production rule changes.',
    methodology: {
      windows: WINDOW_COUNT,
      ordering: 'chronological entryTime',
      sessionSource: 'UTC entryTime; LONDON 07:00-16:00, NEW_YORK 16:00-22:00, otherwise OUTSIDE.',
      minimumWindowN: MIN_WINDOW_N,
      finalWindowRole: 'unseen chronological stability check; not used to define a rule in this report',
      gate: 'A candidate is considered robust only if it remains positive across most eligible rolling windows and the final chronological window; no automatic promotion is performed.',
      warning: 'Multiple subgroup and window comparisons create selection bias risk. This report is evidence, not proof of a tradable edge.',
    },
    overall: summarize(rows),
    candidates,
    nextStep: 'Only a candidate with strong rolling stability should proceed to a fresh untouched holdout / day-of-week robustness test before any Strategy A rule change.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`${timeframe}: baseline=${rows.length}`);
  for (const c of candidates) {
    console.log(`  ${c.label}: n=${c.overall.n} PF=${c.overall.PF?.toFixed(4) ?? 'n/a'} avgR=${c.overall.avgR.toFixed(4)} positiveWindows=${c.stability.positiveWindows}/${c.stability.eligibleWindows} finalPositive=${c.stability.finalWindowPositive}`);
    for (const w of c.windows) {
      console.log(`    W${w.window} n=${w.n} PF=${w.PF?.toFixed(4) ?? 'n/a'} avgR=${w.avgR.toFixed(4)} totalR=${w.totalR.toFixed(4)}`);
    }
  }
  console.log(`Report -> ${out}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
