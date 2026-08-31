import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const INPUT = resolve(ROOT, 'data/reports/strategy-a-baseline');
const DATA = resolve(ROOT, 'data/historical');
const OUTPUT = resolve(ROOT, 'data/reports/strategy-a-structure-feature-forensics');
const PIVOT = 2;
const LOOKBACK = 20;

function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(r => r > 0), losses = rs.filter(r => r < 0);
  const gw = wins.reduce((s, r) => s + r, 0), gl = Math.abs(losses.reduce((s, r) => s + r, 0));
  return { trades: rs.length, wins: wins.length, losses: losses.length, winRate: rs.length ? wins.length / rs.length : 0, avgR: rs.length ? rs.reduce((s, r) => s + r, 0) / rs.length : 0, totalR: rs.reduce((s, r) => s + r, 0), PF: gl ? gw / gl : null };
}

function swingPoints(candles) {
  const out = [];
  for (let i = PIVOT; i < candles.length - PIVOT; i++) {
    const c = candles[i];
    let high = true, low = true;
    for (let j = i - PIVOT; j <= i + PIVOT; j++) {
      if (j === i) continue;
      if (candles[j].high >= c.high) high = false;
      if (candles[j].low <= c.low) low = false;
    }
    if (high) out.push({ index: i, side: 'HIGH', price: c.high });
    if (low) out.push({ index: i, side: 'LOW', price: c.low });
  }
  return out.sort((a, b) => a.index - b.index || a.side.localeCompare(b.side));
}

function contextAt(candles, swings, index) {
  const prior = swings.filter(s => s.index < index - PIVOT);
  const highs = prior.filter(s => s.side === 'HIGH');
  const lows = prior.filter(s => s.side === 'LOW');
  const lastHigh = highs.at(-1), prevHigh = highs.at(-2), lastLow = lows.at(-1), prevLow = lows.at(-2);
  let bias = 'MIXED';
  if (lastHigh && prevHigh && lastLow && prevLow) {
    const bullish = lastHigh.price > prevHigh.price && lastLow.price > prevLow.price;
    const bearish = lastHigh.price < prevHigh.price && lastLow.price < prevLow.price;
    if (bullish) bias = 'BULLISH'; else if (bearish) bias = 'BEARISH';
  }
  const c = candles[index];
  const range = c.high - c.low;
  const body = Math.abs(c.close - c.open);
  const priorRanges = candles.slice(Math.max(0, index - LOOKBACK), index).map(x => x.high - x.low).filter(x => x > 0);
  const medianRange = priorRanges.length ? [...priorRanges].sort((a,b) => a-b)[Math.floor((priorRanges.length - 1) / 2)] : null;
  const displacement = range > 0 ? body / range : null;
  const expansion = medianRange && medianRange > 0 ? range / medianRange : null;
  const buySweep = !!(lastLow && c.low < lastLow.price && c.close > lastLow.price);
  const sellSweep = !!(lastHigh && c.high > lastHigh.price && c.close < lastHigh.price);
  const buyBOS = !!(lastHigh && c.close > lastHigh.price);
  const sellBOS = !!(lastLow && c.close < lastLow.price);
  return { bias, aligned: bias === 'BULLISH' ? 'BUY' : bias === 'BEARISH' ? 'SELL' : 'NEUTRAL', buySweep, sellSweep, buyBOS, sellBOS, displacement, expansion, lastHigh: lastHigh?.price ?? null, lastLow: lastLow?.price ?? null };
}

function featuresForTrade(candles, swings, trade) {
  const i = Number(trade.entryIndex);
  if (!Number.isInteger(i) || i < LOOKBACK || i >= candles.length) return null;
  const x = contextAt(candles, swings, i);
  const aligned = x.aligned === trade.direction;
  const sweep = trade.direction === 'BUY' ? x.buySweep : x.sellSweep;
  const bos = trade.direction === 'BUY' ? x.buyBOS : x.sellBOS;
  const displacement = Number.isFinite(x.displacement) && x.displacement >= 0.60;
  const expansion = Number.isFinite(x.expansion) && x.expansion >= 1.50;
  return { ...trade, feature: { ...x, aligned, sweep, bos, displacement, expansion } };
}

function group(rows, keyFn) {
  const map = new Map();
  for (const r of rows) { const k = keyFn(r); if (!map.has(k)) map.set(k, []); map.get(k).push(r); }
  return Object.fromEntries([...map].map(([k,v]) => [k, stats(v)]));
}

function halves(rows) {
  const a = [...rows].sort((x,y) => String(x.entryTime).localeCompare(String(y.entryTime)));
  const m = Math.floor(a.length / 2); return [a.slice(0,m), a.slice(m)];
}

function analyzeFeature(rows, name) {
  const yes = rows.filter(r => r.feature?.[name] === true);
  const no = rows.filter(r => r.feature?.[name] === false);
  const [y1,y2] = halves(yes);
  return { yes: stats(yes), no: stats(no), firstHalf: stats(y1), secondHalf: stats(y2), stablePositive: y1.length >= 15 && y2.length >= 15 && y1.length > 0 && y2.length > 0 && y1.reduce((s,r)=>s+r.rMultiple,0)/y1.length > 0 && y2.reduce((s,r)=>s+r.rMultiple,0)/y2.length > 0 };
}

async function run(timeframe) {
  const report = JSON.parse(await readFile(resolve(INPUT, `${timeframe}.json`), 'utf8'));
  const dataset = JSON.parse(await readFile(resolve(DATA, `xauusd-${timeframe}.json`), 'utf8'));
  const candles = dataset.candles;
  const swings = swingPoints(candles);
  const rows = (report.trades ?? []).filter(t => Number.isFinite(t.rMultiple)).map(t => featuresForTrade(candles, swings, t)).filter(Boolean);
  const features = ['aligned', 'sweep', 'bos', 'displacement', 'expansion'];
  const featureResults = Object.fromEntries(features.map(name => [name, analyzeFeature(rows, name)]));
  const [first, second] = halves(rows);
  const reportOut = {
    strategy: 'Strategy A / SP2L', timeframe, pivot: PIVOT, lookback: LOOKBACK,
    purpose: 'Diagnostic reconstruction of structural/context features at baseline entries. No strategy rule is activated.',
    sample: { matched: rows.length, firstHalf: first.length, secondHalf: second.length, baseline: stats(rows) },
    features: featureResults,
    combinations: {
      alignedAndSweep: stats(rows.filter(r => r.feature.aligned && r.feature.sweep)),
      alignedAndBOS: stats(rows.filter(r => r.feature.aligned && r.feature.bos)),
      alignedAndDisplacement: stats(rows.filter(r => r.feature.aligned && r.feature.displacement)),
      alignedAndExpansion: stats(rows.filter(r => r.feature.aligned && r.feature.expansion)),
      sweepAndDisplacement: stats(rows.filter(r => r.feature.sweep && r.feature.displacement)),
    },
    byBias: group(rows, r => r.feature.bias),
    oosByBias: { firstHalf: group(first, r => r.feature.bias), secondHalf: group(second, r => r.feature.bias) },
    followUpCandidates: features.filter(name => featureResults[name].stablePositive).map(name => name),
    warnings: [
      'Structural context uses only candles available before the entry index plus the entry candle for reaction features; sweep/BOS/displacement therefore assume the signal is evaluated at entry-candle close.',
      'Pivot=2 is a fixed diagnostic probe, not a validated production parameter.',
      'No feature or combination is promoted to a trading rule by this report.',
      'Small samples and correlated features can create unstable apparent edges.',
    ],
  };
  await mkdir(OUTPUT, { recursive: true });
  const out = resolve(OUTPUT, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(reportOut, null, 2));
  console.log(`${timeframe}: matched=${rows.length} baselinePF=${reportOut.sample.baseline.PF?.toFixed(4) ?? 'n/a'}`);
  for (const [name, value] of Object.entries(featureResults)) console.log(`  ${name}: YES n=${value.yes.trades} PF=${value.yes.PF?.toFixed(4) ?? 'n/a'} avgR=${value.yes.avgR.toFixed(4)} | NO n=${value.no.trades} PF=${value.no.PF?.toFixed(4) ?? 'n/a'} avgR=${value.no.avgR.toFixed(4)} stable=${value.stablePositive}`);
  console.log(`  follow-up candidates: ${reportOut.followUpCandidates.join(', ') || 'NONE'}`);
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
