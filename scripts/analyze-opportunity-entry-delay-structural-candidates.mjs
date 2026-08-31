import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-opportunity-entry-delay-structural-candidates');
const TIMEFRAMES = ['1min', '5min'];

function finiteRows(rows) { return rows.filter(r => Number.isFinite(r.rMultiple)); }
function summarize(rows) {
  const u = finiteRows(rows);
  const grossWin = u.filter(r => r.rMultiple > 0).reduce((s, r) => s + r.rMultiple, 0);
  const grossLoss = u.filter(r => r.rMultiple < 0).reduce((s, r) => s + Math.abs(r.rMultiple), 0);
  return {
    n: u.length,
    wins: u.filter(r => r.rMultiple > 0).length,
    losses: u.filter(r => r.rMultiple < 0).length,
    winRate: u.length ? u.filter(r => r.rMultiple > 0).length / u.length : 0,
    PF: grossLoss ? grossWin / grossLoss : null,
    avgR: u.length ? u.reduce((s, r) => s + r.rMultiple, 0) / u.length : 0,
    totalR: u.reduce((s, r) => s + r.rMultiple, 0),
  };
}
function maxDD(rows) {
  let eq = 0, peak = 0, dd = 0;
  for (const r of finiteRows(rows)) {
    eq += r.rMultiple;
    peak = Math.max(peak, eq);
    dd = Math.max(dd, peak - eq);
  }
  return dd;
}
function bool(r, key) { return Boolean(r[key]); }
function lag(r) {
  const indices = ['spikeIndex','sweepIndex','bosIndex','displacementIndex','expansionIndex','fvgIndex']
    .map(k => r[k]).filter(Number.isInteger);
  return indices.length ? r.entryIndex - Math.max(...indices) : null;
}
function band(r) {
  const d = r.entryDelay;
  if (!Number.isFinite(d)) return 'UNKNOWN';
  if (d <= 2) return 'D0_2';
  if (d <= 5) return 'D3_5';
  if (d <= 8) return 'D6_8';
  if (d <= 12) return 'D9_12';
  return 'D13_PLUS';
}
function candidateSummary(rows, name, predicate) {
  const yes = rows.filter(predicate);
  return { name, ...summarize(yes), maxDD: maxDD(yes) };
}

async function load(tf) {
  return JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-opportunity-window-structural-forensics/${tf}.json`), 'utf8'));
}

async function run(tf) {
  const source = await load(tf);
  const trades = finiteRows(source.tradeRows).filter(r => r.opportunityWindow !== 'OTHER');
  const rows = trades.map(r => ({ ...r, entryDelay: lag(r) })).filter(r => Number.isFinite(r.entryDelay));
  const chronologicalCut = Math.floor(rows.length * 0.5);
  const first = rows.slice(0, chronologicalCut);
  const second = rows.slice(chronologicalCut);
  const target = rows.filter(r => band(r) === 'D9_12');
  const targetOOS = second.filter(r => band(r) === 'D9_12');

  // Descriptive candidates only. These are deliberately compact and are not optimized
  // against the OOS result; they are intended to identify plausible structural mechanisms.
  const candidates = [
    ['FVG_RETEST', r => bool(r, 'fvgRetest')],
    ['EXPANSION', r => Number.isInteger(r.expansionIndex)],
    ['EXPANSION+FVG_RETEST', r => Number.isInteger(r.expansionIndex) && bool(r, 'fvgRetest')],
    ['SWEEP+FVG_RETEST', r => Number.isInteger(r.sweepIndex) && bool(r, 'fvgRetest')],
    ['BOS+FVG_RETEST', r => Number.isInteger(r.bosIndex) && bool(r, 'fvgRetest')],
    ['DISPLACEMENT+FVG_RETEST', r => Number.isInteger(r.displacementIndex) && bool(r, 'fvgRetest')],
    ['SWEEP+BOS+FVG_RETEST', r => Number.isInteger(r.sweepIndex) && Number.isInteger(r.bosIndex) && bool(r, 'fvgRetest')],
    ['BOS+DISPLACEMENT+FVG_RETEST', r => Number.isInteger(r.bosIndex) && Number.isInteger(r.displacementIndex) && bool(r, 'fvgRetest')],
    ['EXPANSION+BOS+FVG_RETEST', r => Number.isInteger(r.expansionIndex) && Number.isInteger(r.bosIndex) && bool(r, 'fvgRetest')],
  ];

  const byBand = ['D0_2','D3_5','D6_8','D9_12','D13_PLUS'].map(b => {
    const bandRows = rows.filter(r => band(r) === b);
    return { band: b, ...summarize(bandRows), maxDD: maxDD(bandRows) };
  });

  const byCandidate = candidates.map(([name, predicate]) => {
    const all = candidateSummary(target, name, predicate);
    const inSample = candidateSummary(first.filter(r => band(r) === 'D9_12'), name, predicate);
    const oos = candidateSummary(targetOOS, name, predicate);
    const complementOOS = summarize(targetOOS.filter(r => !predicate(r)));
    return { ...all, firstHalf: inSample, oos, oosComplement: complementOOS };
  });

  const byWindow = [...new Set(target.map(r => r.opportunityWindow))].map(window => {
    const w = target.filter(r => r.opportunityWindow === window);
    return { window, ...summarize(w), maxDD: maxDD(w), oos: summarize(targetOOS.filter(r => r.opportunityWindow === window)) };
  });

  const byDirection = ['BUY','SELL'].map(direction => {
    const d = target.filter(r => String(r.direction).toUpperCase() === direction);
    return { direction, ...summarize(d), maxDD: maxDD(d), oos: summarize(targetOOS.filter(r => String(r.direction).toUpperCase() === direction)) };
  });

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_OPPORTUNITY_ENTRY_DELAY_STRUCTURAL_CANDIDATES',
    timeframe: tf,
    sourceReport: `strategy-a-opportunity-window-structural-forensics/${tf}.json`,
    methodology: {
      scope: 'defined opportunity windows only',
      target: 'D9_12 entry delay, because prior forensic showed the strongest 1min OOS result there',
      candidates: 'descriptive pre-entry structural feature intersections; no threshold optimization',
      validation: 'chronological first/second-half split; OOS is reported separately and is not used to select a rule',
      guardrail: 'candidate is not considered validated unless it has meaningful OOS sample and remains economically positive without relying on a tiny subgroup',
    },
    overall: summarize(rows),
    targetD9_12: { ...summarize(target), maxDD: maxDD(target), firstHalf: summarize(first.filter(r => band(r) === 'D9_12')), oos: { ...summarize(targetOOS), maxDD: maxDD(targetOOS) } },
    byBand,
    byCandidate,
    byWindow,
    byDirection,
    nextResearchQuestion: 'If a compact structural candidate is positive in both halves, test it on a third chronological holdout before changing the live strategy.',
  };

  await mkdir(REPORT_DIR, { recursive: true });
  const out = resolve(REPORT_DIR, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: D9_12=${target.length} OOS=${targetOOS.length}`);
  for (const c of byCandidate) console.log(`  ${c.name}: all n=${c.n} PF=${c.PF?.toFixed(4) ?? 'n/a'} | OOS n=${c.oos.n} PF=${c.oos.PF?.toFixed(4) ?? 'n/a'} avgR=${c.oos.avgR.toFixed(4)} | OOS complement PF=${c.oosComplement.PF?.toFixed(4) ?? 'n/a'}`);
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
