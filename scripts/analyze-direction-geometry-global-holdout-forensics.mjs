import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = process.cwd();
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-direction-geometry-global-holdout-forensics');
const SOURCE_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-geometry-forensics');
const MIN_N = 10;
const MIN_PF = 1.10;
const TOP_N = 30;

const FEATURES = [
  'impulseScore',
  'retracement',
  'entryLocation',
  'distanceFromExtreme',
  'delayFromImpulse',
  'impulseBodyFraction',
  'compressionRatio',
  'stopToImpulse',
];

function finite(v) { return Number.isFinite(Number(v)); }
function pf(rows) {
  let grossWin = 0, grossLoss = 0;
  for (const r of rows) {
    const x = Number(r.rMultiple);
    if (x > 0) grossWin += x;
    else if (x < 0) grossLoss += -x;
  }
  if (grossLoss === 0) return grossWin > 0 ? Infinity : null;
  return grossWin / grossLoss;
}
function stats(rows) {
  const xs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const p = pf(rows);
  return {
    n: xs.length,
    PF: p,
    avgR: xs.length ? xs.reduce((a,b)=>a+b,0) / xs.length : 0,
    totalR: xs.reduce((a,b)=>a+b,0),
  };
}
function globalSplits(rows) {
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
function bucketValues(rows, feature) {
  return [...new Set(rows.map(r => r[feature]).filter(v => v !== undefined && v !== null && String(v) !== ''))].sort();
}
function classifyDirection(r) {
  const d = String(r.direction ?? r.side ?? r.signalDirection ?? '').toUpperCase();
  if (d === 'BUY' || d === 'SELL') return d;
  return null;
}
function candidateRows(rows, direction, feature, bucket) {
  return rows.filter(r => classifyDirection(r) === direction && String(r[feature]) === String(bucket));
}
function passes(s) { return s.n >= MIN_N && s.PF != null && s.PF >= MIN_PF && s.avgR > 0; }

async function run(timeframe) {
  const p = resolve(SOURCE_DIR, `${timeframe}.json`);
  const src = JSON.parse(await readFile(p, 'utf8'));
  const raw = src.tradeRows || [];
  if (!raw.length) throw new Error(`${timeframe}: missing tradeRows`);
  const rows = raw.filter(r => finite(r.rMultiple) && classifyDirection(r)).sort((a,b) => new Date(a.entryTime) - new Date(b.entryTime));
  const split = globalSplits(rows);
  const all = [];
  for (const direction of ['BUY','SELL']) {
    for (const feature of FEATURES) {
      for (const bucket of bucketValues(rows, feature)) {
        const selected = candidateRows(rows, direction, feature, bucket);
        const dev = stats(selected.filter(r => split.dev.includes(r)));
        const validation = stats(selected.filter(r => split.validation.includes(r)));
        const holdout = stats(selected.filter(r => split.holdout.includes(r)));
        all.push({ direction, feature, bucket, dev, validation, holdout, passesDevValidation: passes(dev) && passes(validation) });
      }
    }
  }
  const candidates = all.filter(x => x.passesDevValidation).sort((a,b) => (b.validation.PF ?? -Infinity) - (a.validation.PF ?? -Infinity) || b.validation.avgR - a.validation.avgR || b.validation.n - a.validation.n);
  const robust = candidates.filter(x => x.holdout.n >= MIN_N && x.holdout.PF != null && x.holdout.PF >= MIN_PF && x.holdout.avgR > 0).sort((a,b) => (b.holdout.PF ?? -Infinity) - (a.holdout.PF ?? -Infinity) || b.holdout.avgR - a.holdout.avgR);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_DIRECTION_GEOMETRY_GLOBAL_HOLDOUT_FORENSICS_V1',
    timeframe,
    scope: 'BUY/SELL × one fixed geometry bucket, evaluated on one shared chronological DEV/VALIDATION/HOLDOUT partition',
    methodology: {
      source: 'strategy-a-entry-geometry-forensics tradeRows',
      search: 'BUY and SELL independently across each fixed geometry definition; no multi-geometry combinations',
      split: 'single global chronological thirds across the complete classified trade universe; same date boundaries for every candidate',
      selectionGate: `DEV and VALIDATION each n >= ${MIN_N}, PF >= ${MIN_PF}, avgR > 0`,
      holdoutGate: `HOLDOUT n >= ${MIN_N}, PF >= ${MIN_PF}, avgR > 0`,
      warning: 'HOLDOUT is not used for ranking; positive holdout results remain exploratory until robustness and multiple-comparison controls are completed.',
    },
    globalBoundaries: split.boundaries,
    globalCounts: { all: rows.length, dev: split.dev.length, validation: split.validation.length, holdout: split.holdout.length },
    pairTests: all.length,
    devValidationCandidates: candidates.length,
    robustHoldoutCandidates: robust.length,
    topCandidates: candidates.slice(0, TOP_N),
    robustCandidates: robust.slice(0, TOP_N),
    allResults: all,
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: trades=${rows.length} tests=${all.length} devValidationCandidates=${candidates.length} robustHoldoutCandidates=${robust.length}`);
  for (const c of candidates.slice(0, TOP_N)) {
    console.log(`  ${c.direction} + ${c.feature}=${c.bucket}: DEV n=${c.dev.n} PF=${c.dev.PF?.toFixed?.(4) ?? 'n/a'} avgR=${c.dev.avgR.toFixed(4)} | VAL n=${c.validation.n} PF=${c.validation.PF?.toFixed?.(4) ?? 'n/a'} avgR=${c.validation.avgR.toFixed(4)} | HOLDOUT n=${c.holdout.n} PF=${c.holdout.PF?.toFixed?.(4) ?? 'n/a'} avgR=${c.holdout.avgR.toFixed(4)} totalR=${c.holdout.totalR.toFixed(4)}${c.holdout.PF != null && c.holdout.PF >= MIN_PF && c.holdout.avgR > 0 && c.holdout.n >= MIN_N ? ' ROBUST_HOLDOUT' : ''}`);
  }
  console.log(`Report -> ${out}`);
}

for (const tf of ['1min','5min']) await run(tf);
