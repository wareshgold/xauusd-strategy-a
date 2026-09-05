import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-poorsamadi-time-direction-quality-v1');
const TIMEFRAMES = ['1min', '5min'];
const TIMEZONE = process.env.POORSAMADI_TIMEZONE ?? 'Europe/Istanbul';
const MIN_N = 10;

// Fixed source-referenced windows. Research partitions only; not production rules.
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

const QUALITY_BUCKETS = ['A', 'B', 'OTHER', 'UNKNOWN'];

function minutes(hhmm) {
  if (hhmm === '24:00') return 1440;
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
}

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

function classifyTime(date) {
  const z = zonedParts(date);
  const window = WINDOWS.find((w) => {
    const m = z.minuteOfDay;
    return m >= minutes(w.start) && m < minutes(w.end);
  });
  return {
    timezone: TIMEZONE,
    localDate: `${z.year}-${z.month}-${z.day}`,
    localTime: `${z.hour}:${z.minute}:${z.second}`,
    windowId: window?.id ?? null,
  };
}

function directionOf(trade) {
  const direction = String(trade.direction ?? '').toUpperCase();
  return direction === 'BUY' || direction === 'SELL' ? direction : 'UNKNOWN';
}

function qualityOf(trade) {
  const raw = trade.qualityGrade ?? trade.quality ?? trade.setupQuality ?? trade.qualityClass;
  const value = String(raw ?? '').trim().toUpperCase();
  if (value === 'A' || value === 'B') return value;
  if (value) return 'OTHER';
  return 'UNKNOWN';
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

function summarizeCell(rows) {
  const stats = summarize(rows);
  return { ...stats, eligible: stats.n >= MIN_N };
}

function matrix(rows) {
  const cells = [];
  for (const w of WINDOWS) {
    const windowRows = rows.filter((r) => r.timing.windowId === w.id);
    const all = summarizeCell(windowRows);
    const byDirection = {};
    for (const direction of ['BUY', 'SELL']) {
      const directionRows = windowRows.filter((r) => directionOf(r) === direction);
      const byQuality = {};
      for (const quality of QUALITY_BUCKETS) {
        byQuality[quality] = summarizeCell(directionRows.filter((r) => qualityOf(r) === quality));
      }
      byDirection[direction] = {
        ...summarizeCell(directionRows),
        quality: byQuality,
      };
    }
    cells.push({ window: w, all, buy: byDirection.BUY, sell: byDirection.SELL });
  }
  return cells;
}

function interactionRows(rows) {
  const groups = new Map();
  for (const row of rows) {
    const key = `${row.timing.windowId}|${directionOf(row)}|${qualityOf(row)}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.entries()].map(([key, group]) => {
    const [windowId, direction, quality] = key.split('|');
    return { windowId, direction, quality, ...summarizeCell(group) };
  }).sort((a, b) => b.n - a.n);
}

function stableCells(dev, valMap) {
  return dev.filter((r) => r.eligible).map((r) => {
    const key = `${r.windowId}|${r.direction}|${r.quality}`;
    const v = valMap.get(key) ?? null;
    const sameSign = Boolean(v && Math.sign(r.avgR) === Math.sign(v.avgR) && r.avgR !== 0 && v.avgR !== 0);
    const bothPositive = Boolean(v && r.avgR > 0 && v.avgR > 0 && r.PF >= 1 && v.PF >= 1);
    const bothNegative = Boolean(v && r.avgR < 0 && v.avgR < 0 && r.PF < 1 && v.PF < 1);
    return { ...r, val: v, sameSign, bothPositive, bothNegative };
  });
}

async function run(timeframe) {
  const source = JSON.parse(await readFile(
    resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`),
    'utf8',
  ));
  const trades = (source.trades ?? [])
    .filter((trade) => Number.isFinite(Number(trade.rMultiple)) && trade.result !== 'AMBIGUOUS')
    .map((trade) => ({
      ...trade,
      rMultiple: Number(trade.rMultiple),
      timing: classifyTime(new Date(trade.entryTime)),
    }))
    .filter((trade) => trade.timing.windowId)
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const { DEV, VAL } = splitDevVal(trades);
  const devMatrix = matrix(DEV);
  const valMatrix = matrix(VAL);
  const devInteractions = interactionRows(DEV);
  const valInteractions = interactionRows(VAL);
  const devStableSource = devInteractions.map((r) => ({ ...r, eligible: r.n >= MIN_N }));
  const valMap = new Map(valInteractions.map((r) => [`${r.windowId}|${r.direction}|${r.quality}`, r]));
  const joined = stableCells(devStableSource, valMap);

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_POORSAMADI_TIME_DIRECTION_QUALITY_V1',
    timeframe,
    timezone: TIMEZONE,
    scope: 'Research-only interaction analysis over canonical baseline resolved trades. Fixed source windows; direction and existing quality metadata only. No production rule changes.',
    methodology: {
      windows: WINDOWS,
      boundary: '[start, end)',
      minCellN: MIN_N,
      devValSplit: 'chronological 60/40 of baseline resolved trades',
      qualityBuckets: QUALITY_BUCKETS,
      qualitySource: 'Existing trade quality fields only; no threshold fitting or re-scoring performed.',
      freshHoldout: 'not used',
      promotion: 'No cell or filter is promoted from this report. A candidate must be pre-registered after DEV→VAL review and then tested on the untouched holdout.',
    },
    overall: summarize(trades),
    dev: {
      overall: summarize(DEV),
      matrix: devMatrix,
      interactions: devInteractions,
    },
    val: {
      overall: summarize(VAL),
      matrix: valMatrix,
      interactions: valInteractions,
    },
    devValJoined: joined,
    diagnosticQuestions: [
      'Does the 5m US-open negative effect persist in both directions, or concentrate in one direction?',
      'Does the 5m late-21:00-24:00 positive effect persist after direction conditioning?',
      'Does setup quality explain the apparent time effect, making a time filter redundant?',
      'Are any apparent effects based on very small cells and therefore only descriptive?',
    ],
    nextStep: 'Use only robust, sufficiently populated DEV→VAL patterns to define at most one pre-registered timing hypothesis. Validate timestamp timezone before economic interpretation. Keep fresh holdout sealed.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const output = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(output, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: N=${trades.length} DEV=${DEV.length} VAL=${VAL.length} timezone=${TIMEZONE}`);
  for (const side of ['dev', 'val']) {
    const eligible = report[side].interactions.filter((r) => r.n >= MIN_N);
    console.log(`${side.toUpperCase()}: ${eligible.map((r) => `${r.windowId}/${r.direction}/${r.quality}:n=${r.n},avgR=${r.avgR.toFixed(4)},PF=${r.PF?.toFixed(3) ?? 'n/a'}`).join(' | ')}`);
  }
  console.log(`Report -> ${output}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
