import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const CONFIGS = ['1min', '5min'];
const HORIZON = 5;
const THRESHOLD = 0.25;
const SEGMENTS = 4;

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
const metrics = (rs) => {
  const totalR = sum(rs);
  return {
    trades: rs.length,
    wins: rs.filter((r) => r > 0).length,
    losses: rs.filter((r) => r < 0).length,
    winRate: rs.length ? rs.filter((r) => r > 0).length / rs.length : 0,
    averageR: rs.length ? totalR / rs.length : 0,
    profitFactor: pf(rs),
    totalR,
    maxDrawdownR: drawdown(rs),
  };
};

const simulate = (trade, forensic) => {
  const terminalBar = Number(trade.barsToExit);
  let exitR = Number(trade.rMultiple);
  let triggered = false;
  let triggerHorizon = null;
  for (const row of forensic.path ?? []) {
    const h = Number(row.horizon);
    const adverse = Number(row.maeR);
    if (h > HORIZON) break;
    if (Number.isFinite(terminalBar) && h >= terminalBar) break;
    if (adverse >= THRESHOLD) {
      exitR = -THRESHOLD;
      triggered = true;
      triggerHorizon = h;
      break;
    }
  }
  return { exitR, triggered, triggerHorizon };
};

for (const timeframe of CONFIGS) {
  const baseline = load(`data/reports/strategy-a-baseline/${timeframe}.json`);
  const earlyPath = load(`data/reports/strategy-a-early-trade-path/${timeframe}.json`);
  const pathByEntry = new Map(earlyPath.trades.map((t) => [t.entryIndex, t]));
  const matched = baseline.trades
    .map((trade) => ({ trade, forensic: pathByEntry.get(trade.entryIndex) }))
    .filter((x) => x.forensic);

  matched.sort((a, b) => a.trade.entryIndex - b.trade.entryIndex);
  const size = Math.ceil(matched.length / SEGMENTS);
  const segments = [];

  for (let i = 0; i < SEGMENTS; i++) {
    const slice = matched.slice(i * size, Math.min((i + 1) * size, matched.length));
    if (!slice.length) continue;
    const baseRs = slice.map(({ trade }) => Number(trade.rMultiple)).filter(Number.isFinite);
    const simRows = slice.map(({ trade, forensic }) => simulate(trade, forensic));
    const simRs = simRows.map((x) => x.exitR);
    const earlyExits = simRows.filter((x) => x.triggered).length;
    const winnerCuts = simRows.filter((x, n) => x.triggered && Number(slice[n].trade.rMultiple) > 0).length;
    const loserCuts = simRows.filter((x, n) => x.triggered && Number(slice[n].trade.rMultiple) < 0).length;
    segments.push({
      segment: i + 1,
      from: slice[0].trade.entryTime,
      to: slice[slice.length - 1].trade.entryTime,
      baseline: metrics(baseRs),
      earlyInvalidation: {
        ...metrics(simRs),
        earlyExits,
        winnerCuts,
        loserCuts,
      },
      delta: {
        totalR: metrics(simRs).totalR - metrics(baseRs).totalR,
        averageR: metrics(simRs).averageR - metrics(baseRs).averageR,
        profitFactor: Number.isFinite(metrics(simRs).profitFactor) && Number.isFinite(metrics(baseRs).profitFactor)
          ? metrics(simRs).profitFactor - metrics(baseRs).profitFactor : null,
        maxDrawdownR: metrics(simRs).maxDrawdownR - metrics(baseRs).maxDrawdownR,
      },
    });
  }

  const allBase = matched.map(({ trade }) => Number(trade.rMultiple)).filter(Number.isFinite);
  const allSim = matched.map(({ trade, forensic }) => simulate(trade, forensic).exitR);
  const validationHalf = Math.ceil(matched.length / 2);
  const oos = matched.slice(validationHalf);
  const oosBase = oos.map(({ trade }) => Number(trade.rMultiple)).filter(Number.isFinite);
  const oosSim = oos.map(({ trade, forensic }) => simulate(trade, forensic).exitR);

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'DIAGNOSTIC_ONLY',
    timeframe,
    hypothesis: {
      horizonBars: HORIZON,
      adverseThresholdR: THRESHOLD,
      rule: 'Exit at -0.25R if MAE reaches 0.25R within the first 5 bars, strictly before the baseline terminal bar.',
    },
    matchedTrades: matched.length,
    sourceBaselineTrades: baseline.trades.length,
    sourceEarlyPathTrades: earlyPath.trades.length,
    fullSample: {
      baseline: metrics(allBase),
      earlyInvalidation: metrics(allSim),
      earlyExits: matched.map(({ trade, forensic }) => simulate(trade, forensic)).filter((x) => x.triggered).length,
    },
    outOfSampleSecondHalf: {
      definition: 'Chronological second half of matched trades; candidate rule was fixed before this report and is not optimized here.',
      from: oos[0]?.trade.entryTime ?? null,
      to: oos[oos.length - 1]?.trade.entryTime ?? null,
      baseline: metrics(oosBase),
      earlyInvalidation: metrics(oosSim),
      deltaTotalR: metrics(oosSim).totalR - metrics(oosBase).totalR,
      deltaAverageR: metrics(oosSim).averageR - metrics(oosBase).averageR,
    },
    chronologicalSegments: segments,
    interpretation: 'Diagnostic validation only. The 0.25R / 5-bar hypothesis was selected during prior research, so this is not a fully independent discovery test. Treat the second half and segment results as confirmation evidence, not proof of a production edge.',
    researchNote: 'No strategy parameters or production trading rules changed.',
  };

  const outDir = path.resolve(ROOT, 'data/reports/strategy-a-early-invalidation-walk-forward');
  fs.mkdirSync(outDir, { recursive: true });
  const out = path.join(outDir, `${timeframe}.json`);
  fs.writeFileSync(out, JSON.stringify(report, null, 2) + '\n');

  const oosBaseM = report.outOfSampleSecondHalf.baseline;
  const oosSimM = report.outOfSampleSecondHalf.earlyInvalidation;
  const pfText = (x) => Number.isFinite(x) ? x.toFixed(4) : 'Infinity';
  console.log(`${timeframe}: matched=${matched.length} fullBaselinePF=${pfText(report.fullSample.baseline.profitFactor)} fullSimPF=${pfText(report.fullSample.earlyInvalidation.profitFactor)}`);
  console.log(`  OOS second-half baseline: trades=${oosBaseM.trades} PF=${pfText(oosBaseM.profitFactor)} avgR=${oosBaseM.averageR.toFixed(4)} totalR=${oosBaseM.totalR.toFixed(4)} DD=${oosBaseM.maxDrawdownR.toFixed(4)}`);
  console.log(`  OOS second-half early:    trades=${oosSimM.trades} PF=${pfText(oosSimM.profitFactor)} avgR=${oosSimM.averageR.toFixed(4)} totalR=${oosSimM.totalR.toFixed(4)} DD=${oosSimM.maxDrawdownR.toFixed(4)}`);
  for (const s of segments) {
    console.log(`  S${s.segment}: basePF=${pfText(s.baseline.profitFactor)} simPF=${pfText(s.earlyInvalidation.profitFactor)} baseR=${s.baseline.totalR.toFixed(2)} simR=${s.earlyInvalidation.totalR.toFixed(2)} exits=${s.earlyInvalidation.earlyExits}`);
  }
  console.log(`Report -> ${out}`);
}
