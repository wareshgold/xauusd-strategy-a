import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASELINE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-global-post-entry-path-association');
const DEV_CANDLES = 6000;
const PRE_HOLDOUT_CANDLES = 10000;
const HORIZONS = [1, 2, 3, 5, 10, 20];

function p(n) { return Number.isFinite(n) ? Number(n.toFixed(6)) : null; }
function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0, p25: null, median: null, p75: null, mean: null };
  const q = f => { const pos = (a.length - 1) * f, lo = Math.floor(pos), hi = Math.ceil(pos); return p(a[lo] + (a[hi] - a[lo]) * (pos - lo)); };
  return { n: a.length, p25: q(.25), median: q(.5), p75: q(.75), mean: p(a.reduce((s, x) => s + x, 0) / a.length) };
}
function metrics(rows) {
  const rs = rows.map(x => x.r).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((s, x) => s + x, 0), gl = -losses.reduce((s, x) => s + x, 0);
  return { n: rs.length, wins: wins.length, losses: losses.length, winRate: p(rs.length ? wins.length / rs.length : 0), avgR: p(rs.length ? rs.reduce((s, x) => s + x, 0) / rs.length : 0), totalR: p(rs.reduce((s, x) => s + x, 0)), PF: gl ? p(gp / gl) : null };
}
function pearson(xs, ys) {
  const pairs = xs.map((x, i) => [x, ys[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 3) return null;
  const mx = pairs.reduce((s, [x]) => s + x, 0) / pairs.length, my = pairs.reduce((s, [, y]) => s + y, 0) / pairs.length;
  let num = 0, dx = 0, dy = 0;
  for (const [x, y] of pairs) { const a = x - mx, b = y - my; num += a * b; dx += a * a; dy += b * b; }
  return dx && dy ? p(num / Math.sqrt(dx * dy)) : null;
}
function rank(values) {
  const indexed = values.map((v, i) => ({ v, i })).filter(x => Number.isFinite(x.v)).sort((a, b) => a.v - b.v);
  const out = Array(values.length).fill(NaN);
  let i = 0;
  while (i < indexed.length) { let j = i + 1; while (j < indexed.length && indexed[j].v === indexed[i].v) j++; const r = (i + j - 1) / 2 + 1; for (let k = i; k < j; k++) out[indexed[k].i] = r; i = j; }
  return out;
}
function spearman(xs, ys) { return pearson(rank(xs), rank(ys)); }

function enrich(candles, trade) {
  const entryIndex = Number(trade.entryIndex), entry = Number(trade.entry), stop = Number(trade.stopLoss);
  const risk = Math.abs(entry - stop);
  if (!Number.isInteger(entryIndex) || !(risk > 0)) return null;
  const path = {};
  for (const h of HORIZONS) {
    const end = Math.min(candles.length - 1, entryIndex + h);
    let mfe = 0, mae = 0;
    for (let i = entryIndex + 1; i <= end; i++) {
      const c = candles[i];
      const fav = trade.direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
      const adv = trade.direction === 'BUY' ? (entry - c.low) / risk : (c.high - entry) / risk;
      mfe = Math.max(mfe, fav); mae = Math.max(mae, adv);
    }
    path[h] = { mfe: Math.max(0, mfe), mae: Math.max(0, mae) };
  }
  const c = candles[entryIndex + 1];
  if (!c) return null;
  const firstFav = trade.direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
  const firstAdv = trade.direction === 'BUY' ? (entry - c.low) / risk : (c.high - entry) / risk;
  const firstClose = trade.direction === 'BUY' ? (c.close - entry) / risk : (entry - c.close) / risk;
  const firstRange = (c.high - c.low) / risk;
  const firstBody = Math.abs(c.close - c.open) / risk;
  const bothOneR = firstFav >= 1 && firstAdv >= 1;
  return { entryIndex, entryTime: trade.entryTime, direction: trade.direction, session: trade.session ?? null, r: Number(trade.rMultiple), firstFav: Math.max(0, firstFav), firstAdv: Math.max(0, firstAdv), firstClose, firstRange, firstBody, favorableDominant: firstFav > firstAdv, adverseDominant: firstAdv > firstFav, oneRConflict: bothOneR, path };
}
function stateSummary(rows) {
  const states = { FAVORABLE_DOMINANT: rows.filter(x => x.favorableDominant), ADVERSE_DOMINANT: rows.filter(x => x.adverseDominant), TIE: rows.filter(x => !x.favorableDominant && !x.adverseDominant) };
  return Object.fromEntries(Object.entries(states).map(([k, v]) => [k, { ...metrics(v), share: p(rows.length ? v.length / rows.length : 0) }]));
}
function continuousAssociation(rows) {
  const y = rows.map(x => x.r);
  return {
    firstFavVsOutcomeR: { pearson: pearson(rows.map(x => x.firstFav), y), spearman: spearman(rows.map(x => x.firstFav), y) },
    firstAdvVsOutcomeR: { pearson: pearson(rows.map(x => x.firstAdv), y), spearman: spearman(rows.map(x => x.firstAdv), y) },
    firstCloseVsOutcomeR: { pearson: pearson(rows.map(x => x.firstClose), y), spearman: spearman(rows.map(x => x.firstClose), y) },
    firstRangeVsOutcomeR: { pearson: pearson(rows.map(x => x.firstRange), y), spearman: spearman(rows.map(x => x.firstRange), y) },
    firstBodyVsOutcomeR: { pearson: pearson(rows.map(x => x.firstBody), y), spearman: spearman(rows.map(x => x.firstBody), y) },
    favorableMinusAdverseVsOutcomeR: { pearson: pearson(rows.map(x => x.firstFav - x.firstAdv), y), spearman: spearman(rows.map(x => x.firstFav - x.firstAdv), y) },
  };
}
function pathSummary(rows) {
  return Object.fromEntries(HORIZONS.map(h => [h, { MFE: quantiles(rows.map(x => x.path[h].mfe)), MAE: quantiles(rows.map(x => x.path[h].mae)) }]));
}
function outcomeClasses(rows) {
  return {
    winners: { ...metrics(rows.filter(x => x.r > 0)), firstFav: quantiles(rows.filter(x => x.r > 0).map(x => x.firstFav)), firstAdv: quantiles(rows.filter(x => x.r > 0).map(x => x.firstAdv)), firstClose: quantiles(rows.filter(x => x.r > 0).map(x => x.firstClose)) },
    losers: { ...metrics(rows.filter(x => x.r < 0)), firstFav: quantiles(rows.filter(x => x.r < 0).map(x => x.firstFav)), firstAdv: quantiles(rows.filter(x => x.r < 0).map(x => x.firstAdv)), firstClose: quantiles(rows.filter(x => x.r < 0).map(x => x.firstClose)) },
  };
}

async function main() {
  const baseline = JSON.parse(await readFile(BASELINE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles;
  const trades = (baseline.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)));
  const rows = trades.map(t => enrich(candles, t)).filter(Boolean).filter(x => x.entryIndex < PRE_HOLDOUT_CANDLES);
  const dev = rows.filter(x => x.entryIndex < DEV_CANDLES);
  const val = rows.filter(x => x.entryIndex >= DEV_CANDLES && x.entryIndex < PRE_HOLDOUT_CANDLES);
  const make = group => ({ counts: { n: group.length, DEV: group.filter(x => x.entryIndex < DEV_CANDLES).length, VAL: group.filter(x => x.entryIndex >= DEV_CANDLES).length }, baseline: metrics(group), firstBarState: stateSummary(group), continuousAssociation: continuousAssociation(group), outcomeClasses: outcomeClasses(group), pathByHorizon: pathSummary(group), firstBarDistributions: { favorableR: quantiles(group.map(x => x.firstFav)), adverseR: quantiles(group.map(x => x.firstAdv)), closeR: quantiles(group.map(x => x.firstClose)), rangeR: quantiles(group.map(x => x.firstRange)), bodyR: quantiles(group.map(x => x.firstBody)), favorableMinusAdverseR: quantiles(group.map(x => x.firstFav - x.firstAdv)) }, oneRConflictRate: p(group.length ? group.filter(x => x.oneRConflict).length / group.length : 0) });
  const report = {
    strategy: 'Strategy A / SP2L', mode: 'GLOBAL_POST_ENTRY_PATH_ASSOCIATION', timeframe: '5m',
    scope: { baselineTrades: trades.length, joined: rows.length, devCandles: DEV_CANDLES, preHoldoutCandles: PRE_HOLDOUT_CANDLES, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: { purpose: 'Test whether the first post-entry candle and early path contain outcome information across the full baseline candidate universe.', source: 'Canonical baseline trades only; AMBIGUOUS excluded. No new entry/exit/management rule is applied.', firstBar: 'Favorable/adverse excursion, close displacement, range and body are normalized by trade risk. Dominance is descriptive: favorable excursion > adverse excursion or vice versa; exact ties are TIE.', association: 'Continuous Pearson and Spearman correlations are reported against realized outcome R; these are descriptive association measures, not predictive claims.', horizons: HORIZONS, noOptimization: true, noThresholdSearch: true, noNewTradingRules: true, holdoutLocked: true, interpretationGuard: 'A relationship is research-worthy only if direction and magnitude remain coherent from DEV to VAL. Fresh holdout remains excluded until a hypothesis is frozen.' },
    DEV: make(dev), VAL: make(val), ALL_PRE_HOLDOUT: make(rows),
    cases: rows.map(x => ({ entryIndex: x.entryIndex, entryTime: x.entryTime, direction: x.direction, session: x.session, r: x.r, firstFavR: p(x.firstFav), firstAdvR: p(x.firstAdv), firstCloseR: p(x.firstClose), firstRangeR: p(x.firstRange), firstBodyR: p(x.firstBody), favorableDominant: x.favorableDominant, adverseDominant: x.adverseDominant, oneRConflict: x.oneRConflict }))
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, '5min.json');
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`5m GLOBAL POST-ENTRY ASSOCIATION: joined=${rows.length} DEV=${dev.length} VAL=${val.length}`);
  for (const [name, group] of [['DEV', dev], ['VAL', val]]) {
    const s = report[name];
    console.log(`${name}: baseline WR=${(s.baseline.winRate * 100).toFixed(2)}% avgR=${s.baseline.avgR.toFixed(4)} PF=${s.baseline.PF?.toFixed(4) ?? 'n/a'}`);
    console.log(`  firstFav median=${s.firstBarDistributions.favorableR.median} firstAdv median=${s.firstBarDistributions.adverseR.median} firstClose median=${s.firstBarDistributions.closeR.median}`);
    console.log(`  state WR: FAV=${(s.firstBarState.FAVORABLE_DOMINANT.winRate * 100).toFixed(2)}% (N=${s.firstBarState.FAVORABLE_DOMINANT.n}) | ADV=${(s.firstBarState.ADVERSE_DOMINANT.winRate * 100).toFixed(2)}% (N=${s.firstBarState.ADVERSE_DOMINANT.n}) | TIE=${(s.firstBarState.TIE.winRate * 100).toFixed(2)}% (N=${s.firstBarState.TIE.n})`);
    console.log(`  corr Spearman: fav=${s.continuousAssociation.firstFavVsOutcomeR.spearman} adv=${s.continuousAssociation.firstAdvVsOutcomeR.spearman} close=${s.continuousAssociation.firstCloseVsOutcomeR.spearman} fav-adv=${s.continuousAssociation.favorableMinusAdverseVsOutcomeR.spearman}`);
    console.log(`  winners firstFav=${s.outcomeClasses.winners.firstFav.median} firstAdv=${s.outcomeClasses.winners.firstAdv.median} | losers firstFav=${s.outcomeClasses.losers.firstFav.median} firstAdv=${s.outcomeClasses.losers.firstAdv.median}`);
  }
  console.log(`Report -> ${out}`);
}
await main();
