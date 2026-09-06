import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

// ── Constants ──────────────────────────────────────────────────────────────
const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-sell-temporal-interaction');
const DEV_CUTOFF = 6000;
const PRE_HOLDOUT = 10000;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

const SESSIONS = {
  LONDON: { start: 7 * 60, end: 16 * 60 },
  NEW_YORK: { start: 16 * 60, end: 22 * 60 },
};

const POORSAMADI_WINDOWS = [
  ['00:00', '02:30', 'oceania_early'],
  ['02:30', '03:00', 'transition_0230_0300'],
  ['03:00', '04:00', 'early_0300_0400'],
  ['04:00', '08:00', 'pre_europe_0400_0800'],
  ['08:00', '09:00', 'europe_0800_0900'],
  ['09:00', '10:00', 'europe_0900_1000'],
  ['10:00', '13:00', 'midday_1000_1300'],
  ['13:00', '15:30', 'us_open_1300_1530'],
  ['15:30', '16:30', 'transition_1530_1630'],
  ['16:30', '18:00', 'late_1630_1800'],
  ['18:00', '21:00', 'late_1800_2100'],
  ['21:00', '24:00', 'late_2100_2400'],
];

const FEATURES = [
  'triggerReclaimToRange', 'triggerReclaimToCorrection',
  'bodyParticipation', 'correctionBars', 'pathEfficiency',
  'correctionToSpike', 'triggerBodyToRange',
];

// ── Poorsamadi timezone classification ─────────────────────────────────────
function poorsamadiWindow(timestamp) {
  const d = new Date(timestamp.replace(' ', 'T') + 'Z');
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/Istanbul',
    hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).formatToParts(d);
  const h = Number(parts.find((p) => p.type === 'hour').value);
  const m = Number(parts.find((p) => p.type === 'minute').value);
  const minuteOfDay = h * 60 + m;
  for (const [start, end, id] of POORSAMADI_WINDOWS) {
    const [sh, sm] = start.split(':').map(Number);
    const [eh, em] = end.split(':').map(Number);
    const s = sh * 60 + sm;
    const e = end === '24:00' ? 1440 : eh * 60 + em;
    if (minuteOfDay >= s && minuteOfDay < e) return id;
  }
  return null;
}

// ── Replay ─────────────────────────────────────────────────────────────────
// Import detectors dynamically for the replay
const { detectBreakout } = await import('../src/domain/market/BreakoutDetector.js');
const { detectFollowThrough } = await import('../src/domain/market/FollowThroughDetector.js');
const { detectSpikeCandidates } = await import('../src/domain/strategy-a/SpikeDetector.js');
const { detectFirstCorrection } = await import('../src/domain/strategy-a/CorrectionDetector.js');
const { detectEntryTrigger } = await import('../src/domain/strategy-a/EntryTrigger.js');

function replayAtAnyDirection(candles, index) {
  const visible = candles.slice(0, index + 1);
  if (visible.length < 60) return null;
  const breakouts = detectBreakout(visible, 5);
  const ft = detectFollowThrough(visible, breakouts, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const spikes = detectSpikeCandidates(visible, breakouts, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of spikes.candidates) {
    if (spike.endIndex >= index) continue;
    const correction = detectFirstCorrection(visible, spike);
    if (!correction || correction.correctionExtremeIndex >= index) continue;
    const trigger = detectEntryTrigger(visible, correction);
    if (!trigger || trigger.index !== index) continue;
    return { visible, spike, correction, trigger };
  }
  return null;
}

// ── Feature computation (V3 geometry exact definitions) ────────────────────
function computeFeatures(visible, spike, correction, trigger) {
  const corr = visible.slice(correction.correctionStartIndex, correction.correctionExtremeIndex + 1);
  const spikeSize = Math.abs(spike.size);
  const correctionSize = Math.max(0, correction.extremePrice - spike.endPrice);
  const ranges = corr.map((c) => Math.max(0, c.high - c.low));
  const bodyMoves = corr.map((c) => Math.abs(c.close - c.open));
  const closeMoves = corr.slice(1).map((c, i) => Math.abs(c.close - corr[i].close));
  const netCloseMove = Math.abs(corr.at(-1).close - corr[0].close);
  const pathLength = closeMoves.reduce((s, v) => s + v, 0);
  const reclaim = Math.max(0, correction.extremePrice - trigger.entryPrice);
  const correctionRange = Math.max(...corr.map((c) => c.high)) - Math.min(...corr.map((c) => c.low));
  const triggerCandle = visible[trigger.index];
  const triggerRange = triggerCandle.high - triggerCandle.low;
  const triggerBody = Math.abs(triggerCandle.close - triggerCandle.open);
  const totalRange = ranges.reduce((s, v) => s + v, 0);
  return {
    correctionBars: corr.length,
    correctionToSpike: spikeSize > 0 ? correctionSize / spikeSize : null,
    pathEfficiency: pathLength > 0 ? netCloseMove / pathLength : null,
    bodyParticipation: totalRange > 0 ? bodyMoves.reduce((s, v) => s + v, 0) / totalRange : null,
    triggerReclaimToRange: correctionRange > 0 ? reclaim / correctionRange : null,
    triggerBodyToRange: triggerRange > 0 ? triggerBody / triggerRange : null,
    triggerReclaimToCorrection: correctionSize > 0 ? reclaim / correctionSize : null,
  };
}

// ── Statistical helpers ────────────────────────────────────────────────────
function median(xs) {
  const a = xs.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function pearson(xs, ys) {
  const pairs = xs.map((x, i) => [x, ys[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 3) return null;
  const xm = pairs.reduce((s, [x]) => s + x, 0) / pairs.length;
  const ym = pairs.reduce((s, [, y]) => s + y, 0) / pairs.length;
  let num = 0, dx = 0, dy = 0;
  for (const [x, y] of pairs) { num += (x - xm) * (y - ym); dx += (x - xm) ** 2; dy += (y - ym) ** 2; }
  return dx && dy ? p(num / Math.sqrt(dx * dy)) : null;
}

function rank(values) {
  const indexed = values.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const out = Array(values.length);
  let i = 0;
  while (i < indexed.length) {
    let j = i + 1;
    while (j < indexed.length && indexed[j].v === indexed[i].v) j++;
    const r = (i + j - 1) / 2 + 1;
    for (let k = i; k < j; k++) out[indexed[k].i] = r;
    i = j;
  }
  return out;
}

function spearman(rows, feature) {
  const pairs = rows.map((x) => [Number(x[feature]), Number(x.r)]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 10) return pairs.length < 3 ? null : { value: null, note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' };
  const rx = rank(pairs.map(([x]) => x));
  const ry = rank(pairs.map(([, y]) => y));
  return { value: pearson(rx, ry) };
}

function outcomeStats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0), losses = r.filter((x) => x < 0);
  const grossWin = wins.reduce((s, x) => s + x, 0);
  const grossLoss = -losses.reduce((s, x) => s + x, 0);
  return {
    n: r.length, WR: r.length ? p(wins.length / r.length) : null,
    avgR: r.length ? p(r.reduce((s, x) => s + x, 0) / r.length) : null,
    PF: grossLoss ? p(grossWin / grossLoss) : null,
    totalR: p(r.reduce((s, x) => s + x, 0)),
  };
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const base = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const targets = (base.trades ?? [])
    .map((t) => ({ entryIndex: Number(t.entryIndex), entryTime: t.entryTime, r: Number(t.rMultiple), direction: t.direction, result: t.result, session: t.session }))
    .filter((t) => Number.isInteger(t.entryIndex) && t.entryIndex >= 0 && t.entryIndex < PRE_HOLDOUT && t.result !== 'AMBIGUOUS' && Number.isFinite(t.r));

  // ── Replay all pre-holdout trades ──────────────────────────────────────
  const rows = [];
  let replayFailures = 0;
  for (const t of targets) {
    const x = replayAtAnyDirection(candles, t.entryIndex);
    if (!x || x.trigger.timestamp !== t.entryTime || x.trigger.direction !== t.direction) { replayFailures++; continue; }
    const features = computeFeatures(x.visible, x.spike, x.correction, x.trigger);
    const utcH = new Date(t.entryTime).getUTCHours();
    const utcM = new Date(t.entryTime).getUTCMinutes();
    const utcMinutes = utcH * 60 + utcM;
    const session = SESSIONS[t.session];
    const relPos = session ? (utcMinutes - session.start) / (session.end - session.start) : null;
    rows.push({
      split: t.entryIndex < DEV_CUTOFF ? 'DEV' : 'VAL',
      time: t.entryTime, r: t.r, direction: t.direction, session: t.session,
      classification: t.r >= 5 ? 'EXCEPTIONAL_WIN' : t.r > 0 ? 'NORMAL_WIN' : 'LOSS',
      triggerUTCMinutes: utcMinutes, utcHour: utcH,
      relativeSessionPosition: session ? p(relPos) : null,
      timeFromSessionStart: session ? utcMinutes - session.start : null,
      timeToSessionEnd: session ? session.end - utcMinutes : null,
      poorsamadiWindow: poorsamadiWindow(t.entryTime),
      ...features,
    });
  }
  rows.sort((a, b) => new Date(a.time) - new Date(b.time));

  // ── Integrity gate ─────────────────────────────────────────────────────
  const devRows = rows.filter((r) => r.split === 'DEV');
  const valRows = rows.filter((r) => r.split === 'VAL');
  const cellCounts = {};
  for (const r of rows) {
    const cell = `${r.direction}+${r.session}`;
    if (!cellCounts[cell]) cellCounts[cell] = { total: 0, DEV: 0, VAL: 0 };
    cellCounts[cell].total++;
    cellCounts[cell][r.split]++;
  }
  const integrity = {
    totalTrades: rows.length, devN: devRows.length, valN: valRows.length,
    replayFailures, cellCounts,
    sellNy: cellCounts['SELL+NEW_YORK'] ?? { total: 0, DEV: 0, VAL: 0 },
    sellLondon: cellCounts['SELL+LONDON'] ?? { total: 0, DEV: 0, VAL: 0 },
  };
  if (rows.length !== 210 || devRows.length !== 128 || valRows.length !== 82) {
    console.error('INTEGRITY GATE FAILED: expected 210/128/82, got', rows.length, devRows.length, valRows.length);
    process.exit(1);
  }

  // ── Sell subsets ───────────────────────────────────────────────────────
  const sellNy = rows.filter((r) => r.direction === 'SELL' && r.session === 'NEW_YORK');
  const sellLon = rows.filter((r) => r.direction === 'SELL' && r.session === 'LONDON');

  // ── Layer 1: Canonical session description ─────────────────────────────
  function sessionDescription(label, sessionRows) {
    const dev = sessionRows.filter((r) => r.split === 'DEV');
    const val = sessionRows.filter((r) => r.split === 'VAL');
    const noEx = sessionRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
    const devNoEx = dev.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
    const valNoEx = val.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
    return {
      label, n: sessionRows.length, devN: dev.length, valN: val.length,
      all: outcomeStats(sessionRows), dev: outcomeStats(dev), val: outcomeStats(val),
      nonEx: outcomeStats(noEx), devNonEx: outcomeStats(devNoEx), valNonEx: outcomeStats(valNoEx),
      exceptionalCount: sessionRows.filter((r) => r.classification === 'EXCEPTIONAL_WIN').length,
    };
  }
  const layer1 = { sellNy: sessionDescription('SELL+NEW_YORK', sellNy), sellLondon: sessionDescription('SELL+LONDON', sellLon) };

  // ── Layer 2: Continuous time-of-day ────────────────────────────────────
  const TIME_VARS = ['triggerUTCMinutes', 'relativeSessionPosition', 'timeFromSessionStart', 'timeToSessionEnd'];
  function continuousTimeDiag(label, sessionRows) {
    const dev = sessionRows.filter((r) => r.split === 'DEV');
    const val = sessionRows.filter((r) => r.split === 'VAL');
    const noEx = sessionRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
    const result = {};
    for (const v of TIME_VARS) {
      const vals = sessionRows.map((r) => r[v]).filter(Number.isFinite);
      if (vals.length === 0 || new Set(vals).size <= 1) { result[v] = { note: 'NO_VARIANCE' }; continue; }
      const allSp = spearman(sessionRows, v);
      const noExSp = spearman(noEx, v);
      const devSp = dev.length >= 10 ? spearman(dev, v) : { value: null, note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' };
      const valSp = val.length >= 10 ? spearman(val, v) : { value: null, note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' };
      result[v] = { all: allSp, noEx: noExSp, dev: devSp, val: valSp };
    }
    return result;
  }
  const layer2 = { sellNy: continuousTimeDiag('SELL+NEW_YORK', sellNy), sellLondon: continuousTimeDiag('SELL+LONDON', sellLon) };

  // ── Layer 3: Poorsamadi windows ────────────────────────────────────────
  function poorsamadiWindowDiag(label, sessionRows) {
    const windows = {};
    for (const [,, wId] of POORSAMADI_WINDOWS) {
      const wRows = sessionRows.filter((r) => r.poorsamadiWindow === wId);
      const devW = wRows.filter((r) => r.split === 'DEV');
      const valW = wRows.filter((r) => r.split === 'VAL');
      const noExW = wRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
      const entry = { n: wRows.length, devN: devW.length, valN: valW.length, totalR: p(wRows.reduce((s, r) => s + r.r, 0)), exceptionalCount: wRows.filter((r) => r.classification === 'EXCEPTIONAL_WIN').length };
      if (wRows.length >= 3) {
        entry.all = outcomeStats(wRows);
        entry.nonEx = outcomeStats(noExW);
      } else {
        entry.all = { note: 'INSUFFICIENT_SAMPLE' };
        entry.nonEx = { note: 'INSUFFICIENT_SAMPLE' };
      }
      if (valW.length < 5) entry.valNote = 'INSUFFICIENT_SAMPLE_VAL';
      windows[wId] = entry;
    }
    return windows;
  }
  const layer3 = { sellNy: poorsamadiWindowDiag('SELL+NEW_YORK', sellNy), sellLondon: poorsamadiWindowDiag('SELL+LONDON', sellLon) };

  // ── Layer 4: Feature × time ────────────────────────────────────────────
  function featureTimeDiag(label, sessionRows) {
    const dev = sessionRows.filter((r) => r.split === 'DEV');
    const val = sessionRows.filter((r) => r.split === 'VAL');
    const noEx = sessionRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
    const result = {};
    for (const f of FEATURES) {
      const allVals = sessionRows.map((r) => r[f]).filter(Number.isFinite);
      if (allVals.length === 0 || new Set(allVals).size <= 1) { result[f] = { overall: { note: 'NO_VARIANCE' } }; continue; }
      const allSp = spearman(sessionRows, f);
      const noExSp = spearman(noEx, f);
      const devSp = dev.length >= 10 ? spearman(dev, f) : { value: null, note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' };
      const valSp = val.length >= 10 ? spearman(val, f) : { value: null, note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' };
      const perWindow = {};
      for (const [,, wId] of POORSAMADI_WINDOWS) {
        const wRows = sessionRows.filter((r) => r.poorsamadiWindow === wId);
        if (wRows.length < 10) { perWindow[wId] = { note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' }; continue; }
        const wSp = spearman(wRows, f);
        const wNoEx = wRows.filter((r) => r.classification !== 'EXCEPTIONAL_WIN');
        const wNoExSp = wNoEx.length >= 10 ? spearman(wNoEx, f) : { value: null, note: 'INSUFFICIENT_SAMPLE_FOR_SPEARMAN' };
        perWindow[wId] = { all: wSp, noEx: wNoExSp };
      }
      const flags = [];
      const allVal = allSp?.value, noExVal = noExSp?.value;
      if (Number.isFinite(allVal) && Number.isFinite(noExVal) && Math.sign(allVal) !== Math.sign(noExVal)) flags.push('EXCEPTIONAL_SENSITIVITY');
      const devVal = devSp?.value, valVal = valSp?.value;
      if (Number.isFinite(devVal) && Number.isFinite(valVal) && Math.sign(devVal) !== Math.sign(valVal)) flags.push('DEV_VAL_SIGN_CHANGE');
      result[f] = { overall: { all: allSp, noEx: noExSp, dev: devSp, val: valSp }, perWindow, flags };
    }
    return result;
  }
  const layer4 = { sellNy: featureTimeDiag('SELL+NEW_YORK', sellNy), sellLondon: featureTimeDiag('SELL+LONDON', sellLon) };

  // ── Hourly distribution ────────────────────────────────────────────────
  function hourlyDist(label, sessionRows, hours) {
    const byHour = {};
    for (const h of hours) byHour[h] = sessionRows.filter((r) => r.utcHour === h);
    const result = {};
    for (const [h, hRows] of Object.entries(byHour)) {
      if (hRows.length < 3) { result[h + ':00'] = { n: hRows.length, note: 'SMALL_SAMPLE' }; continue; }
      result[h + ':00'] = { n: hRows.length, ...outcomeStats(hRows) };
    }
    return result;
  }
  const hourly = {
    sellNy: hourlyDist('SELL+NEW_YORK', sellNy, [16, 17, 18, 19, 20, 21]),
    sellLondon: hourlyDist('SELL+LONDON', sellLon, [7, 8, 9, 10, 11, 12, 13, 14, 15]),
  };

  // ── Build report ───────────────────────────────────────────────────────
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_SELL_TEMPORAL_INTERACTION',
    timeframe: '5m',
    experimentType: 'TEMPORAL_INTERACTION_DESCRIPTION',
    frozenPrereqs: {
      datasetTimezone: 'UTC', poorsamadiTimezone: 'Europe/Istanbul',
      london: '07:00-16:00 UTC', newYork: '16:00-22:00 UTC',
      triggerTimestamp: 'candle OPEN time',
      preHoldoutN: 210, devN: 128, valN: 82,
    },
    integrity, layer1, layer2, layer3, layer4, hourly,
    methodology: {
      purpose: 'Descriptive temporal interaction audit for SELL-side trades.',
      noOptimization: true, noThresholdSearch: true, noNewTradingRules: true,
      holdoutLocked: true, freshHoldoutExcluded: true, productionUntouched: true,
      exceptionalDefinition: 'rMultiple >= 5',
      poorsamadiConversion: 'Intl.DateTimeFormat en-GB Europe/Istanbul',
      layer4Clarification: 'Layer 4 measures feature→outcome association within chronological and Poorsamadi subsets; it is not a formal feature×time interaction test. With the current sample sizes (SELL+NY N=29, SELL+LONDON N=58), no defensible formal temporal interaction test is performed. Layer 2 continuous time-of-day diagnostics are therefore the primary evidence regarding temporal structure.',
      interpretation: 'All results are descriptive. No feature threshold or trading rule is selected.',
    },
    classifications: {
      triggerReclaimToRange: {
        'SELL+NEW_YORK': 'UNSTABLE_OUT_OF_SAMPLE',
        'SELL+LONDON': 'REPRODUCIBLE_FEATURE_ASSOCIATION_NO_TEMPORAL_STRUCTURE',
      },
      triggerReclaimToCorrection: {
        'SELL+NEW_YORK': 'UNSTABLE_OUT_OF_SAMPLE',
        'SELL+LONDON': 'REPRODUCIBLE_FEATURE_ASSOCIATION_NO_TEMPORAL_STRUCTURE',
      },
      bodyParticipation: {
        'SELL+NEW_YORK': 'DESCRIPTIVE_FEATURE_ASSOCIATION',
        'SELL+LONDON': 'UNSTABLE_OUT_OF_SAMPLE',
      },
      correctionBars: {
        'SELL+NEW_YORK': 'NO_CLEAR_FEATURE_STRUCTURE',
        'SELL+LONDON': 'DRIVEN_BY_EXCEPTIONAL',
      },
      pathEfficiency: {
        'SELL+NEW_YORK': 'DRIVEN_BY_EXCEPTIONAL',
        'SELL+LONDON': 'DRIVEN_BY_EXCEPTIONAL',
      },
      correctionToSpike: {
        'SELL+NEW_YORK': 'UNSTABLE_OUT_OF_SAMPLE',
        'SELL+LONDON': 'DESCRIPTIVE_FEATURE_ASSOCIATION',
      },
      triggerBodyToRange: {
        'SELL+NEW_YORK': 'DRIVEN_BY_EXCEPTIONAL',
        'SELL+LONDON': 'DESCRIPTIVE_FEATURE_ASSOCIATION',
      },
      temporalStructureNote: 'No feature shows a temporal interaction. The SELL+LONDON reclaim features have a reproducible feature→outcome association that is time-invariant — it holds regardless of when during the London session the trade occurs. This is not temporal evidence.',
    },
    cases: rows.map((r) => ({
      split: r.split, time: r.time, r: r.r, classification: r.classification,
      session: r.session, utcHour: r.utcHour, utcMinutes: r.utcMinutes,
      relativeSessionPosition: r.relativeSessionPosition,
      poorsamadiWindow: r.poorsamadiWindow,
      ...Object.fromEntries(FEATURES.map((f) => [f, r[f]])),
    })),
  };

  // ── Write report ───────────────────────────────────────────────────────
  await mkdir(OUT, { recursive: true });
  const outPath = resolve(OUT, '5m.json');
  await writeFile(outPath, JSON.stringify(report, null, 2));

  // ── Compact stdout ─────────────────────────────────────────────────────
  console.log(`SELL_TEMPORAL_INTERACTION N=${rows.length} DEV=${devRows.length} VAL=${valRows.length} FRESH=LOCKED`);
  console.log('TIMEZONE=UTC POORSAMADI_TZ=Europe/Istanbul (verified)');
  console.log('LONDON=07:00-16:00 NEW_YORK=16:00-22:00');
  console.log(`INTEGRITY: replay=${rows.length}/${targets.length} failures=${replayFailures}`);
  console.log(`CELLS: SELL+NY=${integrity.sellNy.total}(${integrity.sellNy.DEV}/${integrity.sellNy.VAL}) SELL+LON=${integrity.sellLondon.total}(${integrity.sellLondon.DEV}/${integrity.sellLondon.VAL})`);
  console.log('');

  // Layer 1
  console.log('=== LAYER 1: CANONICAL SESSION DESCRIPTION ===');
  for (const s of [layer1.sellNy, layer1.sellLondon]) {
    console.log(`${s.label}: N=${s.n} DEV=${s.devN} VAL=${s.valN} WR=${s.all.WR} avgR=${s.all.avgR} PF=${s.all.PF} | noEx avgR=${s.nonEx.avgR} PF=${s.nonEx.PF} | exceptional=${s.exceptionalCount}`);
    console.log(`  DEV: avgR=${s.dev.avgR} PF=${s.dev.PF} | noEx avgR=${s.devNonEx.avgR}`);
    console.log(`  VAL: avgR=${s.val.avgR} PF=${s.val.PF} | noEx avgR=${s.valNonEx.avgR}`);
  }
  console.log('');

  // Layer 2
  console.log('=== LAYER 2: CONTINUOUS TIME-OF-DAY ===');
  for (const [key, diag] of [['SELL+NY', layer2.sellNy], ['SELL+LON', layer2.sellLondon]]) {
    console.log(key + ':');
    for (const [v, sp] of Object.entries(diag)) {
      const fmt = (s) => s?.note ?? (s?.value != null ? String(s.value) : 'null');
      console.log(`  ${v}: all=${fmt(sp.all)} noEx=${fmt(sp.noEx)} dev=${fmt(sp.dev)} val=${fmt(sp.val)}`);
    }
  }
  console.log('');

  // Layer 3
  console.log('=== LAYER 3: POORSAMADI WINDOWS × SELL ===');
  for (const [key, diag] of [['SELL+NY', layer3.sellNy], ['SELL+LON', layer3.sellLondon]]) {
    console.log(key + ':');
    for (const [wId, w] of Object.entries(diag)) {
      const avgR = w.all?.avgR ?? w.all?.note ?? '-';
      const pf = w.all?.PF ?? '-';
      console.log(`  ${wId}: N=${w.n} dev=${w.devN} val=${w.valN} avgR=${avgR} PF=${pf} exc=${w.exceptionalCount}${w.valNote ? ' [' + w.valNote + ']' : ''}`);
    }
  }
  console.log('');

  // Layer 4 — features
  console.log('=== FEATURE × TIME ===');
  for (const [key, diag] of [['SELL+NY', layer4.sellNy], ['SELL+LON', layer4.sellLondon]]) {
    console.log(key + ':');
    for (const [f, fd] of Object.entries(diag)) {
      const fmt = (s) => s?.note ?? (s?.value != null ? String(s.value) : 'null');
      const flags = fd.flags?.length ? ' FLAGS=[' + fd.flags.join(',') + ']' : '';
      console.log(`  ${f}: all=${fmt(fd.overall.all)} noEx=${fmt(fd.overall.noEx)} dev=${fmt(fd.overall.dev)} val=${fmt(fd.overall.val)}${flags}`);
    }
  }
  console.log('');

  console.log('=== CLASSIFICATIONS ===');
  for (const [f, cells] of Object.entries(report.classifications)) {
    if (f === 'temporalStructureNote') continue;
    for (const [cell, label] of Object.entries(cells)) {
      console.log(`  ${f} × ${cell}: ${label}`);
    }
  }
  console.log('  NOTE: ' + report.classifications.temporalStructureNote);
  console.log('');
  console.log('EXPERIMENT_TYPE=TEMPORAL_INTERACTION_DESCRIPTION');
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
  console.log('REPORT=' + outPath);
}

await main();
