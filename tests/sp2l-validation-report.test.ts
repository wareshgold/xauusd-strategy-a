import { describe, expect, it } from 'vitest';
import { createResearchCandidate, Sp2lGeometryContract } from '../research/harness/sp2l_geometry_contract_v1';
import {
  aggregateCanonicalMetrics,
  createBlockedValidationReport,
  createReadyValidationReport,
} from '../research/harness/sp2l_validation_report_v1';

describe('SP2L deterministic validation report', () => {
  it('keeps blocked geometry visible but out of canonical metrics', () => {
    const geometry = createResearchCandidate({ pGap: 'source formula unresolved' });
    const report = createBlockedValidationReport('F14', geometry);

    expect(report.status).toBe('BLOCKED_UNRESOLVED_GEOMETRY');
    expect(report.excludedFromMetrics).toBe(true);
    expect(report.provenance.pGap).toBe('UNRESOLVED');

    const metrics = aggregateCanonicalMetrics([report]);
    expect(metrics.tradeCount).toBe(0);
    expect(metrics.winRate).toBeNull();
    expect(metrics.expectancyR).toBeNull();
    expect(metrics.maxDrawdownR).toBeNull();
  });

  it('keeps a ready-but-unexecuted report out of performance denominators', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const report = createReadyValidationReport('FROZEN-READY', geometry);
    const metrics = aggregateCanonicalMetrics([report]);

    expect(report.status).toBe('READY_FOR_EXECUTION');
    expect(metrics.tradeCount).toBe(0);
    expect(metrics.winRate).toBeNull();
  });

  it('aggregates only explicitly executed, included canonical observations', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const executed = createReadyValidationReport('EXECUTED-1', geometry);
    executed.status = 'EXECUTED';
    executed.excludedFromMetrics = false;
    executed.metrics.rValues = [2, -1, 1];

    const blocked = createBlockedValidationReport('BLOCKED-1', createResearchCandidate());
    const metrics = aggregateCanonicalMetrics([blocked, executed]);

    expect(metrics.tradeCount).toBe(3);
    expect(metrics.wins).toBe(2);
    expect(metrics.losses).toBe(1);
    expect(metrics.winRate).toBeCloseTo(2 / 3);
    expect(metrics.expectancyR).toBeCloseTo(2 / 3);
    expect(metrics.maxDrawdownR).toBe(1);
  });

  it('fails closed when an executed report still carries candidate or unresolved provenance', () => {
    const geometry = createResearchCandidate() as Sp2lGeometryContract;
    for (const field of Object.keys(geometry) as (keyof Sp2lGeometryContract)[]) {
      geometry[field] = { provenance: 'SOURCE_CONFIRMED' };
    }

    const nonCanonical = createReadyValidationReport('EXECUTED-NONCANONICAL', geometry);
    nonCanonical.status = 'EXECUTED';
    nonCanonical.excludedFromMetrics = false;
    nonCanonical.provenance.pGap = 'CANDIDATE';
    nonCanonical.metrics.rValues = [125];

    const metrics = aggregateCanonicalMetrics([nonCanonical]);

    expect(metrics.tradeCount).toBe(0);
    expect(metrics.winRate).toBeNull();
    expect(metrics.expectancyR).toBeNull();
    expect(metrics.maxDrawdownR).toBeNull();
    expect(metrics.rValues).toEqual([]);
  });
});