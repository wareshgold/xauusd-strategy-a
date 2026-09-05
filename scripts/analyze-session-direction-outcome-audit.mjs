import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASELINE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-session-direction-outcome-audit');
const DEV_CANDLES = 6000;
const PRE_HOLDOUT_CANDLES = 10000;
const HORIZON = 20;
const SEGMENTS = ['LONDON BUY', 'LONDON SELL', 'NEW_YORK BUY', 'NEW_YORK SELL'];

function p(n) { return Number.isFinite(n) ? Number(n.toFixed(6)) : null; }
function finite(n) { return Number.isFinite(Number(n)); }
function session(entryTime) {
  const d = new Date(entryTime);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  return 'OUTSIDE';
}
function quantile(values, f = .5) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const pos = (a.length - 1) * f, lo = Math.floor(pos), hi = Math.ceil(pos);
  return a[lo] + (a[hi] - a[lo]) * (pos - lo);
}
function summarize(rows) {
  const rs = rows.map(r => r.r).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0), losses = rs.filter(r => r < 0);
  const gp = wins.reduce((s, r) => s + r, 0);
  const gl = -losses.reduce((s, r) => s + r, 0);
  let equity = 0, peak = 0, maxDD = 0;
  for (const r of rs) { equity += r; peak = Math.max(peak, equity); maxDD = Math.max(maxDD, peak - equity); }
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: p(rs.length ? wins.length / rs.length : 0),
    avgR: p(rs.length ? rs.reduce((s, r) => s + r, 0) / rs.length : 0),
    totalR: p(rs.reduce((s, r) => s + r, 0)),
    PF: gl ? p(gp / gl) : (gp ? null : 0),
    maxDD: p(maxDD),
  };
}
function path(rows, candles) {
  const mfe = [], mae = [];
  for (const r of rows) {
    const entry = Number(r.entry), stop = Number(r.stopLoss), idx = Number(r.entryIndex);
    const risk = Math.abs(entry - stop);
    if (!finite(entry) || !finite(stop) || !(risk > 0) || !Number.isInteger(idx)) continue;
    let bestFav = 0, bestAdv = 0;
    const end = Math.min(candles.length - 1, idx + HORIZON);
    for (let i = idx + 1; i <= end; i++) {
      const c = candles[i];
      const fav = r.direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
      const adv = r.direction === 'BUY' ? (entry - c.low) / risk : (c.high - entry) / risk;
      bestFav = Math.max(bestFav, fav);
      bestAdv = Math.max(bestAdv, adv);
    }
    mfe.push(Math.max(0, bestFav));
    mae.push(Math.max(0, bestAdv));
  }
  return { medianMFE: p(quantile(mfe)), medianMAE: p(quantile(mae)) };
}
function classify(trades, candles) {
  const valid = trades
    .filter(t => t.result !== 'AMBIGUOUS' && finite(t.rMultiple) && Number.isInteger(Number(t.entryIndex)))
    .map(t => ({ ...t, r: Number(t.rMultiple), entryIndex: Number(t.entryIndex), session: session(t.entryTime) }));
  const scopes = {
    DEV: valid.filter(t => t.entryIndex < DEV_CANDLES),
    VAL: valid.filter(t => t.entryIndex >= DEV_CANDLES && t.entryIndex < PRE_HOLDOUT_CANDLES),
    FRESH_HOLDOUT: valid.filter(t => t.entryIndex >= PRE_HOLDOUT_CANDLES),
  };
  const report = {};
  for (const [scope, rows] of Object.entries(scopes)) {
    report[scope] = {};
    for (const segment of SEGMENTS) {
      const [sess, direction] = segment.split(' ');
      const group = rows.filter(r => r.session === sess && r.direction === direction);
      report[scope][segment] = { metrics: summarize(group), path20: path(group, candles), cases: group.map(r => ({ entryTime: r.entryTime, entryIndex: r.entryIndex, direction: r.direction, session: r.session, r: r.r })) };
    }
  }
  return { valid, report };
}

async function main() {
  const baseline = JSON.parse(await readFile(BASELINE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles;
  const { valid, report } = classify(baseline.trades ?? [], candles);
  const outside = valid.filter(t => t.session === 'OUTSIDE');
  const out = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_SESSION_DIRECTION_OUTCOME_AUDIT_V1',
    timeframe: '5m',
    scope: { canonicalResolvedTrades: valid.length, DEV: report.DEV, VAL: report.VAL, FRESH_HOLDOUT: report.FRESH_HOLDOUT, outsideExcludedFromSegments: outside.length },
    methodology: {
      segments: SEGMENTS,
      sessionSource: 'UTC entryTime; LONDON 07:00-16:00, NEW_YORK 16:00-22:00, OUTSIDE otherwise.',
      outcome: 'Baseline realized rMultiple; AMBIGUOUS excluded.',
      maxDD: 'Sequential realized-R drawdown within each chronological segment subset.',
      path20: 'Median maximum favorable/adverse excursion over the first 20 candles after entry, normalized by trade risk.',
      freshHoldout: 'Shown descriptively only; not used for hypothesis selection or rule tuning.',
      noOptimization: true,
      noThresholdSearch: true,
      noProductionChange: true,
      outsideTrading: 'OUTSIDE is intentionally absent from the four strategy segments and is not a candidate trading window.'
    },
    report,
    interpretationGuard: 'This is descriptive only. Do not promote a session/direction filter from this report alone. A candidate must show coherent DEV/VAL behavior and then pass a frozen fresh-holdout validation before any rule change.'
  };
  await mkdir(OUT_DIR, { recursive: true });
  const outPath = resolve(OUT_DIR, '5min.json');
  await writeFile(outPath, JSON.stringify(out, null, 2));
  for (const scope of ['DEV', 'VAL', 'FRESH_HOLDOUT']) {
    console.log(`${scope}:`);
    for (const segment of SEGMENTS) {
      const s = report[scope][segment];
      console.log(`  ${segment}: N=${s.metrics.n} WR=${(s.metrics.winRate * 100).toFixed(2)}% avgR=${s.metrics.avgR.toFixed(4)} PF=${s.metrics.PF?.toFixed(4) ?? 'n/a'} totalR=${s.metrics.totalR.toFixed(4)} maxDD=${s.metrics.maxDD.toFixed(4)} medMFE20=${s.path20.medianMFE ?? 'n/a'} medMAE20=${s.path20.medianMAE ?? 'n/a'}`);
    }
  }
  console.log(`OUTSIDE resolved trades (excluded from four segments): ${outside.length}`);
  console.log(`Report -> ${outPath}`);
}
await main();
