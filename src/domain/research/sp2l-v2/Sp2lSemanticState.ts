export type Sp2lDirection = 'BULLISH' | 'BEARISH';

export type Sp2lPhase =
  | 'CONTEXT'
  | 'IMPULSE'
  | 'FOLLOW_THROUGH'
  | 'SPIKE'
  | 'CORRECTION'
  | 'PENDING'
  | 'FILLED'
  | 'INVALIDATED'
  | 'STOPPED'
  | 'TP1_REACHED'
  | 'COMPLETED'
  | 'REJECTED';

export type GeometryStatus = 'SOURCE_CONFIRMED' | 'CANDIDATE' | 'TBD';
export type IntrabarTouchPolicy = 'SL_FIRST' | 'TP_FIRST' | 'AMBIGUOUS';

export interface StructuralReference {
  status: GeometryStatus;
  index: number | null;
  price: number | null;
  rationale: string | null;
}

export interface Sp2lGeometryState {
  firstStructuralReference: StructuralReference;
  pendingEntryPrice: StructuralReference;
  structuralStop: StructuralReference;
  leg1Endpoint: StructuralReference;
  leg2ProjectionOrigin: StructuralReference;
  leg2EqualityTolerance: number | null;
}

export interface Sp2lPositionState {
  entryPrice: number | null;
  stopLoss: number | null;
  tp1: number | null;
  position2xEnabled: false;
}

export interface Sp2lSemanticState {
  phase: Sp2lPhase;
  direction: Sp2lDirection | null;
  contextId: string | null;
  impulseId: string | null;
  followThroughIndex: number | null;
  spikeId: string | null;
  correctionStartedAt: number | null;
  pendingCreatedAt: number | null;
  fillIndex: number | null;
  invalidationIndex: number | null;
  tp1Index: number | null;
  geometry: Sp2lGeometryState;
  position: Sp2lPositionState;
  rejectionReason: string | null;
}

export type Sp2lEvent =
  | { type: 'CONTEXT_IDENTIFIED'; contextId: string }
  | { type: 'STRONG_MOVE_STARTED'; impulseId: string; direction: Sp2lDirection }
  | { type: 'FOLLOW_THROUGH_CONFIRMED'; index: number }
  | { type: 'FOLLOW_THROUGH_REJECTED'; reason?: string }
  | { type: 'SPIKE_CONFIRMED'; spikeId: string }
  | {
      type: 'STRUCTURAL_REFERENCE_IDENTIFIED';
      index: number;
      price: number;
      status?: GeometryStatus;
      rationale?: string;
    }
  | { type: 'CORRECTION_BEGAN'; index: number }
  | {
      type: 'PENDING_LIMIT_CREATED';
      index: number;
      entryPrice: number | null;
      stopLoss: number | null;
      stopStatus?: GeometryStatus;
      entryStatus?: GeometryStatus;
      rationale?: string;
    }
  | {
      type: 'LEG2_PROJECTION_ORIGIN_IDENTIFIED';
      index: number | null;
      price: number | null;
      status?: GeometryStatus;
      rationale?: string;
    }
  | { type: 'LIMIT_TOUCHED'; index: number; price: number }
  | { type: 'STRUCTURAL_INVALIDATION'; index: number }
  | { type: 'STOP_HIT'; index: number; price: number }
  | { type: 'TP1_REACHED'; index: number }
  | { type: 'COMPLETE'; index: number }
  | { type: 'REJECT'; reason: string };

export function createInitialSp2lState(): Sp2lSemanticState {
  const tbd = (): StructuralReference => ({
    status: 'TBD', index: null, price: null, rationale: null,
  });

  return {
    phase: 'CONTEXT',
    direction: null,
    contextId: null,
    impulseId: null,
    followThroughIndex: null,
    spikeId: null,
    correctionStartedAt: null,
    pendingCreatedAt: null,
    fillIndex: null,
    invalidationIndex: null,
    tp1Index: null,
    geometry: {
      firstStructuralReference: tbd(),
      pendingEntryPrice: tbd(),
      structuralStop: tbd(),
      leg1Endpoint: tbd(),
      leg2ProjectionOrigin: tbd(),
      leg2EqualityTolerance: null,
    },
    position: {
      entryPrice: null,
      stopLoss: null,
      tp1: null,
      position2xEnabled: false,
    },
    rejectionReason: null,
  };
}

function assertPhase(state: Sp2lSemanticState, ...allowed: Sp2lPhase[]): void {
  if (!allowed.includes(state.phase)) {
    throw new Error(`Invalid SP2L transition from phase ${state.phase}; expected ${allowed.join(' or ')}`);
  }
}

function reject(state: Sp2lSemanticState, reason: string): Sp2lSemanticState {
  return { ...state, phase: 'REJECTED', rejectionReason: reason };
}

export function applySp2lEvent(state: Sp2lSemanticState, event: Sp2lEvent): Sp2lSemanticState {
  switch (event.type) {
    case 'CONTEXT_IDENTIFIED':
      assertPhase(state, 'CONTEXT');
      return { ...state, contextId: event.contextId };

    case 'STRONG_MOVE_STARTED':
      assertPhase(state, 'CONTEXT');
      if (!state.contextId) return reject(state, 'STRONG_MOVE_REQUIRES_CONTEXT');
      return { ...state, phase: 'IMPULSE', impulseId: event.impulseId, direction: event.direction };

    case 'FOLLOW_THROUGH_CONFIRMED':
      assertPhase(state, 'IMPULSE');
      return { ...state, phase: 'FOLLOW_THROUGH', followThroughIndex: event.index };

    case 'FOLLOW_THROUGH_REJECTED':
      assertPhase(state, 'IMPULSE', 'FOLLOW_THROUGH');
      return reject(state, event.reason ?? 'FOLLOW_THROUGH_REJECTED');

    case 'SPIKE_CONFIRMED':
      assertPhase(state, 'FOLLOW_THROUGH');
      if (state.followThroughIndex === null) return reject(state, 'SPIKE_REQUIRES_FOLLOW_THROUGH');
      return { ...state, phase: 'SPIKE', spikeId: event.spikeId };

    case 'STRUCTURAL_REFERENCE_IDENTIFIED':
      assertPhase(state, 'SPIKE', 'CORRECTION');
      return {
        ...state,
        geometry: {
          ...state.geometry,
          firstStructuralReference: {
            status: event.status ?? 'CANDIDATE',
            index: event.index,
            price: event.price,
            rationale: event.rationale ?? null,
          },
        },
      };

    case 'CORRECTION_BEGAN':
      assertPhase(state, 'SPIKE');
      if (state.geometry.firstStructuralReference.index === null) {
        return reject(state, 'CORRECTION_REQUIRES_STRUCTURAL_REFERENCE');
      }
      if (event.index <= state.geometry.firstStructuralReference.index) {
        return reject(state, 'CORRECTION_MUST_BEGIN_AFTER_STRUCTURAL_REFERENCE');
      }
      return { ...state, phase: 'CORRECTION', correctionStartedAt: event.index };

    case 'PENDING_LIMIT_CREATED':
      assertPhase(state, 'CORRECTION');
      if (state.correctionStartedAt === null) return reject(state, 'PENDING_LIMIT_REQUIRES_CORRECTION');
      if (event.index < state.correctionStartedAt) return reject(state, 'PENDING_LIMIT_CANNOT_PRECEDE_CORRECTION');
      if (event.entryPrice === null) return reject(state, 'PENDING_LIMIT_REQUIRES_EXPLICIT_ENTRY_PRICE');
      if (event.stopLoss === null) return reject(state, 'PENDING_LIMIT_REQUIRES_EXPLICIT_STRUCTURAL_STOP');
      return {
        ...state,
        phase: 'PENDING',
        pendingCreatedAt: event.index,
        geometry: {
          ...state.geometry,
          pendingEntryPrice: {
            status: event.entryStatus ?? 'CANDIDATE',
            index: event.index,
            price: event.entryPrice,
            rationale: event.rationale ?? null,
          },
          structuralStop: {
            status: event.stopStatus ?? 'CANDIDATE',
            index: event.index,
            price: event.stopLoss,
            rationale: event.rationale ?? null,
          },
        },
      };

    case 'LEG2_PROJECTION_ORIGIN_IDENTIFIED':
      assertPhase(state, 'CORRECTION', 'PENDING', 'FILLED');
      if (event.index !== null && state.correctionStartedAt !== null && event.index < state.correctionStartedAt) {
        return reject(state, 'LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION');
      }
      return {
        ...state,
        geometry: {
          ...state.geometry,
          leg2ProjectionOrigin: {
            status: event.status ?? 'CANDIDATE',
            index: event.index,
            price: event.price,
            rationale: event.rationale ?? null,
          },
        },
      };

    case 'LIMIT_TOUCHED':
      assertPhase(state, 'PENDING');
      if (state.geometry.pendingEntryPrice.price === null) return reject(state, 'LIMIT_TOUCH_REQUIRES_EXPLICIT_ENTRY_PRICE');
      if (event.index < (state.pendingCreatedAt ?? event.index)) return reject(state, 'LIMIT_TOUCH_CANNOT_PRECEDE_PENDING_ORDER');
      if (event.price !== state.geometry.pendingEntryPrice.price) return state;
      return {
        ...state,
        phase: 'FILLED',
        fillIndex: event.index,
        position: {
          ...state.position,
          entryPrice: event.price,
          stopLoss: state.geometry.structuralStop.price,
        },
      };

    case 'STRUCTURAL_INVALIDATION':
      assertPhase(state, 'PENDING');
      return { ...state, phase: 'INVALIDATED', invalidationIndex: event.index };

    case 'STOP_HIT':
      assertPhase(state, 'FILLED');
      if (state.position.stopLoss === null) return reject(state, 'STOP_HIT_REQUIRES_EXPLICIT_STOP');
      if (event.price !== state.position.stopLoss) return state;
      return { ...state, phase: 'STOPPED', invalidationIndex: event.index };

    case 'TP1_REACHED':
      assertPhase(state, 'FILLED');
      return { ...state, phase: 'TP1_REACHED', tp1Index: event.index };

    case 'COMPLETE':
      assertPhase(state, 'TP1_REACHED');
      return { ...state, phase: 'COMPLETED' };

    case 'REJECT':
      return reject(state, event.reason);
  }
}

export function resolveSameCandleTouch(
  policy: IntrabarTouchPolicy,
  touches: { entry: boolean; stop: boolean; tp1: boolean },
): 'FILL' | 'STOP' | 'TP1' | 'AMBIGUOUS' | 'NONE' {
  if (!touches.entry) return 'NONE';
  if (touches.stop && touches.tp1) return policy === 'AMBIGUOUS' ? 'AMBIGUOUS' : policy === 'SL_FIRST' ? 'STOP' : 'TP1';
  if (touches.stop) return 'STOP';
  if (touches.tp1) return 'TP1';
  return 'FILL';
}
