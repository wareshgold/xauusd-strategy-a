import { execFileSync } from 'node:child_process';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const BASELINE_COMMIT = '3a96629838fb0a15e5b71f1927dc4f7fe63819e1';
const BASELINE_PATH = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-phase-counterfactual-direction-flip-audit');
const OUT = resolve(OUT_DIR, 'baseline-snapshot-exit-replay-5min.json');

const parseJson = text => JSON.parse(text);
const baseline = parseJson(await readFile(BASELINE_PATH, 'utf8'));
const snapshot = parseJson(execFileSync('git', ['show', `${BASELINE_COMMIT}:data/historical/xauusd-5min.json`], {
  cwd: ROOT,
  encoding: 'utf8',
  maxBuffer: 32 * 1024 * 1024,
}));

const candles = snapshot.candles ?? [];
const trades = baseline.trades ?? [];
if (candles.length !== Number(baseline.candles)) throw new Error(`Snapshot candle count mismatch: ${candles.length} !== ${baseline.candles}`);

function evaluate(trade) {
  const risk = Math.abs(trade.entry - trade.stopLoss);
  if (!Number.isFinite(risk) || risk <= 0) throw new Error(`Invalid risk at ${trade.entryTime}`);
  let exitIndex = null;
  let result = 'OPEN';
  let rMultiple = null;
  for (let i = trade.entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = trade.direction === 'BUY' ? c.low <= trade.stopLoss : c.high >= trade.stopLoss;
    const tp1 = trade.direction === 'BUY' ? c.high >= trade.tp1 : c.low <= trade.tp1;
    const tp2 = trade.tp2 === undefined || trade.tp2 === null
      ? false
      : trade.direction === 'BUY' ? c.high >= trade.tp2 : c.low <= trade.tp2;
    if (sl && (tp1 || tp2)) {
      exitIndex = i;
      result = 'AMBIGUOUS';
      break;
    }
    if (sl) {
      exitIndex = i;
      result = 'SL';
      rMultiple = -1;
      break;
    }
    if (tp2) {
      exitIndex = i;
      result = 'TP2';
      rMultiple = Math.abs(trade.tp2 - trade.entry) / risk;
      break;
    }
    if (tp1) {
      exitIndex = i;
      result = 'TP1';
      rMultiple = Math.abs(trade.tp1 - trade.entry) / risk;
      break;
    }
  }
  return { result, rMultiple, exitIndex, exitTime: exitIndex === null ? null : candles[exitIndex].timestamp };
}

const rows = trades.map((trade, index) => {
  const replay = evaluate(trade);
  return {
    index,
    entryIndex: trade.entryIndex,
    entryTime: trade.entryTime,
    direction: trade.direction,
    storedResult: trade.result,
    storedR: trade.rMultiple,
    replayResult: replay.result,
    replayR: replay.rMultiple,
    replayExitIndex: replay.exitIndex,
    replayExitTime: replay.exitTime,
  };
});

const mismatches = rows.filter(x => x.storedResult !== x.replayResult || (x.storedR === null) !== (x.replayR === null) || (x.storedR !== null && Math.abs(x.storedR - x.replayR) > 1e-9));
const same = rows.length - mismatches.length;
const byTransition = {};
for (const x of mismatches) {
  const key = `${x.storedResult}->${x.replayResult}`;
  byTransition[key] = (byTransition[key] ?? 0) + 1;
}

const result = {
  strategy: baseline.strategy,
  mode: 'PHASE_BASELINE_SNAPSHOT_EXIT_REPLAY',
  timeframe: '5min',
  baselineCommit: BASELINE_COMMIT,
  baselineDataset: {
    candles: candles.length,
    from: candles[0]?.timestamp ?? null,
    to: candles.at(-1)?.timestamp ?? null,
  },
  canonicalTrades: rows.length,
  exactExitSemantics: true,
  parity: {
    same: same,
    mismatch: mismatches.length,
    matchRate: rows.length ? same / rows.length : null,
    transitions: byTransition,
  },
  samples: mismatches.slice(0, 20),
  status: mismatches.length === 0 ? 'BASELINE_EXIT_REPLAY_MATCHES_SNAPSHOT' : 'BASELINE_EXIT_REPLAY_MISMATCH',
};

await mkdir(OUT_DIR, { recursive: true });
await writeFile(OUT, JSON.stringify(result, null, 2));

console.log(`PHASE_BASELINE_SNAPSHOT_EXIT_REPLAY 5min CANONICAL=${rows.length} SAME=${same} MISMATCH=${mismatches.length}`);
console.log(`SNAPSHOT candles=${candles.length} from=${candles[0]?.timestamp} to=${candles.at(-1)?.timestamp}`);
console.log(`MATCH_RATE=${(result.parity.matchRate * 100).toFixed(2)}%`);
console.log(`TRANSITIONS=${JSON.stringify(byTransition)}`);
for (const x of mismatches.slice(0, 10)) console.log(`MISMATCH index=${x.entryIndex} time=${x.entryTime} dir=${x.direction} stored=${x.storedResult} replay=${x.replayResult} exit=${x.replayExitTime}`);
console.log(`REPORT=${OUT}`);
console.log(`STATUS=${result.status}`);
