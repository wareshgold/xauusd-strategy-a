# SP2L Artifact-to-Observation Binding — Source Resolution (2026-11-16)

**Status:** source audit completed; binding contract blocked on missing capture-provenance semantics  
**Canonical status:** non-canonical; no production caller  
**Runtime boundary:** repository/source inspection only; no MT5, broker, filesystem evidence, account worker, or Runner access

## 1. Research question

Can the current evidence model deterministically establish that one exact-byte-verified artifact represents a particular history observation (and, where applicable, the ORDERS or DEALS query within that observation)?

The answer from the inspected source is **not yet**. The current models preserve the relevant identifiers and fingerprints, but do not encode or verify the relationship between an individual artifact and an individual observation/query result.

## 2. Existing source contracts

### 2.1 Manifest record

`scripts/sp2l_evidence_manifest_research.py` defines:

- `EvidenceManifestRecord.observation_ids`: a tuple of observation IDs declared at manifest level;
- `EvidenceManifestRecord.artifacts`: a tuple of artifact records;
- each `EvidenceArtifactRecord`: `artifact_id`, operator-declared `artifact_role`, opaque `locator`, `byte_length`, and exact-byte `byte_sha256`.

The validator checks shape, nonblank values, unique IDs, nonnegative byte length, and digest syntax. It does not associate an artifact with a specific observation ID, query kind, API invocation, or payload fingerprint.

### 2.2 History observation fingerprint

`scripts/sp2l_history_stability_research.py` defines `HistoryObservationFingerprint` with:

- one `observation_id`;
- one `HistoryCompletenessEvidence` containing separate ORDERS and DEALS observations, their reported totals and captured record tuples, plus declared scope;
- one `fingerprint_algorithm_id`;
- separate `orders_payload_sha256` and `deals_payload_sha256` declarations.

The model validates digest shape and compares supplied fingerprints across observations. It deliberately does not define raw-row serialization, ordering, field selection, or hash generation. It does not recompute these payload fingerprints from artifact bytes.

### 2.3 Existing linkage and byte verification

- `scripts/sp2l_evidence_manifest_linkage_research.py` verifies manifest-to-observation ID membership and declared scope agreement. It accepts a non-empty subset of manifest observation IDs; it does not link individual artifacts to those observations.
- `scripts/sp2l_evidence_artifact_verification_research.py` verifies exact bytes at caller-resolved paths against each artifact's declared byte length and SHA-256. It does not interpret locators or establish semantic content.

These are distinct checks. Passing both does not prove that a verified artifact contains the rows or payload represented by a listed observation.

## 3. Source audit findings

The following repository materials were inspected:

- Evidence Manifest record model and research note;
- Evidence Manifest ↔ History Observation linkage model and research note;
- exact-byte Artifact Verification model and research note;
- History Observation Fingerprint and stability model;
- read-only history adapter and paired ORDERS/DEALS observation contract;
- history completeness evidence protocol;
- the multi-account foundation RFC;
- existing MT5 export/reconciliation examples and evidence-intake documents.

The source contracts explicitly defer or omit the needed mapping:

1. Manifest artifact roles are arbitrary operator-declared strings. No required role vocabulary or mapping to API query kinds is defined.
2. The manifest has a manifest-level observation ID list, not a per-artifact observation reference.
3. The history fingerprint contains separate ORDERS and DEALS payload digests, but their algorithm and canonicalization are intentionally external and unresolved.
4. No source defines whether one artifact represents one query result, both query kinds, multiple observations, or a broader export.
5. No capture record binds a specific API invocation and its returned tuple to the exact bytes later written to an artifact.
6. The existing `mt5_history_reconciliation.py` is a separate live reconciliation helper; it initializes MT5 in its script entry point and compares terminal deals with a local journal. It is not a source contract for this offline evidence pipeline and must not be reused as one.
7. Existing candle-data export/manifests describe a different acquisition domain. They do not establish serialization or artifact binding semantics for historical ORDERS/DEALS records.

## 4. Binding questions that remain unresolved

No implementation may choose answers by convention or by what is convenient for tests. The capture/source contract must determine:

- **Artifact granularity:** one file per query response, one file per observation, or another source-defined unit?
- **Query identity:** how is ORDERS distinguished from DEALS in the capture record, independently of an arbitrary role label?
- **Observation cardinality:** can one artifact belong to multiple observations, or can one observation be represented by multiple artifacts?
- **Invocation identity:** what immutable identifier ties a captured API call (including its exact arguments and scope) to the resulting artifact?
- **Payload relationship:** does the observation payload digest hash the raw API tuple, a serialized export, or a separately defined representation?
- **Serialization:** what exact format, field set, field order, type conversion, null handling, timestamp handling, and row ordering are used, if any?
- **Capture completeness:** how are API errors, empty tuples, partial/failed writes, and interrupted capture represented without turning absence of a file into an empty successful result?
- **Provenance:** which source-produced metadata is authoritative, and which values are merely operator declarations?

Until these are resolved, no semantic comparison between artifact bytes and `orders_payload_sha256` / `deals_payload_sha256` is justified.

## 5. Deterministic boundaries already safe to preserve

The current layers can continue to be used for their narrow meanings:

- manifest validation: declared record shape is valid;
- manifest-observation linkage: supplied observation IDs and declared scope agree with the manifest;
- artifact verification: bytes read from the explicitly supplied path match the manifest's declared byte length and exact-byte SHA-256;
- observation stability: externally supplied counts and payload fingerprints match across two distinct observations under the declared algorithm ID.

None of these outcomes establishes artifact-to-observation semantic binding, broker archive completeness, or authorization for recovery.

## 6. Resolution gate

**Current disposition: `BINDING_CONTRACT_UNRESOLVED`.**

Do not add a binding dataclass, role enum, mapping cardinality, serialization algorithm, or pass/fail classifier yet.

The next admissible step is to identify and inspect the actual capture producer (or obtain an authoritative capture specification) that writes the history artifacts and manifest. Its exact output schema and write sequence must be preserved as evidence. If no such source exists, the operator must explicitly decide the capture contract before implementation; that decision must not be silently supplied by this research model.

Once the source contract exists, create synthetic fixtures directly from its specified cases, then freeze the binding geometry before implementation.

## 7. Safety boundary

This audit does not:
- query or connect to MT5 or a broker;
- initialize a terminal or inspect an account;
- read or modify local runtime evidence;
- change manifest, observation, artifact, recovery, or Runner behavior;
- set `history_completeness_verified=True`;
- authorize account activation, order operations, production recovery, or BUY/SELL decisions.

All findings are research-only and non-canonical.
