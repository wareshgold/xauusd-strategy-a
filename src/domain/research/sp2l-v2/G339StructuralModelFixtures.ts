export type FixtureEvent = {
  id: string;
  index: number;
  high: number;
  low: number;
  role: 'RANGE' | 'DEEP_ORIGIN' | 'SPIKE' | 'PARENT_B' | 'CORRECTION' | 'LOWER_HIGH' | 'PENDING_LIMIT' | 'FILL' | 'LEG2_END';
};

export type StructuralCandidate =
  | 'SOURCE_DEEP_ORIGIN'
  | 'FIRST_BREAKOUT_CANDLE'
  | 'NEAREST_SWING'
  | 'FILL_AS_C'
  | 'SOURCE_CORRECTION_REFERENCE';

export const G339_SOURCE_COMPATIBLE_FIXTURE: FixtureEvent[] = [
  { id: 'r0', index: 0, high: 100, low: 98, role: 'RANGE' },
  { id: 'r1', index: 1, high: 101, low: 99, role: 'RANGE' },
  { id: 'origin', index: 2, high: 101, low: 96, role: 'DEEP_ORIGIN' },
  { id: 'spike', index: 3, high: 112, low: 97, role: 'SPIKE' },
  { id: 'parent-b', index: 4, high: 115, low: 108, role: 'PARENT_B' },
  { id: 'corr-1', index: 5, high: 113, low: 106, role: 'LOWER_HIGH' },
  { id: 'corr-2', index: 6, high: 111, low: 104, role: 'LOWER_HIGH' },
  { id: 'correction', index: 7, high: 109, low: 102, role: 'CORRECTION' },
  { id: 'pending', index: 8, high: 108, low: 105, role: 'PENDING_LIMIT' },
  { id: 'fill', index: 9, high: 107, low: 103, role: 'FILL' },
  { id: 'leg2-end', index: 10, high: 114, low: 106, role: 'LEG2_END' },
];

export const G339_NESTED_FIXTURE: FixtureEvent[] = [
  { id: 'n-range', index: 0, high: 200, low: 198, role: 'RANGE' },
  { id: 'n-origin', index: 1, high: 201, low: 190, role: 'DEEP_ORIGIN' },
  { id: 'n-spike', index: 2, high: 210, low: 191, role: 'SPIKE' },
  { id: 'n-parent-b', index: 3, high: 220, low: 205, role: 'PARENT_B' },
  { id: 'n-nested-b', index: 4, high: 215, low: 208, role: 'PARENT_B' },
  { id: 'n-correction', index: 5, high: 212, low: 202, role: 'CORRECTION' },
  { id: 'n-fill', index: 6, high: 209, low: 204, role: 'FILL' },
  { id: 'n-parent-end', index: 7, high: 219, low: 208, role: 'LEG2_END' },
];

export function candidateIsCanonical(candidate: StructuralCandidate): false {
  void candidate;
  return false;
}

export function indexOfRole(events: FixtureEvent[], role: FixtureEvent['role']): number[] {
  return events.filter((event) => event.role === role).map((event) => event.index);
}

export function legMagnitude(events: FixtureEvent[], originId: string, endId: string): number {
  const origin = events.find((event) => event.id === originId);
  const end = events.find((event) => event.id === endId);
  if (!origin || !end) throw new Error('FIXTURE_ANCHOR_MISSING');
  return Math.abs(end.high - origin.low);
}

export function candidateSeparation(events: FixtureEvent[]): {
  deepOriginIndex: number;
  pendingIndex: number;
  fillIndex: number;
  correctionIndex: number;
} {
  const byRole = (role: FixtureEvent['role']) => {
    const event = events.find((item) => item.role === role);
    if (!event) throw new Error(`FIXTURE_ROLE_MISSING:${role}`);
    return event.index;
  };
  return {
    deepOriginIndex: byRole('DEEP_ORIGIN'),
    pendingIndex: byRole('PENDING_LIMIT'),
    fillIndex: byRole('FILL'),
    correctionIndex: byRole('CORRECTION'),
  };
}
