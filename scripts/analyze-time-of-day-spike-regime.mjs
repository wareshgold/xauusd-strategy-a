import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-time-of-day-spike-regime');

const WINDOWS = [
  { name: 'LONDON_OPEN_2H', start: 8 * 60, end: 10 * 60 },
  { name: 'LONDON_NY_TRANSITION', start: 12 * 60, end: 15 * 60 },
  { name: 'NY_OPEN_2H', start: 13 * 60 + 30, end: 15 * 60 + 30 },
  { name: 'LONDON_NY_OVERLAP', start: 13 * 60 + 30, end: 16 * 60 },
];

function pct(values, p) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const i = (a.length - 1) * p;
  const lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? a[lo] : a[lo] + (a[hi] - a[lo]) * (i - lo);
}

function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0), losses = rs.filter(r => r < 0);
  const gw = wins.reduce((s, r) => s + r, 0);
  const gl = Math.abs(losses.reduce((s, r) => s + r, 0));
  return {
    trades: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    avgR: rs.length ? rs.reduce((s, r) => s + r, 0) / rs.length : 0,
    totalR: rs.reduce((s, r) => s + r, 0),
    PF: gl ? gw / gl : null,
    medianR: pct(rs, 0.5),
  };
}

function maxDD(rows) {
  let eq = 0, peak = 0, dd = 0;
  for (const r of [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)))) {
    eq += Number.isFinite(r.rMultiple) ? r.rMultiple : 0;
    peak = Math.max(peak, eq);
    dd = Math.max(dd, peak - eq);
  }
  return dd;
}

function minuteOfDay(iso, timeZone) {
  const d = new Date(iso);
  if (!Number.isFinite(d.getTime())) return null;
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone, hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
  }).formatToParts(d);
  const h = Number(parts.find(p => p.type === 'hour')?.value);
  const m = Number(parts.find(p => p.type === 'minute')?.value);
  return Number.isFinite(h) && Number.isFinite(m) ? h * 60 + m : null;
}

function dayKey(iso) {
  const d = new Date(iso);
  return Number.isFinite(d.getTime()) ? d.toISOString().slice(0, 10) : null;
}

function inWindow(minute, start, end) {
  return minute != null && minute >= start && minute < end;
}

function classify(row) {
  const london = minuteOfDay(row.entryTime, 'Europe/London');
  const ny = minuteOfDay(row.entryTime, 'America/New_York');
  const labels = [];
  for (const w of WINDOWS) {
    if (inWindow(london, w.start, w.end) || inWindow(ny, w.start, w.end)) labels.push(w.name);
  }
  // Explicit NY-open / London-NY transition using each market's local clock.
  const londonOpen = inWindow(london, 8 * 60, 10 * 60);
  const nyOpen = inWindow(ny, 9 * 60 + 30, 11 * 60 + 30);
  const overlap = inWindow(london, 13 * 60 + 30, 16 * 60) || inWindow(ny, 8 * 60 + 30, 11 * 60);
  let regime = 'OTHER';
  if (overlap) regime = 'LONDON_NY_OVERLAP';
  else if (nyOpen) regime = 'NY_OPEN';
  else if (londonOpen) regime = 'LONDON_OPEN';
  return { ...row, regime, day: dayKey(row.entryTime), londonMinute: london, nyMinute: ny };
}

function bucket(minute) {
  if (!Number.isFinite(minute)) return 'NA';
  const h = Math.floor(minute / 60), m = Math.floor((minute % 60) / 30) * 30;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

function by(rows, keyFn) {
  const m = new Map();
  for (const r of rows) {
    const k = keyFn(r);
    if (!m.has(k)) m.set(k, []);
    m.get(k).push(r);
  }
  return Object.fromEntries([...m].map(([k, v]) => [k, { ...stats(v), DD: maxDD(v) }]));
}

function dailyStats(rows) {
  const days = new Map();
  for (const r of rows) {
    if (!r.day) continue;
    if (!days.has(r.day)) days.set(r.day, []);
    days.get(r.day).push(r);
  }
  const counts = [...days.values()].map(v => v.length);
  return {
    days: counts.length,
    meanTradesPerDay: counts.length ? counts.reduce((s, x) => s + x, 0) / counts.length : 0,
    medianTradesPerDay: pct(counts, 0.5),
    p90TradesPerDay: pct(counts, 0.9),
    maxTradesPerDay: counts.length ? Math.max(...counts) : 0,
    daysWithAtLeast1: counts.filter(x => x >= 1).length,
    daysWith2to5: counts.filter(x => x >= 2 && x <= 5).length,
    daysOver5: counts.filter(x => x > 5).length,
  };
}

function regimeReport(rows) {
  const groups = by(rows, r => r.regime);
  for (const g of Object.values(groups)) g.daily = dailyStats(rows.filter(r => r.regime === Object.keys(groups).find(k => groups[k] === g)));
  return groups;
}

function secondHalf(rows) {
  const sorted = [...rows].sort((a, b) => String(a.entryTime).localeCompare(String(b.entryTime)));
  return sorted.slice(Math.floor(sorted.length / 2));
}

async function analyze(timeframe) {
  const baseline = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const rows = (baseline.trades ?? []).filter(r => Number.isFinite(r.rMultiple)).map(classify);
  const oos = secondHalf(rows);
  const report = {
    strategy: 'Strategy A / SP2L', timeframe,
    sourceReport: `data/reports/strategy-a-baseline/${timeframe}.json`,
    purpose: 'Research-only time-of-day and London/New-York spike-regime study. No trading rule is activated.',
    timezoneMethod: 'Entry timestamps are classified using Europe/London and America/New_York local clocks so DST is handled explicitly.',
    targetOperationalConstraint: { minimumSignalsPerDay: 1, maximumSignalsPerDay: 5 },
    fullSample: {
      baseline: { ...stats(rows), DD: maxDD(rows), daily: dailyStats(rows) },
      byRegime: by(rows, r => r.regime),
      london30mBuckets: by(rows, r => bucket(r.londonMinute)),
      newYork30mBuckets: by(rows, r => bucket(r.nyMinute)),
      directionByRegime: by(rows, r => `${r.regime}__${r.direction ?? 'NA'}`),
    },
    oosSecondHalf: {
      baseline: { ...stats(oos), DD: maxDD(oos), daily: dailyStats(oos) },
      byRegime: by(oos, r => r.regime),
      london30mBuckets: by(oos, r => bucket(r.londonMinute)),
      newYork30mBuckets: by(oos, r => bucket(r.nyMinute)),
      directionByRegime: by(oos, r => `${r.regime}__${r.direction ?? 'NA'}`),
    },
    researchWarnings: [
      'London/NY windows are diagnostic probes, not validated production definitions.',
      'This study intentionally does not optimize thresholds or activate a time filter.',
      'Small time buckets can be unstable; OOS stability is required before promotion.',
      'The daily signal target is an operational objective, not a justification to force trades on weak days.',
    ],
  };
  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: trades=${rows.length} baselinePF=${report.fullSample.baseline.PF?.toFixed(4) ?? 'n/a'}`);
  console.log(`  daily mean/median/p90/max=${report.fullSample.baseline.daily.meanTradesPerDay.toFixed(2)}/${report.fullSample.baseline.daily.medianTradesPerDay ?? 'n/a'}/${report.fullSample.baseline.daily.p90TradesPerDay ?? 'n/a'}/${report.fullSample.baseline.daily.maxTradesPerDay}`);
  for (const [k, s] of Object.entries(report.fullSample.byRegime)) console.log(`  ${k}: n=${s.trades} PF=${s.PF?.toFixed(4) ?? 'n/a'} avgR=${s.avgR.toFixed(4)} totalR=${s.totalR.toFixed(4)} DD=${s.DD.toFixed(4)}`);
  console.log(`  OOS second-half: trades=${oos.length} PF=${report.oosSecondHalf.baseline.PF?.toFixed(4) ?? 'n/a'} avgR=${report.oosSecondHalf.baseline.avgR.toFixed(4)} totalR=${report.oosSecondHalf.baseline.totalR.toFixed(4)}`);
  for (const [k, s] of Object.entries(report.oosSecondHalf.byRegime)) console.log(`  OOS ${k}: n=${s.trades} PF=${s.PF?.toFixed(4) ?? 'n/a'} avgR=${s.avgR.toFixed(4)} totalR=${s.totalR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}

await analyze('1min');
await analyze('5min');
