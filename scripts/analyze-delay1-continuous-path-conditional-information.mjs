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
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-nested-conditional-information');
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const BIN_COUNTS = [3, 4, 5];
const PERMUTATIONS = 499;
const SEED = 20260905;
const CONTEXT = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };

const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const finite = x => Number.isFinite(x);
const rng = seed => { let s = seed >>> 0; return () => { s += 0x6D2B79F5; let t = s; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; };

function rank(a) {
  const s = a.map((x, i) => ({ x, i })).sort((u, v) => u.x - v.x);
  const r = Array(a.length); let k = 0;
  while (k < s.length) { let j = k + 1; while (j < s.length && s[j].x === s[k].x) j++; const v = (k + j - 1) / 2 + 1; for (let i = k; i < j; i++) r[s[i].i] = v; k = j; }
  return r;
}
function pearson(x, y) {
  if (x.length < 5) return null;
  const mx = mean(x), my = mean(y); let n = 0, dx = 0, dy = 0;
  for (let i = 0; i < x.length; i++) { const a = x[i] - mx, b = y[i] - my; n += a * b; dx += a * a; dy += b * b; }
  return dx > 0 && dy > 0 ? n / Math.sqrt(dx * dy) : null;
}
function spearman(x, y) {
  const z = x.map((v, i) => [v, y[i]]).filter(q => finite(q[0]) && finite(q[1]));
  return z.length < 5 ? null : pearson(rank(z.map(q => q[0])), rank(z.map(q => q[1])));
}

function quantileEdges(values, bins) {
  const a = values.filter(finite).sort((x, y) => x - y);
  if (!a.length) return [];
  const edges = [];
  for (let i = 1; i < bins; i++) {
    const p = (a.length - 1) * i / bins, lo = Math.floor(p), hi = Math.ceil(p);
    edges.push(a[lo] + (a[hi] - a[lo]) * (p - lo));
  }
  return [...new Set(edges.filter(finite))];
}
function binValue(v, edges) {
  if (!finite(v)) return null;
  let k = 0; while (k < edges.length && v > edges[k]) k++;
  return k;
}
function fitDiscretizer(rows, bins) {
  const specs = {};
  for (const name of ['y', 'T1_MAE', 'T2_MAE', 'T3_MAE']) specs[name] = quantileEdges(rows.map(r => r[name]), bins);
  return specs;
}
function discreteRows(rows, specs) {
  return rows.map(r => ({ y: binValue(r.y, specs.y), T1_MAE: binValue(r.T1_MAE, specs.T1_MAE), T2_MAE: binValue(r.T2_MAE, specs.T2_MAE), T3_MAE: binValue(r.T3_MAE, specs.T3_MAE) })).filter(r => Object.values(r).every(v => v !== null));
}
function entropyCounts(counts, total) { if (!total) return 0; let h = 0; for (const n of counts.values()) if (n) { const p = n / total; h -= p * Math.log(p); } return h; }
function conditionalEntropy(rows, yKey, controls) {
  if (!rows.length) return null;
  if (!controls.length) return entropyCounts(new Map([...new Set(rows.map(r => r[yKey]))].map(k => [k, rows.filter(r => r[yKey] === k).length])), rows.length);
  const groups = new Map();
  for (const r of rows) { const key = controls.map(c => r[c]).join('|'); let g = groups.get(key); if (!g) groups.set(key, g = []); g.push(r[yKey]); }
  let h = 0; for (const g of groups.values()) { const counts = new Map(); for (const y of g) counts.set(y, (counts.get(y) ?? 0) + 1); h += (g.length / rows.length) * entropyCounts(counts, g.length); }
  return h;
}
function conditionalMI(rows, feature, controls) {
  const a = conditionalEntropy(rows, 'y', controls);
  const b = conditionalEntropy(rows.map(r => ({ ...r, _z: [...controls, feature] })), 'y', [...controls, feature]);
  return a === null || b === null ? null : Math.max(0, a - b);
}
function shuffleWithinControls(rows, feature, controls, random) {
  const out = rows.map(r => ({ ...r }));
  const groups = new Map();
  for (let i = 0; i < rows.length; i++) { const key = controls.map(c => rows[i][c]).join('|'); let g = groups.get(key); if (!g) groups.set(key, g = []); g.push(i); }
  for (const idx of groups.values()) {
    const vals = idx.map(i => rows[i][feature]);
    for (let i = vals.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [vals[i], vals[j]] = [vals[j], vals[i]]; }
    idx.forEach((i, k) => { out[i][feature] = vals[k]; });
  }
  return out;
}
function permutationPValue(rows, feature, controls, observed, seed) {
  if (rows.length < 20 || observed === null) return null;
  const random = rng(seed); let ge = 0;
  for (let i = 0; i < PERMUTATIONS; i++) {
    const perm = shuffleWithinControls(rows, feature, controls, random);
    const v = conditionalMI(perm, feature, controls);
    if (v !== null && v >= observed - 1e-12) ge++;
  }
  return (ge + 1) / (PERMUTATIONS + 1);
}
function candidate(candles, index) {
  const v = candles.slice(0, index + 1); if (v.length < 60) return null;
  const bo = detectBreakout(v, 5), ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const cor = detectFirstCorrection(v, spike); if (!cor || cor.correctionExtremeIndex >= index || index - cor.correctionExtremeIndex !== 1) continue;
    const tr = detectEntryTrigger(v, cor); if (!tr || tr.index !== index) continue;
    const pr = projectLeg2(v, cor); if (!pr) continue;
    const inv = getInvalidationRule(cor), ema = buildEMAContext(v.map(c => c.close), CONTEXT), loc = buildLocationContext(tr.entryPrice, CONTEXT), ses = buildSessionContext(tr.timestamp, CONTEXT);
    if (!ema || !scoreSetup(spike, { ema, location: loc, session: ses }).tradeAllowed) continue;
    const risk = Math.abs(tr.entryPrice - inv.invalidationLevel); if (!(risk > 0)) continue;
    return { entryIndex: index, entryTime: tr.timestamp, direction: tr.direction, entry: tr.entryPrice, stopLoss: inv.invalidationLevel, tp1: pr.tp1, risk };
  }
  return null;
}
function path(c) {
  const out = []; let mae = 0, mfe = 0;
  for (let j = c.entryIndex + 1; j <= Math.min(c.entryIndex + 20, c.candles.length - 1); j++) {
    const x = c.candles[j], adv = Math.max(0, (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk), fav = Math.max(0, (c.direction === 'BUY' ? x.high - c.entry : c.entry - x.low) / c.risk);
    mae = Math.max(mae, adv); mfe = Math.max(mfe, fav); out.push({ bar: j - c.entryIndex, mae, mfe });
  }
  return out;
}
async function buildRows(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')), candles = raw.candles ?? raw;
  const base = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8')).trades ?? [];
  const byKey = new Map(base.filter(t => t.result !== 'AMBIGUOUS').map(t => [`${t.entryIndex}|${t.direction}|${Number(t.entry).toPrecision(15)}|${Number(t.stopLoss).toPrecision(15)}|${Number(t.tp1).toPrecision(15)}`, t]));
  const rows = [];
  for (let i = 0; i < PRE; i++) {
    const c = candidate(candles, i); if (!c) continue;
    const k = `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`, t = byKey.get(k); if (!t) continue;
    const p = path({ ...c, candles }); if (p.length !== 20) continue;
    rows.push({ entryIndex: i, r: Number(t.rMultiple), T1_MAE: p[0].mae, T2_MAE: p[1].mae, T3_MAE: p[2].mae, T1_MFE: p[0].mfe, T2_MFE: p[1].mfe, T3_MFE: p[2].mfe });
  }
  return rows;
}
function analyze(rows, splitName, seedOffset) {
  const out = { split: splitName, n: rows.length, binCounts: {} };
  for (const bins of BIN_COUNTS) {
    const specs = fitDiscretizer(rows.filter(r => r.entryIndex < DEV), bins);
    const usable = discreteRows(rows, specs).map((r, i) => ({ ...r, original: rows.filter(q => q.entryIndex < DEV)[i] }));
    // The caller supplies already split rows; for DEV the discretizer is fitted on the same rows, for VAL it is fitted on DEV externally.
    out.binCounts[bins] = specs;
    out.binCounts[bins].results = {};
    const chain = [['T1_MAE', []], ['T2_MAE', ['T1_MAE']], ['T3_MAE', ['T1_MAE', 'T2_MAE']]];
    for (const [feature, controls] of chain) {
      const observed = conditionalMI(usable, feature, controls);
      out.binCounts[bins].results[feature] = { controls, conditionalMutualInformationNats: observed, permutationPValue: permutationPValue(usable, feature, controls, observed, SEED + seedOffset + bins * 100 + feature.length) };
    }
  }
  return out;
}
function analyzeWithFixedSpecs(rows, devRows, splitName, seedOffset) {
  const out = { split: splitName, n: rows.length, binCounts: {} };
  for (const bins of BIN_COUNTS) {
    const specs = fitDiscretizer(devRows, bins);
    const usable = discreteRows(rows, specs);
    const results = {};
    for (const [feature, controls] of [['T1_MAE', []], ['T2_MAE', ['T1_MAE']], ['T3_MAE', ['T1_MAE', 'T2_MAE']]]) {
      const observed = conditionalMI(usable, feature, controls);
      results[feature] = { controls, conditionalMutualInformationNats: observed, permutationPValue: permutationPValue(usable, feature, controls, observed, SEED + seedOffset + bins * 100 + feature.length) };
    }
    out.binCounts[bins] = { fittedOn: splitName === 'DEV' ? 'DEV' : 'DEV_ONLY', specs, results };
  }
  return out;
}
function summarizeAcrossBins(split) {
  const summary = {};
  for (const feature of ['T1_MAE', 'T2_MAE', 'T3_MAE']) {
    const values = BIN_COUNTS.map(b => split.binCounts[b].results[feature].conditionalMutualInformationNats).filter(finite);
    const p = BIN_COUNTS.map(b => split.binCounts[b].results[feature].permutationPValue).filter(finite);
    summary[feature] = { cmiNatsMeanAcrossFixedBins: mean(values), cmiNatsByBinCount: Object.fromEntries(BIN_COUNTS.map(b => [b, split.binCounts[b].results[feature].conditionalMutualInformationNats])), permutationPValueByBinCount: Object.fromEntries(BIN_COUNTS.map(b => [b, split.binCounts[b].results[feature].permutationPValue])), minPValue: p.length ? Math.min(...p) : null };
  }
  return summary;
}
async function run(tf) {
  const rows = await buildRows(tf), devRows = rows.filter(r => r.entryIndex < DEV), valRows = rows.filter(r => r.entryIndex >= DEV);
  const dev = analyzeWithFixedSpecs(devRows, devRows, 'DEV', 0), val = analyzeWithFixedSpecs(valRows, devRows, 'VAL', 100000);
  const report = { strategy: 'Strategy A', mode: 'DELAY1_NESTED_CONDITIONAL_INFORMATION', timeframe: tf, scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutExcluded: true, delayExactly: 1 }, methodology: { quantity: 'Discrete conditional mutual information I(Y; X | C) = H(Y|C) - H(Y|C,X), measured in nats.', nestedChain: ['I(Y; T1_MAE)', 'I(Y; T2_MAE | T1_MAE)', 'I(Y; T3_MAE | T1_MAE,T2_MAE)'], discretization: 'Equal-frequency quantile bins fitted on DEV only and reused unchanged on VAL.', fixedBinCounts: BIN_COUNTS, nullTest: `Conditional permutation of the candidate feature within exact control strata; ${PERMUTATIONS} permutations; deterministic seed.`, noThresholdOptimization: true, diagnosticOnly: true, productionUntouched: true }, overall: { n: rows.length, devN: devRows.length, valN: valRows.length }, dev, val, summary: { dev: summarizeAcrossBins(dev), val: summarizeAcrossBins(val) } };
  await mkdir(OUT, { recursive: true });
  const file = resolve(OUT, `${tf}.json`); await writeFile(file, JSON.stringify(report, null, 2));
  console.log(`\n=== ${tf} NESTED CONDITIONAL INFORMATION ===`); console.log(`joined=${rows.length} dev=${devRows.length} val=${valRows.length}`);
  for (const f of ['T1_MAE', 'T2_MAE', 'T3_MAE']) console.log(`${f}: DEV meanCMI=${report.summary.dev[f].cmiNatsMeanAcrossFixedBins?.toFixed(4) ?? 'n/a'} minP=${report.summary.dev[f].minPValue ?? 'n/a'} | VAL meanCMI=${report.summary.val[f].cmiNatsMeanAcrossFixedBins?.toFixed(4) ?? 'n/a'} minP=${report.summary.val[f].minPValue ?? 'n/a'}`);
  console.log(`Report -> ${file}`);
}
for (const tf of ['1min', '5min']) await run(tf);
