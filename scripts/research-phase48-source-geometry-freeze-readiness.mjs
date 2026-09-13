import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const exists = (p) => fs.existsSync(path.join(root, p));

const semantic = read('src/domain/research/sp2l-v2/Sp2lSemanticState.ts');
const phase32 = read('docs/research/PHASE_32_SP2L_V2_SEMANTIC_STATE_AND_FIXTURES.md');

const geometry = [
  {
    id: 'G1', name: 'First structural high/low', field: 'firstStructuralReference',
    status: semantic.includes("firstStructuralReference: StructuralReference") && phase32.includes('First structural reference is explicit') ? 'CANDIDATE' : 'TBD',
    basis: 'Semantic model explicitly carries the reference, but Phase 32 preserves it as CANDIDATE/TBD and does not provide a frozen source geometry formula.'
  },
  {
    id: 'G2', name: 'Pending-limit price', field: 'pendingEntryPrice',
    status: semantic.includes('pendingEntryPrice: StructuralReference') && phase32.includes('Entry price must be explicit') ? 'CANDIDATE' : 'TBD',
    basis: 'Pending-limit entry is source-aligned and explicit in the semantic model; the exact geometric price construction is not frozen by the available evidence.'
  },
  {
    id: 'G3', name: 'Structural stop', field: 'structuralStop',
    status: semantic.includes('structuralStop: StructuralReference') && phase32.includes('Structural stop must be explicit') ? 'CANDIDATE' : 'TBD',
    basis: 'Structural invalidation/stop is explicit, but the exact source anchor/offset is not frozen by the available evidence.'
  },
  {
    id: 'G4', name: 'Leg 1 endpoint', field: 'leg1Endpoint',
    status: semantic.includes('leg1Endpoint: StructuralReference') && phase32.includes('Leg 1 endpoint remains explicitly `TBD`') ? 'TBD' : 'CANDIDATE',
    basis: 'Phase 32 explicitly states that the Leg 1 endpoint remains TBD until source-complete.'
  },
  {
    id: 'G5', name: 'Leg 2 projection origin', field: 'leg2ProjectionOrigin',
    status: semantic.includes('leg2ProjectionOrigin: Leg2ProjectionOrigin') && phase32.includes('Leg 2 projection origin remains explicitly `TBD`') ? 'TBD' : 'CANDIDATE',
    basis: 'Phase 32 explicitly states that the Leg 2 projection origin remains TBD until source-complete.'
  },
  {
    id: 'G6', name: 'AB=CD / Leg equality tolerance', field: 'leg2EqualityTolerance',
    status: semantic.includes('leg2EqualityTolerance: number | null') && phase32.includes('Leg 2 equality tolerance remains unset rather than fitted') ? 'TBD' : 'CANDIDATE',
    basis: 'AB=CD is a source hypothesis, but no source-confirmed numeric tolerance is frozen; the state intentionally stores null rather than a fitted threshold.'
  },
  {
    id: 'G7', name: 'Fill / intrabar semantics', field: 'resolveSameCandleTouch',
    status: semantic.includes('resolveSameCandleTouch') && phase32.includes('Same-candle entry/SL/TP ordering requires an explicit simulator policy') ? 'CANDIDATE' : 'TBD',
    basis: 'The model requires an explicit policy (SL_FIRST/TP_FIRST/AMBIGUOUS), but the source evidence does not establish a canonical intrabar ordering policy here.'
  },
];

const unresolved = geometry.filter(g => g.status !== 'SOURCE_CONFIRMED');
const ready = unresolved.length === 0;
const criticalUnresolved = geometry.filter(g => ['G1','G2','G3','G4','G5','G6','G7'].includes(g.id) && g.status !== 'SOURCE_CONFIRMED');

const report = {
  mode: 'PHASE48_SOURCE_GEOMETRY_FREEZE_READINESS',
  generatedAt: new Date().toISOString(),
  decision: ready ? 'READY_FOR_FREEZE_REVIEW' : 'NOT_READY_FOR_FREEZE',
  sourceFirst: true,
  historicalPerformanceCannotPromoteGeometry: true,
  productionTouched: false,
  freshHoldoutUnlocked: false,
  geometry,
  criticalUnresolved: criticalUnresolved.map(g => g.id),
  evidenceFiles: [
    'docs/research/PHASE_32_SP2L_V2_SEMANTIC_STATE_AND_FIXTURES.md',
    'src/domain/research/sp2l-v2/Sp2lSemanticState.ts'
  ],
  protectedPrinciples: [
    'Do not invent P-Gap formula.',
    'Do not invent A/B/C/D anchors.',
    'Do not invent AB=CD tolerance.',
    'Do not equate P-Gap with a generic three-candle imbalance without source confirmation.',
    'Do not replace pending-limit entry with close-reclaim execution.',
    'Do not use profitability to resolve source meaning.',
    'Unresolved geometry remains explicit rather than promoted.'
  ],
  gate: ready ? 'SOURCE_RESOLUTION_COMPLETE_PENDING_FORMAL_FREEZE' : 'SOURCE_RESOLUTION_INCOMPLETE',
};

const outDir = path.join(root, 'artifacts/phase48');
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'phase48-source-geometry-freeze-readiness.json'), JSON.stringify(report, null, 2) + '\n');

console.log(JSON.stringify(report, null, 2));
if (!exists('src/domain/research/sp2l-v2/Sp2lSemanticState.ts')) process.exit(2);
if (!ready) process.exitCode = 0;
