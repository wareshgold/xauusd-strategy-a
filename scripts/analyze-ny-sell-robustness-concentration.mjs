import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASELINE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-ny-sell-robustness-concentration');
const DEV = 6000;
const PRE_HOLDOUT = 10000;
const WINDOWS = 6;

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
function quantile(values, f) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const pos = (a.length - 1) * f;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
}
function metrics(rows) {
  const rs = rows.map((x) => Number(x.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter((x) => x > 0), losses = rs.filter((x) => x < 0);
  const gp = wins.reduce((s, x) => s + x, 0);
  const gl = -losses.reduce((s, x) => s + x, 0);
  return { n: rs.length, wins: wins.length, losses: losses.length, winRate: p(rs.length ? wins.length / rs.length : 0), avgR: p(rs.length ? rs.reduce((s, x) => s + x, 0) / rs.length : 0), totalR: p(rs.reduce((s, x) => s + x, 0)), PF: gl ? p(gp / gl) : (gp ? null : 0) };
}
function maxDrawdown(rows) {
  let equity = 0, peak = 0, maxDD = 0;
  for (const row of [...rows].sort((a, b) => a.entryIndex - b.entryIndex)) {
    equity += Number(row.rMultiple);
    peak = Math.max(peak, equity);
    maxDD = Math.max(maxDD, peak - equity);
  }
  return p(maxDD);
}
function consecutiveLosses(rows) {
  let current = 0, max = 0;
  for (const row of [...rows].sort((a, b) => a.entryIndex - b.entryIndex)) {
    if (Number(row.rMultiple) < 0) { current++; max = Math.max(max, current); }
    else current = 0;
  }
  return max;
}
function classifyOutcome(r) {
  if (r > 3) return 'EXCEPTIONAL_WIN';
  if (r > 0) return 'NORMAL_WIN';
  return 'LOSS';
}
function pathStats(rows, candles) {
  const enriched = [];
  for (const t of rows) {
    const entryIndex = Number(t.entryIndex), entry = Number(t.entry), stop = Number(t.stopLoss);
    const risk = Math.abs(entry - stop);
    if (!Number.isInteger(entryIndex) || !(risk > 0) || !candles[entryIndex + 1]) continue;
    let mfe = 0, mae = 0;
    for (let i = entryIndex + 1; i <= Math.min(candles.length - 1, entryIndex + 20); i++) {
      const c = candles[i];
      mfe = Math.max(mfe, (entry - c.low) / risk);
      mae = Math.max(mae, (c.high - entry) / risk);
    }
    enriched.push({ ...t, mfe20: Math.max(0, mfe), mae20: Math.max(0, mae) });
  }
  return { medMFE20: p(quantile(enriched.map(x => x.mfe20), .5)), medMAE20: p(quantile(enriched.map(x => x.mae20), .5)), nEnriched: enriched.length };
}
function splitRolling(rows) {
  const sorted = [...rows].sort((a, b) => a.entryIndex - b.entryIndex);
  const base = Math.floor(sorted.length / WINDOWS);
  return Array.from({ length: WINDOWS }, (_, i) => sorted.slice(i * base, i === WINDOWS - 1 ? sorted.length : (i + 1) * base));
}
function weekday(rows) {
  const names = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
  return Object.fromEntries(names.map((name, day) => [name, metrics(rows.filter(r => new Date(r.entryTime).getUTCDay() === day))]));
}
function summarize(rows, candles) {
  const m = metrics(rows);
  return { ...m, maxDD: maxDrawdown(rows), maxConsecutiveLosses: consecutiveLosses(rows), outcomeClasses: { exceptionalWins: rows.filter(r => classifyOutcome(Number(r.rMultiple)) === 'EXCEPTIONAL_WIN').length, normalWins: rows.filter(r => classifyOutcome(Number(r.rMultiple)) === 'NORMAL_WIN').length, losses: rows.filter(r => Number(r.rMultiple) <= 0).length }, path: pathStats(rows, candles) };
}
function rolling(rows, candles) {
  return splitRolling(rows).map((w, i) => ({ window: i + 1, from: w[0]?.entryTime ?? null, to: w.at(-1)?.entryTime ?? null, ...summarize(w, candles) }));
}
function concentration(rows) {
  const wins = rows.filter(r => Number(r.rMultiple) > 0).sort((a, b) => Number(b.rMultiple) - Number(a.rMultiple));
  const totalR = rows.reduce((s, r) => s + Number(r.rMultiple), 0);
  const top = (n) => {
    const r = wins.slice(0, n).reduce((s, x) => s + Number(x.rMultiple), 0);
    return { topN: n, winnerR: p(r), shareOfTotalR: p(totalR ? r / totalR : null) };
  };
  const exceptional = rows.filter(r => Number(r.rMultiple) > 3);
  const exceptionalR = exceptional.reduce((s, r) => s + Number(r.rMultiple), 0);
  return { top1: top(1), top3: top(3), top5: top(5), exceptional: { n: exceptional.length, totalR: p(exceptionalR), shareOfTotalR: p(totalR ? exceptionalR / totalR : null), avgR: p(exceptional.length ? exceptionalR / exceptional.length : 0) } };
}
async function main() {
  const baseline = JSON.parse(await readFile(BASELINE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles;
  const raw = baseline.trades ?? [];
  const canonical = raw.filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && Number.isInteger(Number(t.entryIndex)) && t.direction === 'SELL');
  const allNY = canonical.filter(t => {
    const d = new Date(t.entryTime); const m = d.getUTCHours() * 60 + d.getUTCMinutes();
    return m >= 960 && m < 1320;
  });
  const dev = allNY.filter(t => Number(t.entryIndex) < DEV);
  const val = allNY.filter(t => Number(t.entryIndex) >= DEV && Number(t.entryIndex) < PRE_HOLDOUT);
  const fresh = allNY.filter(t => Number(t.entryIndex) >= PRE_HOLDOUT);
  const build = (rows, includeCases = false) => ({ summary: summarize(rows, candles), rolling: rolling(rows, candles), weekday: weekday(rows), concentration: concentration(rows), ...(includeCases ? { cases: rows.map(r => ({ entryTime: r.entryTime, r: Number(r.rMultiple), outcome: classifyOutcome(Number(r.rMultiple)), entryIndex: Number(r.entryIndex) })) } : {}) });
  const report = {
    strategy: 'Strategy A / SP2L', mode: 'RESEARCH_NY_SELL_ROBUSTNESS_CONCENTRATION', timeframe: '5m',
    scope: { direction: 'SELL', session: 'NEW_YORK_LATE', sessionDefinitionUTC: '16:00-22:00', rawBaselineTrades: raw.length, canonicalNYSELL: allNY.length, DEV: dev.length, VAL: val.length, FRESH_HOLDOUT: fresh.length, freshHoldoutExcludedFromHypothesis: true, productionUntouched: true },
    methodology: { purpose: 'Descriptive robustness and return-concentration audit of the pre-defined NY SELL segment.', rollingWindows: WINDOWS, outcomeExceptionalThresholdR: '>3R', maxDrawdown: 'chronological cumulative realized R', path: '20 post-entry 5m candles normalized by initial risk', weekday: 'UTC entry weekday', noOptimization: true, noThresholdSearch: true, noNewTradingRules: true, holdoutLocked: true },
    DEV: build(dev), VAL: build(val), FRESH_HOLDOUT: build(fresh),
    interpretationGuard: 'This report does not promote NY SELL to a trading rule. A candidate remains exploratory until concentration, rolling stability, and independent holdout behavior are jointly judged robust.'
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, '5min.json');
  await writeFile(out, JSON.stringify(report, null, 2));
  for (const [name, rows] of [['DEV', dev], ['VAL', val], ['FRESH_HOLDOUT', fresh]]) {
    const s = report[name].summary;
    console.log(`${name}: N=${s.n} WR=${(s.winRate * 100).toFixed(2)}% avgR=${s.avgR.toFixed(4)} PF=${s.PF?.toFixed(4) ?? 'n/a'} totalR=${s.totalR.toFixed(4)} maxDD=${s.maxDD.toFixed(4)} maxLossStreak=${s.maxConsecutiveLosses}`);
    console.log(`  classes=${JSON.stringify(s.outcomeClasses)} medMFE20=${s.path.medMFE20} medMAE20=${s.path.medMAE20}`);
    console.log(`  concentration=${JSON.stringify(report[name].concentration)}`);
  }
  console.log('DEV rolling:');
  for (const w of report.DEV.rolling) console.log(`  W${w.window}: N=${w.n} WR=${(w.winRate*100).toFixed(2)}% PF=${w.PF?.toFixed(4) ?? 'n/a'} avgR=${w.avgR.toFixed(4)} totalR=${w.totalR.toFixed(4)} maxDD=${w.maxDD.toFixed(4)}`);
  console.log('VAL rolling:');
  for (const w of report.VAL.rolling) console.log(`  W${w.window}: N=${w.n} WR=${(w.winRate*100).toFixed(2)}% PF=${w.PF?.toFixed(4) ?? 'n/a'} avgR=${w.avgR.toFixed(4)} totalR=${w.totalR.toFixed(4)} maxDD=${w.maxDD.toFixed(4)}`);
  console.log(`Report -> ${out}`);
}
await main();
