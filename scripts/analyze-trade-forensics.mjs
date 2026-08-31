import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const ROOT = process.cwd();
const configs = {
  '1min': { breakoutLookback: 5, ftMaxBars: 2, spikeMaxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 },
  '5min': { breakoutLookback: 5, ftMaxBars: 2, spikeMaxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 },
};

async function loadModule(file) {
  return import(pathToFileURL(path.resolve(ROOT, file)).href);
}

const [{ detectBreakout }, { detectFollowThrough }, { detectSpikeCandidates }, { detectFirstCorrection }, { detectEntryTrigger }, { getInvalidationRule }, { projectLeg2 }, { buildEMAContext, buildLocationContext, buildSessionContext }, { scoreSetup }] = await Promise.all([
  loadModule('src/domain/market/BreakoutDetector.ts'),
  loadModule('src/domain/market/FollowThroughDetector.ts'),
  loadModule('src/domain/strategy-a/SpikeDetector.ts'),
  loadModule('src/domain/strategy-a/CorrectionDetector.ts'),
  loadModule('src/domain/strategy-a/EntryTrigger.ts'),
  loadModule('src/domain/strategy-a/Invalidation.ts'),
  loadModule('src/domain/strategy-a/LegProjection.ts'),
  loadModule('src/domain/strategy-a/Context.ts'),
  loadModule('src/domain/strategy-a/QualityScore.ts'),
]);

const CONTEXT = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [
  { name: 'LONDON', startMinutes: 7 * 60, endMinutes: 16 * 60 },
  { name: 'NEW_YORK', startMinutes: 13 * 60, endMinutes: 22 * 60 },
], avoidWindows: [] };

function findSetup(candles, index, cfg) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < Math.max(cfg.breakoutLookback + 2, CONTEXT.emaPeriod)) return null;
  const breakouts = detectBreakout(visible, cfg.breakoutLookback);
  const followThrough = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: cfg.ftMaxBars, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, followThrough, { maxCandles: cfg.spikeMaxCandles, minDirectionalFraction: cfg.minDirectionalFraction, maxOverlapFraction: cfg.maxOverlapFraction });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    const projection = projectLeg2(visible, correction);
    if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map(c => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const sessionContext = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session: sessionContext });
    if (!quality.tradeAllowed) continue;
    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (!(risk > 0 && reward > 0)) continue;
    return { spike, correction, trigger, projection, invalidation, quality, risk, reward, targetR: reward / risk };
  }
  return null;
}

function evaluate(trade, candles) {
  let result = 'OPEN', exitIndex = null;
  let mfe = 0, mae = 0;
  for (let i = trade.entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const favorable = trade.direction === 'BUY' ? c.high - trade.entry : trade.entry - c.low;
    const adverse = trade.direction === 'BUY' ? trade.entry - c.low : c.high - trade.entry;
    mfe = Math.max(mfe, favorable / trade.riskDistance);
    mae = Math.max(mae, Math.max(0, adverse) / trade.riskDistance);
    const sl = trade.direction === 'BUY' ? c.low <= trade.stopLoss : c.high >= trade.stopLoss;
    const tp = trade.direction === 'BUY' ? c.high >= trade.tp1 : c.low <= trade.tp1;
    if (sl && tp) { result = 'AMBIGUOUS'; exitIndex = i; break; }
    if (sl) { result = 'SL'; exitIndex = i; break; }
    if (tp) { result = 'TP1'; exitIndex = i; break; }
  }
  return { result, exitIndex, mfeR: mfe, maeR: mae, barsToExit: exitIndex === null ? null : exitIndex - trade.entryIndex };
}

function session(timestamp) {
  const h = Number(String(timestamp).slice(11, 13));
  return h >= 7 && h < 13 ? 'LONDON_ONLY' : h >= 13 && h < 16 ? 'OVERLAP' : h >= 16 && h < 22 ? 'NEW_YORK_ONLY' : 'OUTSIDE';
}

for (const timeframe of ['1min', '5min']) {
  const data = JSON.parse(await fs.readFile(path.resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8'));
  const baseline = JSON.parse(await fs.readFile(path.resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`), 'utf8'));
  const candles = data.candles;
  const rows = [];
  for (const trade of baseline.trades.filter(t => Number.isFinite(t.rMultiple))) {
    const setup = findSetup(candles, trade.entryIndex, configs[timeframe]);
    const outcome = evaluate(trade, candles);
    rows.push({
      entryIndex: trade.entryIndex, entryTime: trade.entryTime, direction: trade.direction, session: session(trade.entryTime),
      entry: trade.entry, stopLoss: trade.stopLoss, tp1: trade.tp1, riskDistance: trade.riskDistance, rMultiple: trade.rMultiple,
      result: trade.result, mfeR: outcome.mfeR, maeR: outcome.maeR, barsToExit: outcome.barsToExit,
      setupFound: Boolean(setup),
      ...(setup ? {
        spikeStartIndex: setup.spike.startIndex, spikeEndIndex: setup.spike.endIndex, spikeSize: setup.spike.size,
        spikeStructureScore: setup.spike.structureScore, spikeOverlapScore: setup.spike.overlapScore, spikeHasPGAPEvidence: setup.spike.hasPGAPEvidence,
        correctionStartIndex: setup.correction.correctionStartIndex, correctionExtremeIndex: setup.correction.correctionExtremeIndex,
        correctionSize: Math.abs(setup.correction.extremePrice - setup.spike.endPrice),
        leg1Size: setup.projection.leg1Size, leg1StartIndex: setup.projection.leg1StartIndex, leg1EndIndex: setup.projection.leg1EndIndex,
        projectionFrom: setup.projection.projectionFrom, targetR: setup.targetR,
        leg2ToLeg1Ratio: setup.correction.extremePrice === setup.projection.projectionFrom ? null : Math.abs((setup.projection.tp1 - setup.projection.projectionFrom) / setup.projection.leg1Size),
        qualityScore: setup.quality.score,
      } : {})
    });
  }
  const topWinners = [...rows].sort((a,b)=>b.rMultiple-a.rMultiple).slice(0,20);
  const tinyRisk = rows.filter(r => r.riskDistance <= percentile(rows.map(x=>x.riskDistance), .05));
  const report = { timeframe, trades: rows.length, summary: { winnersOver5R: rows.filter(r=>r.rMultiple>5).length, winnersOver10R: rows.filter(r=>r.rMultiple>10).length, tinyRiskCount: tinyRisk.length }, topWinners, tinyRisk, trades: rows };
  const out = path.resolve(ROOT, `data/reports/strategy-a-trade-forensics/${timeframe}.json`);
  await fs.mkdir(path.dirname(out), { recursive: true });
  await fs.writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: trades=${rows.length} setupFound=${rows.filter(r=>r.setupFound).length} >5R=${report.summary.winnersOver5R} >10R=${report.summary.winnersOver10R} tinyRisk=${tinyRisk.length}`);
  console.log(`Report -> ${out}`);
}

function percentile(values, p) {
  if (!values.length) return 0;
  const a=[...values].sort((x,y)=>x-y), i=(a.length-1)*p, lo=Math.floor(i), hi=Math.ceil(i);
  return lo===hi?a[lo]:a[lo]+(a[hi]-a[lo])*(i-lo);
}
