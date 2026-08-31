import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-tp1-full-exit-rolling-robustness');
const TIMEFRAMES = ['1min', '5min'];
const WINDOW_COUNT = 6;

const finite = (v) => Number.isFinite(Number(v));

const stats = (rows) => {
  const rs = rows.map((r) => Number(r.rMultiple)).filter(Number.isFinite);
  const w = rs.filter((x) => x > 0);
  const l = rs.filter((x) => x < 0);
  const gp = w.reduce((a, b) => a + b, 0);
  const gl = -l.reduce((a, b) => a + b, 0);
  const totalR = rs.reduce((a, b) => a + b, 0);

  let peak = 0;
  let equity = 0;
  let maxDD = 0;
  let run = 0;
  let maxLoss = 0;

  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDD = Math.max(maxDD, peak - equity);
    if (r < 0) {
      run += 1;
      maxLoss = Math.max(maxLoss, run);
    } else {
      run = 0;
    }
  }

  return {
    n: rs.length,
    wins: w.length,
    losses: l.length,
    winRate: rs.length ? w.length / rs.length : 0,
    PF: gl ? gp / gl : (gp ? null : 0),
    avgR: rs.length ? totalR / rs.length : 0,
    totalR,
    maxDrawdownR: maxDD,
    maxConsecutiveLosses: maxLoss,
  };
};

function splitRolling(rows) {
  const sorted = [...rows].sort(
    (x, y) => new Date(x.entryTime).getTime() - new Date(y.entryTime).getTime(),
  );
  const n = Math.floor(sorted.length / WINDOW_COUNT);
  const out = [];
  for (let i = 0; i < WINDOW_COUNT; i += 1) {
    out.push(sorted.slice(i * n, i === WINDOW_COUNT - 1 ? sorted.length : (i + 1) * n));
  }
  return out;
}

function group(rows, key) {
  const map = new Map();
  for (const row of rows) {
    const value = row[key] ?? 'UNKNOWN';
    if (!map.has(value)) map.set(value, []);
    map.get(value).push(row);
  }
  return Object.fromEntries([...map].map(([keyValue, value]) => [keyValue, stats(value)]));
}

async function run(tf) {
  const raw = JSON.parse(
    await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${tf}.json`), 'utf8'),
  );
  const rows = (raw.trades ?? [])
    .filter((r) => finite(r.rMultiple))
    .map((r) => ({ ...r, rMultiple: Number(r.rMultiple) }));
  const windows = splitRolling(rows);

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_TP1_FULL_EXIT_ROLLING_ROBUSTNESS_V1',
    timeframe: tf,
    management: '100% exit at TP1; no runner; entry generation unchanged.',
    methodology: {
      windows: WINDOW_COUNT,
      ordering: 'chronological',
      costs: 'same as baseline dataset/backtest',
      selection: 'no optimization; fixed TP1 full-exit rule',
      warning: 'Rolling-window stability is robustness evidence, not proof of future profitability.',
    },
    overall: stats(rows),
    windows: windows.map((window, i) => {
      const first = window[0];
      const last = window[window.length - 1];
      return {
        window: i + 1,
        from: first?.entryTime ?? null,
        to: last?.entryTime ?? null,
        ...stats(window),
        byDirection: group(window, 'direction'),
        bySession: group(window, 'session'),
      };
    }),
  };

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(
    `${tf}: trades=${rows.length} PF=${report.overall.PF?.toFixed(4) ?? 'n/a'} avgR=${report.overall.avgR.toFixed(4)} maxDD=${report.overall.maxDrawdownR.toFixed(4)} maxCL=${report.overall.maxConsecutiveLosses}`,
  );
  for (const window of report.windows) {
    console.log(
      `  W${window.window} n=${window.n} PF=${window.PF?.toFixed(4) ?? 'n/a'} avgR=${window.avgR.toFixed(4)} totalR=${window.totalR.toFixed(4)} DD=${window.maxDrawdownR.toFixed(4)} CL=${window.maxConsecutiveLosses}`,
    );
  }
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
