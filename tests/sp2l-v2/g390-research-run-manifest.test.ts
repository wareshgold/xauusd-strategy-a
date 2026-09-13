import { describe, expect, it } from 'vitest';
import { createResearchRunManifest } from '../../src/domain/research/sp2l-v2/G390ResearchRunManifest.js';

describe('G390 research run manifest', () => {
  it('is deterministic and never authorizes canonical execution', () => {
    const input = {
      runId: 'fixture-run-001', datasetVersion: 'snapshot-2026-09-07', provider: 'twelvedata',
      symbol: 'XAU/USD', timeframe: '5min', timezone: 'UTC', splitPolicy: 'chronological_non_random' as const,
      strategyVersion: 'SP2L-SEMANTIC-ONLY'
    };
    const a = createResearchRunManifest(input);
    const b = createResearchRunManifest(input);
    expect(a).toEqual(b);
    expect(a.canonicalExecution).toBe(false);
  });
});
