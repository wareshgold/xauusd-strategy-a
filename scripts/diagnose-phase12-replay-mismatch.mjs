import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
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
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const BASELINE_REF = '3a96629838fb0a15e5b71f1927dc4f7fe63819e1';
const PRE_REFRESH_REF = '0017947aac1be7a6f315717d38fec6e2fc58ecb7';
const TARGET_TIME = '2026-08-26 12:35:00';
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

function loadGitDataset(ref) {
  const raw = execFileSync('git', ['show', `${ref}:data/historical/xauusd-5min.json`], {
    cwd: ROOT,
    maxBuffer: 256 * 1024 * 1024,
  });
  return JSON.parse(raw.toString('utf8')).candles ?? [];
}

function detectChains(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < Math.max(5 + 2, CONTEXT.emaPeriod)) return [];

  const breakouts = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, breakouts, {
    maxBarsAfterBreakout: 2,
    requireCloseBeyondBrokenLevel: true,
  });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, {
    maxCandles: 8,
    minDirectionalFraction: 0.5,
    maxOverlapFraction: 0.8,
  });

  const chains = [];
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;

    const breakout = breakouts.find((x) =>
      x.index === spike.breakoutIndex && x.direction === spike.direction,
    );
    const followThrough = ft.find((x) =>
      x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction,
    );
    if (!breakout || !followThrough) continue;

    const projection = projectLeg2(visible, correction);
    if (!projection) continue;
    const invalidation = getInvalidationRule(correction);
    const ema = buildEMAContext(visible.map((c) => c.close), CONTEXT);
    if (!ema) continue;
    const location = buildLocationContext(trigger.entryPrice, CONTEXT);
    const session = buildSessionContext(trigger.timestamp, CONTEXT);
    const quality = scoreSetup(spike, { ema, location, session });
    const risk = Math.abs(trigger.entryPrice - invalidation.invalidationLevel);
    const reward = Math.abs(projection.tp1 - trigger.entryPrice);
    if (risk <= 0 || reward <= 0) continue;

    chains.push({
      breakout,
      followThrough,
      spike,
      correction,
      trigger,
      projection,
      invalidation,
      quality,
      risk,
      reward,
    });
  }
  return chains;
}

function replayAt(candles, index) {
  const chains = detectChains(candles, index);
  const selected = chains.find((chain) => chain.quality.tradeAllowed);
  if (!selected) return null;
  return selected;
}

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const current = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const baselineSnapshot = loadGitDataset(BASELINE_REF);
  const preRefresh = loadGitDataset(PRE_REFRESH_REF);

  const targetTrade = (base.trades ?? []).find((t) => t.entryTime === TARGET_TIME);
  if (!targetTrade) throw new Error(`PHASE12 FORENSIC: target trade not found: ${TARGET_TIME}`);

  const datasets = [
    ['BASELINE_SNAPSHOT', baselineSnapshot],
    ['PRE_REFRESH_15K', preRefresh],
    ['CURRENT_REFRESHED_50K', current],
  ];

  const results = datasets.map(([name, candles]) => {
    const index = candles.findIndex((c) => c.timestamp === TARGET_TIME);
    const chains = index >= 0 ? detectChains(candles, index) : [];
    const replay = chains.find((chain) => chain.quality.tradeAllowed) ?? null;
    return {
      dataset: name,
      count: candles.length,
      targetIndex: index,
      targetCandle: index >= 0 ? candles[index] : null,
      replay,
      candidateChainsAtTarget: chains,
      allowedCandidates: chains.filter((chain) => chain.quality.tradeAllowed),
    };
  });

  const exact = results[0];
  const mismatches = results.filter((r) =>
    r.replay?.trigger?.direction !== targetTrade.direction,
  );

  console.log(JSON.stringify({
    diagnostic: 'PHASE12_TARGET_FORENSIC_EXACT_BASELINE_SNAPSHOT',
    selectionSemantics: 'EXACT_BASELINE_DECIDE_FIRST_TRADE_ALLOWED_CANDIDATE',
    baselineSnapshotRef: BASELINE_REF,
    preRefreshRef: PRE_REFRESH_REF,
    targetTime: TARGET_TIME,
    baselineTrade: targetTrade,
    baselineSnapshotReplayMatchesBaseline: exact.replay?.trigger?.direction === targetTrade.direction &&
      exact.replay?.spike?.structureScore === targetTrade.structureScore &&
      exact.replay?.spike?.overlapScore === targetTrade.overlapScore,
    datasetResults: results,
    mismatchDatasets: mismatches.map((r) => ({
      dataset: r.dataset,
      direction: r.replay?.trigger?.direction ?? null,
    })),
  }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
