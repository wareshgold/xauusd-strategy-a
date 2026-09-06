import fs from 'node:fs';
import path from 'node:path';

const REPORT_DIR = 'data/reports/strategy-a-delay1-early-mae-recovery-transition';
const REPORT_FILE = path.join(REPORT_DIR, '5m.json');
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [3, 5, 10];
const STATES = [0.25, 0.5, 0.75, 1.0];

// Phase 10C is a diagnostic state-transition study only.
// It does not select thresholds, create exits, or access the fresh holdout.
const ROOT = path.resolve(process.cwd());
const loadJson = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

function finite(x) { return Number.isFinite(x); }
function mean(xs) { return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null; }
function pf(rows) {
  const wins = rows.filter(r => r.rMultiple > 0).reduce((s, r) => s + r.rMultiple, 0);
  const losses = rows.filter(r => r.rMultiple < 0).reduce((s, r) => s + Math.abs(r.rMultiple), 0);
  return losses > 0 ? wins / losses : null;
}
function stats(rows) {
  return {
    n: rows.length,
    avgR: mean(rows.map(r => r.rMultiple)),
    pf: pf(rows),
    winRate: rows.length ? rows.filter(r => r.rMultiple > 0).length / rows.length : null,
    exceptional: rows.filter(r => r.rMultiple >= 5).length,
  };
}
function state(mae) {
  if (!finite(mae)) return null;
  if (mae < 0.25) return '<0.25R';
  if (mae < 0.5) return '0.25-0.50R';
  if (mae < 0.75) return '0.50-0.75R';
  if (mae < 1.0) return '0.75-1.00R';
  return '>=1.00R';
}
function maxAdverse(pathRows, direction, entry, risk) {
  if (!risk || !finite(risk)) return null;
  let max = 0;
  for (const c of pathRows) {
    const adverse = direction === 'BUY' ? (entry - c.low) / risk : (c.high - entry) / risk;
    if (finite(adverse)) max = Math.max(max, adverse);
  }
  return max;
}
function maxFavorable(pathRows, direction, entry, risk) {
  if (!risk || !finite(risk)) return null;
  let max = 0;
  for (const c of pathRows) {
    const favorable = direction === 'BUY' ? (c.high - entry) / risk : (entry - c.low) / risk;
    if (finite(favorable)) max = Math.max(max, favorable);
  }
  return max;
}
function canonicalKey(t) {
  return `${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`;
}

// This analyzer intentionally reads the already-produced Phase 10 post-entry report.
// The report contains the canonical DELAY1 rows and their 20-bar path measurements.
const source = loadJson('data/reports/strategy-a-post-entry-path-dynamics/5m.json');
const rows = source.rows ?? source.trades ?? [];
if (!Array.isArray(rows) || rows.length === 0) throw new Error('Phase 10 source rows not found');

const delay1 = rows.filter(r => r.delay1 === true || r.triggerDelay === 1 || r.entryDelayFromCorrection === 1 || r.correctionExtremeIndex === r.entryIndex - 1);
const usable = delay1.filter(r => finite(r.rMultiple) && r.result !== 'AMBIGUOUS' && r.entryIndex < PRE);

const integrity = {
  baselinePre: source.integrity?.baselinePre ?? null,
  candidates: source.integrity?.candidates ?? null,
  matched: usable.length,
  duplicateKeys: new Set(usable.map(canonicalKey)).size === usable.length ? 0 : usable.length - new Set(usable.map(canonicalKey)).size,
  complete: usable.length === 144,
  freshHoldoutExcluded: true,
};
if (!integrity.complete || integrity.duplicateKeys !== 0) throw new Error(`Integrity gate failed: matched=${integrity.matched} duplicateKeys=${integrity.duplicateKeys}`);

// Path rows are expected in the source report as path candles. If unavailable, reconstruct
// MAE/MFE only from the source's fixed-horizon values; no new detector semantics are introduced.
function horizonMae(r, h) {
  const direct = r[`t${h}Mae`];
  return finite(direct) ? direct : null;
}
function horizonMfe(r, h) {
  const direct = r[`t${h}Mfe`];
  return finite(direct) ? direct : null;
}

const horizons = {};
for (const h of HORIZONS) {
  const valid = usable.filter(r => finite(horizonMae(r, h)) && finite(horizonMfe(r, h)));
  const byState = {};
  for (const s of ['<0.25R', '0.25-0.50R', '0.50-0.75R', '0.75-1.00R', '>=1.00R']) {
    const subset = valid.filter(r => state(horizonMae(r, h)) === s);
    const recovered1 = subset.filter(r => horizonMfe(r, 10) >= 1).length;
    const recovered2 = subset.filter(r => horizonMfe(r, 10) >= 2).length;
    const failed = subset.filter(r => horizonMfe(r, 10) < 1).length;
    byState[s] = {
      n: subset.length,
      outcome: stats(subset),
      eventualMfe10: {
        ge1R: subset.length ? recovered1 / subset.length : null,
        ge2R: subset.length ? recovered2 / subset.length : null,
        lt1R: subset.length ? failed / subset.length : null,
      },
    };
  }

  const transitions = {};
  for (const from of ['<0.25R', '0.25-0.50R', '0.50-0.75R', '0.75-1.00R', '>=1.00R']) {
    transitions[from] = {};
    const fromRows = valid.filter(r => state(horizonMae(r, h)) === from);
    for (const toH of HORIZONS.filter(x => x > h)) {
      const to = {};
      for (const s of ['<0.25R', '0.25-0.50R', '0.50-0.75R', '0.75-1.00R', '>=1.00R']) {
        const n = fromRows.filter(r => state(horizonMae(r, toH)) === s).length;
        to[s] = fromRows.length ? n / fromRows.length : null;
      }
      transitions[from][`T${toH}`] = to;
    }
  }

  const recovery = {
    anyRecoveryTo1R: valid.filter(r => horizonMae(r, h) >= 0.5 && horizonMfe(r, 10) >= 1).length,
    adverseGE1R_thenMfeGE1R: valid.filter(r => horizonMae(r, h) >= 1 && horizonMfe(r, 10) >= 1).length,
    adverseGE1R_thenMfeGE2R: valid.filter(r => horizonMae(r, h) >= 1 && horizonMfe(r, 10) >= 2).length,
    denominatorGE1R: valid.filter(r => horizonMae(r, h) >= 1).length,
  };

  horizons[`T${h}`] = { n: valid.length, byState, transitions, recovery };
}

const report = {
  phase: '10C',
  name: 'Early-MAE Recovery/Failure State Transition',
  timeframe: '5m',
  universe: { n: usable.length, dev: usable.filter(r => r.entryIndex < DEV).length, val: usable.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE).length },
  integrity,
  fixedStates: STATES,
  horizons,
  methodology: {
    freshHoldoutExcluded: true,
    noThresholdOptimization: true,
    noExitRuleCreation: true,
    noBrokerExecutionModel: true,
    diagnosticOnly: true,
    productionUntouched: true,
    outcomeUsesCanonicalFinalR: true,
    stateTransitionsUseFixedExistingHorizons: true,
  },
};

fs.mkdirSync(path.join(ROOT, REPORT_DIR), { recursive: true });
fs.writeFileSync(path.join(ROOT, REPORT_FILE), JSON.stringify(report, null, 2));

console.log(`PHASE_10C_EARLY_MAE_RECOVERY N=${usable.length} DEV=${report.universe.dev} VAL=${report.universe.val} FRESH=LOCKED`);
console.log(`INTEGRITY baselinePre=${integrity.baselinePre} candidates=${integrity.candidates} matched=${integrity.matched} duplicateKeys=${integrity.duplicateKeys} complete=${integrity.complete}`);
for (const h of HORIZONS) {
  const d = horizons[`T${h}`];
  console.log(`\nT${h} STATE OUTCOMES`);
  for (const [s, x] of Object.entries(d.byState)) {
    const o = x.outcome;
    const r = x.eventualMfe10;
    console.log(`${s} N=${o.n} WR=${o.winRate == null ? 'NA' : (o.winRate * 100).toFixed(2) + '%'} avgR=${o.avgR == null ? 'NA' : o.avgR.toFixed(4)} PF=${o.pf == null ? 'NA' : o.pf.toFixed(4)} | MFE10>=1R=${r.ge1R == null ? 'NA' : (r.ge1R * 100).toFixed(2) + '%'} >=2R=${r.ge2R == null ? 'NA' : (r.ge2R * 100).toFixed(2) + '%'}`);
  }
}
console.log('\n=== ADVERSE >=1R RECOVERY ===');
for (const h of HORIZONS) {
  const r = horizons[`T${h}`].recovery;
  const den = r.denominatorGE1R;
  console.log(`T${h}: N=${den} -> MFE10>=1R ${r.adverseGE1R_thenMfeGE1R} (${den ? (r.adverseGE1R_thenMfeGE1R / den * 100).toFixed(2) : 'NA'}%) | MFE10>=2R ${r.adverseGE1R_thenMfeGE2R} (${den ? (r.adverseGE1R_thenMfeGE2R / den * 100).toFixed(2) : 'NA'}%)`);
}
console.log('\nSTATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
