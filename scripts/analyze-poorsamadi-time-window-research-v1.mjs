import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-poorsamadi-time-window-v1');
const TIMEFRAMES = ['1min', '5min'];
const TIMEZONE = process.env.POORSAMADI_TIMEZONE ?? 'Europe/Istanbul';
const MIN_N = 20;

// Source-referenced windows. These are research partitions, not production rules.
// Boundaries are explicit and half-open: [start, end).
const WINDOWS = [
  ['00:00', '02:30', 'oceania_early'],
  ['02:30', '03:00', 'transition_0230_0300'],
  ['03:00', '04:00', 'early_0300_0400'],
  ['04:00', '08:00', 'pre_europe_0400_0800'],
  ['08:00', '09:00', 'europe_0800_0900'],
  ['09:00', '10:00', 'europe_0900_1000'],
  ['10:00', '13:00', 'midday_1000_1300'],
  ['13:00', '15:30', 'us_open_1300_1530'],
  ['15:30', '16:30', 'transition_1530_1630'],
  ['16:30', '18:00', 'late_1630_1800'],
  ['18:00', '21:00', 'late_1800_2100'],
  ['21:00', '24:00', 'late_2100_2400'],
].map(([start, end, id]) => ({ start, end, id }));

const POINTS = ['02:30', '03:00', '04:00', '17:00', '18:30'];

function zonedParts(date) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: TIMEZONE,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(date);
  const out = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return { ...out, minuteOfDay: Number(out.hour) * 60 + Number(out.minute) + Number(out.second) / 60 };
}

function minutes(hhmm) {
  if (hhmm === '24:00') return 1440;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

function classify(date) {
  const z = zonedParts(date);
  const m = z.minuteOfDay;
  const window = WINDOWS.find((w) => m >= minutes(w.start) && m < minutes(w.end));
  const dayKey = `${z.year}-${z.month}-${z.day}`;
  const proximity = POINTS.map((p) => ({ point: p, distanceMinutes: Math.abs(m - minutes(p)) }))
    .sort((a, b) => a.distanceMinutes - b.distanceMinutes)[0];
  return {
    timezone: TIMEZONE,
    localDate: dayKey,
    localTime: `${z.hour}:${z.minute}:${z.second}`,
    windowId: window?.id ?? null,
    windowStart: window?.start ?? null,
    windowEnd: window?.end ?? null,
    nearestPoint: proximity?.point ?? null,
    nearestPointDistanceMinutes: proximity?.distanceMinutes ?? null,
  };
}

function summarize(rows) {
  const ordered = [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const rs = ordered.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const grossProfit = wins.reduce((a, b) => a + b, 0);
  const grossLoss = -losses.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);
  let equity = 0;
  let peak = 0;
  let maxDrawdown = 0;
  let consecutiveLosses = 0;
  let maxConsecutiveLosses = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, peak - equity);
    if (r < 0) {
      consecutiveLosses += 1;
      maxConsecutiveLosses = Math.max(maxConsecutiveLosses, consecutiveLosses);
    } else {
      consecutiveLosses = 0;
    }
  }
  return {
    n: rs.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    PF: grossLoss ? grossProfit / grossLoss : (grossProfit ? null : 0),
    avgR: rs.length ? totalR / rs.length : 0,
    totalR,
    maxDrawdown,
    maxConsecutiveLosses,
  };
}

function splitDevVal(rows) {
  const sorted = [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const devN = Math.floor(sorted.length * 0.6);
  return { DEV: sorted.slice(0, devN), VAL: sorted.slice(devN) };
}

function analyzePartition(rows) {
  const groups = new Map(WINDOWS.map((w) => [w.id, []]));
  for (const row of rows) {
    const c = classify(new Date(row.entryTime));
    if (c.windowId) groups.get(c.windowId).push({ ...row, timing: c });
  }
  return WINDOWS.map((w) => {
    const group = groups.get(w.id) ?? [];
    const stats = summarize(group);
    return {
      window: w,
      ...stats,
      eligible: stats.n >= MIN_N,
      buy: summarize(group.filter((r) => String(r.direction ?? '').toUpperCase() === 'BUY')),
      sell: summarize(group.filter((r) => String(r.direction ?? '').toUpperCase() === 'SELL')),
    };
  });
}

function pointProximity(rows, radius = 15) {
  const groups = new Map(POINTS.map((p) => [p, []]));
  const control = [];
  for (const row of rows) {
    const c = classify(new Date(row.entryTime));
    if (c.nearestPoint && c.nearestPointDistanceMinutes <= radius) groups.get(c.nearestPoint).push(row);
    else control.push(row);
  }
  return {
    radiusMinutes: radius,
    points: Object.fromEntries(POINTS.map((p) => [p, summarize(groups.get(p))])),
    outsidePointRadius: summarize(control),
  };
}

async function run(timeframe) {
  const path = resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`);
  const source = JSON.parse(await readFile(path, 'utf8'));
  const trades = (source.trades ?? [])
    .filter((trade) => Number.isFinite(Number(trade.rMultiple)) && trade.result !== 'AMBIGUOUS')
    .map((trade) => ({ ...trade, rMultiple: Number(trade.rMultiple) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const { DEV, VAL } = splitDevVal(trades);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_POORSAMADI_TIME_WINDOW_V1',
    timeframe,
    timezone: TIMEZONE,
    sourceTimeConvention: 'Poorsamadi source-referenced broker/chart-time partitions; exact dataset timezone remains a validation prerequisite.',
    scope: 'Research-only timing classification over canonical baseline resolved trades. No production rule changes.',
    assumptions: {
      windows: WINDOWS,
      boundary: '[start, end)',
      pointRadiusMinutes: 15,
      minN: MIN_N,
      devValSplit: 'chronological 60/40 of baseline resolved trades',
      freshHoldout: 'not used',
      selection: 'no window optimization or promotion is performed',
    },
    overall: summarize(trades),
    dev: { overall: summarize(DEV), windows: analyzePartition(DEV), points: pointProximity(DEV) },
    val: { overall: summarize(VAL), windows: analyzePartition(VAL), points: pointProximity(VAL) },
    nextStep: 'Validate dataset timestamp timezone against provider semantics before interpreting any window effect. Then compare fixed source windows DEV vs VAL, including direction and setup-quality interactions. Fresh holdout remains sealed until a pre-registered hypothesis survives DEV→VAL.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const output = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(output, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: N=${report.overall.n} DEV=${DEV.length} VAL=${VAL.length} timezone=${TIMEZONE}`);
  for (const side of ['dev', 'val']) {
    const eligible = report[side].windows.filter((w) => w.eligible);
    console.log(`${side.toUpperCase()}: ${eligible.map((w) => `${w.window.id}:n=${w.n},avgR=${w.avgR.toFixed(4)},PF=${w.PF?.toFixed(3) ?? 'n/a'}`).join(' | ')}`);
  }
  console.log(`Report -> ${output}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
