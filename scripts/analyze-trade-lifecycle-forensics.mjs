import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-trade-lifecycle-forensics');
const src = tf => resolve(ROOT, `data/reports/strategy-a-mae-mfe-forensics/${tf}.json`);

const HORIZONS = [1, 2, 3, 5, 8, 12, 20];
const MAE_LEVELS = [0.25, 0.5, 0.75, 1];
const MFE_LEVELS = [0.5, 1, 1.5, 2];

function finite(v) { return Number.isFinite(Number(v)); }
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const n = rs.length;
  if (!n) return { n: 0, avgR: 0, totalR: 0, winRate: 0, PF: null };
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return { n, avgR: rs.reduce((a, b) => a + b, 0) / n, totalR: rs.reduce((a, b) => a + b, 0), winRate: wins.length / n, PF: gl ? gp / gl : (gp ? null : 0) };
}
function split(rows) {
  const a = [...rows].sort((x, y) => new Date(x.entryTime) - new Date(y.entryTime));
  const c = Math.floor(a.length / 3);
  return { dev: a.slice(0, c), validation: a.slice(c, 2 * c), holdout: a.slice(2 * c) };
}
function num(r, ...keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function fieldRows(rows, predicate) { return rows.filter(predicate); }
function excursionAt(row, h) {
  const mae = num(row, `maeR_H${h}`, `maeH${h}`, `earlyMaeR_H${h}`, `earlyMAE_H${h}`);
  const mfe = num(row, `mfeR_H${h}`, `mfeH${h}`, `earlyMfeR_H${h}`, `earlyMFE_H${h}`);
  return { mae, mfe };
}

function enrich(row) {
  const exitBar = num(row, 'exitBar', 'barsToExit', 'timeToExitBars', 'holdingBars', 'barsHeld');
  const mae = num(row, 'maeR', 'mae', 'MAE');
  const mfe = num(row, 'mfeR', 'mfe', 'MFE');
  const timeMfe = num(row, 'timeToMfeBars', 'barsToMfe', 'barsToMaxFavorable');
  const timeMae = num(row, 'timeToMaeBars', 'barsToMae', 'barsToMaxAdverse');
  const r = Number(row.rMultiple);
  return {
    ...row,
    lifecycle: {
      outcome: r > 0 ? 'WIN' : r < 0 ? 'LOSS' : 'FLAT',
      exitBars: exitBar,
      maeR: mae,
      mfeR: mfe,
      timeToMfeBars: timeMfe,
      timeToMaeBars: timeMae,
      mfeBeforeExit: finite(mfe) && finite(exitBar) && finite(timeMfe) ? timeMfe <= exitBar : null,
      maeBeforeExit: finite(mae) && finite(exitBar) && finite(timeMae) ? timeMae <= exitBar : null,
      excursionEfficiency: finite(mfe) && finite(mae) ? mfe / Math.max(1, mae) : null,
    },
  };
}

function descriptive(rows) {
  const winners = rows.filter(r => r.lifecycle.outcome === 'WIN');
  const losers = rows.filter(r => r.lifecycle.outcome === 'LOSS');
  const q = rs => {
    const vals = rs.filter(Number.isFinite).sort((a, b) => a - b);
    if (!vals.length) return null;
    const at = p => vals[Math.min(vals.length - 1, Math.floor((vals.length - 1) * p))];
    return { p25: at(.25), median: at(.5), p75: at(.75), mean: vals.reduce((a,b)=>a+b,0)/vals.length };
  };
  const metrics = rows2 => ({
    n: rows2.length,
    exitBars: q(rows2.map(r => r.lifecycle.exitBars).filter(finite)),
    maeR: q(rows2.map(r => r.lifecycle.maeR).filter(finite)),
    mfeR: q(rows2.map(r => r.lifecycle.mfeR).filter(finite)),
    timeToMfeBars: q(rows2.map(r => r.lifecycle.timeToMfeBars).filter(finite)),
    timeToMaeBars: q(rows2.map(r => r.lifecycle.timeToMaeBars).filter(finite)),
  });
  return { all: metrics(rows), winners: metrics(winners), losers: metrics(losers) };
}

async function run(tf) {
  const raw = JSON.parse(await readFile(src(tf), 'utf8'));
  const rows = (raw.tradeRows || []).filter(r => finite(r.rMultiple)).map(enrich);
  const s = split(rows);
  const out = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_TRADE_LIFECYCLE_FORENSICS_V1',
    timeframe: tf,
    scope: 'Descriptive lifecycle analysis only. No entry rule, exit rule, threshold, or holdout selection is performed.',
    methodology: {
      source: 'strategy-a-mae-mfe-forensics tradeRows',
      dimensions: ['exit timing', 'MAE', 'MFE', 'time-to-MAE', 'time-to-MFE', 'winner/loser lifecycle separation'],
      split: 'single chronological thirds: DEV / VALIDATION / HOLDOUT; holdout is reported descriptively and never ranked',
      horizons: HORIZONS,
      note: 'Early-horizon excursion fields are consumed when present; missing fields are not imputed.'
    },
    counts: { all: rows.length, dev: s.dev.length, validation: s.validation.length, holdout: s.holdout.length },
    lifecycle: {
      all: descriptive(rows),
      dev: descriptive(s.dev),
      validation: descriptive(s.validation),
      holdout: descriptive(s.holdout),
    },
    outcomeByDirection: {},
    outcomeBySession: {},
    thresholds: {},
  };

  for (const direction of ['BUY', 'SELL']) {
    out.outcomeByDirection[direction] = {
      all: stats(fieldRows(rows, r => r.direction === direction)),
      dev: stats(fieldRows(s.dev, r => r.direction === direction)),
      validation: stats(fieldRows(s.validation, r => r.direction === direction)),
      holdout: stats(fieldRows(s.holdout, r => r.direction === direction)),
    };
  }
  for (const session of ['LONDON', 'NEW_YORK', 'OUTSIDE']) {
    out.outcomeBySession[session] = {
      all: stats(fieldRows(rows, r => r.session === session)),
      dev: stats(fieldRows(s.dev, r => r.session === session)),
      validation: stats(fieldRows(s.validation, r => r.session === session)),
      holdout: stats(fieldRows(s.holdout, r => r.session === session)),
    };
  }

  for (const x of MAE_LEVELS) {
    out.thresholds[`mae_ge_${x}R`] = {
      all: stats(rows.filter(r => finite(r.lifecycle.maeR) && r.lifecycle.maeR >= x)),
      dev: stats(s.dev.filter(r => finite(r.lifecycle.maeR) && r.lifecycle.maeR >= x)),
      validation: stats(s.validation.filter(r => finite(r.lifecycle.maeR) && r.lifecycle.maeR >= x)),
      holdout: stats(s.holdout.filter(r => finite(r.lifecycle.maeR) && r.lifecycle.maeR >= x)),
    };
  }
  for (const x of MFE_LEVELS) {
    out.thresholds[`mfe_ge_${x}R`] = {
      all: stats(rows.filter(r => finite(r.lifecycle.mfeR) && r.lifecycle.mfeR >= x)),
      dev: stats(s.dev.filter(r => finite(r.lifecycle.mfeR) && r.lifecycle.mfeR >= x)),
      validation: stats(s.validation.filter(r => finite(r.lifecycle.mfeR) && r.lifecycle.mfeR >= x)),
      holdout: stats(s.holdout.filter(r => finite(r.lifecycle.mfeR) && r.lifecycle.mfeR >= x)),
    };
  }

  const pathClasses = [
    ['fast_winner', r => r.lifecycle.outcome === 'WIN' && finite(r.lifecycle.timeToMfeBars) && r.lifecycle.timeToMfeBars <= 3],
    ['slow_winner', r => r.lifecycle.outcome === 'WIN' && finite(r.lifecycle.timeToMfeBars) && r.lifecycle.timeToMfeBars > 3],
    ['fast_loser', r => r.lifecycle.outcome === 'LOSS' && finite(r.lifecycle.exitBars) && r.lifecycle.exitBars <= 3],
    ['slow_loser', r => r.lifecycle.outcome === 'LOSS' && finite(r.lifecycle.exitBars) && r.lifecycle.exitBars > 3],
    ['low_adverse_winner', r => r.lifecycle.outcome === 'WIN' && finite(r.lifecycle.maeR) && r.lifecycle.maeR < 0.5],
    ['high_adverse_winner', r => r.lifecycle.outcome === 'WIN' && finite(r.lifecycle.maeR) && r.lifecycle.maeR >= 0.5],
  ];
  out.pathClasses = Object.fromEntries(pathClasses.map(([name, fn]) => [name, {
    all: stats(rows.filter(fn)), dev: stats(s.dev.filter(fn)), validation: stats(s.validation.filter(fn)), holdout: stats(s.holdout.filter(fn))
  }]));

  await mkdir(OUT, { recursive: true });
  const path = resolve(OUT, `${tf}.json`);
  await writeFile(path, JSON.stringify(out, null, 2));
  console.log(`${tf}: trades=${rows.length} winners=${rows.filter(r=>r.lifecycle.outcome==='WIN').length} losers=${rows.filter(r=>r.lifecycle.outcome==='LOSS').length}`);
  console.log(`Report -> ${path}`);
}

for (const tf of ['1min', '5min']) await run(tf);
