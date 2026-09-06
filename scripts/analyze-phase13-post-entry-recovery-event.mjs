import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { buildSessionContext } from '../src/domain/strategy-a/Context.js';

const ROOT = resolve(process.cwd());
const PRE = 10000;
const DEV = 6000;
const BLOCK = 2000;
const H20 = 20;
const MAE_BOUNDARY = 0.5;
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase13-post-entry-recovery-event');
const CONTEXT = { tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 960, endMinutes: 1320 }] };

const stats = rows => {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const grossWin = wins.reduce((s, x) => s + x, 0), grossLoss = -losses.reduce((s, x) => s + x, 0);
  return { n: rs.length, avgR: rs.length ? rs.reduce((s, x) => s + x, 0) / rs.length : null, PF: grossLoss ? grossWin / grossLoss : null, WR: rs.length ? wins.length / rs.length : null, totalR: rs.reduce((s, x) => s + x, 0) };
};
const fmt = x => Number.isFinite(x) ? x.toFixed(4) : '-';

function path(candles, trade) {
  const entry = Number(trade.entry), stopLoss = Number(trade.stopLoss), entryIndex = Number(trade.entryIndex);
  const risk = Math.abs(entry - stopLoss);
  if (!(risk > 0) || !Number.isInteger(entryIndex)) return [];
  const out = [];
  for (let j = entryIndex + 1; j <= Math.min(candles.length - 1, entryIndex + H20); j++) {
    const x = candles[j];
    out.push({ bar: j - entryIndex, adverse: Math.max(0, (trade.direction === 'BUY' ? entry - x.low : x.high - entry) / risk), close: x.close });
  }
  return out;
}

function classify(trade, p) {
  let mae = 0, adverseBar = null;
  for (const x of p) {
    mae = Math.max(mae, x.adverse);
    if (adverseBar === null && mae >= MAE_BOUNDARY) adverseBar = x.bar;
  }
  if (adverseBar === null) return { state: 'NO_ADVERSE_0_5R', adverseBar: null, recoveryBar: null };
  for (const x of p) {
    if (x.bar <= adverseBar) continue;
    const recovered = trade.direction === 'BUY' ? x.close >= Number(trade.entry) : x.close <= Number(trade.entry);
    if (recovered) return { state: 'RECOVERY_AFTER_0_5R', adverseBar, recoveryBar: x.bar, recoveryDelay: x.bar - adverseBar };
  }
  return { state: 'NO_RECOVERY_H20', adverseBar, recoveryBar: null };
}

async function run(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE) throw new Error(`${tf}: expected at least ${PRE} candles, found ${candles.length}`);
  const baselineReport = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8'));
  const cutoff = new Date(candles[PRE].timestamp);
  const baseline = (baselineReport.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < cutoff);

  // Canonical post-entry population: every baseline trade with recorded entryIndex participates.
  // Do not reconstruct/filter through DELAY1 or any new detector condition.
  const missingEntryIndex = baseline.filter(t => !Number.isInteger(Number(t.entryIndex))).length;
  if (missingEntryIndex) throw new Error(`INTEGRITY missing entryIndex=${missingEntryIndex}`);
  const rows = baseline.map(t => ({
    entryIndex: Number(t.entryIndex), time: t.entryTime, direction: t.direction,
    session: buildSessionContext(t.entryTime, CONTEXT)?.sessionName ?? 'OUT_OF_SESSION',
    rMultiple: Number(t.rMultiple), exceptional: Number(t.rMultiple) >= 5,
    event: classify(t, path(candles, t)),
  }));
  const noPath = rows.filter(r => r.event.state === 'NO_PATH').length;
  if (rows.length !== baseline.length) throw new Error(`INTEGRITY mismatch baseline=${baseline.length} rows=${rows.length}`);

  const states = ['NO_ADVERSE_0_5R', 'RECOVERY_AFTER_0_5R', 'NO_RECOVERY_H20', 'NO_PATH'];
  const eventGroups = Object.fromEntries(states.map(state => {
    const g = rows.filter(r => r.event.state === state), noEx = g.filter(r => !r.exceptional);
    return [state, { stats: stats(g), noExceptional: stats(noEx), recoveryTiming: state === 'RECOVERY_AFTER_0_5R' && g.length ? { mean: g.reduce((s,r)=>s+r.event.recoveryDelay,0)/g.length } : null }];
  }));

  const windows = [];
  for (let start = 0; start < PRE; start += BLOCK) {
    const end = Math.min(PRE, start + BLOCK), g = rows.filter(r => r.entryIndex >= start && r.entryIndex < end);
    windows.push({ label: start < DEV ? `DEV_${start / BLOCK + 1}` : `VAL_${(start - DEV) / BLOCK + 1}`, start, endExclusive: end, n: g.length, stats: stats(g), groups: Object.fromEntries(states.map(s => [s, stats(g.filter(r => r.event.state === s))])) });
  }

  const segments = [];
  for (const direction of ['BUY', 'SELL']) for (const session of ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']) {
    const g = rows.filter(r => r.direction === direction && r.session === session);
    if (g.length < 5) continue;
    segments.push({ segment: `${direction}+${session}`, n: g.length, all: Object.fromEntries(states.map(s=>[s,stats(g.filter(r=>r.event.state===s))])), dev: Object.fromEntries(states.map(s=>[s,stats(g.filter(r=>r.entryIndex<DEV&&r.event.state===s))])), val: Object.fromEntries(states.map(s=>[s,stats(g.filter(r=>r.entryIndex>=DEV&&r.event.state===s))])) });
  }

  const report = { mode:'PHASE_13_POST_ENTRY_RECOVERY_EVENT', timeframe:tf, scope:{ baselinePre:baseline.length, joined:rows.length, dev:rows.filter(r=>r.entryIndex<DEV).length, val:rows.filter(r=>r.entryIndex>=DEV).length, freshLocked:true }, integrity:{ canonicalBaselineUniverse:true, baselinePre:baseline.length, joined:rows.length, missingEntryIndex, noPath }, eventDefinition:{ boundaryR:MAE_BOUNDARY, horizon:H20, adverseEvent:'first cumulative MAE >= 0.50R after entry', recoveryEvent:'first strictly later candle close through entry price in trade direction', noIntrabarInference:true }, overall:stats(rows), eventGroups, windows, segments, cases:rows, methodology:{ canonicalBaselineFieldsOnly:true, fixedChronologicalWindows:true, noThresholdSearch:true, noHorizonSelection:true, noNewRule:true, noFresh:true, productionUnchanged:true, diagnosticOnly:true } };
  await mkdir(OUT,{recursive:true}); const file=resolve(OUT,`${tf}.json`); await writeFile(file,JSON.stringify(report,null,2));
  console.log(`PHASE_13_RECOVERY_EVENT ${tf} N=${rows.length} DEV=${report.scope.dev} VAL=${report.scope.val} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${baseline.length} joined=${rows.length} missingEntryIndex=${missingEntryIndex} noPath=${noPath}`);
  console.log(`BASELINE avgR=${fmt(report.overall.avgR)} PF=${fmt(report.overall.PF)} WR=${fmt(report.overall.WR*100)}%`);
  for (const [s,x] of Object.entries(eventGroups)) console.log(`${s}: N=${x.stats.n} avgR=${fmt(x.stats.avgR)} PF=${fmt(x.stats.PF)} WR=${fmt(x.stats.WR*100)}% | NO_EX avgR=${fmt(x.noExceptional.avgR)} PF=${fmt(x.noExceptional.PF)} | recoveryDelayMean=${fmt(x.recoveryTiming?.mean)}`);
  console.log('=== WINDOWS ==='); for (const w of windows) console.log(`${w.label} idx=${w.start}-${w.endExclusive-1} N=${w.n} avgR=${fmt(w.stats.avgR)} | ${Object.entries(w.groups).map(([s,x])=>`${s}=${x.n}/${fmt(x.avgR)}`).join(' | ')}`);
  console.log('=== SEGMENTS ==='); for (const s of segments) console.log(`${s.segment} N=${s.n} | ALL ${Object.entries(s.all).map(([k,x])=>`${k}:${x.n}/${fmt(x.avgR)}`).join(' ')} | DEV ${Object.entries(s.dev).map(([k,x])=>`${k}:${x.n}/${fmt(x.avgR)}`).join(' ')} | VAL ${Object.entries(s.val).map(([k,x])=>`${k}:${x.n}/${fmt(x.avgR)}`).join(' ')}`);
  console.log(`REPORT=${file}`); console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_HORIZON_SELECTION NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
for (const tf of ['1min','5min']) await run(tf);
