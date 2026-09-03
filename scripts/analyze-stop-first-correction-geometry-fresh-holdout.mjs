import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TOTAL = 15000;
const FRESH = 5000;
const PRE = TOTAL - FRESH;

function loadJson(file) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, file), 'utf8'));
}

function finite(v) { return Number.isFinite(Number(v)); }
function pf(trades) {
  const wins = trades.filter(t => t > 0).reduce((a, b) => a + b, 0);
  const losses = -trades.filter(t => t < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? wins / losses : 'n/a';
}
function avg(trades) { return trades.length ? trades.reduce((a, b) => a + b, 0) / trades.length : 0; }
function winRate(trades) { return trades.length ? trades.filter(t => t > 0).length / trades.length : 0; }
function maxDD(trades) {
  let equity = 0, peak = 0, dd = 0;
  for (const r of trades) {
    equity += r;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
  }
  return dd;
}
function maxCL(trades) {
  let cur = 0, max = 0;
  for (const r of trades) {
    cur = r < 0 ? cur + 1 : 0;
    max = Math.max(max, cur);
  }
  return max;
}
function stats(trades) {
  return { n: trades.length, avgR: avg(trades), pf: pf(trades), winRate: winRate(trades), totalR: trades.reduce((a,b)=>a+b,0), maxDD: maxDD(trades), maxCL: maxCL(trades) };
}

function normalizeDirection(direction, value, low, high) {
  const range = high - low;
  if (!finite(value) || !finite(low) || !finite(high) || range <= 0) return null;
  return direction === 'BUY' ? (value - low) / range : (high - value) / range;
}

function reconstructCandidates(candModule, candles, start, end) {
  // The research scripts expose the same detector chain through the module used by
  // the existing forensic scripts. This loader intentionally keeps the fresh test
  // dependent on the repository's canonical candidate detector rather than creating
  // a second strategy implementation.
  return candModule.detectCandidates(candles, start, end);
}

async function runTimeframe(tf, historicalPath, baselinePath) {
  const candles = loadJson(historicalPath);
  const baseline = loadJson(baselinePath);

  const detectorPath = path.join(ROOT, 'scripts', 'analyze-candidate-selection-competition.mjs');
  const detectorText = fs.readFileSync(detectorPath, 'utf8');
  const modPath = path.join(ROOT, 'scripts', `.tmp-stop-geometry-detector-${tf}.mjs`);
  // This file is generated only during execution so the fresh test can reuse the
  // exact candidate reconstruction already present in the competition forensic.
  fs.writeFileSync(modPath, detectorText.replace(/\nmain\(\);?\s*$/s, '\nexport { detectCandidates };\n'));
  const mod = await import(`file://${modPath}?v=${Date.now()}`);
  try {
    const joined = [];
    const freshBaseline = baseline.filter(x => Number(x.entryIndex) >= PRE);

    for (const t of freshBaseline) {
      if (!finite(t.entryIndex)) continue;
      const candidates = reconstructCandidates(mod, candles, Number(t.entryIndex), Number(t.entryIndex));
      const selected = candidates.find(c => Number(c.entryIndex) === Number(t.entryIndex));
      if (!selected?.geometry) continue;
      joined.push({ r: Number(t.rMultiple), geometry: selected.geometry });
    }

    const baselineTrades = joined.map(x => x.r).filter(Number.isFinite);
    const tests = [
      {
        name: 'riskToImpulse 0.25-<0.50',
        pass: g => Number(g.riskToImpulse) >= 0.25 && Number(g.riskToImpulse) < 0.50,
      },
      {
        name: 'stopToCorrectionLeg 0.25-<0.50',
        pass: g => Number(g.stopToCorrectionLeg) >= 0.25 && Number(g.stopToCorrectionLeg) < 0.50,
      },
      {
        name: 'intersection: riskToImpulse 0.25-<0.50 AND stopToCorrectionLeg 0.25-<0.50',
        pass: g => Number(g.riskToImpulse) >= 0.25 && Number(g.riskToImpulse) < 0.50 && Number(g.stopToCorrectionLeg) >= 0.25 && Number(g.stopToCorrectionLeg) < 0.50,
      },
    ];

    console.log(`${tf}: fresh joined=${joined.length} baseline=${JSON.stringify(stats(baselineTrades))}`);
    for (const test of tests) {
      const trades = joined.filter(x => test.pass(x.geometry)).map(x => x.r).filter(Number.isFinite);
      console.log(` ${test.name}: ${JSON.stringify(stats(trades))}`);
    }
  } finally {
    fs.rmSync(modPath, { force: true });
  }
}

await runTimeframe('1min', 'data/historical/xauusd-1min.json', 'data/reports/strategy-a-baseline-backtest/1min.json');
await runTimeframe('5min', 'data/historical/xauusd-5min.json', 'data/reports/strategy-a-baseline-backtest/5min.json');
