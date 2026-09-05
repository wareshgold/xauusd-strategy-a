import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const ANATOMY = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-case-anatomy/5m.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-milestone-survival');
const HORIZONS = [12, 24, 48];
const MILESTONES_R = [1, 2, 3];
const GROUPS = ['EXCEPTIONAL_WIN', 'NORMAL_WIN', 'LOSS'];

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
const pct = (n) => Number.isFinite(n) ? `${(n * 100).toFixed(1)}%` : '—';
const fmt = (n) => Number.isFinite(n) ? Number(n.toFixed(3)) : '—';

function rowsFor(cases, group) {
  return cases.filter((x) => x.classification === group);
}

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return { n: a.length, min: p(a[0]), p25: q(0.25), median: q(0.5), p75: q(0.75), max: p(a[a.length - 1]), mean: p(a.reduce((s, x) => s + x, 0) / a.length) };
}

function firstMilestone(candles, entryIndex, entry, stopLoss, milestoneR, maxBars) {
  const risk = Math.abs(entry - stopLoss);
  if (!(risk > 0)) return { status: 'INVALID' };
  const target = entry - milestoneR * risk;
  const end = Math.min(candles.length - 1, entryIndex + maxBars);
  for (let i = entryIndex + 1; i <= end; i += 1) {
    const c = candles[i];
    const hitFavorable = c.low <= target;
    const hitStop = c.high >= stopLoss;
    if (hitFavorable && hitStop) return { status: 'INTRABAR_CONFLICT', index: i, timestamp: c.timestamp, bars: i - entryIndex };
    if (hitFavorable) return { status: 'REACHED', index: i, timestamp: c.timestamp, bars: i - entryIndex };
    if (hitStop) return { status: 'STOPPED_BEFORE_MILESTONE', index: i, timestamp: c.timestamp, bars: i - entryIndex };
  }
  return { status: 'NOT_REACHED', index: null, timestamp: null, bars: null };
}

function postMilestonePath(candles, milestoneIndex, entry, stopLoss, milestoneR, maxBars) {
  const risk = Math.abs(entry - stopLoss);
  const end = Math.min(candles.length - 1, milestoneIndex + maxBars);
  if (milestoneIndex == null || !(risk > 0) || milestoneIndex > end) return null;
  const path = candles.slice(milestoneIndex + 1, end + 1);
  if (!path.length) return { barsObserved: 0, mfeAfterR: 0, maeAfterR: 0, pullbackFromMilestoneR: 0 };
  const milestonePrice = entry - milestoneR * risk;
  const mfeAfter = Math.max(0, ...path.map((c) => entry - c.low)) / risk;
  const maeAfter = Math.max(0, ...path.map((c) => c.high - entry)) / risk;
  const pullbackFromMilestoneR = Math.max(0, ...path.map((c) => c.high - milestonePrice)) / risk;
  return { barsObserved: path.length, mfeAfterR: p(mfeAfter), maeAfterR: p(maeAfter), pullbackFromMilestoneR: p(pullbackFromMilestoneR) };
}

function firstReachAndSurvival(candles, row, milestoneR, horizon) {
  const entry = Number(row.entry);
  const stopLoss = Number(row.stopLoss);
  const risk = Math.abs(entry - stopLoss);
  const plannedRR = Number(row.geometry?.plannedRR);
  if (!(risk > 0 && plannedRR >= milestoneR)) return { eligible: false, status: 'TARGET_BELOW_MILESTONE' };

  const first = firstMilestone(candles, row.entryIndex, entry, stopLoss, milestoneR, horizon);
  if (first.status !== 'REACHED') {
    return { eligible: true, status: first.status, barsToMilestone: first.bars ?? null, milestoneIndex: first.index ?? null, milestoneTime: first.timestamp ?? null, reached: false };
  }

  const path = postMilestonePath(candles, first.index, entry, stopLoss, milestoneR, horizon);
  const horizonEnd = Math.min(candles.length - 1, row.entryIndex + horizon);
  let stopAfterMilestone = null;
  for (let i = first.index + 1; i <= horizonEnd; i += 1) {
    const c = candles[i];
    if (c.high >= stopLoss) { stopAfterMilestone = { index: i, timestamp: c.timestamp, barsAfterMilestone: i - first.index }; break; }
  }
  return {
    eligible: true,
    status: 'REACHED',
    reached: true,
    barsToMilestone: first.bars,
    milestoneIndex: first.index,
    milestoneTime: first.timestamp,
    milestonePrice: p(entry - milestoneR * risk),
    survivalToHorizon: stopAfterMilestone == null,
    stopAfterMilestoneBars: stopAfterMilestone?.barsAfterMilestone ?? null,
    stopAfterMilestoneTime: stopAfterMilestone?.timestamp ?? null,
    ...path,
  };
}

function groupMilestoneStats(cases, milestoneR, horizon) {
  return Object.fromEntries(GROUPS.map((group) => {
    const rows = rowsFor(cases, group).map((row) => row.milestones[String(horizon)]?.[String(milestoneR)]).filter(Boolean);
    const eligible = rows.filter((x) => x.eligible);
    const reached = eligible.filter((x) => x.reached);
    const conflicts = eligible.filter((x) => x.status === 'INTRABAR_CONFLICT');
    const stopped = eligible.filter((x) => x.status === 'STOPPED_BEFORE_MILESTONE');
    return [group, {
      n: rows.length,
      eligible: eligible.length,
      reached: reached.length,
      reachRateAmongEligible: eligible.length ? p(reached.length / eligible.length) : null,
      intrabarConflict: conflicts.length,
      stoppedBeforeMilestone: stopped.length,
      medianBarsToMilestone: quantiles(reached.map((x) => Number(x.barsToMilestone))).median,
      medianPullbackFromMilestoneR: quantiles(reached.map((x) => Number(x.pullbackFromMilestoneR))).median,
      medianMaeAfterR: quantiles(reached.map((x) => Number(x.maeAfterR))).median,
      survivedToHorizon: reached.filter((x) => x.survivalToHorizon).length,
      survivalRateAmongReached: reached.length ? p(reached.filter((x) => x.survivalToHorizon).length / reached.length) : null,
    }];
  }));
}

function caseRows(cases) {
  return cases.map((row) => {
    const out = { split: row.split, time: row.entryTime, class: row.classification, r: row.r, plannedRR: row.geometry?.plannedRR };
    for (const horizon of HORIZONS) {
      for (const milestone of MILESTONES_R) {
        const x = row.milestones[String(horizon)][String(milestone)];
        out[`h${horizon}_r${milestone}_status`] = x.status;
        out[`h${horizon}_r${milestone}_bars`] = x.barsToMilestone ?? null;
        out[`h${horizon}_r${milestone}_survive`] = x.survivalToHorizon ?? null;
        out[`h${horizon}_r${milestone}_pullback`] = x.pullbackFromMilestoneR ?? null;
        out[`h${horizon}_r${milestone}_maeAfter`] = x.maeAfterR ?? null;
      }
    }
    return out;
  });
}

function compactStatus(x) {
  if (!x) return '—';
  if (x.status === 'TARGET_BELOW_MILESTONE') return 'N/A';
  if (x.status === 'INTRABAR_CONFLICT') return 'CONFLICT';
  if (x.status === 'STOPPED_BEFORE_MILESTONE') return 'STOP';
  if (x.status === 'REACHED') return x.survivalToHorizon ? `+R (${x.barsToMilestone}b) ✓` : `+R (${x.barsToMilestone}b) ×`;
  return 'NO';
}

function printReachTable(report, milestoneR) {
  console.log(`\n+${milestoneR}R REACH / SURVIVAL`);
  console.log('Class             | DEV 12 | VAL 12 | ALL 12 | DEV 24 | VAL 24 | ALL 24 | DEV 48 | VAL 48 | ALL 48');
  console.log('------------------|--------|--------|--------|--------|--------|--------|--------|--------|--------');
  for (const group of GROUPS) {
    const values = [];
    for (const horizon of HORIZONS) {
      const stats = report.groupStats[String(horizon)][String(milestoneR)];
      for (const split of ['DEV', 'VAL', 'ALL']) {
        const selected = split === 'ALL' ? stats[group] : null;
        if (selected) {
          values.push(`${selected.reached}/${selected.eligible} ${pct(selected.reachRateAmongEligible)}`);
        } else {
          const subset = report.cases.filter((x) => x.split === split && x.class === group).map((x) => x.milestones[String(horizon)][String(milestoneR)]);
          const eligible = subset.filter((x) => x.eligible);
          const reached = eligible.filter((x) => x.reached);
          values.push(`${reached.length}/${eligible.length} ${pct(eligible.length ? reached.length / eligible.length : null)}`);
        }
      }
    }
    console.log(`${group.padEnd(18)}| ${values.map((v) => v.padEnd(6)).join(' | ')}`);
  }
}

function printPathQuality(report, milestoneR) {
  console.log(`\n+${milestoneR}R PATH QUALITY (reached cases only)`);
  console.log('Class             | N | median bars | median pullback R | median MAE after R | survived @12/24/48');
  console.log('------------------|---|-------------|--------------------|--------------------|-------------------');
  for (const group of GROUPS) {
    const reached = report.cases.filter((x) => x.class === group).map((x) => x.milestones['48'][String(milestoneR)]).filter((x) => x?.status === 'REACHED');
    const bars = quantiles(reached.map((x) => Number(x.barsToMilestone))).median;
    const pullback = quantiles(reached.map((x) => Number(x.pullbackFromMilestoneR))).median;
    const mae = quantiles(reached.map((x) => Number(x.maeAfterR))).median;
    const survival = HORIZONS.map((h) => {
      const r = report.cases.filter((x) => x.class === group).map((x) => x.milestones[String(h)][String(milestoneR)]).filter((x) => x?.status === 'REACHED');
      return `${r.filter((x) => x.survivalToHorizon).length}/${r.length}`;
    }).join('/');
    console.log(`${group.padEnd(18)}| ${String(reached.length).padEnd(1)} | ${String(fmt(bars)).padEnd(11)} | ${String(fmt(pullback)).padEnd(18)} | ${String(fmt(mae)).padEnd(18)} | ${survival}`);
  }
}

function printCaseMatrix(report) {
  console.log('\nCASE PATH MATRIX — 48-bar horizon');
  console.log('Time             | Class           | R      | +1R         | +2R         | +3R');
  console.log('-----------------|-----------------|--------|-------------|-------------|-------------');
  for (const row of report.cases) {
    const values = MILESTONES_R.map((r) => compactStatus(row.milestones['48'][String(r)]));
    console.log(`${row.time.padEnd(16)} | ${row.class.padEnd(15)} | ${fmt(row.r).toString().padStart(6)} | ${values.map((v) => v.padEnd(11)).join(' | ')}`);
  }
}

async function main() {
  const anatomy = JSON.parse(await readFile(ANATOMY, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const sourceCases = anatomy.cases ?? [];
  if (sourceCases.length !== 15) throw new Error(`Expected 15 anatomy cases, got ${sourceCases.length}`);

  const cases = sourceCases.map((row) => {
    const enriched = { ...row, entryIndex: Number(row.entryIndex) };
    enriched.milestones = Object.fromEntries(HORIZONS.map((horizon) => [String(horizon), Object.fromEntries(MILESTONES_R.map((milestoneR) => [String(milestoneR), firstReachAndSurvival(candles, enriched, milestoneR, horizon)]))]));
    return enriched;
  });

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_LATE_SELL_MILESTONE_SURVIVAL',
    timeframe: '5m',
    scope: { source: 'NY late sell case anatomy', n: cases.length, dev: cases.filter((x) => x.split === 'DEV').length, val: cases.filter((x) => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: {
      purpose: 'Descriptive temporal analysis of favorable-excursion milestones and post-milestone stop survival.',
      milestonesR: MILESTONES_R,
      horizonsBars: HORIZONS,
      noOptimization: true,
      noNewTradingRules: true,
      noThresholdSearch: true,
      holdoutLocked: true,
      firstTouchSemantics: 'A milestone is considered reached only when its favorable price level is touched on a candle without that same candle also touching the stop. Same-candle favorable/stop contact is INTRABAR_CONFLICT because OHLC data cannot identify the intrabar order.',
      eligibility: 'Milestones above the recorded plannedRR are not eligible for that case; this is a geometric feasibility condition, not an optimized threshold.',
      survival: 'survivalToHorizon means no stop touch after the milestone through the specified fixed horizon. This is descriptive and does not imply a management rule.',
      note: 'This analysis does not alter entry, stop, target, candidate selection, or production Strategy A logic.',
    },
    groupStats: Object.fromEntries(HORIZONS.map((horizon) => [String(horizon), Object.fromEntries(MILESTONES_R.map((milestoneR) => [String(milestoneR), groupMilestoneStats(cases, milestoneR, horizon)]))])),
    cases: caseRows(cases),
  };

  // Reattach the rich per-case milestone objects for console analysis without changing the JSON schema.
  report.cases = cases.map((row, i) => ({ ...report.cases[i], milestones: row.milestones }));

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify({ ...report, cases: report.cases.map(({ milestones, ...row }) => ({ ...row, milestones })) }, null, 2));

  console.log('\n══════════════════════════════════════════════════════════════════════════════');
  console.log(`5m MILESTONE SURVIVAL — NY LATE SELL | cases=${cases.length} | DEV=9 | VAL=6`);
  console.log('Descriptive only • no optimization • fresh holdout excluded • production untouched');
  console.log('══════════════════════════════════════════════════════════════════════════════');

  for (const milestoneR of MILESTONES_R) {
    printReachTable(report, milestoneR);
    printPathQuality(report, milestoneR);
  }

  printCaseMatrix(report);

  console.log('\nLegend: +R = milestone reached cleanly | ✓ = survived horizon | × = stop touched after milestone');
  console.log('        CONFLICT = favorable level and stop touched in same OHLC candle; intrabar order unknown.');
  console.log('        N/A = plannedRR makes that milestone geometrically unreachable.');
}

await main();
