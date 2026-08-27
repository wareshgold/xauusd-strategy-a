export interface EMAContext {
  readonly ema: number;
  readonly price: number;
  readonly distance: number;
  readonly side: 'ABOVE' | 'BELOW' | 'AT';
  readonly aligned: boolean;
}

export interface LocationContext {
  readonly nearestRoundLevel: number | null;
  readonly distanceToRoundLevel: number | null;
  readonly nearRoundLevel: boolean;
  readonly locationLabel: 'ROUND_LEVEL' | 'STRUCTURE' | 'NEUTRAL';
}

export interface SessionContext {
  readonly session: string;
  readonly inTradingSession: boolean;
  readonly avoidWindow: boolean;
  readonly sessionRisk: 'NORMAL' | 'ELEVATED' | 'BLOCKED';
}

export interface StrategyAContext {
  readonly ema: EMAContext;
  readonly location: LocationContext;
  readonly session: SessionContext;
}

export interface ContextConfig {
  readonly emaPeriod: number;
  readonly roundStep: number;
  readonly roundDistance: number;
  readonly tradingSessions: readonly { name: string; startMinutes: number; endMinutes: number }[];
  readonly avoidWindows: readonly { startMinutes: number; endMinutes: number }[];
}

export function ema(values: readonly number[], period: number): number | null {
  if (period <= 0 || values.length === 0) return null;
  const k = 2 / (period + 1);
  let result = values[0]!;
  for (let i = 1; i < values.length; i += 1) result = values[i]! * k + result * (1 - k);
  return result;
}

export function buildEMAContext(prices: readonly number[], config: ContextConfig): EMAContext | null {
  const current = prices.at(-1);
  const value = ema(prices, config.emaPeriod);
  if (current === undefined || value === null) return null;
  const distance = Math.abs(current - value);
  return { ema: value, price: current, distance, side: current > value ? 'ABOVE' : current < value ? 'BELOW' : 'AT', aligned: current !== value };
}

function minutesOfDay(timestamp: string): number {
  const d = new Date(timestamp);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}

function inWindow(minute: number, start: number, end: number): boolean {
  return start <= end ? minute >= start && minute < end : minute >= start || minute < end;
}

export function buildSessionContext(timestamp: string, config: ContextConfig): SessionContext {
  const minute = minutesOfDay(timestamp);
  const active = config.tradingSessions.find((s) => inWindow(minute, s.startMinutes, s.endMinutes));
  const avoid = config.avoidWindows.some((w) => inWindow(minute, w.startMinutes, w.endMinutes));
  return { session: active?.name ?? 'OUTSIDE', inTradingSession: Boolean(active), avoidWindow: avoid, sessionRisk: avoid ? 'BLOCKED' : active ? 'NORMAL' : 'ELEVATED' };
}

export function buildLocationContext(price: number, config: ContextConfig): LocationContext {
  if (config.roundStep <= 0 || config.roundDistance < 0) return { nearestRoundLevel: null, distanceToRoundLevel: null, nearRoundLevel: false, locationLabel: 'NEUTRAL' };
  const nearest = Math.round(price / config.roundStep) * config.roundStep;
  const distance = Math.abs(price - nearest);
  const near = distance <= config.roundDistance;
  return { nearestRoundLevel: nearest, distanceToRoundLevel: distance, nearRoundLevel: near, locationLabel: near ? 'ROUND_LEVEL' : 'NEUTRAL' };
}
