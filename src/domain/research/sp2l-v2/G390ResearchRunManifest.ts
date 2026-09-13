export interface ResearchRunManifest {
  runId: string;
  datasetVersion: string;
  provider: string;
  symbol: string;
  timeframe: string;
  timezone: string;
  splitPolicy: 'chronological_non_random';
  strategyVersion: string;
  canonicalExecution: false;
}

export function createResearchRunManifest(input: Omit<ResearchRunManifest, 'canonicalExecution'>): ResearchRunManifest {
  return { ...input, canonicalExecution: false };
}
