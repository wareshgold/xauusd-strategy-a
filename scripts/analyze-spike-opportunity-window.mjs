import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-spike-opportunity-window');
const TIMEFRAMES = ['1min', '5min'];
const LOOKBACK = 60;
const BIN_MINUTES = 15;
const OOS_SPLIT = 0.5;

function median(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function quantile(values, q) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const p = (a.length - 1) * q;
  const lo = Math.floor(p);
  const hi = Math.ceil(p);
  if (lo === hi) return a[lo];
  return a[lo] + (a[hi] - a[lo]) * (p - lo);
}

function parseTime(value) {
  const d = new Date(value.includes('T') ? value : value.replace(' ', 'T') + 'Z');
  if (Number.isNaN(d.getTime())) return null;
  return d;
}

function sessionFor(minutes) {
  const london = minutes >= 7 * 60 && minutes < 16 * 60;
  const ny = minutes >= 13 * 60 && minutes < 22 * 60;
  if (london && ny) return 'LONDON_NY_OVERLAP';
  if (ny) return 'NEW_YORK_ONLY';
  if (london) return 'LONDON_ONLY';
  return 'OUTSIDE';
}

function hourLabel(minutes) {
  return String(Math.floor(minutes / 60)).padStart(2, '0');
}

function add(map, key, value) {
  const a = map.get(key) ?? [];
  a.push(value);
  map.set(key, a);
}

function summarizeTrades(trades) {
  const usable = trades.filter(t => Number.isFinite(t.rMultiple));
  const wins = usable.filter(t => t.rMultiple > 0).reduce((s, t) => s + t.rMultiple, 0);
  const losses = usable.filter(t => t.rMultiple < 0).reduce((s, t) => s + Math.abs(t.rMultiple), 0);
  const pf = losses > 0 ? wins / losses : null;
  return { n: usable.length, PF: pf, avgR: usable.length ? usable.reduce((s, t) => s + t.rMultiple, 0) / usable.length : 0, totalR: usable.reduce((s, t) => s + t.rMultiple, 0) };
}

function maxDrawdown(trades) {
  let equity = 0, peak = 0, dd = 0;
  for (const t of trades.filter(x => Number.isFinite(x.rMultiple))) {
    equity += t.rMultiple;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
  }
  return dd;
}

async function load(path) {
  return JSON.parse(await readFile(path, 'utf8'));
}

async function run(timeframe) {
  const candlePath = resolve(ROOT, `data/historical/xauusd-${timeframe}.json`);
  const baselinePath = resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`);
  const dataset = await load(candlePath);
  const baseline = await load(baselinePath);
  const candles = dataset.candles;

  const tr = candles.map(c => Math.max(c.high - c.low, Math.abs(c.high - (c.close ?? c.open)), Math.abs(c.low - (c.close ?? c.open))));
  const normalized = candles.map((c, i) => {
    if (i < LOOKBACK) return null;
    const base = median(tr.slice(i - LOOKBACK, i));
    return base && base > 0 ? tr[i] / base : null;
  });

  const allScores = normalized.filter(Number.isFinite);
  const spikeCut = quantile(allScores, 0.90);
  const extremeCut = quantile(allScores, 0.95);

  const bins = new Map();
  const days = new Map();
  for (let i = LOOKBACK; i < candles.length; i++) {
    const d = parseTime(candles[i].timestamp);
    const score = normalized[i];
    if (!d || !Number.isFinite(score)) continue;
    const minutes = d.getUTCHours() * 60 + d.getUTCMinutes();
    const bin = Math.floor(minutes / BIN_MINUTES) * BIN_MINUTES;
    const key = String(bin);
    const rec = bins.get(key) ?? { scores: [], spikes: 0, extreme: 0, n: 0 };
    rec.scores.push(score); rec.n++;
    if (score >= spikeCut) rec.spikes++;
    if (score >= extremeCut) rec.extreme++;
    bins.set(key, rec);

    const day = d.toISOString().slice(0, 10);
    const dayRec = days.get(day) ?? { n: 0, spikes: 0, extreme: 0, max: 0 };
    dayRec.n++; if (score >= spikeCut) dayRec.spikes++; if (score >= extremeCut) dayRec.extreme++; dayRec.max = Math.max(dayRec.max, score);
    days.set(day, dayRec);
  }

  const hourly = [...Array(24)].map((_, hour) => {
    const relevant = [...bins.entries()].filter(([k]) => Math.floor(Number(k) / 60) === hour).map(([, v]) => v).flatMap(v => v.scores);
    const spikeCount = [...bins.entries()].filter(([k]) => Math.floor(Number(k) / 60) === hour).reduce((s, [, v]) => s + v.spikes, 0);
    return { hourUTC: hour, medianScore: median(relevant), p90Score: quantile(relevant, 0.90), spikeBars: spikeCount, observations: relevant.length };
  });

  const windowDefs = [
    { name: 'LONDON_OPEN_WINDOW', start: 7 * 60, end: 9 * 60 },
    { name: 'LONDON_NY_OVERLAP', start: 13 * 60, end: 16 * 60 },
    { name: 'NY_OPEN_WINDOW', start: 13 * 60, end: 14 * 60 },
    { name: 'PRE_NY_BUILD', start: 11 * 60, end: 13 * 60 },
    { name: 'OTHER', start: 0, end: 24 * 60 },
  ];

  const windowStats = windowDefs.map(w => {
    const rows = [];
    for (let i = LOOKBACK; i < candles.length; i++) {
      const d = parseTime(candles[i].timestamp); if (!d || !Number.isFinite(normalized[i])) continue;
      const m = d.getUTCHours() * 60 + d.getUTCMinutes();
      if (w.name !== 'OTHER' && !(m >= w.start && m < w.end)) continue;
      rows.push(normalized[i]);
    }
    const spikes = rows.filter(x => x >= spikeCut).length;
    const extremes = rows.filter(x => x >= extremeCut).length;
    return { name: w.name, observations: rows.length, medianScore: median(rows), p90Score: quantile(rows, 0.90), spikeRate: rows.length ? spikes / rows.length : 0, extremeRate: rows.length ? extremes / rows.length : 0 };
  });

  const trades = baseline.trades.filter(t => Number.isFinite(t.rMultiple));
  const tradeRows = trades.map(t => {
    const d = parseTime(t.entryTime);
    const m = d ? d.getUTCHours() * 60 + d.getUTCMinutes() : null;
    const candle = Number.isInteger(t.entryIndex) ? candles[t.entryIndex] : null;
    return { ...t, hourUTC: d?.getUTCHours() ?? null, minuteUTC: m, session: m == null ? 'UNKNOWN' : sessionFor(m), spikeScoreAtEntry: candle && normalized[t.entryIndex] != null ? normalized[t.entryIndex] : null };
  });

  const tradeWindows = windowDefs.map(w => {
    const rows = tradeRows.filter(t => {
      if (t.minuteUTC == null) return false;
      return w.name === 'OTHER' ? true : t.minuteUTC >= w.start && t.minuteUTC < w.end;
    });
    return { name: w.name, ...summarizeTrades(rows), maxDD: maxDrawdown(rows), spikeScoreP50: median(rows.map(x => x.spikeScoreAtEntry)) };
  });

  const daysList = [...days.entries()].map(([date, v]) => ({ date, ...v, spikeRate: v.spikes / v.n })).sort((a, b) => a.date.localeCompare(b.date));
  const dailyTargetCheck = daysList.map(d => ({ ...d, desiredSignalRange: '1-5', spikeEventCountProxy: d.spikes }));

  const mid = Math.floor(tradeRows.length * OOS_SPLIT);
  const oosTrades = tradeRows.slice(mid);
  const oosWindowStats = windowDefs.map(w => {
    const rows = oosTrades.filter(t => t.minuteUTC != null && (w.name === 'OTHER' || (t.minuteUTC >= w.start && t.minuteUTC < w.end)));
    return { name: w.name, ...summarizeTrades(rows) };
  });

  const report = {
    strategy: 'Strategy A / SP2L', mode: 'RESEARCH_SPIKE_OPPORTUNITY_WINDOW', timeframe,
    data: { symbol: dataset.symbol, source: dataset.source, candles: candles.length, from: candles[0]?.timestamp ?? null, to: candles.at(-1)?.timestamp ?? null },
    methodology: {
      lookbackBars: LOOKBACK,
      binMinutes: BIN_MINUTES,
      spikeDefinition: 'Exploratory only: true-range divided by the median true-range of the preceding 60 bars; spike bars are the top 10% of normalized scores in this dataset and extreme bars are the top 5%. No strategy gate is changed.',
      sessionClock: 'UTC; aligned with current Strategy A context (London 07:00-16:00, New York 13:00-22:00).',
      validation: 'Descriptive and split-sample diagnostics only. No threshold is accepted for production from this report.'
    },
    thresholds: { spikeP90: spikeCut, extremeP95: extremeCut },
    hourly,
    windows: windowStats,
    baselineTradeWindows: tradeWindows,
    oosBaselineTradeWindows: oosWindowStats,
    dailySpikeDistribution: dailyTargetCheck,
    decisionHints: {
      targetSignalsPerDay: { min: 1, max: 5 },
      nextResearchGate: 'Test whether high-spike opportunity windows combine with structurally valid SP2L setups and remain positive in OOS, without forcing a daily signal quota.',
      warning: 'The current sample is short. A 1-5 signal/day target is a design objective, not evidence that the market supplies 1-5 valid setups every day.'
    }
  };

  await mkdir(REPORT_DIR, { recursive: true });
  const out = resolve(REPORT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: candles=${candles.length} spikeP90=${spikeCut?.toFixed(4) ?? 'n/a'} extremeP95=${extremeCut?.toFixed(4) ?? 'n/a'}`);
  for (const w of windowStats) console.log(`  ${w.name}: n=${w.observations} median=${w.medianScore?.toFixed(3) ?? 'n/a'} p90=${w.p90Score?.toFixed(3) ?? 'n/a'} spikeRate=${(w.spikeRate * 100).toFixed(2)}%`);
  for (const w of tradeWindows) console.log(`  TRADES ${w.name}: n=${w.n} PF=${w.PF?.toFixed(4) ?? 'n/a'} avgR=${w.avgR.toFixed(4)} totalR=${w.totalR.toFixed(4)} spikeAtEntryP50=${w.spikeScoreP50?.toFixed(3) ?? 'n/a'}`);
  console.log(`  OOS trade half: ${summarizeTrades(oosTrades).n} trades PF=${summarizeTrades(oosTrades).PF?.toFixed(4) ?? 'n/a'} avgR=${summarizeTrades(oosTrades).avgR.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
