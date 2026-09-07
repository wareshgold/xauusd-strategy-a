import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const BASELINE_REF = '3a96629838fb0a15e5b71f1927dc4f7fe63819e1';
const PRE_REFRESH_REF = '0017947aac1be7a6f315717d38fec6e2fc58ecb7';
const TARGET_TIME = '2026-08-26 12:35:00';

function loadGitDataset(ref) {
  const raw = execFileSync('git', ['show', `${ref}:data/historical/xauusd-5min.json`], {
    cwd: ROOT,
    maxBuffer: 256 * 1024 * 1024,
  });
  return JSON.parse(raw.toString('utf8')).candles ?? [];
}

function replayAt(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;

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

  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    if (trigger.direction !== (spike.direction === 'BULLISH' ? 'BUY' : 'SELL')) continue;

    const breakout = breakouts.find((x) =>
      x.index === spike.breakoutIndex && x.direction === spike.direction,
    );
    const followThrough = ft.find((x) =>
      x.breakoutIndex === spike.breakoutIndex && x.direction === spike.direction,
    );
    if (!breakout || !followThrough) continue;

    return { trigger, spike, correction, breakout, followThrough };
  }

  return null;
}

function candidateChainsAt(candles, index) {
  const visible = candles.slice(0, index + 1);
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
    chains.push({ breakout, followThrough, spike, correction, trigger });
  }
  return chains;
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
    const replay = index >= 0 ? replayAt(candles, index) : null;
    const chains = index >= 0 ? candidateChainsAt(candles, index) : [];
    return {
      dataset: name,
      count: candles.length,
      targetIndex: index,
      targetCandle: index >= 0 ? candles[index] : null,
      replay,
      candidateChainsAtTarget: chains,
    };
  });

  const exact = results[0];
  const mismatches = results.filter((r) =>
    r.replay?.trigger?.direction !== targetTrade.direction,
  );

  console.log(JSON.stringify({
    diagnostic: 'PHASE12_TARGET_FORENSIC_EXACT_BASELINE_SNAPSHOT',
    baselineSnapshotRef: BASELINE_REF,
    preRefreshRef: PRE_REFRESH_REF,
    targetTime: TARGET_TIME,
    baselineTrade: targetTrade,
    baselineSnapshotReplayMatchesBaseline: exact.replay?.trigger?.direction === targetTrade.direction,
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
