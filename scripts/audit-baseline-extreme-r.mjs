import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'docs/research/SP2L_BASELINE_EXTREME_R_FORENSIC_2026-09-16.md');

const configs = [
  ['1min', resolve(REPORT_DIR, '1min.json')],
  ['5min', resolve(REPORT_DIR, '5min.json')],
];

const lines = [
  '# SP2L Baseline Extreme-R Forensic Audit — 2026-09-16',
  '',
  '## Purpose',
  '',
  'Research-only forensic accounting of the already-generated baseline reports. No trade is removed, clipped, winsorized, or reclassified by this audit.',
  '',
  '## Method',
  '',
  '- inspect every persisted trade record;',
  '- recompute `abs(entry - stopLoss)` and the displayed R from TP1/SL geometry;',
  '- identify tiny-risk observations and extreme positive R observations;',
  '- compare persisted closed-trade count with the report denominator;',
  '- flag arithmetic inconsistencies without selecting a replacement rule.',
  '',
];

for (const [timeframe, path] of configs) {
  const report = JSON.parse(await readFile(path, 'utf8'));
  const trades = report.trades ?? [];
  const closed = trades.filter((t) => t.rMultiple !== null);
  const ambiguous = trades.filter((t) => t.result === 'AMBIGUOUS');
  const open = trades.filter((t) => t.result === 'OPEN');
  const extreme = closed.filter((t) => Math.abs(t.rMultiple) >= 20).sort((a, b) => Math.abs(b.rMultiple) - Math.abs(a.rMultiple));
  const tiny = [...trades].sort((a, b) => a.riskDistance - b.riskDistance).slice(0, 10);
  const arithmetic = trades.map((t) => {
    const risk = Math.abs(t.entry - t.stopLoss);
    const reward = Math.abs(t.tp1 - t.entry);
    const expected = risk > 0 ? (t.direction === 'BUY' ? (t.tp1 - t.entry) / risk : (t.entry - t.tp1) / risk) : null;
    const delta = expected === null || t.rMultiple === null ? null : Math.abs(expected - t.rMultiple);
    return { t, risk, expected, delta };
  });
  const inconsistent = arithmetic.filter((x) => x.delta !== null && x.delta > 1e-9);

  lines.push(`## ${timeframe}`,'');
  lines.push(`- persisted trade records: **${trades.length}**`);
  lines.push(`- persisted closed records: **${closed.length}**`);
  lines.push(`- persisted AMBIGUOUS records: **${ambiguous.length}**`);
  lines.push(`- persisted OPEN records: **${open.length}**`);
  lines.push(`- report metric trades: **${report.metrics?.trades ?? 'n/a'}**`);
  lines.push(`- arithmetic inconsistencies in persisted R: **${inconsistent.length}**`,'');
  lines.push('### Extreme-R observations','');
  if (!extreme.length) lines.push('- none at |R| >= 20');
  for (const x of extreme) lines.push(`- ${x.t.entryTime} ${x.t.direction}: entry=${x.t.entry}, SL=${x.t.stopLoss}, TP1=${x.t.tp1}, risk=${x.risk}, R=${x.t.rMultiple}`);
  lines.push('','### Smallest-risk observations','');
  for (const x of tiny) lines.push(`- ${x.entryTime} ${x.direction}: risk=${x.riskDistance}, result=${x.result}, R=${x.rMultiple}`);
  lines.push('');
}

lines.push('## Gate interpretation','');
lines.push('- An extreme-R observation is not automatically an implementation error.');
lines.push('- A tiny-risk observation is not automatically discarded.');
lines.push('- Any confirmed implementation error must be fixed at the engine/rule layer and the baseline regenerated, rather than patched in the metrics.');
lines.push('- No geometry, threshold, or execution rule is promoted by this audit.');
lines.push('- Frozen Geometry remains BLOCKED and Production remains OFF.');

await mkdir(resolve(ROOT, 'docs/research'), { recursive: true });
await writeFile(OUT, lines.join('\n'));
console.log(`Forensic report -> ${OUT}`);
