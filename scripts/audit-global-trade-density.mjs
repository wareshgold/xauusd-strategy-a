import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASELINE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-global-trade-density');
const DEV = 6000;
const PRE_HOLDOUT = 10000;
const CLUSTER_GAPS = [1, 3, 6, 12];

function p(n) { return Number.isFinite(n) ? Number(n.toFixed(6)) : null; }
function finite(n) { return Number.isFinite(Number(n)); }
function quantile(values, f) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const pos = (a.length - 1) * f, lo = Math.floor(pos), hi = Math.ceil(pos);
  return a[lo] + (a[hi] - a[lo]) * (pos - lo);
}
function parseTime(t) { const ms = Date.parse(t); return Number.isFinite(ms) ? ms : null; }
function dayKey(t) { const ms = parseTime(t); return ms === null ? 'UNKNOWN' : new Date(ms).toISOString().slice(0, 10); }
function hourKey(t) { const ms = parseTime(t); return ms === null ? 'UNKNOWN' : new Date(ms).toISOString().slice(0, 13); }
function groupCounts(rows, keyFn) {
  const m = new Map();
  for (const r of rows) { const k = keyFn(r); m.set(k, (m.get(k) ?? 0) + 1); }
  return [...m.values()];
}
function frequencyStats(rows) {
  const days = groupCounts(rows, r => dayKey(r.entryTime));
  const hours = groupCounts(rows, r => hourKey(r.entryTime));
  return {
    trades: rows.length,
    uniqueDays: days.length,
    tradesPerDay: p(days.length ? rows.length / days.length : 0),
    medianTradesPerDay: p(quantile(days, .5)),
    p75TradesPerDay: p(quantile(days, .75)),
    maxTradesPerDay: days.length ? Math.max(...days) : 0,
    uniqueHours: hours.length,
    tradesPerHour: p(hours.length ? rows.length / hours.length : 0),
    maxTradesPerHour: hours.length ? Math.max(...hours) : 0,
  };
}
function distribution(rows, keyFn) {
  const m = new Map();
  for (const r of rows) { const k = keyFn(r); m.set(k, (m.get(k) ?? 0) + 1); }
  return Object.fromEntries([...m.entries()].sort((a, b) => String(a[0]).localeCompare(String(b[0]))));
}
function gapStats(rows) {
  const sorted = [...rows].sort((a, b) => a.entryIndex - b.entryIndex);
  const gaps = [];
  for (let i = 1; i < sorted.length; i++) gaps.push(sorted[i].entryIndex - sorted[i - 1].entryIndex);
  return {
    n: gaps.length,
    medianCandles: p(quantile(gaps, .5)),
    p25Candles: p(quantile(gaps, .25)),
    p75Candles: p(quantile(gaps, .75)),
    minCandles: gaps.length ? Math.min(...gaps) : null,
    maxCandles: gaps.length ? Math.max(...gaps) : null,
    adjacentShare: p(gaps.length ? gaps.filter(x => x <= 1).length / gaps.length : 0),
    clusterShare: Object.fromEntries(CLUSTER_GAPS.map(g => [String(g), p(gaps.length ? gaps.filter(x => x <= g).length / gaps.length : 0)])),
  };
}
function split(rows, name) {
  const directions = { BUY: rows.filter(r => r.direction === 'BUY').length, SELL: rows.filter(r => r.direction === 'SELL').length };
  const sessions = distribution(rows, r => r.session ?? 'UNKNOWN');
  return { name, frequency: frequencyStats(rows), gap: gapStats(rows), direction: directions, directionShare: { BUY: p(rows.length ? directions.BUY / rows.length : 0), SELL: p(rows.length ? directions.SELL / rows.length : 0) }, sessionCounts: sessions, sessionShare: Object.fromEntries(Object.entries(sessions).map(([k, v]) => [k, p(rows.length ? v / rows.length : 0)])), dayCounts: distribution(rows, r => dayKey(r.entryTime)), hourCounts: distribution(rows, r => hourKey(r.entryTime)) };
}
async function main() {
  const baseline = JSON.parse(await readFile(BASELINE, 'utf8'));
  const trades = (baseline.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && finite(t.rMultiple) && Number.isInteger(Number(t.entryIndex)));
  const rows = trades.map(t => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, direction: t.direction, session: t.session ?? null, r: Number(t.rMultiple) }));
  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE_HOLDOUT);
  const fresh = rows.filter(r => r.entryIndex >= PRE_HOLDOUT);
  const report = {
    strategy: 'Strategy A / SP2L', mode: 'GLOBAL_TRADE_DENSITY_CLUSTERING_AUDIT', timeframe: '5m',
    scope: { rawBaseline: (baseline.trades ?? []).length, canonical: rows.length, DEV: dev.length, VAL: val.length, FRESH_HOLDOUT: fresh.length, freshHoldoutNotUsedForHypothesis: true },
    methodology: { purpose: 'Descriptive audit of signal frequency, temporal clustering, direction and session concentration.', clusterGapsCandles: CLUSTER_GAPS, timezoneForCalendarBuckets: 'UTC from entryTime ISO strings', noOptimization: true, noThresholdSearch: true, noProductionChange: true, noNewTradingRules: true },
    ALL: split(rows, 'ALL'), DEV: split(dev, 'DEV'), VAL: split(val, 'VAL'), FRESH_HOLDOUT: split(fresh, 'FRESH_HOLDOUT'),
    interpretationGuard: 'High frequency or clustering is diagnostic only. Do not filter or change the strategy from this report alone; first identify whether clustered entries represent repeated structural events or legitimate independent setups.'
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, '5min.json');
  await writeFile(out, JSON.stringify(report, null, 2));
  for (const s of [report.ALL, report.DEV, report.VAL, report.FRESH_HOLDOUT]) {
    console.log(`${s.name}: N=${s.frequency.trades} days=${s.frequency.uniqueDays} trades/day=${s.frequency.tradesPerDay} medGap=${s.gap.medianCandles} max/day=${s.frequency.maxTradesPerDay} max/hour=${s.frequency.maxTradesPerHour}`);
    console.log(`  BUY=${s.direction.BUY} SELL=${s.direction.SELL} sessions=${JSON.stringify(s.sessionCounts)} cluster<=1=${s.gap.clusterShare['1']} <=3=${s.gap.clusterShare['3']} <=6=${s.gap.clusterShare['6']} <=12=${s.gap.clusterShare['12']}`);
  }
  console.log(`Report -> ${out}`);
}
await main();
