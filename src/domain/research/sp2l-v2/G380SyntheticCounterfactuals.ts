/**
 * G380 research-only counterfactual executor.
 *
 * IMPORTANT: every formula in this file is a named hypothesis encoding, not a
 * Strategy A rule. The purpose is to make competing interpretations observable
 * on controlled OHLC fixtures without promoting any interpretation to canonical.
 */

export interface Ohlc {
  open: number;
  high: number;
  low: number;
  close: number;
}

export type G380Family = 'PGAP' | 'ABCD' | 'ENTRY' | 'SL' | 'TP';

export interface G380Fixture {
  id: string;
  family: G380Family;
  bars: readonly Ohlc[];
  hypothesisA: string;
  hypothesisB: string;
  expected: 'DISTINCT' | 'EQUIVALENT';
  canonical: false;
}

export interface G380Observation {
  id: string;
  family: G380Family;
  hypothesisA: string;
  hypothesisB: string;
  outputA: number | string | boolean;
  outputB: number | string | boolean;
  classification: 'DISTINCT' | 'EQUIVALENT';
  canonical: false;
}

const bodyHigh = (b: Ohlc) => Math.max(b.open, b.close);
const bodyLow = (b: Ohlc) => Math.min(b.open, b.close);

// Candidate P-Gap encodings — deliberately non-canonical.
function pgH01(bars: readonly Ohlc[]): boolean {
  if (bars.length < 3) return false;
  return bars[2].low > bars[0].high;
}
function pgH02(bars: readonly Ohlc[]): boolean {
  if (bars.length < 3) return false;
  const pressure = bars[0].close > bars[0].open && bars[1].close > bars[1].open;
  return pressure && bars[2].low > bars[0].high;
}
function pgH03(bars: readonly Ohlc[]): string {
  return bars.length >= 3 && bars[2].low > bars[0].high ? 'post-breakout' : 'none';
}
function pgH04(bars: readonly Ohlc[]): string {
  if (bars.length < 3 || !(bars[2].low > bars[0].high)) return 'none';
  const higherLow = bars[1].low > bars[0].low;
  return higherLow ? 'higher-low' : 'none';
}

// Candidate A/B/C/D encodings — deliberately non-canonical.
function abcdH01(bars: readonly Ohlc[]): number {
  return bars.length < 2 ? 0 : bars[1].high - bars[0].low;
}
function abcdH02(bars: readonly Ohlc[]): number {
  return bars.length < 2 ? 0 : bodyHigh(bars[1]) - bodyLow(bars[0]);
}
function abcdH03(bars: readonly Ohlc[]): number {
  return bars.length < 2 ? 0 : bars[1].close - bars[0].close;
}

// Candidate entry encodings — no candidate is asserted as source meaning.
function enH01(bars: readonly Ohlc[]): number {
  return bars.length < 2 ? 0 : bars[0].low;
}
function enH02(bars: readonly Ohlc[]): number {
  return bars.length < 2 ? 0 : bars[1].low;
}
function enH03(bars: readonly Ohlc[]): number {
  if (bars.length < 2) return 0;
  return (bars[0].low + bars[0].high) / 2;
}

// Candidate SL encodings.
function slH01(bars: readonly Ohlc[]): number {
  return bars.length === 0 ? 0 : bars[0].low;
}
function slH02(bars: readonly Ohlc[]): number {
  return bars.length === 0 ? 0 : bodyLow(bars[0]);
}

// Candidate target encodings: AB=CD projection vs default 1:1 reward.
function tpH01(bars: readonly Ohlc[]): number {
  if (bars.length < 3) return 0;
  const leg1 = bars[1].high - bars[0].low;
  return bars[2].close + leg1;
}
function tpH04(bars: readonly Ohlc[]): number {
  if (bars.length < 3) return 0;
  const entry = bars[2].close;
  const risk = entry - bars[0].low;
  return entry + risk;
}

export const G380_FIXTURES: readonly G380Fixture[] = [
  { id:'G380-PG-01', family:'PGAP', bars:[{open:100,high:102,low:99,close:101},{open:101,high:103,low:100,close:102},{open:103,high:106,low:104,close:105}], hypothesisA:'PG-H01', hypothesisB:'PG-H02', expected:'EQUIVALENT', canonical:false },
  { id:'G380-PG-02', family:'PGAP', bars:[{open:100,high:102,low:99,close:101},{open:101,high:103,low:100,close:102},{open:103,high:106,low:104,close:105}], hypothesisA:'PG-H01', hypothesisB:'PG-H03', expected:'EQUIVALENT', canonical:false },
  { id:'G380-PG-03', family:'PGAP', bars:[{open:100,high:102,low:99,close:101},{open:98,high:100,low:96,close:99},{open:103,high:106,low:104,close:105}], hypothesisA:'PG-H03', hypothesisB:'PG-H04', expected:'DISTINCT', canonical:false },
  { id:'G380-AB-01', family:'ABCD', bars:[{open:100,high:102,low:95,close:101},{open:101,high:110,low:100,close:108}], hypothesisA:'ABCD-H01', hypothesisB:'ABCD-H02', expected:'DISTINCT', canonical:false },
  { id:'G380-AB-02', family:'ABCD', bars:[{open:100,high:102,low:95,close:101},{open:101,high:110,low:100,close:108}], hypothesisA:'ABCD-H02', hypothesisB:'ABCD-H03', expected:'DISTINCT', canonical:false },
  { id:'G380-EN-01', family:'ENTRY', bars:[{open:100,high:104,low:96,close:103},{open:103,high:105,low:98,close:99}], hypothesisA:'EN-H01', hypothesisB:'EN-H02', expected:'DISTINCT', canonical:false },
  { id:'G380-EN-02', family:'ENTRY', bars:[{open:100,high:104,low:96,close:103},{open:103,high:105,low:98,close:99}], hypothesisA:'EN-H02', hypothesisB:'EN-H03', expected:'DISTINCT', canonical:false },
  { id:'G380-SL-01', family:'SL', bars:[{open:100,high:104,low:96,close:103}], hypothesisA:'SL-H01', hypothesisB:'SL-H02', expected:'DISTINCT', canonical:false },
  { id:'G380-TP-01', family:'TP', bars:[{open:100,high:102,low:95,close:101},{open:101,high:110,low:100,close:108},{open:108,high:112,low:106,close:109}], hypothesisA:'TP-H01', hypothesisB:'TP-H04', expected:'DISTINCT', canonical:false },
  { id:'G380-TP-02', family:'TP', bars:[{open:100,high:102,low:99,close:101},{open:101,high:103,low:100,close:102},{open:102,high:104,low:101,close:103}], hypothesisA:'TP-H01', hypothesisB:'TP-H04', expected:'EQUIVALENT', canonical:false },
] as const;

function evaluate(fixture: G380Fixture, hypothesis: string): number | string | boolean {
  switch (hypothesis) {
    case 'PG-H01': return pgH01(fixture.bars);
    case 'PG-H02': return pgH02(fixture.bars);
    case 'PG-H03': return pgH03(fixture.bars);
    case 'PG-H04': return pgH04(fixture.bars);
    case 'ABCD-H01': return abcdH01(fixture.bars);
    case 'ABCD-H02': return abcdH02(fixture.bars);
    case 'ABCD-H03': return abcdH03(fixture.bars);
    case 'EN-H01': return enH01(fixture.bars);
    case 'EN-H02': return enH02(fixture.bars);
    case 'EN-H03': return enH03(fixture.bars);
    case 'SL-H01': return slH01(fixture.bars);
    case 'SL-H02': return slH02(fixture.bars);
    case 'TP-H01': return tpH01(fixture.bars);
    case 'TP-H04': return tpH04(fixture.bars);
    default: throw new Error(`Unsupported research hypothesis: ${hypothesis}`);
  }
}

export function runG380(): readonly G380Observation[] {
  return G380_FIXTURES.map((fixture) => {
    const outputA = evaluate(fixture, fixture.hypothesisA);
    const outputB = evaluate(fixture, fixture.hypothesisB);
    return {
      id: fixture.id,
      family: fixture.family,
      hypothesisA: fixture.hypothesisA,
      hypothesisB: fixture.hypothesisB,
      outputA,
      outputB,
      classification: Object.is(outputA, outputB) ? 'EQUIVALENT' : 'DISTINCT',
      canonical: false,
    };
  });
}

export function g380ExpectedClassificationsMatch(): boolean {
  const results = runG380();
  return results.every((result) => {
    const fixture = G380_FIXTURES.find((f) => f.id === result.id);
    return fixture?.expected === result.classification;
  });
}

export function g380AllNonCanonical(): boolean {
  return G380_FIXTURES.every((f) => f.canonical === false) && runG380().every((r) => r.canonical === false);
}
