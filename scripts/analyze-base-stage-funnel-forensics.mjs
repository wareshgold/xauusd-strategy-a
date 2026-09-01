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

function emptyStage() { return { seen: 0, passed: 0, rejected: 0 }; }
function bump(stage, pass) { stage.seen += 1; if (pass) stage.passed += 1; else stage.rejected += 1; }
function groupCount(rows, key) { const out = {}; for (const r of rows) { const v = r[key] ?? 'UNKNOWN'; out[v] = (out[v] ?? 0) + 1; } return out; }
function outcome(candles, c) {
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

  // IMPORTANT: process each breakout path once. The previous implementation
  // re-counted every historical breakout on every later visible prefix,
  // producing millions of fake stage observations. This version keeps one
  // chronological path per breakout and only advances a stage when its
  // required information is actually observable.
  const allBreakouts = Breakout.detectBreakout(candles, BREAKOUT_LOOKBACK);
  for (let index = 0; index < candles.length; index += 1) {
    replayEvents += 1;
    bump(stages.sufficientHistory, index + 1 >= Math.max(BREAKOUT_LOOKBACK + 2, CONTEXT.emaPeriod));
  }

  for (const breakout of allBreakouts) {
    if (breakout.index < CONTEXT.emaPeriod - 1) continue;
    bump(stages.breakout, true);

    let ft = null;
    let spike = null;
    let correction = null;
    let trigger = null;
    let projection = null;
    let invalidation = null;
    let quality = null;
    let session = null;
    let location = null;
    let emaContext = null;
    let finalized = false;

    for (let index = breakout.index + 1; index < candles.length; index += 1) {
      const visible = candles.slice(0, index + 1);

      if (!ft) {
        ft = FT.detectFollowThrough(visible, [breakout], {
          maxBarsAfterBreakout: FT_MAX_BARS,
          requireCloseBeyondBrokenLevel: true,
        })[0] ?? null;
        if (ft) bump(stages.followThrough, true);
        else if (index >= breakout.index + FT_MAX_BARS) { bump(stages.followThrough, false); break; }
      }
      if (!ft) continue;

      if (!spike) {
        spike = Spike.detectSpikeCandidates(visible, [breakout], [ft], {
          maxCandles: SPIKE_MAX_CANDLES,
          minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
          maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
        }).candidates.find((s) => s.breakoutIndex === breakout.index && s.endIndex < index) ?? null;
        if (!spike) {
          const spikeWindowEnd = ft.followThroughIndex;
          if (index >= spikeWindowEnd) {
            const result = Spike.detectSpikeCandidates(visible, [breakout], [ft], {
              maxCandles: SPIKE_MAX_CANDLES,
              minDirectionalFraction: SPIKE_MIN_DIRECTIONAL_FRACTION,
              maxOverlapFraction: SPIKE_MAX_OVERLAP_FRACTION,
            });
            if (!result.candidates.some((s) => s.breakoutIndex === breakout.index)) { bump(stages.spike, false); break; }
          }
        } else bump(stages.spike, true);
      }
      if (!spike) continue;

      if (!correction) {
        const candidate = Correction.detectFirstCorrection(visible, spike);
        if (candidate && candidate.correctionExtremeIndex < index) {
          correction = candidate;
          bump(stages.correction, true);
        }
      }
      if (!correction) continue;

      if (!trigger) {
        const candidate = Trigger.detectEntryTrigger(visible, correction);
        if (candidate && candidate.index === index) {
          trigger = candidate;
          bump(stages.trigger, true);
        }
      }
      if (!trigger) continue;

      if (!projection) {
        projection = Projection.projectLeg2(visible, correction);
        bump(stages.projection, !!projection);
      }
      if (!projection) continue;

      if (!invalidation) {
        invalidation = Invalidation.getInvalidationRule(correction);
        bump(stages.invalidation, !!invalidation);
      }
      if (!invalidation) continue;

      if (!emaContext) emaContext = Context.buildEMAContext(visible.map((c) => c.close), CONTEXT);
      if (!location) location = Context.buildLocationContext(trigger.entryPrice, CONTEXT);
      if (!session) session = Context.buildSessionContext(trigger.timestamp, CONTEXT);
      const contextOk = !!emaContext && !!location && !!session;
      bump(stages.context, contextOk);
      if (!contextOk) continue;

      quality = Quality.scoreSetup(spike, { ema: emaContext, location, session });
      bump(stages.quality, !!quality.tradeAllowed);
      if (!quality.tradeAllowed) break;

      const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
      const reward = Math.abs(projection.tp1 - trigger.entryPrice);
      const directional = trigger.direction === 'BUY' ? projection.tp1 > trigger.entryPrice : projection.tp1 < trigger.entryPrice;
      const rrOk = risk > 0 && reward > 0 && directional;
      bump(stages.riskReward, rrOk);
      if (!rrOk) break;

      const candidate = {
        entryIndex: trigger.index, entryTime: trigger.timestamp, direction: trigger.direction,
        entry: trigger.entryPrice, stopLoss: invalidation.invalidationLevel, tp1: projection.tp1,
        session: session.session, qualityGrade: quality.grade, qualityScore: quality.score,
        structureScore: spike.structureScore, overlapScore: spike.overlapScore,
        hasPGAPEvidence: spike.hasPGAPEvidence, nearRoundLevel: location.nearRoundLevel, emaAligned: emaContext.aligned,
      };
      bump(stages.finalCandidate, true);
      finals.push({ ...candidate, result: outcome(candles, candidate) });
      finalized = true;
      break;
    }

    // A path that reached a stage but never reached its next stage by the end
    // of the dataset is a genuine rejection/censoring outcome, not a new
    // observation at every later candle.
    if (ft && !spike) continue;
    if (spike && !correction) bump(stages.correction, false);
    else if (correction && !trigger) bump(stages.trigger, false);
    else if (trigger && !projection) bump(stages.projection, false);
    else if (trigger && projection && !invalidation) bump(stages.invalidation, false);
    else if (trigger && projection && invalidation && !finalized) {
      // quality/riskReward failures are already counted at their decision bar.
    }
  }

  const unique = new Map();
  for (const row of finals) if (!unique.has(row.entryIndex)) unique.set(row.entryIndex, row);
  const finalRows = [...unique.values()];
  const closed = finalRows.filter((r) => r.result === 'TP1' || r.result === 'SL');
  const wins = closed.filter((r) => r.result === 'TP1').length;
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_BASE_STAGE_FUNNEL_FORENSICS_V3_UNIQUE_PATHS',
    timeframe: tf,
    replayEvents,
    methodology: 'Each historical breakout is one path. Stages are counted once per path and only when the required information is observable. No strategy-rule changes.',
    stages,
    rawFinalCandidateCount: finals.length,
    finalCandidates: finalRows.length,
    resolvedFinalCandidates: closed.length,
    finalWinRate: closed.length ? wins / closed.length : null,
    finalOutcomeCounts: {
      TP1: wins,
      SL: closed.length - wins,
      AMBIGUOUS: finalRows.filter((r) => r.result === 'AMBIGUOUS').length,
      OPEN: finalRows.filter((r) => r.result === 'OPEN').length,
    },
    finalByDirection: groupCount(finalRows, 'direction'),
    finalBySession: groupCount(finalRows, 'session'),
    finalByQuality: groupCount(finalRows, 'qualityGrade'),
    finalByResult: groupCount(finalRows, 'result'),
  };
  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: events=${replayEvents} breakouts=${stages.breakout.passed} rawFinals=${finals.length} finals=${finalRows.length} resolved=${closed.length} winRate=${closed.length ? (wins / closed.length * 100).toFixed(2) : 'n/a'}%`);
  for (const [name, s] of Object.entries(stages)) console.log(`  ${name}: seen=${s.seen} passed=${s.passed} rejected=${s.rejected}`);
  console.log(`Report -> ${out}`);
}

const api = await imports();
await run('1min', api);
await run('5min', api);
