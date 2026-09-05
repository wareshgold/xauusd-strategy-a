import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASELINE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const DEV = 6000;
const PRE_HOLDOUT = 10000;

function finite(v) { return Number.isFinite(Number(v)); }

async function main() {
  const baseline = JSON.parse(await readFile(BASELINE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles;
  const trades = baseline.trades ?? [];
  const canonical = trades.filter(t => t.result !== 'AMBIGUOUS' && finite(t.rMultiple));

  const byReason = { validPreHoldout: [], freshHoldout: [], missingEntryIndex: [], invalidR: [], ambiguous: [] };
  for (const t of trades) {
    if (t.result === 'AMBIGUOUS') { byReason.ambiguous.push(t); continue; }
    if (!finite(t.rMultiple)) { byReason.invalidR.push(t); continue; }
    const idx = Number(t.entryIndex);
    if (!Number.isInteger(idx)) { byReason.missingEntryIndex.push(t); continue; }
    if (idx >= PRE_HOLDOUT) { byReason.freshHoldout.push(t); continue; }
    byReason.validPreHoldout.push(t);
  }

  const pathEligible = byReason.validPreHoldout.filter(t => Number(t.entryIndex) + 1 < candles.length);
  const noNextCandle = byReason.validPreHoldout.filter(t => Number(t.entryIndex) + 1 >= candles.length);
  const dev = pathEligible.filter(t => Number(t.entryIndex) < DEV);
  const val = pathEligible.filter(t => Number(t.entryIndex) >= DEV && Number(t.entryIndex) < PRE_HOLDOUT);

  const uniqueEntries = new Set(pathEligible.map(t => `${t.entryTime}|${t.entryIndex}|${t.direction}|${t.rMultiple}`));
  const duplicateCount = pathEligible.length - uniqueEntries.size;

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'GLOBAL_POST_ENTRY_PATH_COVERAGE_AUDIT',
    timeframe: '5m',
    baseline: {
      totalTrades: trades.length,
      canonicalNonAmbiguousFiniteR: canonical.length,
      ambiguousExcluded: byReason.ambiguous.length,
      invalidRExcluded: byReason.invalidR.length,
      missingEntryIndex: byReason.missingEntryIndex.length,
    },
    temporalPartition: {
      DEV: dev.length,
      VAL: val.length,
      preHoldoutPathEligible: pathEligible.length,
      freshHoldoutExcluded: byReason.freshHoldout.length,
      freshHoldoutBoundary: PRE_HOLDOUT,
      DEVBoundary: DEV,
    },
    pathCoverage: {
      preHoldoutExpected: byReason.validPreHoldout.length,
      preHoldoutJoinedByAssociation: pathEligible.length,
      missingNextCandle: noNextCandle.length,
      coverageRate: byReason.validPreHoldout.length ? pathEligible.length / byReason.validPreHoldout.length : 0,
      duplicateRows: duplicateCount,
    },
    interpretation: {
      associationUniverseShouldEqual: 'preHoldoutPathEligible',
      holdoutPolicy: 'Fresh holdout is excluded by entryIndex >= 10000.',
      noOptimization: true,
      noProductionChange: true,
    },
    missingNextCandleEntries: noNextCandle.map(t => ({ entryIndex: t.entryIndex, entryTime: t.entryTime, direction: t.direction, r: t.rMultiple })),
  };

  const out = resolve(ROOT, 'data/reports/strategy-a-global-post-entry-path-association/coverage-audit-5min.json');
  await import('node:fs/promises').then(fs => fs.writeFile(out, JSON.stringify(report, null, 2)));
  console.log(`5m COVERAGE AUDIT: baseline=${trades.length} canonical=${canonical.length} | DEV=${dev.length} VAL=${val.length} PRE=${pathEligible.length} FRESH_EXCLUDED=${byReason.freshHoldout.length}`);
  console.log(`  excluded: ambiguous=${byReason.ambiguous.length} invalidR=${byReason.invalidR.length} missingEntryIndex=${byReason.missingEntryIndex.length} missingNextCandle=${noNextCandle.length}`);
  console.log(`  coverage=${(report.pathCoverage.coverageRate * 100).toFixed(2)}% duplicates=${duplicateCount}`);
  console.log(`Report -> ${out}`);
}

await main();
