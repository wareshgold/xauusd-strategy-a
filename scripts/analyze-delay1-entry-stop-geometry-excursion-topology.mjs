import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [1, 3, 5, 10, 20];
const PRE_FAV_THRESHOLDS = [0.25, 0.5, 0.75, 1.0, 1.5];
const POST_FAV_THRESHOLDS = [0.25, 0.5, 1.0];
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-delay1-entry-stop-geometry-excursion-topology');

const median = values => {
  if (!values.length) return null;
  const a = [...values].sort((x, y) => x - y);
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};
const pct = (n, d) => d ? n / d : null;
const pf = rs => {
  const gains = rs.filter(x => x > 0).reduce((a, b) => a + b, 0);
  const losses = -rs.filter(x => x < 0).reduce((a, b) => a + b, 0);
  return losses > 0 ? gains / losses : null;
};

function directionalExcursions(candle, direction, entry, risk) {
  const favorable = direction === 'BUY' ? candle.high - entry : entry - candle.low;
  const adverse = direction === 'BUY' ? entry - candle.low : candle.high - entry;
  return { favorableR: favorable / risk, adverseR: adverse / risk };
}

function analyzeTrade(candles, trade) {
  const entryIndex = Number.isInteger(trade.entryIndex) ? trade.entryIndex : Number(trade.index);
  const entry = Number(trade.entry);
  const stop = Number(trade.stopLoss ?? trade.sl);
  const direction = trade.direction;
  const risk = Math.abs(entry - stop);
  if (!Number.isFinite(entryIndex) || !Number.isFinite(entry) || !Number.isFinite(stop) || !risk || !direction) return null;

  const path = [];
  let maxFav = 0;
  let maxAdv = 0;
  let firstFav1 = null;
  let firstAdv025 = null;
  let firstAdv05 = null;
  let firstAdv075 = null;
  let firstAdv1 = null;
  let firstAdv15 = null;
  let firstFav025 = null;
  let firstFav05 = null;
  let firstFav1 = null;
  let firstFav2 = null;
  const end = Math.min(candles.length - 1, entryIndex + 20);

  for (let i = entryIndex + 1; i <= end; i++) {
    const ex = directionalExcursions(candles[i], direction, entry, risk);
    maxFav = Math.max(maxFav, ex.favorableR);
    maxAdv = Math.max(maxAdv, ex.adverseR);
    const bars = i - entryIndex;
    if (firstFav025 === null && ex.favorableR >= .25) firstFav025 = bars;
    if (firstFav05 === null && ex.favorableR >= .5) firstFav05 = bars;
    if (firstFav1 === null && ex.favorableR >= 1) firstFav1 = bars;
    if (firstFav2 === null && ex.favorableR >= 2) firstFav2 = bars;
    if (firstAdv025 === null && ex.adverseR >= .25) firstAdv025 = bars;
    if (firstAdv05 === null && ex.adverseR >= .5) firstAdv05 = bars;
    if (firstAdv075 === null && ex.adverseR >= .75) firstAdv075 = bars;
    if (firstAdv1 === null && ex.adverseR >= 1) firstAdv1 = bars;
    if (firstAdv15 === null && ex.adverseR >= 1.5) firstAdv15 = bars;
    path.push({ bars, favorableR: ex.favorableR, adverseR: ex.adverseR });
  }

  const fav1 = firstFav1;
  const adv1 = firstAdv1;
  const reachedFav1 = fav1 !== null;
  const stopFirst = adv1 !== null && (fav1 === null || adv1 < fav1);
  const sameBar1 = adv1 !== null && fav1 !== null && adv1 === fav1;
  const adverseBeforeFav1 = reachedFav1 ? Math.max(0, ...path.filter(p => p.bars <= fav1).map(p => p.adverseR)) : maxAdv;
  const favorableBeforeAdv1 = adv1 !== null ? Math.max(0, ...path.filter(p => p.bars <= adv1).map(p => p.favorableR)) : maxFav;

  let pathClass;
  if (stopFirst || sameBar1) pathClass = sameBar1 ? 'STOP_SAME_BAR_AMBIGUOUS' : 'STOP_FIRST';
  else if (!reachedFav1) pathClass = 'NO_PLUS_1R_BY_H20';
  else {
    let whipsaw = false;
    const fav1Bar = fav1;
    for (const p of path) {
      if (p.bars > fav1Bar && p.adverseR >= .5) { whipsaw = true; break; }
    }
    if (whipsaw) pathClass = 'WHIPSAW_AFTER_PLUS_1R';
    else if (adverseBeforeFav1 <= .25) pathClass = 'CLEAN_PLUS_1R';
    else if (adverseBeforeFav1 <= .5) pathClass = 'SHALLOW_PULLBACK';
    else pathClass = 'DEEP_PULLBACK';
  }

  const horizon = {};
  for (const h of HORIZONS) {
    const sub = path.filter(p => p.bars <= h);
    const fav = Math.max(0, ...sub.map(p => p.favorableR));
    const adv = Math.max(0, ...sub.map(p => p.adverseR));
    let f1 = null, a1 = null;
    for (const p of sub) {
      if (f1 === null && p.favorableR >= 1) f1 = p.bars;
      if (a1 === null && p.adverseR >= 1) a1 = p.bars;
    }
    horizon[`h${h}`] = { mfe: fav, mae: adv, firstPlus1: f1, firstMinus1: a1 };
  }

  return {
    entryIndex,
    entryTime: trade.entryTime,
    direction,
    session: trade.session ?? null,
    entry,
    stop,
    risk,
    rMultiple: Number(trade.rMultiple),
    pathClass,
    maxMFER: maxFav,
    maxMAER: maxAdv,
    firstPlus025: firstFav025,
    firstPlus05: firstFav05,
    firstPlus1: firstFav1,
    firstPlus2: firstFav2,
    firstMinus025: firstAdv025,
    firstMinus05: firstAdv05,
    firstMinus075: firstAdv075,
    firstMinus1: firstAdv1,
    firstMinus15: firstAdv15,
    adverseBeforePlus1R: adverseBeforeFav1,
    favorableBeforeMinus1R: favorableBeforeAdv1,
    horizons: horizon,
  };
}

function summarize(rows) {
  const classes = ['CLEAN_PLUS_1R','SHALLOW_PULLBACK','DEEP_PULLBACK','WHIPSAW_AFTER_PLUS_1R','STOP_FIRST','STOP_SAME_BAR_AMBIGUOUS','NO_PLUS_1R_BY_H20'];
  const out = {
    n: rows.length,
    avgR: rows.length ? rows.reduce((s, r) => s + r.rMultiple, 0) / rows.length : null,
    pf: pf(rows.map(r => r.rMultiple)),
    winRate: pct(rows.filter(r => r.rMultiple > 0).length, rows.length),
    medianRisk: median(rows.map(r => r.risk)),
    medianMFEH20: median(rows.map(r => r.horizons.h20.mfe)),
    medianMAEH20: median(rows.map(r => r.horizons.h20.mae)),
    medianAdverseBeforePlus1R: median(rows.filter(r => r.firstPlus1 !== null).map(r => r.adverseBeforePlus1R)),
    medianFavorableBeforeMinus1R: median(rows.filter(r => r.firstMinus1 !== null).map(r => r.favorableBeforeMinus1R)),
    pathClasses: Object.fromEntries(classes.map(c => {
      const x = rows.filter(r => r.pathClass === c);
      return [c, { n: x.length, rate: pct(x.length, rows.length), avgR: x.length ? mean(x.map(r => r.rMultiple)) : null, pf: pf(x.map(r => r.rMultiple)), medianMFEH20: median(x.map(r => r.horizons.h20.mfe)), medianMAEH20: median(x.map(r => r.horizons.h20.mae)) }];
    })),
    prePlus1AdverseThresholds: Object.fromEntries(PRE_FAV_THRESHOLDS.map(t => {
      const plus1 = rows.filter(r => r.firstPlus1 !== null);
      return [`adverseBeforePlus1<=${t}R`, { n: plus1.filter(r => r.adverseBeforePlus1R <= t).length, rate: pct(plus1.filter(r => r.adverseBeforePlus1R <= t).length, plus1.length) }];
    })),
    postPlus1AdverseThresholds: Object.fromEntries(POST_FAV_THRESHOLDS.map(t => {
      const plus1 = rows.filter(r => r.firstPlus1 !== null);
      return [`adverseAfterPlus1>=${t}R`, { n: plus1.filter(r => {
        const bar = r.firstPlus1;
        return r.pathClass === 'WHIPSAW_AFTER_PLUS_1R' && rows && r.horizons.h20.mae >= t && bar !== null;
      }).length, rate: null }];
    })),
    horizons: Object.fromEntries(HORIZONS.map(h => {
      const plus = rows.filter(r => r.horizons[`h${h}`].firstPlus1 !== null);
      const minus = rows.filter(r => r.horizons[`h${h}`].firstMinus1 !== null);
      return [`h${h}`, {
        plus1ReachRate: pct(plus.length, rows.length),
        minus1ReachRate: pct(minus.length, rows.length),
        medianMFE: median(rows.map(r => r.horizons[`h${h}`].mfe)),
        medianMAE: median(rows.map(r => r.horizons[`h${h}`].mae)),
        favorableFirst: rows.filter(r => { const p=r.horizons[`h${h}`].firstPlus1,a=r.horizons[`h${h}`].firstMinus1; return p!==null&&(a===null||p<a); }).length,
        adverseFirst: rows.filter(r => { const p=r.horizons[`h${h}`].firstPlus1,a=r.horizons[`h${h}`].firstMinus1; return a!==null&&(p===null||a<p); }).length,
        sameBar: rows.filter(r => { const p=r.horizons[`h${h}`].firstPlus1,a=r.horizons[`h${h}`].firstMinus1; return p!==null&&a!==null&&p===a; }).length,
      };
    }))
  };
  return out;
}
function mean(a){return a.length?a.reduce((x,y)=>x+y,0)/a.length:null;}

async function run(tf) {
  const candlesRaw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = candlesRaw.candles ?? candlesRaw;
  const baseline = JSON.parse(await readFile(resolve(ROOT, `data/reports/strategy-a-baseline/${tf}.json`), 'utf8'));
  const trades = (baseline.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && Number.isInteger(t.entryIndex) && t.entryIndex < PRE);
  const rows = trades.map(t => analyzeTrade(candles, t)).filter(Boolean);
  const dev = rows.filter(r => r.entryIndex < DEV);
  const val = rows.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_ENTRY_STOP_GEOMETRY_EXCURSION_TOPOLOGY',
    timeframe: tf,
    scope: { preHoldoutCandles: PRE, devCandles: DEV, valCandles: PRE-DEV, freshHoldoutExcluded: true, delayExactly1Required: true },
    methodology: {
      source: 'canonical baseline trades; no production logic reconstructed or modified',
      horizons: HORIZONS,
      pathClasses: {
        CLEAN_PLUS_1R: 'reaches +1R before any >0.25R adverse excursion',
        SHALLOW_PULLBACK: 'reaches +1R after >0.25R and <=0.50R adverse excursion, before -1R',
        DEEP_PULLBACK: 'reaches +1R after >0.50R and <1R adverse excursion, before -1R',
        WHIPSAW_AFTER_PLUS_1R: 'reaches +1R, then later reaches >=0.50R adverse excursion by H20',
        STOP_FIRST: 'reaches -1R before +1R',
        STOP_SAME_BAR_AMBIGUOUS: '+1R and -1R touched on the same OHLC bar',
        NO_PLUS_1R_BY_H20: 'neither +1R nor -1R reached by H20'
      },
      thresholds: { preFavorableAdverseR: PRE_FAV_THRESHOLDS, postFavorableAdverseR: POST_FAV_THRESHOLDS },
      note: 'Forensic diagnostic only. No optimization, no fresh holdout, no production rule change. OHLC cannot establish intrabar ordering when both thresholds occur on one bar.'
    },
    DEV: summarize(dev),
    VAL: summarize(val),
    allPreHoldout: summarize(rows),
    rows,
  };
  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  const print = (label, s) => {
    console.log(`${label}: n=${s.n} AvgR=${s.avgR?.toFixed(3)} PF=${s.pf?.toFixed(3)} WR=${(100*s.winRate).toFixed(1)} riskMed=${s.medianRisk?.toFixed(2)} MFE/MAE H20=${s.medianMFEH20?.toFixed(2)}/${s.medianMAEH20?.toFixed(2)}`);
    for (const [c,v] of Object.entries(s.pathClasses)) console.log(`  ${c}: n=${v.n} rate=${(100*v.rate).toFixed(1)} AvgR=${v.avgR?.toFixed(3)} PF=${v.pf?.toFixed(3)}`);
    console.log(`  adverse-before +1R: ${s.prePlus1AdverseThresholds['adverseBeforePlus1<=0.25R'].n}/${s.prePlus1AdverseThresholds['adverseBeforePlus1<=0.5R'].n}/${s.prePlus1AdverseThresholds['adverseBeforePlus1<=0.75R'].n}/${s.prePlus1AdverseThresholds['adverseBeforePlus1<=1R'].n}/${s.prePlus1AdverseThresholds['adverseBeforePlus1<=1.5R'].n}`);
  };
  console.log(`\n=== ${tf} DELAY1 ENTRY→STOP GEOMETRY / EXCURSION TOPOLOGY ===`);
  print('DEV', report.DEV); print('VAL', report.VAL);
  console.log(`Report -> ${out}`);
}

for (const tf of ['1min','5min']) await run(tf);
