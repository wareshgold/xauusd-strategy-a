import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const FIXED = resolve(ROOT, 'data/reports/strategy-a-delay1-fixed-horizon-exit-economics/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-delay1-fixed-horizon-exceptional-dependence');
const PRE = 10000;
const DEV = 6000;
const H = [3, 5, 10, 20];

const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const pf = rs => {
  const wins = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses ? wins / losses : null;
};
const maxDD = rs => {
  let equity = 0, peak = 0, dd = 0;
  for (const r of rs) {
    equity += r;
    peak = Math.max(peak, equity);
    dd = Math.max(dd, peak - equity);
  }
  return dd;
};
const stats = rs => ({
  n: rs.length,
  avgR: mean(rs),
  PF: pf(rs),
  WR: rs.length ? rs.filter(x => x > 0).length / rs.length : null,
  totalR: rs.reduce((a, b) => a + b, 0),
  maxDrawdownR: maxDD(rs),
});

async function main() {
  const raw = JSON.parse(await readFile(resolve(ROOT, 'data/historical/xauusd-5min.json'), 'utf8'));
  const candles = raw.candles ?? raw;
  const baseline = JSON.parse(await readFile(BASE, 'utf8')).trades ?? [];
  const fixedReport = JSON.parse(await readFile(FIXED, 'utf8'));

  const usable = baseline.filter(t =>
    t.result !== 'AMBIGUOUS' &&
    finite(Number(t.rMultiple)) &&
    Number(t.entryIndex) < PRE
  );

  if (fixedReport.integrity?.matched !== 144) {
    throw new Error(`Phase 10F integrity expected 144 matched rows, got ${fixedReport.integrity?.matched}.`);
  }

  const delay1Indices = fixedReport.delay1EntryIndices;
  if (!Array.isArray(delay1Indices) || delay1Indices.length !== 144) {
    throw new Error('Phase 10F report does not expose the canonical 144 DELAY1 entry indices.');
  }

  const delay1Set = new Set(delay1Indices.map(Number));
  const delay1 = usable.filter(t => delay1Set.has(Number(t.entryIndex)));
  if (delay1.length !== 144) {
    throw new Error(`Expected 144 canonical DELAY1 baseline rows, got ${delay1.length}.`);
  }

  const rows = [];
  for (const t of delay1) {
    const entryIndex = Number(t.entryIndex);
    if (H.some(h => entryIndex + h >= candles.length)) continue;

    const entry = Number(t.entry);
    const risk = Math.abs(entry - Number(t.stopLoss));
    const direction = t.direction;
    const horizonR = {};
    for (const h of H) {
      const close = Number(candles[entryIndex + h].close);
      horizonR[h] = (direction === 'BUY' ? close - entry : entry - close) / risk;
    }

    rows.push({
      entryIndex,
      baselineR: Number(t.rMultiple),
      exceptional: Number(t.rMultiple) >= 5,
      horizonR,
    });
  }

  if (rows.length !== 144) {
    throw new Error(`Expected 144 complete DELAY1 rows, got ${rows.length}.`);
  }

  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const exceptional = rows.filter(r => r.exceptional);
  const normal = rows.filter(r => !r.exceptional);
  const results = {};

  for (const h of H) {
    const allR = rows.map(r => r.horizonR[h]);
    const noExR = normal.map(r => r.horizonR[h]);
    const devNoExR = dev.filter(r => !r.exceptional).map(r => r.horizonR[h]);
    const valNoExR = val.filter(r => !r.exceptional).map(r => r.horizonR[h]);
    const exR = exceptional.map(r => r.horizonR[h]);

    results[`H${h}`] = {
      all: stats(allR),
      noExceptional: stats(noExR),
      devNoExceptional: stats(devNoExR),
      valNoExceptional: stats(valNoExR),
      exceptional: {
        n: exR.length,
        totalR: exR.reduce((a, b) => a + b, 0),
        avgR: mean(exR),
        shareOfAllTotalR: mean(allR) !== null && stats(allR).totalR !== 0
          ? exR.reduce((a, b) => a + b, 0) / stats(allR).totalR
          : null,
      },
    };
  }

  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_FIXED_HORIZON_EXCEPTIONAL_DEPENDENCE',
    timeframe: '5min',
    scope: {
      preHoldoutCandles: PRE,
      devCutoff: DEV,
      delay1N: 144,
      exceptionalDefinition: 'Canonical baseline rMultiple >= 5R.',
      horizons: H,
      freshHoldoutAccessed: false,
    },
    integrity: {
      baselinePre: usable.length,
      delay1Baseline: delay1.length,
      rows: rows.length,
      devN: dev.length,
      valN: val.length,
      exceptionalN: exceptional.length,
      normalN: normal.length,
      pathComplete: rows.length === 144,
      deterministic: true,
    },
    methodology: {
      purpose: 'Audit whether Phase 10F fixed-horizon economics depends materially on exceptional canonical winners.',
      exceptionalLabelSource: 'Canonical baseline rMultiple only.',
      horizonOutcomeSource: 'Pure close-to-close fixed-horizon R recomputed from historical candles; no SL/TP execution.',
      noExceptionalIsDiagnosticOnly: true,
      noThresholdOptimization: true,
      noHorizonOptimization: true,
      noExitRuleCreation: true,
      noBrokerExecutionModel: true,
      diagnosticOnly: true,
      freshHoldoutExcluded: true,
      productionUntouched: true,
    },
    population: {
      all: rows.length,
      exceptional: exceptional.length,
      normal: normal.length,
    },
    horizons: results,
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(report, null, 2));

  console.log(`PHASE_10F_EXCEPTIONAL_DEPENDENCE N=${rows.length} DEV=${dev.length} VAL=${val.length} FRESH=LOCKED`);
  console.log(`INTEGRITY baselinePre=${usable.length} delay1=${delay1.length} exceptional=${exceptional.length} normal=${normal.length} pathComplete=${rows.length === 144} deterministic=true`);

  for (const h of H) {
    const x = results[`H${h}`];
    console.log(
      `H${h}: ALL avgR=${x.all.avgR.toFixed(4)} PF=${x.all.PF?.toFixed(4)} WR=${(x.all.WR * 100).toFixed(2)}%` +
      ` | NO_EX avgR=${x.noExceptional.avgR.toFixed(4)} PF=${x.noExceptional.PF?.toFixed(4)} WR=${(x.noExceptional.WR * 100).toFixed(2)}%` +
      ` | DEV NO_EX avgR=${x.devNoExceptional.avgR.toFixed(4)} PF=${x.devNoExceptional.PF?.toFixed(4)} WR=${(x.devNoExceptional.WR * 100).toFixed(2)}%` +
      ` | VAL NO_EX avgR=${x.valNoExceptional.avgR.toFixed(4)} PF=${x.valNoExceptional.PF?.toFixed(4)} WR=${(x.valNoExceptional.WR * 100).toFixed(2)}%`
    );
  }

  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

main().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
