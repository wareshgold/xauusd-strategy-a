import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-opportunity-window-global-holdout');
const TIMEFRAMES = ['1min', '5min'];
const WINDOWS = [0, 1, 2, 3, 5, 8];
const MIN_N = 10;
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

function summarize(rows) {
  const a = rows.filter((r) => finite(r.rMultiple));
  const wins = a.filter((r) => Number(r.rMultiple) > 0);
  const losses = a.filter((r) => Number(r.rMultiple) < 0);
  const grossProfit = wins.reduce((s, r) => s + Number(r.rMultiple), 0);
  const grossLoss = Math.abs(losses.reduce((s, r) => s + Number(r.rMultiple), 0));
  const totalR = a.reduce((s, r) => s + Number(r.rMultiple), 0);
  return {
    n: a.length,
    wins: wins.length,
    losses: losses.length,
    winRate: a.length ? wins.length / a.length : null,
    avgR: a.length ? totalR / a.length : null,
    PF: grossLoss ? grossProfit / grossLoss : null,
    totalR,
  };
}

function split(rows) {
  const n = rows.length;
  const a = Math.floor(n / 3);
  const b = Math.floor((2 * n) / 3);
  return {
    dev: rows.slice(0, a),
    validation: rows.slice(a, b),
    holdout: rows.slice(b),
    boundaries: {
      devEnd: rows[a - 1]?.entryTime ?? null,
      validationEnd: rows[b - 1]?.entryTime ?? null,
      holdoutStart: rows[b]?.entryTime ?? null,
    },
  };
}

function gate(dev, validation) {
  return Boolean(
    dev.n >= MIN_N && validation.n >= MIN_N &&
    dev.PF != null && validation.PF != null &&
    dev.PF >= 1 && validation.PF >= 1 &&
    dev.avgR > 0 && validation.avgR > 0,
  );
}

async function reconstruct(tf) {
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
      const ft = FT.detectFollowThrough(visible, [breakout], {
        maxBarsAfterBreakout: CFG.ftMaxBars,
        requireCloseBeyondBrokenLevel: true,
      })[0];
      if (!ft) continue;
      const spike = Spike.detectSpikeCandidates(visible, [breakout], [ft], {
        maxCandles: CFG.spikeMaxCandles,
        minDirectionalFraction: CFG.minDirectionalFraction,
        maxOverlapFraction: CFG.maxOverlapFraction,
      }).candidates.find((s) => s.endIndex < entryIndex);
      if (!spike) continue;
      const correction = Correction.detectFirstCorrection(visible, spike);
      if (!correction || correction.correctionExtremeIndex >= entryIndex) continue;
      const trigger = Trigger.detectEntryTrigger(visible, correction);
      if (!trigger || trigger.index !== entryIndex) continue;
      if (trade.direction && trigger.direction !== trade.direction) continue;
      matched = { correction, trigger };
      break;
    }

    if (!matched) continue;
    rows.push({
      entryIndex,
      entryTime: trade.entryTime ?? matched.trigger.timestamp,
      direction: matched.trigger.direction,
      session: trade.session ?? 'UNKNOWN',
      delayBars: entryIndex - matched.correction.correctionExtremeIndex,
      rMultiple: Number(trade.rMultiple),
    });
  }

  return rows.sort((a, b) => a.entryIndex - b.entryIndex);
}

function evaluateWindow(rows, window) {
  const selected = rows.filter((r) => r.delayBars <= window);
  return { windowBars: window, ...summarize(selected) };
}

async function run(tf) {
  const rows = await reconstruct(tf);
  const s = split(rows);
  const candidates = WINDOWS.map((windowBars) => {
    const dev = evaluateWindow(s.dev, windowBars);
    const validation = evaluateWindow(s.validation, windowBars);
    const holdout = evaluateWindow(s.holdout, windowBars);
    return {
      windowBars,
      dev,
      validation,
      holdout,
      passesDevValidation: gate(dev, validation),
    };
  });

  const eligible = candidates.filter((x) => x.passesDevValidation);
  const ranked = [...eligible].sort((a, b) => {
    if (b.validation.avgR !== a.validation.avgR) return b.validation.avgR - a.validation.avgR;
    return b.validation.PF - a.validation.PF;
  });
  const selected = ranked[0] ?? null;

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_OPPORTUNITY_WINDOW_GLOBAL_HOLDOUT_V1',
    timeframe: tf,
    symbol: 'XAU/USD',
    hypothesis: 'A valid Strategy A entry opportunity may have a limited lifetime after the correction extreme; entries that occur too late may have weaker expectancy.',
    methodology: 'Post-hoc reconstruction of actual baseline entries using only candles visible through each entry bar. Opportunity window is a pre-declared maximum number of bars from correction extreme to actual trigger. No entry rule or baseline trade is changed by this analysis.',
    candidateWindowsBars: WINDOWS,
    selectionGate: `DEV and VALIDATION each n >= ${MIN_N}, PF >= 1, avgR > 0. Candidates are pre-declared; HOLDOUT is untouched during selection.`,
    multipleTestingWarning: 'Candidate windows are a small pre-declared research grid. The selected window is not a production rule and requires a separate fresh/OOS validation before adoption.',
    overall: summarize(rows),
    globalBoundaries: s.boundaries,
    globalCounts: { all: rows.length, dev: s.dev.length, validation: s.validation.length, holdout: s.holdout.length },
    candidates,
    selectedForOOS: selected ? { windowBars: selected.windowBars, dev: selected.dev, validation: selected.validation } : null,
    selectedHoldout: selected?.holdout ?? null,
    decision: selected ? 'CANDIDATE_FOR_FRESH_OOS' : 'NO_SURVIVOR',
    rows,
  };

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`${tf}: matched=${rows.length} DEV=${s.dev.length} VAL=${s.validation.length} HOLDOUT=${s.holdout.length}`);
  for (const c of candidates) {
    console.log(`  window<=${c.windowBars} bars: DEV n=${c.dev.n} PF=${c.dev.PF?.toFixed(4) ?? 'n/a'} avgR=${c.dev.avgR?.toFixed(4) ?? 'n/a'} | VAL n=${c.validation.n} PF=${c.validation.PF?.toFixed(4) ?? 'n/a'} avgR=${c.validation.avgR?.toFixed(4) ?? 'n/a'} | HOLDOUT n=${c.holdout.n} PF=${c.holdout.PF?.toFixed(4) ?? 'n/a'} avgR=${c.holdout.avgR?.toFixed(4) ?? 'n/a'} gate=${c.passesDevValidation}`);
  }
  console.log(`  selectedForOOS=${selected?.windowBars ?? 'none'} holdoutAvgR=${selected?.holdout.avgR?.toFixed(4) ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
