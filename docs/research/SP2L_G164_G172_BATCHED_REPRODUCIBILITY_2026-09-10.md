# SP2L G164-G172 — Batched Reproducibility Boundary

## Status

Infrastructure-only. Reproducibility is a prerequisite for trustworthy research, not a production authorization.

## Gates

- G164: dataset fingerprint must match.
- G165: specification version must match.
- G166: source provenance must match.
- G167: execution must be deterministic.
- G168: output fingerprint must match.
- G169: dataset mismatch blocks.
- G170: specification or source mismatch blocks.
- G171: nondeterministic execution blocks.
- G172: output mismatch blocks.

## Boundary

This batch does not reinterpret Strategy A. No P-Gap formula, A/B/C/D anchor, AB=CD tolerance, trigger timing, pending-limit fill semantics, stop geometry, or Leg-2 projection is introduced. Production remains independently gated.
