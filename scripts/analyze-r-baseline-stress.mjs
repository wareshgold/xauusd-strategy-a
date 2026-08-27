import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const reportDir = path.join(root, 'data', 'reports', 'strategy-a-baseline');
const caps = [5, 10, 20];

function load(timeframe) {
  const file = path.join(reportDir, `${timeframe}.json`);
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  return raw.trades.filter((t) => Number.isFinite(t.rMultiple));
}

function pf(trades) {
  const grossWin = trades.reduce((s, t) => s + Math.max(0, t.rMultiple), 0);
  const grossLoss = trades.reduce((s, t) => s + Math.max(0, -t.rMultiple), 0);
  return grossLoss === 0 ? (grossWin > 0 ? Infinity : 0) : grossWin / grossLoss;
}

function avg(trades) {
  return trades.length ? trades.reduce((s, t) => s + t.rMultiple, 0) / trades.length : 0;
}

function total(trades) {
  return trades.reduce((s, t) => s + t.rMultiple, 0);
}

function percentile(values, p) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const i = (sorted.length - 1) * p;
  const lo = Math.floor(i);
  const hi = Math.ceil(i);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo);
}

for (const timeframe of ['1min', '5min']) {
  const trades = load(timeframe);
  const rs = trades.map((t) => t.rMultiple);
  const p99 = percentile(rs, 0.99);
  const largest = [...trades].sort((a, b) => b.rMultiple - a.rMultiple);

  console.log(`${timeframe}: trades=${trades.length} rawPF=${pf(trades).toFixed(4)} rawAvgR=${avg(trades).toFixed(4)} totalR=${total(trades).toFixed(4)} p99=${p99.toFixed(4)}`);

  for (const cap of caps) {
    const capped = trades.map((t) => ({ ...t, rMultiple: Math.min(t.rMultiple, cap) }));
    console.log(`  cap=${cap}R PF=${pf(capped).toFixed(4)} avgR=${avg(capped).toFixed(4)} totalR=${total(capped).toFixed(4)}`);
  }

  const withoutP99 = trades.filter((t) => t.rMultiple <= p99);
  console.log(`  <=P99 PF=${pf(withoutP99).toFixed(4)} avgR=${avg(withoutP99).toFixed(4)} totalR=${total(withoutP99).toFixed(4)} excluded=${trades.length - withoutP99.length}`);

  console.log('  top winners:');
  for (const t of largest.slice(0, 5)) {
    console.log(`    ${t.entryTime} ${t.direction} R=${t.rMultiple.toFixed(4)} risk=${Number(t.riskDistance).toFixed(5)}`);
  }
}
