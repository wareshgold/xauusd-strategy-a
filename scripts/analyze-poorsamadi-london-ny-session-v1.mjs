import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-poorsamadi-london-ny-session-v1');
const TIMEFRAMES = ['1min', '5min'];
const LONDON_TZ = 'Europe/London';
const NEW_YORK_TZ = 'America/New_York';
const MIN_N = 20;

// Research-only session definition. Stored timestamps remain canonical UTC.
// Trading universe: London session start through end of New York session.
// The session boundaries are evaluated in the actual market timezones so DST is
// handled by the IANA timezone database rather than fixed UTC offsets.
const LONDON_START = '08:00';
const NEW_YORK_END = '17:00';

function zonedParts(date, timeZone) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(date);
  const out = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return out;
}

function minuteOfDay(parts) {
  return Number(parts.hour) * 60 + Number(parts.minute) + Number(parts.second) / 60;
}

function hhmm(parts) {
  return `${parts.hour}:${parts.minute}`;
}

function offsetMinutes(date, timeZone) {
  const parts = zonedParts(date, timeZone);
  const asUtc = Date.UTC(
    Number(parts.year), Number(parts.month) - 1, Number(parts.day),
    Number(parts.hour), Number(parts.minute), Number(parts.second),
  );
  return Math.round((asUtc - date.getTime()) / 60000);
}

function classify(date) {
  const london = zonedParts(date, LONDON_TZ);
  const ny = zonedParts(date, NEW_YORK_TZ);
  const londonMinutes = minuteOfDay(london);
  const nyMinutes = minuteOfDay(ny);

  // Start boundary is London-local 08:00. End boundary is New-York-local 17:00.
  // A candle is in the trading universe when it is after both corresponding
  // session-day boundaries. Using the two local clocks also naturally handles
  // the periods where London and New York DST offsets differ.
  const londonStarted = londonMinutes >= 8 * 60;
  const nyFinished = nyMinutes >= 17 * 60;
  const sameTradingDate = londonStarted && !nyFinished;

  return {
    inTradingWindow: sameTradingDate,
    london: {
      timezone: LONDON_TZ,
      localDate: `${london.year}-${london.month}-${london.day}`,
      localTime: hhmm(london),
      offsetMinutes: offsetMinutes(date, LONDON_TZ),
    },
    newYork: {
      timezone: NEW_YORK_TZ,
      localDate: `${ny.year}-${ny.month}-${ny.day}`,
      localTime: hhmm(ny),
      offsetMinutes: offsetMinutes(date, NEW_YORK_TZ),
    },
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
  let streak = 0;
  let maxConsecutiveLosses = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, peak - equity);
    if (r < 0) {
      streak += 1;
      maxConsecutiveLosses = Math.max(maxConsecutiveLosses, streak);
    } else {
      streak = 0;
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

function sideStats(rows) {
  return {
    all: summarize(rows),
    buy: summarize(rows.filter((r) => String(r.direction ?? '').toUpperCase() === 'BUY')),
    sell: summarize(rows.filter((r) => String(r.direction ?? '').toUpperCase() === 'SELL')),
  };
}

async function run(timeframe) {
  const path = resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`);
  const source = JSON.parse(await readFile(path, 'utf8'));
  const trades = (source.trades ?? [])
    .filter((trade) => Number.isFinite(Number(trade.rMultiple)) && trade.result !== 'AMBIGUOUS')
    .map((trade) => ({ ...trade, rMultiple: Number(trade.rMultiple) }))
    .sort((a, b) => new Date(a.entryTime) - new Date(b.entryTime));

  const classified = trades.map((trade) => ({ ...trade, session: classify(new Date(trade.entryTime)) }));
  const inWindow = classified.filter((trade) => trade.session.inTradingWindow);
  const outsideWindow = classified.filter((trade) => !trade.session.inTradingWindow);
  const { DEV, VAL } = splitDevVal(inWindow);

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_POORSAMADI_LONDON_NY_SESSION_V1',
    timeframe,
    canonicalTimestamp: 'UTC',
    sessionTimezones: {
      london: LONDON_TZ,
      newYork: NEW_YORK_TZ,
    },
    tradingWindow: {
      start: `${LONDON_TZ} ${LONDON_START}`,
      end: `${NEW_YORK_TZ} ${NEW_YORK_END}`,
      semantics: 'Entry is eligible only after London 08:00 local and before New York 17:00 local on the corresponding trading day.',
      dst: 'IANA timezone rules; no fixed UTC offset is used.',
      iranTimezone: 'display/context only; not used for session classification',
    },
    scope: 'Research-only timing classification over canonical baseline resolved trades. No production rule changes. Fresh holdout is excluded.',
    assumptions: {
      minN: MIN_N,
      devValSplit: 'chronological 60/40 of trades inside the corrected London-to-New-York universe',
      freshHoldout: 'not used',
      selection: 'no optimization or production promotion',
    },
    overall: summarize(trades),
    correctedUniverse: {
      inWindow: sideStats(inWindow),
      outsideWindow: sideStats(outsideWindow),
      excludedCount: outsideWindow.length,
    },
    dev: sideStats(DEV),
    val: sideStats(VAL),
    sanity: {
      sampleOffsets: classified.slice(0, 5).map((trade) => ({
        entryTime: trade.entryTime,
        london: trade.session.london,
        newYork: trade.session.newYork,
        inTradingWindow: trade.session.inTradingWindow,
      })),
    },
    nextStep: 'Compare corrected DEV vs VAL. If a timing hypothesis survives with sufficient sample and stable direction/quality attribution, pre-register it before any fresh-holdout evaluation. Fresh holdout remains sealed.',
  };

  await mkdir(OUT_DIR, { recursive: true });
  const output = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(output, JSON.stringify(report, null, 2));

  console.log(`${timeframe}: overall=${trades.length} correctedWindow=${inWindow.length} outside=${outsideWindow.length} DEV=${DEV.length} VAL=${VAL.length}`);
  console.log(`DEV ALL: avgR=${report.dev.all.avgR.toFixed(4)} PF=${report.dev.all.PF?.toFixed(3) ?? 'n/a'} | BUY avgR=${report.dev.buy.avgR.toFixed(4)} PF=${report.dev.buy.PF?.toFixed(3) ?? 'n/a'} | SELL avgR=${report.dev.sell.avgR.toFixed(4)} PF=${report.dev.sell.PF?.toFixed(3) ?? 'n/a'}`);
  console.log(`VAL ALL: avgR=${report.val.all.avgR.toFixed(4)} PF=${report.val.all.PF?.toFixed(3) ?? 'n/a'} | BUY avgR=${report.val.buy.avgR.toFixed(4)} PF=${report.val.buy.PF?.toFixed(3) ?? 'n/a'} | SELL avgR=${report.val.sell.avgR.toFixed(4)} PF=${report.val.sell.PF?.toFixed(3) ?? 'n/a'}`);
  console.log(`Report -> ${output}`);
}

for (const timeframe of TIMEFRAMES) await run(timeframe);
