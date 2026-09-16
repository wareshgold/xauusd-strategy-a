import { Provenance, Sp2lGeometryContract } from './sp2l_geometry_contract_v1';

export type ValidationStatus =
  | 'BLOCKED_UNRESOLVED_GEOMETRY'
  | 'READY_FOR_EXECUTION'
  | 'EXECUTED';

export type CanonicalMetricSet = {
  tradeCount: number;
  wins: number;
  losses: number;
  winRate: number | null;
  expectancyR: number | null;
  maxDrawdownR: number | null;
  rValues: number[];
};

export type ValidationReport = {
  fixtureId: string;
  status: ValidationStatus;
  provenance: Record<keyof Sp2lGeometryContract, Provenance>;
  excludedFromMetrics: boolean;
  exclusionReason?: string;
  metrics: CanonicalMetricSet;
};

const EMPTY_METRICS: CanonicalMetricSet = {
  tradeCount: 0,
  wins: 0,
  losses: 0,
  winRate: null,
  expectancyR: null,
  maxDrawdownR: null,
  rValues: [],
};

function provenanceOf(geometry: Sp2lGeometryContract) {
  return Object.fromEntries(
    (Object.keys(geometry) as Array<keyof Sp2lGeometryContract>)
      .sort()
      .map((key) => [key, geometry[key].provenance]),
  ) as Record<keyof Sp2lGeometryContract, Provenance>;
}

export function createBlockedValidationReport(
  fixtureId: string,
  geometry: Sp2lGeometryContract,
): ValidationReport {
  return {
    fixtureId,
    status: 'BLOCKED_UNRESOLVED_GEOMETRY',
    provenance: provenanceOf(geometry),
    excludedFromMetrics: true,
    exclusionReason: 'Canonical geometry is not fully SOURCE_CONFIRMED.',
    metrics: { ...EMPTY_METRICS, rValues: [] },
  };
}

export function createReadyValidationReport(
  fixtureId: string,
  geometry: Sp2lGeometryContract,
): ValidationReport {
  return {
    fixtureId,
    status: 'READY_FOR_EXECUTION',
    provenance: provenanceOf(geometry),
    excludedFromMetrics: true,
    exclusionReason: 'No canonical execution has occurred yet.',
    metrics: { ...EMPTY_METRICS, rValues: [] },
  };
}

/** Research-only aggregation boundary. Blocked/candidate reports never enter metrics. */
export function aggregateCanonicalMetrics(
  reports: ValidationReport[],
): CanonicalMetricSet {
  const executed = reports.filter(
    (report) => report.status === 'EXECUTED' && !report.excludedFromMetrics,
  );

  const rValues = executed.flatMap((report) => report.metrics.rValues);
  const tradeCount = rValues.length;
  const wins = rValues.filter((r) => r > 0).length;
  const losses = rValues.filter((r) => r <= 0).length;
  const winRate = tradeCount === 0 ? null : wins / tradeCount;
  const expectancyR = tradeCount === 0
    ? null
    : rValues.reduce((sum, r) => sum + r, 0) / tradeCount;

  let peak = 0;
  let equity = 0;
  let maxDrawdownR = 0;
  for (const r of rValues) {
    equity += r;
    peak = Math.max(peak, equity);
    maxDrawdownR = Math.max(maxDrawdownR, peak - equity);
  }

  return {
    tradeCount,
    wins,
    losses,
    winRate,
    expectancyR,
    maxDrawdownR: tradeCount === 0 ? null : maxDrawdownR,
    rValues: [...rValues],
  };
}
