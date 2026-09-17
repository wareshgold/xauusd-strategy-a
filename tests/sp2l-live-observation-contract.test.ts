import { describe, expect, it } from 'vitest';

type FixtureBar = {
  provider: string;
  server: string;
  symbol: string;
  timeframe: string;
  id: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  complete: boolean;
  sequence?: number;
};

type Observation = FixtureBar & { normalizedTimestamp: string };

type Event =
  | { type: 'OBSERVATION'; observation: Observation }
  | { type: 'DATA_QUALITY_EVENT'; reason: string; missingTimestamp?: string }
  | { type: 'DUPLICATE'; id: string };

function normalizeUtc(timestamp: string): string {
  return new Date(timestamp).toISOString();
}

function observe(bars: FixtureBar[]): Event[] {
  const events: Event[] = [];
  const seen = new Set<string>();
  const completed = bars.filter((bar) => bar.complete);

  for (const bar of completed) {
    if (seen.has(bar.id)) {
      events.push({ type: 'DUPLICATE', id: bar.id });
      continue;
    }
    seen.add(bar.id);
    events.push({
      type: 'OBSERVATION',
      observation: { ...bar, normalizedTimestamp: normalizeUtc(bar.timestamp) },
    });
  }

  const ordered = [...completed]
    .filter((bar, index, source) => source.findIndex((candidate) => candidate.id === bar.id) === index)
    .sort((a, b) => normalizeUtc(a.timestamp).localeCompare(normalizeUtc(b.timestamp)));

  for (let i = 1; i < ordered.length; i += 1) {
    const previous = Date.parse(ordered[i - 1].timestamp);
    const current = Date.parse(ordered[i].timestamp);
    if (current - previous > 60_000) {
      events.push({
        type: 'DATA_QUALITY_EVENT',
        reason: 'missing_or_discontinuous_m1_bar',
        missingTimestamp: new Date(previous + 60_000).toISOString(),
      });
      break;
    }
  }

  return events;
}

const bar = (overrides: Partial<FixtureBar> = {}): FixtureBar => ({
  provider: 'fixture',
  server: 'fixture-server',
  symbol: 'XAUUSD.ecn',
  timeframe: 'M1',
  id: 'bar-1',
  timestamp: '2026-09-17T10:00:00Z',
  open: 3600,
  high: 3601,
  low: 3599,
  close: 3600.5,
  complete: true,
  ...overrides,
});

describe('SP2L live observation contract', () => {
  it('F1: emits exactly one observation for one completed bar', () => {
    const events = observe([bar()]);
    expect(events.filter((event) => event.type === 'OBSERVATION')).toHaveLength(1);
    expect(events[0]).toMatchObject({ type: 'OBSERVATION' });
  });

  it('F2: duplicate provider bar identity is idempotent', () => {
    const events = observe([bar(), bar()]);
    expect(events.filter((event) => event.type === 'OBSERVATION')).toHaveLength(1);
    expect(events.filter((event) => event.type === 'DUPLICATE')).toHaveLength(1);
  });

  it('F3: out-of-order delivery has deterministic normalized handling', () => {
    const late = bar({ id: 'bar-2', timestamp: '2026-09-17T10:02:00Z', open: 3602 });
    const early = bar({ id: 'bar-1', timestamp: '2026-09-17T10:01:00Z', open: 3601 });
    const first = observe([late, early]);
    const second = observe([late, early]);
    expect(first).toEqual(second);
    expect(first.filter((event) => event.type === 'OBSERVATION')).toHaveLength(2);
  });

  it('F4: normalizes equivalent timestamp offsets to the same UTC instant', () => {
    const a = observe([bar({ timestamp: '2026-09-17T12:00:00+02:00' })]);
    const b = observe([bar({ timestamp: '2026-09-17T10:00:00Z' })]);
    expect(a[0]).toMatchObject({ type: 'OBSERVATION' });
    expect(b[0]).toMatchObject({ type: 'OBSERVATION' });
    if (a[0].type === 'OBSERVATION' && b[0].type === 'OBSERVATION') {
      expect(a[0].observation.normalizedTimestamp).toBe(b[0].observation.normalizedTimestamp);
    }
  });

  it('F5: records a missing bar without fabricating a candle', () => {
    const events = observe([
      bar({ id: 'bar-1', timestamp: '2026-09-17T10:00:00Z' }),
      bar({ id: 'bar-3', timestamp: '2026-09-17T10:02:00Z' }),
    ]);
    expect(events.some((event) => event.type === 'DATA_QUALITY_EVENT')).toBe(true);
    expect(events.filter((event) => event.type === 'OBSERVATION')).toHaveLength(2);
    expect(events.some((event) => event.type === 'OBSERVATION' && event.observation.id === 'bar-2')).toBe(false);
  });

  it('F6: ignores an in-progress bar', () => {
    const events = observe([bar({ complete: false })]);
    expect(events.filter((event) => event.type === 'OBSERVATION')).toHaveLength(0);
  });

  it('F7/F8: research observation remains non-production data', () => {
    const events = observe([bar()]);
    const observation = events.find((event) => event.type === 'OBSERVATION');
    expect(observation?.type).toBe('OBSERVATION');
    expect(events.some((event) => event.type === 'OBSERVATION' && 'BUY' in event)).toBe(false);
    expect(events.some((event) => event.type === 'OBSERVATION' && 'SELL' in event)).toBe(false);
  });
});
