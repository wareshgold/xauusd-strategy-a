import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const CONFIGS = ['1min', '5min'];
const HORIZONS = [2, 3, 5];
const THRESHOLDS = [0.25, 0.5, 0.75, 1];

const load = (p) => JSON.parse(fs.readFileSync(path.resolve(ROOT, p), 'utf8'));
const sum = (xs) => xs.reduce((a, b) => a + b, 0);
const pf = (rs) => {
  const grossWin = sum(rs.filter((r) => r > 0));
  const grossLoss = -sum(rs.filter((r) => r < 0));
  return grossLoss === 0 ? Infinity : grossWin / grossLoss;
};
const drawdown = (rs) => {
  let equity = 0, peak = 0, max = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    max = Math.max(max, peak - equity);
  }
  return max;
};

for (const timeframe of CONFIGS) {
  const baseline = load(`data/reports/strategy-a-baseline/${timeframe}.json`);
  const earlyPath = load(`data/reports/strategy-a-early-trade-path/${timeframe}.json`);
  const pathByEntry = new Map(earlyPath.trades.map((t) => [t.entryIndex, t]));
  const trades = baseline.trades;
  const baselineRs = trades.map((t) => Number(t.rMultiple)).filter(Number.isFinite);
  const simulations = [];

  for (const horizon of HORIZONS) {
    for (const threshold of THRESHOLDS) {
      const simulated = [];
      let earlyExits = 0;
      let earlyWinnerCuts = 0;
      let earlyLoserCuts = 0;
      let sameBarExcluded = 0;

      for (const trade of trades) {
        const forensic = pathByEntry.get(trade.entryIndex);
        if (!forensic) continue;
        const terminalBar = Number(trade.barsToExit);
        let exitR = Number(trade.rMultiple);
        let triggerHorizon = null;

        // Conservative rule: only an adverse hit strictly before the baseline
        // terminal bar is actionable. If both happen on the same OHLC bar,
        // intrabar order is unknowable and we do not invent one.
        for (const row of forensic.path ?? []) {
          const h = Number(row.horizon);
          const adverse = Number(row.maeR);
          if (h > horizon) break;
          if (Number.isFinite(terminalBar) && h >= terminalBar) {
            if (h === terminalBar && adverse >= threshold) sameBarExcluded++;
            break;
          }
          if (adverse >= threshold) {
            exitR = -threshold;
            triggerHorizon = h;
            earlyExits++;
            if (Number(trade.rMultiple) > 0) earlyWinnerCuts++;
            else if (Number(trade.rMultiple) < 0) earlyLoserCuts++;
            break;
          }
        }
        simulated.push({ entryIndex: trade.entryIndex, r: exitR, triggerHorizon });
      }

      simulated.sort((a, b) => a.entryIndex - b.entryIndex);
      const rs = simulated.map((x) => x.r);
      const totalR = sum(rs);
      simulations.push({
        horizon,
        thresholdR: threshold,
        trades: rs.length,
        earlyExits,
        earlyWinnerCuts,
        earlyLoserCuts,
        sameBarExcluded,
        winRate: rs.length ? rs.filter((r) => r > 0).length / rs.length : 0,
        averageR: rs.length ? totalR / rs.length : 0,
        profitFactor: pf(rs),
        totalR,
        maxDrawdownR: drawdown(rs),
      });
    }
  }

  const baseTotal = sum(baselineRs);
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'DIAGNOSTIC_ONLY',
    timeframe,
    baseline: {
      trades: baselineRs.length,
      totalR: baseTotal,
      averageR: baseTotal / baselineRs.length,
      profitFactor: pf(baselineRs),
      maxDrawdownR: drawdown(baselineRs),
    },
    simulations,
    methodology: {
      horizons: HORIZONS,
      thresholdsR: THRESHOLDS,
      exitRule: 'Close at -thresholdR when MAE reaches threshold within the selected horizon.',
      sameBarPolicy: 'If adverse threshold and baseline terminal event occur on the same OHLC bar, exclude that trigger because intrabar ordering is unknowable.',
      ordering: 'Simulated results are evaluated in entryIndex order.',
    },
    researchNote: 'Diagnostic only. No strategy parameters or trading rules changed. This is a retrospective path simulation, not a validated production exit rule.',
  };

  const outDir = path.resolve(ROOT, 'data/reports/strategy-a-early-exit-simulation');
  fs.mkdirSync(outDir, { recursive: true });
  const out = path.join(outDir, `${timeframe}.json`);
  fs.writeFileSync(out, JSON.stringify(report, null, 2) + '\n');

  console.log(`${timeframe}: baseline trades=${baselineRs.length} PF=${pf(baselineRs).toFixed(4)} avgR=${(baseTotal / baselineRs.length).toFixed(4)} totalR=${baseTotal.toFixed(4)}`);
  for (const r of simulations) {
    const pfText = Number.isFinite(r.profitFactor) ? r.profitFactor.toFixed(4) : 'Infinity';
    console.log(`  h+${r.horizon} adverse>=${r.thresholdR}R: exits=${r.earlyExits} winnerCuts=${r.earlyWinnerCuts} loserCuts=${r.earlyLoserCuts} sameBarExcluded=${r.sameBarExcluded} PF=${pfText} avgR=${r.averageR.toFixed(4)} totalR=${r.totalR.toFixed(4)} DD=${r.maxDrawdownR.toFixed(4)}`);
  }
  console.log(`Report -> ${out}`);
}
