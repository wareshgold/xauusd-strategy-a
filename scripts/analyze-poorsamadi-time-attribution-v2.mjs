import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-poorsamadi-time-attribution-v2');
const TIMEFRAMES = ['5min'];
const TIMEZONE = process.env.POORSAMADI_TIMEZONE ?? 'Europe/Istanbul';
const MIN_N = 10;

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

const DIRECTIONS = ['BUY', 'SELL'];
const QUALITIES = ['A', 'B', 'OTHER', 'UNKNOWN'];
const CANDIDATE_WINDOWS = new Set([
  'midday_1000_1300',
  'us_open_1300_1530',
  'late_2100_2400',
]);

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
  return {
    ...out,
    minuteOfDay: Number(out.hour) * 60 + Number(out.minute) + Number(out.second) / 60,
  };
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
  const value = String(trade.direction ?? '').toUpperCase();
  return DIRECTIONS.includes(value) ? value : 'UNKNOWN';
}

function qualityOf(trade) {
  const raw = trade.qualityGrade ?? trade.quality ?? trade.setupQuality ?? trade.qualityClass;
  const value = String(raw ?? '').trim().toUpperCase();
  if (QUALITIES.includes(value)) return value;
  return value ? 'OTHER' : 'UNKNOWN';
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
  let lossRun = 0;
  let maxConsecutiveLosses = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, peak - equity);
    if (r < 0) {
      lossRun += 1;
      maxConsecutiveLosses = Math.max(maxConsecutiveLosses, lossRun);
    } else {
      lossRun = 0;
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

function keyOf(row) {
  return `${row.timing.windowId}|${directionOf(row)}|${qualityOf(row)}`;
}

function groupRows(rows, keyFn) {
  const groups = new Map();
  for (const row of rows) {
    const key = keyFn(row);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return groups;
}

function summarizeGroup(group, overallTotalR) {
  const stats = summarize(group);
  return {
    ...stats,
    eligible: stats.n >= MIN_N,
    contributionPctTotalR: overallTotalR ? (stats.totalR / overallTotalR) * 100 : null,
  };
}

function windowRows(rows, id) {
  return rows.filter((r) => r.timing.windowId === id);
}

function attribution(rows) {
  const overall = summarize(rows);
  const windows = WINDOWS.map((w) => {
    const group = windowRows(rows, w.id);
    const stats = summarizeGroup(group, overall.totalR);
    const direction = {};
    for (const side of DIRECTIONS) {
      const sideRows = group.filter((r) => directionOf(r) === side);
      direction[side] = {
        ...summarizeGroup(sideRows, overall.totalR),
        quality: Object.fromEntries(QUALITIES.map((q) => {
          const qRows = sideRows.filter((r) => qualityOf(r) === q);
          return [q, summarizeGroup(qRows, overall.totalR)];
        })),
      };
    }
    return {
      window: w,
      all: stats,
      direction,
      candidate: CANDIDATE_WINDOWS.has(w.id),
    };
  });

  const byDirection = Object.fromEntries(DIRECTIONS.map((side) => {
    const group = rows.filter((r) => directionOf(r) === side);
    return [side, summarizeGroup(group, overall.totalR)];
  }));

  const byQuality = Object.fromEntries(QUALITIES.map((q) => {
    const group = rows.filter((r) => qualityOf(r) === q);
    return [q, summarizeGroup(group, overall.totalR)];
  }));

  const candidateRows = rows.filter((r) => CANDIDATE_WINDOWS.has(r.timing.windowId));
  const nonCandidateRows = rows.filter((r) => !CANDIDATE_WINDOWS.has(r.timing.windowId));

  return {
    overall,
    windows,
    byDirection,
    byQuality,
    candidateVsOther: {
      candidate: summarizeGroup(candidateRows, overall.totalR),
      other: summarizeGroup(nonCandidateRows, overall.totalR),
    },
  };
}

function joinedInteractions(devRows, valRows) {
  const devMap = groupRows(devRows, keyOf);
  const valMap = groupRows(valRows, keyOf);
  const keys = [...new Set([...devMap.keys(), ...valMap.keys()])];
  return keys.map((key) => {
    const dev = devMap.get(key) ?? [];
    const val = valMap.get(key) ?? [];
    const [windowId, direction, quality] = key.split('|');
    const d = summarize(dev);
    const v = summarize(val);
    const eligible = d.n >= MIN_N && v.n >= MIN_N;
    const sameSign = d.avgR !== 0 && v.avgR !== 0 && Math.sign(d.avgR) === Math.sign(v.avgR);
    const bothPositive = eligible && d.avgR > 0 && v.avgR > 0 && d.PF >= 1 && v.PF >= 1;
    const bothNegative = eligible && d.avgR < 0 && v.avgR < 0 && d.PF < 1 && v.PF < 1;
    return {
      windowId,
      direction,
      quality,
      dev: { ...d, eligible: d.n >= MIN_N },
      val: { ...v, eligible: v.n >= MIN_N },
      eligible,
      sameSign,
      bothPositive,
      bothNegative,
      candidateWindow: CANDIDATE_WINDOWS.has(windowId),
    };
  }).sort((a, b) => (Number(b.eligible) - Number(a.eligible)) || (b.dev.n + b.val.n) - (a.dev.n + a.val.n));
}

function compactCandidateTable(attr) {
  return attr.windows
    .filter((x) => x.candidate)
    .map((x) => ({
      windowId: x.window.id,
      all: x.all,
      buy: x.direction.BUY,
      sell: x.direction.SELL,
    }));
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
  const devAttr = attribution(DEV);
  const valAttr = attribution(VAL);
  const joined = joinedInteractions(DEV, VAL);

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_POORSAMADI_TIME_ATTRIBUTION_V2',
    timeframe,
    timezone: TIMEZONE,
    scope: 'Research-only attribution diagnostic over canonical baseline resolved trades. No production rule changes and no fresh holdout access.',
    methodology: {
      windows: WINDOWS,
      candidateWindows: [...CANDIDATE_WINDOWS],
      minCellN: MIN_N,
      devValSplit: 'chronological 60/40',
      qualityBuckets: QUALITIES,
      qualitySource: 'Existing trade quality fields only; no re-scoring or threshold fitting.',
      contributionDefinition: 'subgroup totalR divided by the split overall totalR; percentage is descriptive and can be unstable when denominator is near zero.',
      freshHoldout: 'sealed / not used',
      promotion: 'No filter or rule is promoted by this report.',
    },
    DEV: devAttr,
    VAL: valAttr,
    candidateWindowSummary: {
      DEV: compactCandidateTable(devAttr),
      VAL: compactCandidateTable(valAttr),
    },
    joinedInteractions: joined,
    interpretationChecklist: [
      'US-open effect: compare DEV and VAL all-direction results, then BUY/SELL subgroups; a negative effect in both directions is evidence for a regime-level hypothesis, not a direction rule.',
      'Late-21:00-24:00 effect: require direction-specific DEV→VAL stability before considering any timing hypothesis.',
      'Quality confounding: compare the same quality bucket across windows and the same window across quality buckets; do not infer causality from raw subgroup differences.',
      'Small cells: MIN_N is descriptive eligibility only. No small cell is promotable regardless of apparent AvgR/PF.',
      'Timezone: Europe/Istanbul remains an explicit research assumption and must be validated against source timestamp semantics before economic interpretation.',
    ],
    nextStep: 'After reviewing DEV→VAL attribution, pre-register at most one timing hypothesis if a sufficiently populated pattern is stable. Then test only that hypothesis on the untouched fresh holdout.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const output = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(output, JSON.stringify(report, null, 2));

  console.log(`${timeframe}: N=${trades.length} DEV=${DEV.length} VAL=${VAL.length} timezone=${TIMEZONE}`);
  for (const split of ['DEV', 'VAL']) {
    const attr = report[split];
    console.log(`${split} candidate windows:`);
    for (const row of attr.windows.filter((x) => x.candidate)) {
      const b = row.direction.BUY;
      const s = row.direction.SELL;
      console.log(`  ${row.window.id}: ALL n=${row.all.n} avgR=${row.all.avgR.toFixed(4)} PF=${row.all.PF?.toFixed(3) ?? 'n/a'} | BUY n=${b.n} avgR=${b.avgR.toFixed(4)} PF=${b.PF?.toFixed(3) ?? 'n/a'} | SELL n=${s.n} avgR=${s.avgR.toFixed(4)} PF=${s.PF?.toFixed(3) ?? 'n/a'}`);
    }
  }
  console.log('Eligible DEV->VAL interaction cells:');
  for (const row of joined.filter((x) => x.eligible)) {
    console.log(`  ${row.windowId}/${row.direction}/${row.quality}: DEV n=${row.dev.n} avgR=${row.dev.avgR.toFixed(4)} PF=${row.dev.PF?.toFixed(3) ?? 'n/a'} | VAL n=${row.val.n} avgR=${row.val.avgR.toFixed(4)} PF=${row.val.PF?.toFixed(3) ?? 'n/a'} | sameSign=${row.sameSign}`);
  }
  console.log(`Report -> ${output}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
