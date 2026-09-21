import { describe, expect, it } from 'vitest';

type Candle = {
  open: number; high: number; low: number; close: number;
};

function pressureScore(candles: Candle[]): number {
  return candles.reduce((s, c) => s + (c.close - c.open), 0);
}

function range(c: Candle): number { return c.high - c.low; }
function body(c: Candle): number { return Math.abs(c.close - c.open); }

function candidate(
  pressure: Candle[],
  pause: Candle[],
  trend: Candle[],
  direction: 'BULLISH' | 'BEARISH',
  compressionFactor = 0.75,
  trendBodyFactor = 1.5,
): boolean {
  if (pressure.length < 10 || pressure.length > 30 || pause.length < 2 || trend.length !== 1) return false;
  const pAvgRange = pressure.reduce((s, c) => s + range(c), 0) / pressure.length;
  const pauseAvgRange = pause.reduce((s, c) => s + range(c), 0) / pause.length;
  const avgPressureBody = pressure.reduce((s, c) => s + body(c), 0) / pressure.length;
  const t = trend[0]!;
  const directionalPressure = direction === 'BULLISH' ? pressureScore(pressure) > 0 : pressureScore(pressure) < 0;
  const directionalTrend = direction === 'BULLISH' ? t.close > t.open : t.close < t.open;
  return directionalPressure &&
    pauseAvgRange <= pAvgRange * compressionFactor &&
    directionalTrend &&
    body(t) >= avgPressureBody * trendBodyFactor;
}

function slFromSpike(spike: Candle, direction: 'BULLISH' | 'BEARISH', spread: number): number {
  return direction === 'BULLISH' ? spike.low - spread : spike.high + spread;
}

const bull = (o:number,h:number,l:number,c:number): Candle => ({open:o,high:h,low:l,close:c});
const bear = (o:number,h:number,l:number,c:number): Candle => ({open:o,high:h,low:l,close:c});

describe('SP2L research P-Gap candidate fixtures', () => {
  it('accepts bullish pressure -> compression -> trend-bar', () => {
    const p = Array.from({length: 10}, (_, i) => bull(100+i, 102+i, 99+i, 101+i));
    const pause = [bull(110,111,109.5,110.2), bull(110.2,111.1,109.7,110.4)];
    const t = [bull(110.4,115,110,114)];
    expect(candidate(p,pause,t,'BULLISH')).toBe(true);
  });

  it('accepts bearish mirror', () => {
    const p = Array.from({length: 10}, (_, i) => bear(101-i, 102-i, 99-i, 100-i));
    const pause = [bear(90,90.5,89,89.8), bear(89.8,90.3,89.1,89.6)];
    const t = [bear(89.6,90,84.5,85)];
    expect(candidate(p,pause,t,'BEARISH')).toBe(true);
  });

  it('rejects fewer than 10 pressure candles', () => {
    const p = Array.from({length: 9}, (_, i) => bull(100+i,102+i,99+i,101+i));
    expect(candidate(p,[bull(109,110,108.5,109.2),bull(109.2,110,108.7,109.4)],[bull(109.4,114,109,113)],'BULLISH')).toBe(false);
  });

  it('rejects missing compression', () => {
    const p = Array.from({length: 10}, (_, i) => bull(100+i,102+i,99+i,101+i));
    const pause = [bull(110,114,106,113),bull(113,117,109,116)];
    expect(candidate(p,pause,[bull(116,121,115,120)],'BULLISH')).toBe(false);
  });

  it('uses spike wick/shadow plus spread for SL', () => {
    const spike = bull(100, 110, 95, 108);
    expect(slFromSpike(spike,'BULLISH',0.25)).toBe(94.75);
    expect(slFromSpike(spike,'BEARISH',0.25)).toBe(110.25);
  });

  it('keeps zero spread deterministic', () => {
    const spike = bear(108,110,100,101);
    expect(slFromSpike(spike,'BEARISH',0)).toBe(110);
  });
});
