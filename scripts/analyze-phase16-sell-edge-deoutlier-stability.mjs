import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(process.cwd());
const PRE = 10000;
const DEV = 6000;
const CFG = {
  breakoutLookback: 5,
  followThrough: { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true },
  spike: { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 },
};
const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 },
  ],
  avoidWindows: [],
};
const WINDOWS = [
  { name: 'DEV_1', start: 0, end: 1999 },
  { name: 'DEV_2', start: 2000, end: 3999 },
  { name: 'DEV_3', start: 4000, end: 5999 },
  { name: 'VAL_1', start: 6000, end: 7999 },
  { name: 'VAL_2', start: 8000, end: 9999 },
];

const round = n => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
const pct = n => Number.isFinite(n) ? Number((n * 100).toFixed(4)) : null;
const stats = rows => {
  const r = rows.filter(x => Number.isFinite(x.r));
  const w = r.filter(x => x.r > 0);
  const l = r.filter(x => x.r <= 0);
  const gw = w.reduce((s, x) => s + x.r, 0);
  const gl = l.reduce((s, x) => s + Math.abs(x.r), 0);
  return { n: r.length, wins: w.length, losses: l.length, WR: r.length ? w.length / r.length : null, avgR: r.length ? r.reduce((s, x) => s + x.r, 0) / r.length : null, PF: gl ? gw / gl : null, totalR: r.reduce((s, x) => s + x.r, 0) };
};
const byR = rows => [...rows].sort((a, b) => b.r - a.r);
const withoutTop = (rows, k) => {
  const drop = new Set(byR(rows).slice(0, k).map(x => x.entryIndex));
  return rows.filter(x => !drop.has(x.entryIndex));
};
const concentration = (rows, k) => {
  const s = stats(rows);
  const topR = byR(rows).slice(0, k).reduce((a, x) => a + x.r, 0);
  return { sTotal: s.totalR, topR, topShare: s.totalR ? topR / s.totalR : null };
};
const bucketStats = (rows, key) => Object.fromEntries(
  [...new Set(rows.map(x => x[key]))].sort().map(k => [k, stats(rows.filter(x => x[key] === k))])
);
const session = ts => {
  const d = new Date(ts);
  const m = d.getUTCHours() * 60 + d.getUTCMinutes();
  if (m >= 420 && m < 960) return 'LONDON';
  if (m >= 960 && m < 1320) return 'NEW_YORK';
  return 'OUTSIDE';
};

function replay(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, CFG.breakoutLookback);
  const followThrough = detectFollowThrough(visible, breakouts, CFG.followThrough);
  const spikes = detectSpikeCandidates(visible, breakouts, followThrough, CFG.spike);
  const candidates = [];
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    const breakout = breakouts.find(x => x.index === spike.breakoutIndex && x.direction === spike.direction);
    const follow = followThrough.find(x => x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction);
    if (!breakout || !follow) continue;
    const projection = projectLeg2(visible, correction);
    if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map(x => x.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const sessionContext = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session: sessionContext });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    const targetIsDirectional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
    if (risk <= 0 || reward <= 0 || !targetIsDirectional) continue;
    candidates.push({ trigger, projection, invalidation });
  }
  return candidates[0] ?? null;
}

async function main() {
  const base = JSON.parse(await readFile(resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json'), 'utf8'));
  const candles = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8')).candles ?? [];
  if (!candles.length) throw new Error('PHASE16: historical 5min dataset is empty');

  const indexByTime = new Map();
  for (let i = 0; i < candles.length; i++) {
    const ts = candles[i]?.timestamp;
    if (!ts) throw new Error(`PHASE16: candle ${i} missing timestamp`);
    if (indexByTime.has(ts)) throw new Error(`PHASE16: duplicate candle timestamp ${ts}`);
    indexByTime.set(ts, i);
  }

  const raw = (base.trades ?? []).filter(t => Number.isInteger(Number(t.entryIndex)) && Number(t.entryIndex) < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL'));
  const rows = [];
  let mismatch = 0;
  let noReplay = 0;
  let missingCanonicalTimestamp = 0;

  for (const t of raw) {
    const canonicalIndex = indexByTime.get(t.entryTime);
    if (!Number.isInteger(canonicalIndex)) {
      missingCanonicalTimestamp++;
      continue;
    }
    const replayed = replay(candles, canonicalIndex);
    if (!replayed || replayed.trigger.timestamp !== t.entryTime || replayed.trigger.direction !== t.direction) {
      mismatch++;
      if (!replayed) noReplay++;
      continue;
    }
    const entryIndex = Number(t.entryIndex);
    rows.push({
      entryIndex,
      canonicalIndex,
      entryTime: t.entryTime,
      split: entryIndex < DEV ? 'DEV' : 'VAL',
      window: WINDOWS.find(w => entryIndex >= w.start && entryIndex <= w.end)?.name ?? 'UNKNOWN',
      direction: t.direction,
      session: session(t.entryTime),
      r: Number(t.rMultiple),
      exceptional: Number(t.rMultiple) >= 5,
    });
  }

  if (missingCanonicalTimestamp > 0 || mismatch > 0 || noReplay > 0) {
    throw new Error(`PHASE16: canonical replay integrity failed: mismatch=${mismatch} noReplay=${noReplay} missingCanonicalTimestamp=${missingCanonicalTimestamp}`);
  }

  const sell = rows.filter(x => x.direction === 'SELL');
  const sellNoEx = sell.filter(x => !x.exceptional);
  const london = sell.filter(x => x.session === 'LONDON');
  const ny = sell.filter(x => x.session === 'NEW_YORK');
  const londonNoEx = london.filter(x => !x.exceptional);
  const nyNoEx = ny.filter(x => !x.exceptional);
  const dev = sell.filter(x => x.split === 'DEV');
  const val = sell.filter(x => x.split === 'VAL');

  const windows = Object.fromEntries(WINDOWS.map(w => {
    const all = sell.filter(x => x.window === w.name);
    const noEx = all.filter(x => !x.exceptional);
    return [w.name, {
      outcome: stats(all),
      noExceptional: stats(noEx),
      top1Excluded: stats(withoutTop(all, 1)),
      top2Excluded: stats(withoutTop(all, 2)),
      top3Excluded: stats(withoutTop(all, 3)),
      concentration: { k1: concentration(all, 1), k2: concentration(all, 2), k3: concentration(all, 3) },
    }];
  }));

  const segments = {
    SELL: stats(sell),
    SELL_NO_EXCEPTIONAL: stats(sellNoEx),
    SELL_DEV: stats(dev),
    SELL_VAL: stats(val),
    SELL_LONDON: stats(london),
    SELL_LONDON_NO_EXCEPTIONAL: stats(londonNoEx),
    SELL_NEW_YORK: stats(ny),
    SELL_NEW_YORK_NO_EXCEPTIONAL: stats(nyNoEx),
  };

  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'PHASE_16_SELL_EDGE_DEOUTLIER_STABILITY',
    timeframe: '5min',
    scope: { rawBaselinePre: raw.length, canonicalReplayed: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    integrity: { expectedCanonical: raw.length, rawBaselinePre: raw.length, canonicalReplayed: rows.length, mismatch, noReplay, missingCanonicalTimestamp, canonicalTimestampReplay: true, canonicalPopulationMatch: rows.length === raw.length },
    methodology: {
      purpose: 'Descriptive stability audit of the existing SELL baseline edge across London/New York and fixed chronological windows, with exceptional-trade concentration removed diagnostically only.',
      population: 'Exact baseline candidate-selection semantics replayed on the refreshed dataset using canonical entryTime; baseline entryIndex is retained only for DEV/VAL split and chronological audit.',
      fixedWindows: WINDOWS,
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      noFreshHoldoutAccess: true,
      exceptionalDefinition: 'rMultiple >= 5R',
      tests: ['SELL vs SELL without exceptional', 'SELL DEV/VAL', 'SELL London/NY', 'fixed chronological window outcomes', 'top-1/top-2/top-3 exclusion diagnostics', 'window concentration'],
    },
    segments,
    windows,
    cases: sell,
  };

  const out = resolve(ROOT, 'data/reports/strategy-a-phase16-sell-edge-deoutlier-stability');
  await mkdir(out, { recursive: true });
  await writeFile(resolve(out, '5min.json'), JSON.stringify(result, null, 2));

  const fmt = s => `N=${s.n} avgR=${round(s.avgR)} PF=${round(s.PF)} WR=${pct(s.WR)}% totalR=${round(s.totalR)}`;
  console.log(`PHASE_16_SELL_EDGE_DEOUTLIER_STABILITY 5min N=${rows.length} SELL=${sell.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY expected=${raw.length} raw=${raw.length} actual=${rows.length} mismatch=${mismatch} noReplay=${noReplay} missingCanonicalTimestamp=${missingCanonicalTimestamp}`);
  console.log('=== SELL SEGMENTS ===');
  for (const [k, v] of Object.entries(segments)) console.log(`${k}: ${fmt(v)}`);
  console.log('=== FIXED CHRONOLOGICAL WINDOWS ===');
  for (const [k, v] of Object.entries(windows)) console.log(`${k}: ALL ${fmt(v.outcome)} | NO_EX ${fmt(v.noExceptional)} | -TOP1 ${fmt(v.top1Excluded)} | -TOP2 ${fmt(v.top2Excluded)} | -TOP3 ${fmt(v.top3Excluded)}`);
  console.log('=== WINDOW CONCENTRATION ===');
  for (const [k, v] of Object.entries(windows)) console.log(`${k}: K1 share=${round(v.concentration.k1.topShare)} K2 share=${round(v.concentration.k2.topShare)} K3 share=${round(v.concentration.k3.topShare)}`);
  console.log(`REPORT=${resolve(out, '5min.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}

main().catch(e => { console.error(e); process.exit(1); });
