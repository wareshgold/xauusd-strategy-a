import { describe, expect, it } from 'vitest';
import { runDataset } from '../../src/domain/research/sp2l-v2/G388DatasetRunner.js';
import type { DevConfig, RawCandle } from '../../src/domain/research/sp2l-v2/G386DevHarness.js';

const config: DevConfig = {
  devStart:'2026-03-17 15:15:00', devEnd:'2026-06-30 23:59:59',
  valStart:'2026-07-01 00:00:00', valEnd:'2026-08-31 23:59:59',
  holdoutStart:'2026-09-01 00:00:00', holdoutEnd:'2026-09-07 07:05:00',
  costs:{spreadPrice:0,slippagePrice:0,commissionPrice:0}
};
const c=(t:string):RawCandle=>({symbol:'XAU/USD',timestamp:t,timezone:'UTC',timeframe:'5min',open:1,high:2,low:.5,close:1.5,provider:'twelvedata',datasetVersion:'snapshot-2026-09-07'});

describe('G388 reproducibility',()=>{
 it('is byte-for-byte stable at the structured-result level',()=>{
   const data=[c('2026-03-17 15:15:00'),c('2026-07-01 00:00:00'),c('2026-09-01 00:00:00')];
   expect(JSON.stringify(runDataset(data,config))).toBe(JSON.stringify(runDataset(data,config)));
 });
 it('keeps holdout isolated as a count-only partition',()=>{
   const data=[c('2026-06-30 23:59:59'),c('2026-07-01 00:00:00'),c('2026-09-01 00:00:00')];
   const r=runDataset(data,config);
   expect(r.counts).toEqual({DEV:1,VAL:1,HOLDOUT:1});
   expect(r.canonicalTradesGenerated).toBe(0);
 });
});
