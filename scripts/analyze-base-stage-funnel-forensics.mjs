import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-base-stage-funnel-forensics');
const BREAKOUT_LOOKBACK = 5;
const FT_MAX_BARS = 2;
const SPIKE_MAX_CANDLES = 8;
const SPIKE_MIN_DIRECTIONAL_FRACTION = 0.5;
const SPIKE_MAX_OVERLAP_FRACTION = 0.8;
const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 7 * 60, endMinutes: 16 * 60 },
    { name: 'NEW_YORK', startMinutes: 13 * 60, endMinutes: 22 * 60 },
  ],
  avoidWindows: [],
};

async function imports() {
  return Promise.all([
    import('../src/domain/market/BreakoutDetector.ts'),
    import('../src/domain/market/FollowThroughDetector.ts'),
    import('../src/domain/strategy-a/SpikeDetector.ts'),
    import('../src/domain/strategy-a/CorrectionDetector.ts'),
    import('../src/domain/strategy-a/EntryTrigger.ts'),
    import('../src/domain/strategy-a/Invalidation.ts'),
    import('../src/domain/strategy-a/LegProjection.ts'),
    import('../src/domain/strategy-a/Context.ts'),
    import('../src/domain/strategy-a/QualityScore.ts'),
  ]);
}

function finite(x) { return Number.isFinite(Number(x)); }
function emptyStage() { return { seen: 0, passed: 0, rejected: 0 }; }
function bump(stage, pass) { stage.seen += 1; if (pass) stage.passed += 1; else stage.rejected += 1; }
function groupCount(rows, key) {
  const out = {};
  for (const r of rows) { const v = r[key] ?? 'UNKNOWN'; out[v] = (out[v] ?? 0) + 1; }
  return out;
}
function outcome(candles, c) {
  const risk = Math.abs(c.entry - c.stopLoss);
  for (let i = c.entryIndex + 1; i < candles.length; i += 1) {
    const x = candles[i];
    const sl = c.direction === 'BUY' ? x.low <= c.stopLoss : x.high >= c.stopLoss;
    const tp = c.direction === 'BUY' ? x.high >= c.tp1 : x.low <= c.tp1;
    if (sl && tp) return 'AMBIGUOUS';
    if (sl) return 'SL';
    if (tp) return 'TP1';
  }
  return 'OPEN';
}

async function run(tf, api) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles;
  const [Breakout, FT, Spike, Correction, Trigger, Invalidation, Projection, Context, Quality] = api;
  const stages = {
    sufficientHistory: emptyStage(), breakout: emptyStage(), followThrough: emptyStage(), spike: emptyStage(),
    correction: emptyStage(), trigger: emptyStage(), projection: emptyStage(), invalidation: emptyStage(),
    context: emptyStage(), quality: emptyStage(), riskReward: emptyStage(), finalCandidate: emptyStage(),
  };
  const finals = [];
  let replayEvents = 0;

  for (let index = 0; index < candles.length; index += 1) {
    replayEvents += 1;
    const visible = candles.slice(0, index + 1);
    const enough = visible.length >= Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod);
    bump(stages.sufficientHistory, enough);
    if (!enough) continue;

    const breakouts = Breakout.detectBreakout(visible, BREAKOUT_LOOKBACK);
    const breakout = breakouts.at(-1);
    bump(stages.breakout, !!breakout);
    if (!breakout || breakout.index >= index) continue;

    const follow = FT.detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: FT_MAX_BARS, requireCloseBeyondBrokenLevel: true });
    const ft = follow.find(e => e.breakoutIndex === breakout.index);
    bump(stages.followThrough, !!ft);
    if (!ft) continue;

    const spikes = Spike.detectSpikeCandidates(visible, breakouts, follow, { maxCandles: SPIKE_MAX_CANDLES, minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION, maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION });
    const spike = spikes.candidates.find(s => s.breakoutIndex === breakout.index && s.endIndex < index);
    bump(stages.spike, !!spike);
    if (!spike) continue;

    const correction = Correction.detectFirstCorrection(visible, spike);
    const validCorrection = !!correction && correction.correctionExtremeIndex < index;
    bump(stages.correction, validCorrection);
    if (!validCorrection) continue;

    const trigger = Trigger.detectEntryTrigger(visible, correction);
    const validTrigger = !!trigger && trigger.index === index;
    bump(stages.trigger, validTrigger);
    if (!validTrigger) continue;

    const projection = Projection.projectLeg2(visible, correction);
    bump(stages.projection, !!projection);
    if (!projection) continue;

    const invalidation = Invalidation.getInvalidationRule(correction);
    bump(stages.invalidation, !!invalidation);
    if (!invalidation) continue;

    const ema = Context.buildEMAContext(visible.map(c => c.close), CONTEXT);
    const location = Context.buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = Context.buildSessionContext(trigger.timestamp, CONTEXT);
    const contextOk = !!ema && !!location && !!session;
    bump(stages.context, contextOk);
    if (!contextOk) continue;

    const quality = Quality.scoreSetup(spike, { ema, location, session });
    bump(stages.quality, !!quality.tradeAllowed);
    if (!quality.tradeAllowed) continue;

    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    const directional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
    const rrOk = risk > 0 && reward > 0 && directional;
    bump(stages.riskReward, rrOk);
    if (!rrOk) continue;

    const candidate = {
      entryIndex: trigger.index, entryTime: trigger.timestamp, direction: trigger.direction,
      entry: trigger.entryPrice, stopLoss: invalidation.invalidationLevel, tp1: projection.tp1,
      session: session.session, qualityGrade: quality.grade, qualityScore: quality.score,
      structureScore: spike.structureScore, overlapScore: spike.overlapScore,
      hasPGAPEvidence: spike.hasPGAPEvidence, nearRoundLevel: location.nearRoundLevel, emaAligned: ema.aligned,
    };
    bump(stages.finalCandidate, true);
    finals.push({ ...candidate, result: outcome(candles, candidate) });
  }

  const closed = finals.filter(r => r.result === 'TP1' || r.result === 'SL');
  const wins = closed.filter(r => r.result === 'TP1').length;
  const losses = closed.filter(r => r.result === 'SL').length;
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_BASE_STAGE_FUNNEL_FORENSICS_V1',
    timeframe: tf,
    replayEvents,
    methodology: 'Same deterministic baseline pipeline; no strategy-rule changes. Each stage is evaluated only on candles visible at replay time.',
    stages,
    finalCandidates: finals.length,
    resolvedFinalCandidates: closed.length,
    finalWinRate: closed.length ? wins / closed.length : null,
    finalOutcomeCounts: { TP1: wins, SL: losses, AMBIGUOUS: finals.filter(r => r.result === 'AMBIGUOUS').length, OPEN: finals.filter(r => r.result === 'OPEN').length },
    finalByDirection: groupCount(finals, 'direction'),
    finalBySession: groupCount(finals, 'session'),
    finalByQuality: groupCount(finals, 'qualityGrade'),
    finalByResult: groupCount(finals, 'result'),
  };
  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: events=${replayEvents} finals=${finals.length} resolved=${closed.length} winRate=${closed.length ? (wins / closed.length * 100).toFixed(2) : 'n/a'}%`);
  for (const [name, s] of Object.entries(stages)) console.log(`  ${name}: seen=${s.seen} passed=${s.passed} rejected=${s.rejected}`);
  console.log(`Report -> ${out}`);
}

const api = await imports();
await run('1min', api);
await run('5min', api);
