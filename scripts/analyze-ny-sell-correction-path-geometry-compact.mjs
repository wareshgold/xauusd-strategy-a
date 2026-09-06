import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const GENERATOR = resolve(ROOT, 'scripts/analyze-ny-sell-correction-path-geometry-v2.mjs');
const REPORT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-correction-path-geometry-v2/5m.json');

const runGenerator = () => new Promise((resolvePromise, reject) => {
  const child = spawn(process.execPath, [GENERATOR], { stdio: ['ignore', 'ignore', 'inherit'], shell: false });
  child.on('error', reject);
  child.on('exit', (code) => code === 0 ? resolvePromise() : reject(new Error(`geometry-v2 exited with code ${code}`)));
});

const f = (x) => Number.isFinite(x) ? Number(x.toFixed(2)) : null;
const pct = (x) => Number.isFinite(x) ? Number((x * 100).toFixed(1)) : null;
const stat = (b) => `${b.n}/${pct(b.WR)}%/${f(b.avgR)}/${f(b.PF)}`;

function compactFeature(result, feature) {
  const q = (split) => ['Q1', 'Q2', 'Q3', 'Q4'].map((k) => stat(result.buckets[feature][split][k])).join(' | ');
  return `${feature}: DEV ${q('DEV')} ; VAL ${q('VAL')}`;
}

function composite(result) {
  const corr = result.buckets.correctionToSpike;
  const close = result.buckets.triggerCloseLocation;
  const rows = result.cases ?? [];
  const favorable = rows.filter((r) =>
    Number.isFinite(r.correctionToSpike) && Number.isFinite(r.triggerCloseLocation) &&
    r.correctionToSpike <= corr.ALL.Q2.featureMedian &&
    r.triggerCloseLocation >= close.ALL.Q3.featureMedian
  );
  const summarize = (xs) => {
    const wins = xs.filter((x) => x.r > 0).length;
    const total = xs.reduce((s, x) => s + x.r, 0);
    const grossWin = xs.filter((x) => x.r > 0).reduce((s, x) => s + x.r, 0);
    const grossLoss = xs.filter((x) => x.r <= 0).reduce((s, x) => s + Math.abs(x.r), 0);
    return `${xs.length}/${xs.length ? pct(wins / xs.length) : null}%/${f(xs.length ? total / xs.length : null)}/${f(grossLoss ? grossWin / grossLoss : null)}`;
  };
  return `COMPOSITE exploratory corrToSpike<=ALL-Q2-med & closeLoc>=ALL-Q3-med: ALL ${summarize(favorable)} | DEV ${summarize(favorable.filter(x => x.split === 'DEV'))} | VAL ${summarize(favorable.filter(x => x.split === 'VAL'))}`;
}

await runGenerator();
const result = JSON.parse(await readFile(REPORT, 'utf8'));
console.log(`GEOM_V2_COMPACT N=${result.total} DEV=${result.dev} VAL=${result.val} FRESH=LOCKED`);
for (const feature of ['correctionToSpike', 'reclaimToCorrection', 'triggerBodyToRange', 'triggerCloseLocation']) console.log(compactFeature(result, feature));
console.log(composite(result));
console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
