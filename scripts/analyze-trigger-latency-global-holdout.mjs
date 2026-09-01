import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-trigger-latency-global-holdout');
const CFG = {
  breakoutLookback: 5,
  ftMaxBars: 2,
  spikeMaxCandles: 8,
  minDirectionalFraction: 0.5,
  maxOverlapFraction: 0.8,
};

const [Breakout, FT, Spike, Correction, Trigger] = await Promise.all([
  import('../src/domain/market/BreakoutDetector.ts'),
  import('../src/domain/market/FollowThroughDetector.ts'),
  import('../src/domain/strategy-a/SpikeDetector.ts'),
  import('../src/domain/strategy-a/CorrectionDetector.ts'),
  import('../src/domain/strategy-a/EntryTrigger.ts'),
]);

function finite(x) { return Number.isFinite(Number(x)); }
function stats(rows) {
  const delays = rows.map((r) => r.delayBars).filter(finite).map(Number).sort((a, b) => a - b);
  const r = rows.map((x) => Number(x.rMultiple)).filter(Number.isFinite);
  const mean = (a) => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
  const q = (p) => delays.length ? delays[Math.min(delays.length - 1, Math.floor((delays.length - 1) * p))] : null;
  return { n: rows.length, meanDelayBars: mean(delays), medianDelayBars: q(0.5), p25DelayBars: q(0.25), p75DelayBars: q(0.75), minDelayBars: delays[0] ?? null, maxDelayBars: delays.at(-1) ?? null, avgR: mean(r) };
}
function split(rows) {
  const n = rows.length;
  const a = Math.floor(n / 3);
  const b = Math.floor((2 * n) / 3);
  return [rows.slice(0, a), rows.slice(a, b), rows.slice(b)];
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${tf}.json`), 'utf8'));
  const candles = raw.candles;
  const rows = [];

  for (const trade of baseline.trades ?? []) {
    if (!finite(trade.entryIndex)) continue;
    const entryIndex = Number(trade.entryIndex);
    const visible = candles.slice(0, entryIndex + 1);
    const breakouts = Breakout.detectBreakout(visible, CFG.breakoutLookback).filter((b) => b.index < entryIndex);
    let matched = null;
    for (const breakout of breakouts) {
      const ft = FT.detectFollowThrough(visible, [breakout], { maxBarsAfterBreakout: CFG.ftMaxBars, requireCloseBeyondBrokenLevel: true })[0];
      if (!ft) continue;
      const spike = Spike.detectSpikeCandidates(visible, [breakout], [ft], { maxCandles: CFG.spikeMaxCandles, minDirectionalFraction: CFG.minDirectionalFraction, maxOverlapFraction: CFG.maxOverlapFraction }).candidates.find((s) => s.endIndex < entryIndex);
      if (!spike) continue;
      const correction = Correction.detectFirstCorrection(visible, spike);
      if (!correction || correction.correctionExtremeIndex >= entryIndex) continue;
      const trigger = Trigger.detectEntryTrigger(visible, correction);
      if (!trigger || trigger.index !== entryIndex) continue;
      if (trade.direction && trigger.direction !== trade.direction) continue;
      matched = { breakout, spike, correction, trigger };
      break;
    }
    if (!matched) continue;
    rows.push({
      entryIndex,
      entryTime: trade.entryTime ?? matched.trigger.timestamp,
      direction: matched.trigger.direction,
      session: trade.session ?? 'UNKNOWN',
      delayBars: entryIndex - matched.correction.correctionExtremeIndex,
      correctionDepthBars: matched.correction.correctionExtremeIndex - matched.correction.correctionStartIndex,
      rMultiple: Number(trade.rMultiple),
    });
  }

  rows.sort((a, b) => a.entryIndex - b.entryIndex);
  const [dev, val, holdout] = split(rows);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_TRIGGER_LATENCY_GLOBAL_HOLDOUT_V1',
    timeframe: tf,
    methodology: 'Post-hoc reconstruction of actual baseline entries using only candles visible through each entry bar. No entry rule changes and no future candles used for latency measurement.',
    overall: stats(rows),
    dev: stats(dev),
    validation: stats(val),
    holdout: stats(holdout),
    holdoutByDelayBucket: Object.fromEntries([['0', 0], ['1', 0], ['2', 0], ['3-5', 0], ['6+', 0]].map(([k]) => [k, stats(holdout.filter((r) => k === '0' ? r.delayBars === 0 : k === '1' ? r.delayBars === 1 : k === '2' ? r.delayBars === 2 : k === '3-5' ? r.delayBars >= 3 && r.delayBars <= 5 : r.delayBars >= 6))])),
    rows,
  };
  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: matched=${rows.length} overallDelayMedian=${report.overall.medianDelayBars ?? 'n/a'} holdoutDelayMedian=${report.holdout.medianDelayBars ?? 'n/a'} holdoutAvgR=${report.holdout.avgR?.toFixed(4) ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
