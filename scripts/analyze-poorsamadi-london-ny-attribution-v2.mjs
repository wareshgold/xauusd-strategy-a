import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-poorsamadi-london-ny-attribution-v2');
const TIMEFRAMES = ['1min', '5min'];
const LONDON_TZ = 'Europe/London';
const NEW_YORK_TZ = 'America/New_York';
const MIN_N = 20;

// Research-only, mutually-exclusive event windows inside the corrected
// London -> end-of-New-York trading universe. Stored timestamps remain UTC.
// London start is the market-universe boundary. After that boundary, windows
// are anchored to New York local session events so DST is handled by IANA.
const LONDON_START = '08:00';
const NY_OPEN = 8 * 60 + 30;
const NY_OPEN_END = 10 * 60 + 30;
const NY_MID_END = 13 * 60;
const NY_END = 17 * 60;

function zonedParts(date, timeZone) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(date);
  return Object.fromEntries(parts.map((p) => [p.type, p.value]));
}

function minuteOfDay(parts) {
  return Number(parts.hour) * 60 + Number(parts.minute) + Number(parts.second) / 60;
}

function offsetMinutes(date, timeZone) {
  const p = zonedParts(date, timeZone);
  const asUtc = Date.UTC(Number(p.year), Number(p.month) - 1, Number(p.day), Number(p.hour), Number(p.minute), Number(p.second));
  return Math.round((asUtc - date.getTime()) / 60000);
}

function classify(date) {
  const london = zonedParts(date, LONDON_TZ);
  const ny = zonedParts(date, NEW_YORK_TZ);
  const londonMinutes = minuteOfDay(london);
  const nyMinutes = minuteOfDay(ny);
  const inUniverse = londonMinutes >= 8 * 60 && nyMinutes < NY_END;

  let window = 'outside';
  if (inUniverse) {
    if (nyMinutes < NY_OPEN) window = 'london_pre_ny_open';
    else if (nyMinutes < NY_OPEN_END) window = 'ny_open';
    else if (nyMinutes < NY_MID_END) window = 'ny_mid';
    else window = 'ny_late';
  }

  return {
    inUniverse,
    window,
    london: { localDate: `${london.year}-${london.month}-${london.day}`, localTime: `${london.hour}:${london.minute}`, offsetMinutes: offsetMinutes(date, LONDON_TZ) },
    newYork: { localDate: `${ny.year}-${ny.month}-${ny.day}`, localTime: `${ny.hour}:${ny.minute}`, offsetMinutes: offsetMinutes(date, NEW_YORK_TZ) },
  };
}

function summarize(rows) {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  let equity = 0, peak = 0, dd = 0, streak = 0, maxCL = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
    if (r < 0) { streak += 1; maxCL = Math.max(maxCL, streak); } else streak = 0;
  }
  return {
    n: rs.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    avgR: rs.length ? rs.reduce((a, b) => a + b, 0) / rs.length : 0,
    totalR: rs.reduce((a, b) => a + b, 0),
    PF: gl ? gp / gl : (gp ? null : 0),
    maxDrawdown: dd,
    maxConsecutiveLosses: maxCL,
  };
}

function groupStats(rows) {
  return {
    all: summarize(rows),
    buy: summarize(rows.filter((r) => String(r.direction ?? '').toUpperCase() === 'BUY')),
    sell: summarize(rows.filter((r) => String(r.direction ?? '').toUpperCase() === 'SELL')),
    qualityA: summarize(rows.filter((r) => String(r.qualityGrade ?? r.quality ?? '').toUpperCase() === 'A')),
    qualityB: summarize(rows.filter((r) => String(r.qualityGrade ?? r.quality ?? '').toUpperCase() === 'B')),
    buyA: summarize(rows.filter((r) => String(r.direction ?? '').toUpperCase() === 'BUY' && String(r.qualityGrade ?? r.quality ?? '').toUpperCase() === 'A')),
    sellA: summarize(rows.filter((r) => String(r.direction ?? '').toUpperCase() === 'SELL' && String(r.qualityGrade ?? r.quality ?? '').toUpperCase() === 'A')),
  };
}

function splitDevVal(rows) {
  const sorted = [...rows].sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));
  const n = Math.floor(sorted.length * 0.6);
  return { DEV: sorted.slice(0, n), VAL: sorted.slice(n) };
}

function windowStats(rows) {
  const names = ['london_pre_ny_open', 'ny_open', 'ny_mid', 'ny_late'];
  return Object.fromEntries(names.map((name) => {
    const subset = rows.filter((r) => r.session.window === name);
    const { DEV, VAL } = splitDevVal(subset);
    return [name, { n: subset.length, dev: groupStats(DEV), val: groupStats(VAL) }];
  }));
}

async function run(timeframe) {
  const sourcePath = resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`);
  const source = JSON.parse(await readFile(sourcePath, 'utf8'));
  const trades = (source.trades ?? [])
    .filter((t) => Number.isFinite(Number(t.rMultiple)) && t.result !== 'AMBIGUOUS')
    .map((t) => ({ ...t, rMultiple: Number(t.rMultiple) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const classified = trades.map((t) => ({ ...t, session: classify(new Date(t.entryTime)) }));
  const universe = classified.filter((t) => t.session.inUniverse);
  const { DEV, VAL } = splitDevVal(universe);

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_POORSAMADI_LONDON_NY_ATTRIBUTION_V2',
    timeframe,
    canonicalTimestamp: 'UTC',
    sessionTimezones: { london: LONDON_TZ, newYork: NEW_YORK_TZ },
    universe: {
      start: `${LONDON_TZ} ${LONDON_START}`,
      end: `${NEW_YORK_TZ} 17:00`,
      dst: 'IANA timezone rules; no fixed UTC offset',
    },
    windows: {
      london_pre_ny_open: 'London 08:00 local until New York 08:30 local',
      ny_open: 'New York 08:30-10:30 local',
      ny_mid: 'New York 10:30-13:00 local',
      ny_late: 'New York 13:00-17:00 local',
    },
    scope: 'Research-only attribution. Fresh holdout excluded. No production rule changes and no threshold optimization.',
    assumptions: { minN: MIN_N, devValSplit: 'chronological 60/40 within the corrected London-to-New-York universe', freshHoldout: 'not used' },
    overall: groupStats(universe),
    dev: groupStats(DEV),
    val: groupStats(VAL),
    windows: windowStats(universe),
    sanity: classified.slice(0, 5).map((t) => ({ entryTime: t.entryTime, window: t.session.window, london: t.session.london, newYork: t.session.newYork })),
    interpretationRules: {
      candidate: 'A timing cell is only a research candidate when DEV and VAL have the same sign and economically meaningful stability with sufficient N.',
      promotion: 'No promotion from this report alone. Any candidate must be pre-registered before fresh-holdout evaluation.',
      minN: `Cells below N=${MIN_N} are descriptive only.`,
    },
    nextStep: 'Review DEV/VAL window, direction, and quality attribution. Pre-register at most a small number of stable hypotheses before any fresh-holdout test.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const output = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(output, JSON.stringify(report, null, 2));

  console.log(`${timeframe}: universe=${universe.length} DEV=${DEV.length} VAL=${VAL.length}`);
  for (const [name, data] of Object.entries(report.windows)) {
    console.log(`${name}: n=${data.n} DEV ALL avgR=${data.dev.all.avgR.toFixed(4)} PF=${data.dev.all.PF?.toFixed(3) ?? 'n/a'} WR=${(data.dev.all.winRate * 100).toFixed(1)}% | VAL ALL avgR=${data.val.all.avgR.toFixed(4)} PF=${data.val.all.PF?.toFixed(3) ?? 'n/a'} WR=${(data.val.all.winRate * 100).toFixed(1)}% | DEV A=${data.dev.qualityA.n} VAL A=${data.val.qualityA.n}`);
    console.log(`  BUY DEV avgR=${data.dev.buy.avgR.toFixed(4)} PF=${data.dev.buy.PF?.toFixed(3) ?? 'n/a'} | VAL avgR=${data.val.buy.avgR.toFixed(4)} PF=${data.val.buy.PF?.toFixed(3) ?? 'n/a'} | SELL DEV avgR=${data.dev.sell.avgR.toFixed(4)} PF=${data.dev.sell.PF?.toFixed(3) ?? 'n/a'} | VAL avgR=${data.val.sell.avgR.toFixed(4)} PF=${data.val.sell.PF?.toFixed(3) ?? 'n/a'}`);
  }
  console.log(`Report -> ${output}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
