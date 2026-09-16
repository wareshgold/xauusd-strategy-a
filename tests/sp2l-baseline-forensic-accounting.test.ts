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

const REPORTS = [
  '1min',
  '5min',
] as const;

const EPSILON = 1e-9;

async function loadReport(timeframe: string): Promise<BaselineReport> {
  const path = resolve(
    process.cwd(),
    'data/reports/strategy-a-baseline',
    `${timeframe}.json`,
  );
  return JSON.parse(await readFile(path, 'utf8')) as BaselineReport;
}

describe('SP2L baseline forensic accounting', () => {
  for (const timeframe of REPORTS) {
    it(`${timeframe}: candidate, outcome, risk, and R accounting is internally consistent`, async () => {
      const report = await loadReport(timeframe);
      const trades = report.trades ?? [];
      const closed = trades.filter((trade) => trade.rMultiple !== null);
      const unresolved = trades.filter((trade) => trade.rMultiple === null);
      const ambiguous = trades.filter((trade) => trade.result === 'AMBIGUOUS');
      const open = trades.filter((trade) => trade.result === 'OPEN');
      const extreme = closed.filter((trade) => Math.abs(trade.rMultiple ?? 0) >= 20);
      const tinyRisk = trades.filter((trade) => trade.riskDistance < 0.1);

      expect(trades.length).toBeGreaterThan(0);
      expect(report.metrics?.trades).toBe(closed.length);
      expect(ambiguous.length + open.length).toBe(unresolved.length);

      for (const trade of trades) {
        const expectedRisk = Math.abs(trade.entry - trade.stopLoss);
        expect(Math.abs(expectedRisk - trade.riskDistance)).toBeLessThanOrEqual(EPSILON);
      }

      for (const trade of closed) {
        const risk = Math.abs(trade.entry - trade.stopLoss);
        const expectedR = trade.direction === 'BUY'
          ? (trade.tp1 - trade.entry) / risk
          : (trade.entry - trade.tp1) / risk;
        expect(Math.abs(expectedR - (trade.rMultiple ?? 0))).toBeLessThanOrEqual(EPSILON);
      }

      console.log(JSON.stringify({
        timeframe,
        candidates: trades.length,
        closed: closed.length,
        ambiguous: ambiguous.length,
        open: open.length,
        extremeRAbsGe20: extreme.length,
        tinyRiskLt0_1: tinyRisk.length,
      }));
    });
  }
});
