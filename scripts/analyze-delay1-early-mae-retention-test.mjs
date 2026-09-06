import { readFile, mkdir, writeFile } from 'node:fs/promises';
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
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-early-mae-retention-test');
const PRE = 10000;
const DEV = 6000;
const BANDS = [0.25, 0.5, 0.75, 1.0];

const CTX = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 960, endMinutes: 1320 },
  ],
  avoidWindows: [],
};

const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { const v = [...a].filter(finite).sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };
const pct = (n, d) => d ? n / d : null;

function pf(rs) {
  const wins = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? wins / losses : null;
}

function stats(rows) {
  const rs = rows.map(r => r.rMultiple).filter(finite);
  const wins = rs.filter(x => x > 0);
  const losses = rs.filter(x => x < 0);
  return {
    n: rows.length,
    avgR: mean(rs),
    medianR: median(rs),
    WR: pct(wins.length, rs.length),
    PF: pf(rs),
    totalR: rs.reduce((a, b) => a + b, 0),
    exceptional: rs.filter(x => x >= 5).length,
  };
}

function key(t) {
  return `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
}

function candidate(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < 60) return null;
  const bo = detectBreakout(v, 5);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: 0.5, maxOverlapFraction: 0.8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const cor = detectFirstCorrection(v, spike);
    if (!cor || cor.correctionExtremeIndex >= index || index - cor.correctionExtremeIndex !== 1) continue;
    const tr = detectEntryTrigger(v, cor);
    if (!tr || tr.index !== index) continue;
    const pr = projectLeg2(v, cor);
    if (!pr) continue;
    const inv = getInvalidationRule(cor);
    const ema = buildEMAContext(v.map(c => c.close), CTX);
    if (!ema) continue;
    const loc = buildLocationContext(tr.entryPrice, CTX);
    const ses = buildSessionContext(tr.timestamp, CTX);
    if (!scoreSetup(spike, { ema, location: loc, session: ses }).tradeAllowed) continue;
    const risk = Math.abs(tr.entryPrice - inv.invalidationLevel);
    if (!(risk > 0)) continue;
    if (!(tr.direction === 'BUY' ? pr.tp1 > tr.entryPrice : pr.tp1 < tr.entryPrice)) continue;
    return {
      entryIndex: index,
      direction: tr.direction,
      entry: tr.entryPrice,
      stopLoss: inv.invalidationLevel,
      tp1: pr.tp1,
      risk,
    };
  }
  return null;
}

function maeAt(candles, c, horizon) {
  const end = c.entryIndex + horizon;
  if (end >= candles.length) return null;
  let mae = 0;
  for (let j = c.entryIndex + 1; j <= end; j++) {
    const x = candles[j];
    const adverse = (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk;
    mae = Math.max(mae, Math.max(0, adverse));
  }
  return mae;
}

function retention(rows, feature, maxMae) {
  const complete = rows.filter(r => finite(r[feature]));
  const retained = complete.filter(r => r[feature] < maxMae);
  const removed = complete.filter(r => r[feature] >= maxMae);
  const winnersRemoved = removed.filter(r => r.rMultiple > 0).length;
  const losersRemoved = removed.filter(r => r.rMultiple < 0).length;
  const exceptionalRemoved = removed.filter(r => r.rMultiple >= 5).length;
  return {
    threshold: maxMae,
    source: stats(complete),
    retained: stats(retained),
    removed: stats(removed),
    retainedFraction: pct(retained.length, complete.length),
    removedFraction: pct(removed.length, complete.length),
    winnersRemoved,
    losersRemoved,
    exceptionalRemoved,
    loserToWinnerRemovalRatio: winnersRemoved > 0 ? losersRemoved / winnersRemoved : null,
    totalRRemoved: removed.reduce((s, r) => s + r.rMultiple, 0),
    totalRRetained: retained.reduce((s, r) => s + r.rMultiple, 0),
  };
}

function evaluate(rows, feature) {
  const result = {};
  for (const threshold of BANDS) result[threshold] = retention(rows, feature, threshold);
  return result;
}

async function load() {
  const raw = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE) throw new Error(`5min: expected at least ${PRE} candles, found ${candles.length}`);
  const baseline = JSON.parse(await readFile(resolve(BASE, '5min.json'), 'utf8')).trades ?? [];
  const usable = baseline.filter(t => t.result !== 'AMBIGUOUS' && finite(Number(t.rMultiple)) && Number(t.entryIndex) < PRE);
  const counts = new Map();
  for (const t of usable) counts.set(key(t), (counts.get(key(t)) ?? 0) + 1);
  const duplicates = [...counts.entries()].filter(([, n]) => n > 1);
  if (duplicates.length) throw new Error(`Duplicate canonical baseline keys: ${duplicates.length}`);
  const byKey = new Map(usable.map(t => [key(t), t]));
  const rows = [];
  let candidates = 0, matched = 0;
  for (let i = 0; i < PRE; i++) {
    const c = candidate(candles, i);
    if (!c) continue;
    candidates++;
    const t = byKey.get(key(c));
    if (!t) continue;
    matched++;
    const sameBarSL = c.direction === 'BUY'
      ? candles[i + 1]?.low <= c.stopLoss
      : candles[i + 1]?.high >= c.stopLoss;
    const t1 = maeAt(candles, c, 1);
    const t3 = maeAt(candles, c, 3);
    const t5 = maeAt(candles, c, 5);
    const t10 = maeAt(candles, c, 10);
    if (![t1, t3, t5, t10].every(finite)) continue;
    rows.push({
      entryIndex: Number(t.entryIndex),
      direction: t.direction,
      rMultiple: Number(t.rMultiple),
      sameBarSL,
      t1Mae: t1,
      t3Mae: t3,
      t5Mae: t5,
      t10Mae: t10,
    });
  }
  return { candles, rows, baselinePre: usable.length, candidates, matched, duplicateKeys: duplicates.length };
}

function compact(s) {
  return `N=${s.n} avgR=${finite(s.avgR) ? s.avgR.toFixed(4) : 'NA'} PF=${finite(s.PF) ? s.PF.toFixed(4) : 'NA'} WR=${finite(s.WR) ? (s.WR * 100).toFixed(2) : 'NA'}%`;
}

async function run() {
  const loaded = await load();
  const rows = loaded.rows;
  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const post = rows.filter(r => !r.sameBarSL);
  const postDev = post.filter(r => r.entryIndex < DEV);
  const postVal = post.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_EARLY_MAE_RETENTION_TEST',
    timeframe: '5min',
    scope: { preHoldoutCandles: PRE, devCutoff: DEV, freshHoldoutAccessed: false, freshHoldoutLocked: true },
    integrity: {
      baselinePreHoldout: loaded.baselinePre,
      reconstructedCandidates: loaded.candidates,
      matchedCandidates: loaded.matched,
      rows: rows.length,
      devN: dev.length,
      valN: val.length,
      duplicateCanonicalKeys: loaded.duplicateKeys,
      sameBarSL: rows.filter(r => r.sameBarSL).length,
      postEntryN: post.length,
      completeAtAllHorizons: rows.length,
    },
    methodology: {
      purpose: 'Diagnostic retention-value test for fixed pre-declared MAE bands; not an exit simulation',
      features: ['t1Mae', 't3Mae', 't5Mae', 't10Mae'],
      thresholdsR: BANDS,
      retentionRuleForDiagnostic: 'retain only rows with MAE < fixed threshold at the stated horizon',
      retainedOutcome: 'canonical baseline final rMultiple; used only to measure selection/retention value',
      removedOutcome: 'canonical baseline final rMultiple; not interpreted as realized exit P&L',
      postEntryPopulation: 'same-bar SL rows excluded to test whether value survives mechanical stop-loss conditioning',
      noThresholdOptimization: true,
      noExitRuleCreation: true,
      noBrokerExecutionModel: true,
      diagnosticOnly: true,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    baseline: {
      all: stats(rows),
      dev: stats(dev),
      val: stats(val),
      postEntry: stats(post),
      postEntryDev: stats(postDev),
      postEntryVal: stats(postVal),
    },
    retention: {},
  };

  for (const feature of ['t1Mae', 't3Mae', 't5Mae', 't10Mae']) {
    report.retention[feature] = {
      all: evaluate(rows, feature),
      dev: evaluate(dev, feature),
      val: evaluate(val, feature),
      postEntryAll: evaluate(post, feature),
      postEntryDev: evaluate(postDev, feature),
      postEntryVal: evaluate(postVal, feature),
    };
  }

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(report, null, 2));

  console.log(`PHASE_10B_EARLY_MAE_RETENTION N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${loaded.baselinePre} candidates=${loaded.candidates} matched=${loaded.matched} duplicateKeys=${loaded.duplicateKeys} complete=${rows.length}`);
  console.log(`POPULATION all=${rows.length} sameBarSL=${rows.filter(r => r.sameBarSL).length} postEntry=${post.length}`);
  console.log(`BASELINE ALL ${compact(stats(rows))} | POST_ENTRY ${compact(stats(post))}`);
  console.log('=== FIXED RETENTION TEST (DIAGNOSTIC; NO THRESHOLD SELECTION) ===');
  for (const feature of ['t1Mae', 't3Mae', 't5Mae', 't10Mae']) {
    console.log(`\n${feature}`);
    for (const threshold of BANDS) {
      const d = report.retention[feature].postEntryDev[threshold];
      const v = report.retention[feature].postEntryVal[threshold];
      console.log(`  <${threshold.toFixed(2)}R | DEV retained=${compact(d.retained)} removed=${compact(d.removed)} Wremoved=${d.winnersRemoved} Lremoved=${d.losersRemoved} Xremoved=${d.exceptionalRemoved} | VAL retained=${compact(v.retained)} removed=${compact(v.removed)} Wremoved=${v.winnersRemoved} Lremoved=${v.losersRemoved} Xremoved=${v.exceptionalRemoved}`);
    }
  }
  console.log('\nSTATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

run().catch(err => { console.error(err); process.exitCode = 1; });
