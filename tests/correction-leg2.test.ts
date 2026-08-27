import { describe, expect, it } from 'vitest';
import type { Candle } from '../src/domain/market/Candle.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';

const c = (i:number,o:number,h:number,l:number,cl:number): Candle => ({ timestamp:`2026-01-01T00:${String(i).padStart(2,'0')}:00Z`, timeframe:'1m', open:o, high:h, low:l, close:cl });

describe('Strategy A correction and Leg 2 projection', () => {
  it('detects the first bullish correction beyond the setup low', () => {
    const candles = [c(0,100,101,99,100),c(1,100,103,100,102),c(2,102,106,102,105),c(3,105,107,103,106),c(4,106,106.5,99.5,100)];
    const spike = { startIndex:0,endIndex:3,direction:'BULLISH' as const,startPrice:100,endPrice:107,size:7,structureScore:1,overlapScore:1,hasPGAPEvidence:false };
    const correction = detectFirstCorrection(candles, spike);
    expect(correction?.correctionExtremeIndex).toBe(4);
    expect(correction?.extremePrice).toBe(99.5);
  });

  it('projects TP1 from the correction extreme by Leg 1 size', () => {
    const candles = [c(0,100,101,99,100),c(1,100,103,100,102),c(2,102,106,102,105),c(3,105,107,103,106)];
    const correction = { spikeStartIndex:0, spikeEndIndex:3, correctionStartIndex:4, correctionExtremeIndex:4, direction:'BULLISH' as const, extremePrice:99.5 };
    const projection = projectLeg2(candles, correction);
    expect(projection?.direction).toBe('BUY');
    expect(projection?.leg1Size).toBe(6);
    expect(projection?.tp1).toBe(105.5);
  });
});
