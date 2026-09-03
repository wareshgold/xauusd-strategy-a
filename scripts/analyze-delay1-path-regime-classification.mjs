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
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-path-regime-classification');
const PRE = 10000, DEV = 6000, BLOCK = 2000;
const BREAKOUT_LOOKBACK = 5, FT_MAX_BARS = 2, SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5, SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const HORIZONS = [1, 3, 5, 10, 20];
const THRESHOLDS = [0.5, 1, 2];
const CONTEXT = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };

const key = c => `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const pf = rs => { const w = rs.filter(x => x > 0), l = rs.filter(x => x < 0), gl = -l.reduce((a, b) => a + b, 0); return gl ? w.reduce((a, b) => a + b, 0) / gl : null; };

function build(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod)) return [];
  const bo = detectBreakout(v, BREAKOUT_LOOKBACK);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
  const out = [];
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(v, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(v, correction);
    if (!trigger || trigger.index !== index) continue;
    const projection = projectLeg2(v, correction);
    if (!projection) continue;
    const inv = getInvalidationRule(correction);
    const ema = buildEMAContext(v.map(c => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - inv.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0 && (trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice))) continue;
    out.push({ entryIndex: index, entryTime: trigger.timestamp, direction: trigger.direction, entry: trigger.entryPrice, stopLoss: inv.invalidationLevel, tp1: projection.tp1 });
  }
  return out;
}

function firstTouch(candles, r, threshold, horizon) {
  const risk = Math.abs(r.entry - r.stopLoss);
  if (!(risk > 0)) return { event: 'NONE', bars: null };
  const end = Math.min(candles.length - 1, r.entryIndex + horizon);
  for (let i = r.entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const favorable = r.direction === 'BUY' ? c.high >= r.entry + threshold * risk : c.low <= r.entry - threshold * risk;
    const adverse = r.direction === 'BUY' ? c.low <= r.entry - threshold * risk : c.high >= r.entry + threshold * risk;
    if (favorable && adverse) return { event: 'SAME_BAR', bars: i - r.entryIndex };
    if (favorable) return { event: 'FAVORABLE_FIRST', bars: i - r.entryIndex };
    if (adverse) return { event: 'ADVERSE_FIRST', bars: i - r.entryIndex };
  }
  return { event: 'NONE', bars: null };
}

function classify(candles, r) {
  const f = firstTouch(candles, r, 1, 20);
  if (f.event === 'FAVORABLE_FIRST') return 'CLEAN';
  if (f.event === 'ADVERSE_FIRST') return 'HOSTILE';
  if (f.event === 'SAME_BAR') return 'SAME_BAR_AMBIGUOUS';
  return 'DEAD';
}

function rowStats(rows, candles) {
  const rs = rows.map(r => r.r).filter(Number.isFinite);
  const classes = { CLEAN: 0, HOSTILE: 0, DEAD: 0, SAME_BAR_AMBIGUOUS: 0 };
  for (const r of rows) classes[r.regime]++;
  const out = { n: rows.length, avgR: mean(rs), PF: pf(rs), winRate: rs.length ? rs.filter(x => x > 0).length / rs.length : null, regimeRates: {} };
  for (const [k, v] of Object.entries(classes)) out.regimeRates[k] = rows.length ? v / rows.length : 0;
  out.cleanHostileNonAmbiguous = classes.CLEAN + classes.HOSTILE ? { clean: classes.CLEAN / (classes.CLEAN + classes.HOSTILE), hostile: classes.HOSTILE / (classes.CLEAN + classes.HOSTILE) } : null;
  out.timeTo = {};
  for (const h of HORIZONS) {
    const f = rows.map(r => firstTouch(candles, r, 1, h)).filter(x => x.event === 'FAVORABLE_FIRST').map(x => x.bars);
    const a = rows.map(r => firstTouch(candles, r, 1, h)).filter(x => x.event === 'ADVERSE_FIRST').map(x => x.bars);
    out.timeTo[`h${h}`] = { favorableFirstMedianBars: median(f), adverseFirstMedianBars: median(a), favorableFirstN: f.length, adverseFirstN: a.length };
  }
  out.thresholdOrdering = {};
  for (const th of THRESHOLDS) {
    out.thresholdOrdering[`pm${th}R`] = {};
    for (const h of HORIZONS) {
      const c = { FAVORABLE_FIRST: 0, ADVERSE_FIRST: 0, SAME_BAR: 0, NONE: 0 };
      for (const r of rows) c[firstTouch(candles, r, th, h).event]++;
      out.thresholdOrdering[`pm${th}R`][`h${h}`] = { n: rows.length, favorableFirst: rows.length ? c.FAVORABLE_FIRST / rows.length : 0, adverseFirst: rows.length ? c.ADVERSE_FIRST / rows.length : 0, sameBar: rows.length ? c.SAME_BAR / rows.length : 0, none: rows.length ? c.NONE / rows.length : 0 };
    }
  }
  return out;
}

async function run(tf) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')).candles ?? [];
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${tf}.json`), 'utf8'));
  if (candles.length < PRE) throw new Error(`${tf}: expected at least ${PRE} candles`);
  const cutoff = new Date(candles[PRE].timestamp), devCut = new Date(candles[DEV].timestamp);
  const canonical = new Map((base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff).map(t => [key({ entryIndex: t.entryIndex, direction: t.direction, entry: t.entry, stopLoss: t.stopLoss, tp1: t.tp1 }), t]));
  const rows = [];
  for (let i = 0; i < PRE; i++) {
    const cs = build(candles, i); if (!cs.length) continue;
    const c = cs[0], t = canonical.get(key(c)); if (!t) continue;
    if (c.entryIndex - c.entryIndex + (c.entryIndex - c.entryIndex) !== 0) continue;
    // Delay=1: trigger is exactly one candle after correction extreme.
    const probe = c;
    const correctionExtremeIndex = probe.entryIndex - 1;
    // The canonical build above does not retain correction, so reconstruct the condition through the source candidate chain.
    const v = candles.slice(0, i + 1);
    const bo = detectBreakout(v, BREAKOUT_LOOKBACK);
    const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
    const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
    const match = sp.candidates.find(s => { const cor = detectFirstCorrection(v, s); return cor && cor.correctionExtremeIndex === i - 1 && detectEntryTrigger(v, cor)?.index === i; });
    if (!match) continue;
    const row = { entryIndex: i, entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, entry: Number(t.entry), stopLoss: Number(t.stopLoss), tp1: Number(t.tp1) };
    row.regime = classify(candles, row);
    rows.push(row);
  }
  const dev = rows.filter(r => r.entryIndex < DEV), val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const windows = [];
  for (let start = 0; start < PRE; start += BLOCK) {
    const end = Math.min(PRE, start + BLOCK), label = start < DEV ? `DEV_${String(start / BLOCK + 1).padStart(2, '0')}` : `VAL_${String((start - DEV) / BLOCK + 1).padStart(2, '0')}`;
    const rs = rows.filter(r => r.entryIndex >= start && r.entryIndex < end);
    windows.push({ label, candleStart: start, candleEndExclusive: end, startTime: candles[start]?.timestamp ?? null, endTime: candles[end - 1]?.timestamp ?? null, stats: rowStats(rs, candles) });
  }
  const report = { strategy: 'Strategy A', mode: 'DELAY1_PATH_REGIME_CLASSIFICATION', timeframe: tf, scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, blockCandles: BLOCK, delayExactly: 1, freshHoldoutExcluded: true }, methodology: { classification: 'CLEAN = +1R first within H20; HOSTILE = -1R first within H20; DEAD = neither; SAME_BAR_AMBIGUOUS = both thresholds touched in same OHLC bar.', timeTo: 'Median bars to first +1R/-1R for horizons H1/H3/H5/H10/H20.', thresholdOrdering: 'First-touch ordering for ±0.5R/±1R/±2R at H1/H3/H5/H10/H20.', noOptimization: true, productionUntouched: true }, overall: { DEV: rowStats(dev, candles), VAL: rowStats(val, candles), joined: rows.length }, windows, decision: 'Diagnostic only; no production rule, stop, delay filter, or fresh-holdout decision is authorized.' };
  await mkdir(OUT_DIR, { recursive: true }); await writeFile(resolve(OUT_DIR, `${tf}.json`), JSON.stringify(report, null, 2));
  console.log(`\n=== ${tf} DELAY1 PATH REGIME CLASSIFICATION ===`);
  console.log(`Overall DEV n=${report.overall.DEV.n} AvgR=${report.overall.DEV.avgR?.toFixed(3)} PF=${report.overall.DEV.PF?.toFixed(2) ?? 'n/a'} | VAL n=${report.overall.VAL.n} AvgR=${report.overall.VAL.avgR?.toFixed(3)} PF=${report.overall.VAL.PF?.toFixed(2) ?? 'n/a'}`);
  for (const w of windows) { const s = w.stats, rr = s.regimeRates; console.log(`${w.label} n=${s.n} AvgR=${s.avgR?.toFixed(3)} PF=${s.PF?.toFixed(2) ?? 'n/a'} CLEAN/HOSTILE/DEAD/SAME=${(rr.CLEAN*100).toFixed(1)}/${(rr.HOSTILE*100).toFixed(1)}/${(rr.DEAD*100).toFixed(1)}/${(rr.SAME_BAR_AMBIGUOUS*100).toFixed(1)}%`); console.log(`  +1R first median bars H1/H3/H5/H10/H20=${HORIZONS.map(h => s.timeTo[`h${h}`].favorableFirstMedianBars ?? 'n/a').join('/')}`); console.log(`  -1R first median bars H1/H3/H5/H10/H20=${HORIZONS.map(h => s.timeTo[`h${h}`].adverseFirstMedianBars ?? 'n/a').join('/')}`); }
  console.log(`Report -> ${resolve(OUT_DIR, `${tf}.json`)}`);
}
for (const tf of ['1min', '5min']) await run(tf);
