export interface ReplayRunManifest {
  readonly runId: string;
  readonly datasetId: string;
  readonly datasetVersion: string;
  readonly datasetFingerprint: string;
  readonly strategyId: string;
  readonly strategyVersion: string;
  readonly executionPolicy: string;
  readonly symbol: string;
  readonly timeframe: string;
  readonly startedAt: string;
  readonly completedAt: string;
  readonly candleCount: number;
  readonly signalCount: number;
  readonly blockedCount: number;
  readonly noSignalCount: number;
  readonly executionEventCount: number;
  readonly ambiguousEventCount: number;
}

/** Serialize a run manifest deterministically for audit/reproducibility. */
export function serializeRunManifest(manifest: ReplayRunManifest): string {
  return JSON.stringify(manifest, null, 2) + "\n";
}
