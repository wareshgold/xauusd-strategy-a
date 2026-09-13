import { describe, expect, it } from 'vitest';
import { adaptSnapshot, runSnapshot, type SnapshotRecord } from '../../src/domain/research/sp2l-v2/G389SnapshotAdapter.js';

const config = {
  devStart:'2026-03-17 15:15:00', devEnd:'2026-06-30 23:59:59',
  valStart:'2026-07-01 00:00:00', valEnd:'2026-08-31 23:59:59',
  holdoutStart:'2026-09-01 00:00:00', holdoutEnd:'2026-09-07 07:05:00',
  costs:{spreadPrice:0,slippagePrice:0,commissionPrice:0}
};
const snapshot: SnapshotRecord = {
  symbol:'XAU/USD', timeframe:'5min', source:'twelvedata', timezone:'UTC', candles:[
    {timestamp:'2026-03-17 15:15:00',open:1,high:2,low:.5,close:1.5},
    {timestamp:'2026-07-01 00:00:00',open:1,high:2,low:.5,close:1.5},
    {timestamp:'2026-09-01 00:00:00',open:1,high:2,low:.5,close:1.5}
  ]
};

describe('G389 snapshot adapter',()=>{
 it('preserves source metadata and injects explicit version',()=>{
   const rows=adaptSnapshot(snapshot,'snapshot-2026-09-07');
   expect(rows[0]?.provider).toBe('twelvedata');
   expect(rows[0]?.datasetVersion).toBe('snapshot-2026-09-07');
   expect(rows).toHaveLength(3);
 });
 it('runs through the same deterministic runner without creating trades',()=>{
   const result=runSnapshot(snapshot,'snapshot-2026-09-07',config);
   expect(result.counts).toEqual({DEV:1,VAL:1,HOLDOUT:1});
   expect(result.leakageFree).toBe(true);
   expect(result.canonicalTradesGenerated).toBe(0);
 });
});
