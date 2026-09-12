import { execFileSync } from 'node:child_process';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASELINE_COMMIT = '3a96629838fb0a15e5b71f1927dc4f7fe63819e1';
const TIMEFRAME = '5min';
const DATA_PATH = `data/historical/xauusd-${TIMEFRAME}.json`;
const BASELINE_PATH = resolve(ROOT, `data/reports/strategy-a-baseline/${TIMEFRAME}.json`);
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-phase-counterfactual-direction-flip-audit');
const REPORT_PATH = resolve(REPORT_DIR, `dataset-provenance-${TIMEFRAME}.json`);

function loadJson(path) {
  return JSON.parse(require('node:fs').readFileSync(path, 'utf8'));
}

function loadGitJson(commit, path) {
  const raw = execFileSync('git', ['show', `${commit}:${path}`], { cwd: ROOT, encoding: 'utf8' });
  return JSON.parse(raw);
}

function candleAt(dataset, index) {
  return dataset.candles?.[index] ?? null;
}

function findTimestamp(dataset, timestamp) {
  return dataset.candles.findIndex((c) => c.timestamp === timestamp);
}

const baseline = loadJson(BASELINE_PATH);
const current = loadJson(resolve(ROOT, DATA_PATH));
const snapshot = loadGitJson(BASELINE_COMMIT, DATA_PATH);
const trades = baseline.trades ?? [];

const rows = trades.map((trade) => {
  const currentCandle = candleAt(current, trade.entryIndex);
  const snapshotCandle = candleAt(snapshot, trade.entryIndex);
  const snapshotIndexByTime = findTimestamp(snapshot, trade.entryTime);
  return {
    entryIndex: trade.entryIndex,
    entryTime: trade.entryTime,
    direction: trade.direction,
    currentTimestampAtIndex: currentCandle?.timestamp ?? null,
    snapshotTimestampAtIndex: snapshotCandle?.timestamp ?? null,
    snapshotIndexByEntryTime: snapshotIndexByTime,
    currentIndexTimeMatch: currentCandle?.timestamp === trade.entryTime,
    snapshotIndexTimeMatch: snapshotCandle?.timestamp === trade.entryTime,
  };
});

const summary = {
  strategy: 'Strategy A / SP2L',
  mode: 'BASELINE_DATASET_PROVENANCE_DIAGNOSTIC',
  timeframe: TIMEFRAME,
  baselineCommit: BASELINE_COMMIT,
  baselineDataset: {
    candles: snapshot.candles?.length ?? null,
    from: snapshot.candles?.[0]?.timestamp ?? null,
    to: snapshot.candles?.at(-1)?.timestamp ?? null,
  },
  currentDataset: {
    candles: current.candles?.length ?? null,
    from: current.candles?.[0]?.timestamp ?? null,
    to: current.candles?.at(-1)?.timestamp ?? null,
  },
  canonicalTrades: trades.length,
  currentIndexTimeMatches: rows.filter((r) => r.currentIndexTimeMatch).length,
  snapshotIndexTimeMatches: rows.filter((r) => r.snapshotIndexTimeMatch).length,
  snapshotEntryTimeFoundAtSameIndex: rows.filter((r) => r.snapshotIndexTimeMatch).length,
  snapshotEntryTimeMissing: rows.filter((r) => r.snapshotIndexByEntryTime < 0).length,
  sample: rows.slice(0, 10),
  status: rows.every((r) => r.snapshotIndexTimeMatch) ? 'BASELINE_SNAPSHOT_ALIGNS_CURRENT_DOES_NOT' : 'BASELINE_SNAPSHOT_ALSO_MISMATCHES',
};

await mkdir(REPORT_DIR, { recursive: true });
await writeFile(REPORT_PATH, JSON.stringify({ ...summary, rows }, null, 2));

console.log(`PHASE_BASELINE_DATASET_PROVENANCE ${TIMEFRAME} CANONICAL=${trades.length}`);
console.log(`BASELINE_COMMIT=${BASELINE_COMMIT}`);
console.log(`SNAPSHOT candles=${summary.baselineDataset.candles} from=${summary.baselineDataset.from} to=${summary.baselineDataset.to}`);
console.log(`CURRENT  candles=${summary.currentDataset.candles} from=${summary.currentDataset.from} to=${summary.currentDataset.to}`);
console.log(`CURRENT_INDEX_TIME_MATCH=${summary.currentIndexTimeMatches}/${trades.length}`);
console.log(`SNAPSHOT_INDEX_TIME_MATCH=${summary.snapshotIndexTimeMatches}/${trades.length}`);
console.log(`SNAPSHOT_ENTRY_TIME_MISSING=${summary.snapshotEntryTimeMissing}`);
for (const row of rows.slice(0, 10)) {
  console.log(`CHECK index=${row.entryIndex} stored=${row.entryTime} snapshot=${row.snapshotTimestampAtIndex} current=${row.currentTimestampAtIndex}`);
}
console.log(`REPORT=${REPORT_PATH}`);
console.log(`STATUS=${summary.status}`);
