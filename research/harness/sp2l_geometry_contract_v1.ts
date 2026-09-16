export type Provenance =
  | 'SOURCE_CONFIRMED'
  | 'CANDIDATE'
  | 'UNRESOLVED';

export type Resolution = {
  provenance: Provenance;
  note?: string;
};

/**
 * Research-only contract. This is not production signal generation.
 * Unresolved source geometry is represented explicitly rather than defaulted.
 */
export type Sp2lGeometryContract = {
  entry: Resolution;
  invalidation: Resolution;
  limitRefresh: Resolution;
  trigger: Resolution;
  twoX: Resolution;
  abcd: Resolution;
  pGap: Resolution;
};

export function assertCanonicalGeometryFrozen(
  geometry: Sp2lGeometryContract,
): void {
  const unresolved = Object.entries(geometry)
    .filter(([, value]) => value.provenance === 'UNRESOLVED')
    .map(([key]) => key);

  if (unresolved.length > 0) {
    throw new Error(
      `CANONICAL_GEOMETRY_NOT_FROZEN: ${unresolved.join(', ')}`,
    );
  }
}

export function createResearchCandidate(
  notes: Partial<Record<keyof Sp2lGeometryContract, string>> = {},
): Sp2lGeometryContract {
  const keys: (keyof Sp2lGeometryContract)[] = [
    'entry',
    'invalidation',
    'limitRefresh',
    'trigger',
    'twoX',
    'abcd',
    'pGap',
  ];

  return Object.fromEntries(
    keys.map((key) => [
      key,
      { provenance: 'UNRESOLVED', note: notes[key] },
    ]),
  ) as Sp2lGeometryContract;
}
