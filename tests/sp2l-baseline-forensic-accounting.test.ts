import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { describe, expect, it } from 'vitest';

type Trade = {
  entryIndex: number;
  entryTime: string;
  direction: 'BUY' | 'SELL';
  entry: number;
  stopLoss: number;
  tp1: number;
  riskDistance: number;
  result: string;
  rMultiple: number | null;
};

type BaselineReport = {
  timeframe: string;
  metrics?: { trades?: number };
  trades?: Trade[];
};

const REPORTS = ['1min', '5min'] as const;
const EPSILON = 1e-9;
const EXTREME_R_THRESHOLD = 20;
const TINY_RISK_THRESHOLD = 0.1;

async function loadReport(timeframe: string): Promise<BaselineReport> {
  const path = resolve(process.cwd(), 'data/reports/strategy-a-baseline', `${timeframe}.json`);
  return JSON.parse(await readFile(path, 'utf8')) as BaselineReport;
}

describe('SP2L baseline forensic accounting', () => {
  for (const timeframe of REPORTS) {
    it(`${timeframe}: preserves observed accounting without inventing R semantics`, async () => {
      const report = await loadReport(timeframe);
      const trades = report.trades ?? [];
      const closed = trades.filter((trade) => trade.rMultiple !== null);
      const unresolved = trades.filter((trade) => trade.rMultiple === null);
      const ambiguous = trades.filter((trade) => trade.result === 'AMBIGUOUS');
      const open = trades.filter((trade) => trade.result === 'OPEN');
      const extreme = closed.filter((trade) => Math.abs(trade.rMultiple ?? 0) >= EXTREME_R_THRESHOLD);
      const tinyRisk = trades.filter((trade) => trade.riskDistance < TINY_RISK_THRESHOLD);

      expect(trades.length).toBeGreaterThan(0);
      expect(report.metrics?.trades).toBe(closed.length);
      expect(ambiguous.length + open.length).toBe(unresolved.length);

      for (const trade of trades) {
        expect(trade.riskDistance).toBeGreaterThan(0);
        const expectedRisk = Math.abs(trade.entry - trade.stopLoss);
        expect(Math.abs(expectedRisk - trade.riskDistance)).toBeLessThanOrEqual(EPSILON);
      }

      for (const trade of closed) {
        expect(Number.isFinite(trade.rMultiple)).toBe(true);
      }

      console.log(JSON.stringify({
        timeframe,
        candidates: trades.length,
        closed: closed.length,
        ambiguous: ambiguous.length,
        open: open.length,
        extremeRAbsGe20: extreme.length,
        tinyRiskLt0_1: tinyRisk.length,
        rSemantics: 'UNRESOLVED',
      }));
    });
  }
});
