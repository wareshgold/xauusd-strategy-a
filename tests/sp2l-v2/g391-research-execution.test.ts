import { describe, expect, it } from 'vitest';
import { executeResearch } from '../../src/domain/research/sp2l-v2/G391ResearchExecution.js';
import { noCanonicalStrategyAdapter } from '../../src/domain/research/sp2l-v2/G390StrategyAdapter.js';
import type { DevConfig, RawCandle } from '../../src/domain/research/sp2l-v2/G386DevHarness.js';

const config: DevConfig = {devStart:'2026-03-17 15:15:00',devEnd:'2026-06-30 23:59:59',valStart:'2026-07-01 00:00:00',valEnd:'2026-08-31 23:59:59',holdoutStart:'2026-09-01 00:00:00',holdoutEnd:'2026-09-07 07:05:00',costs:{spreadPrice:0,slippagePrice:0,commissionPrice:0}};
const c=(timestamp:string):RawCandle=>({symbol:'XAU/USD',timestamp,timezone:'UTC',timeframe:'5min',open:1,high:2,low:.5,close:1.5,provider:'twelvedata',datasetVersion:'snapshot-2026-09-07'});

describe('G391 research execution',()=>{
 it('runs the complete plumbing without canonical candidates',()=>{
   const result=executeResearch([c('2026-03-17 15:15:00'),c('2026-07-01 00:00:00'),c('2026-09-01 00:00:00')],config,noCanonicalStrategyAdapter());
   expect(result.evaluatedCandles).toBe(3);
   expect(result.candidateCount).toBe(0);
   expect(result.canonicalCandidates).toBe(0);
   expect(result.leakageFree).toBe(true);
 });
});
