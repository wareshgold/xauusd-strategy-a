import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const REPORT = resolve(ROOT, 'data/reports/strategy-a-phase12-preentry-geometry-robustness/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-phase12-reclaim-temporal-replication');
const WINDOWS = [
  ['W1', 0, 4320],
  ['W2', 4320, 8640],
  ['W3', 8640, 12960],
  ['W4', 12960, 17280],
];
const DEV = 6000;
const PRE = 10000;

const rank = (values) => {
  const pairs = values.map((v, i) => ({ v, i })).filter((x) => Number.isFinite(x.v)).sort((a, b) => a.v - b.v);
  const out = Array(values.length).fill(null);
  let i = 0;
  while (i < pairs.length) {
    let j = i + 1;
    while (j < pairs.length && pairs[j].v === pairs[i].v) j++;
    const r = (i + 1 + j) / 2;
    for (let k = i; k < j; k++) out[pairs[k].i] = r;
    i = j;
  }
  return out;
};
const spearman = (rows, f) => {
  const xs = rows.filter((r) => Number.isFinite(r[f]) && Number.isFinite(r.r));
  if (xs.length < 5) return null;
  const a = rank(xs.map((r) => r[f]));
  const b = rank(xs.map((r) => r.r));
  const ma = a.reduce((s, x) => s + x, 0) / a.length;
  const mb = b.reduce((s, x) => s + x, 0) / b.length;
  let n = 0, da = 0, db = 0;
  for (let i = 0; i < a.length; i++) { const x = a[i] - ma, y = b[i] - mb; n += x * y; da += x * x; db += y * y; }
  return da && db ? n / Math.sqrt(da * db) : null;
};
const stats = (rows) => {
  const wins = rows.filter((r) => r.r > 0), losses = rows.filter((r) => r.r <= 0);
  const gw = wins.reduce((s, r) => s + r.r, 0), gl = losses.reduce((s, r) => s + Math.abs(r.r), 0);
  return { n: rows.length, avgR: rows.length ? rows.reduce((s, r) => s + r.r, 0) / rows.length : null, PF: gl ? gw / gl : null, WR: rows.length ? wins.length / rows.length : null };
};
const fmt = (x) => Number.isFinite(x) ? x.toFixed(4) : '-';
const timeMs = (t) => new Date(t).getTime();
const median = (rows, f) => {
  const a = rows.map((r) => r[f]).filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2); return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};

async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const geom = JSON.parse(await readFile(REPORT, 'utf8'));
  const baseRows = (base.trades ?? []).filter((t) => Number(t.entryIndex) < PRE && t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && (t.direction === 'BUY' || t.direction === 'SELL'));
  const byIndex = new Map(geom.cases.map((r) => [r.entryIndex, r]));
  const rows = baseRows.map((t) => byIndex.get(Number(t.entryIndex))).filter(Boolean).map((r) => ({ ...r, r: Number(r.r), entryIndex: Number(r.entryIndex), timeMs: timeMs(r.time) }));
  if (rows.length !== baseRows.length) throw new Error(`Geometry join mismatch: ${rows.length}/${baseRows.length}`);

  const windowed = [];
  const ordered = [...rows].sort((a, b) => a.entryIndex - b.entryIndex);
  const min = ordered[0]?.entryIndex ?? 0;
  for (const [name, lo, hi] of WINDOWS) {
    const subset = ordered.filter((r) => r.entryIndex >= min + lo && r.entryIndex < min + hi);
    if (!subset.length) continue;
    windowed.push({ name, startIndex: min + lo, endIndexExclusive: min + hi, n: subset.length, stats: stats(subset), noExceptional: stats(subset.filter((r) => r.r < 5)), feature: {
      spearman: spearman(subset, 'triggerReclaimToRange'),
      noExceptionalSpearman: spearman(subset.filter((r) => r.r < 5), 'triggerReclaimToRange'),
      median: median(subset, 'triggerReclaimToRange'),
    }});
  }

  const temporal = [];
  for (const session of ['LONDON', 'NEW_YORK', 'OUT_OF_SESSION']) {
    for (const direction of ['BUY', 'SELL']) {
      const subset = rows.filter((r) => r.session === session && r.direction === direction);
      if (!subset.length) continue;
      const dev = subset.filter((r) => r.entryIndex < DEV);
      const val = subset.filter((r) => r.entryIndex >= DEV);
      temporal.push({ segment: `${direction}+${session}`, n: subset.length, devN: dev.length, valN: val.length, all: { sp: spearman(subset, 'triggerReclaimToRange'), delta: median(subset.filter((r) => r.r > 0 && r.r < 5), 'triggerReclaimToRange') - (median(subset.filter((r) => r.r < 0), 'triggerReclaimToRange') ?? 0) }, dev: { sp: spearman(dev, 'triggerReclaimToRange'), stats: stats(dev) }, val: { sp: spearman(val, 'triggerReclaimToRange'), stats: stats(val) } });
    }
  }

  const result = {
    mode: 'PHASE_12_RECLAIM_TEMPORAL_REPLICATION',
    timeframe: '5m',
    scope: { baselinePre: baseRows.length, geometryRows: rows.length, dev: rows.filter((r) => r.entryIndex < DEV).length, val: rows.filter((r) => r.entryIndex >= DEV).length, freshHoldoutExcluded: true },
    methodology: { feature: 'triggerReclaimToRange', windows: 'Four fixed consecutive index windows of equal 4320-bar width; no best-window selection.', noThresholdOptimization: true, noNewRule: true, noFresh: true, note: 'This is a temporal replication audit of an existing descriptive feature association. It does not establish a trading edge.' },
    fixedWindows: windowed,
    sessionDirection: temporal,
    cases: rows,
  };
  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));
  console.log(`PHASE_12_RECLAIM_TEMPORAL N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${baseRows.length} geometryJoin=${rows.length} deterministicRequired=true`);
  console.log('=== FIXED TEMPORAL WINDOWS ===');
  for (const w of windowed) console.log(`${w.name} idx=${w.startIndex}-${w.endIndexExclusive - 1} N=${w.n} avgR=${fmt(w.stats.avgR)} PF=${fmt(w.stats.PF)} WR=${fmt(w.stats.WR * 100)}% | sp=${fmt(w.feature.spearman)} noExSp=${fmt(w.feature.noExceptionalSpearman)} median=${fmt(w.feature.median)}`);
  console.log('=== SESSION × DIRECTION ===');
  for (const x of temporal) console.log(`${x.segment} N=${x.n} DEV=${x.devN} VAL=${x.valN} | ALL sp=${fmt(x.all.sp)} | DEV sp=${fmt(x.dev.sp)} avgR=${fmt(x.dev.stats.avgR)} | VAL sp=${fmt(x.val.sp)} avgR=${fmt(x.val.stats.avgR)}`);
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED');
}
await main();
