# Raw MT5 acquisition byte-preservation policy — 2026-10-11

## Finding

On Windows with `core.autocrlf=true`, the tracked artifact
`data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv` was checked out
with CRLF line endings. The committed Git blob and its manifest agree on SHA-256
`9df9a0ca0333c185396fb3407c7c816fd77a2ab57d88f71cea30a73462e75aa4`, while the
working-tree bytes hash to `09fb33790e46539df7ea072d0796a84f1136b242e32e28b365ccd2c604dd8cae`.
Both versions have 28,815 data rows; the observed byte-size difference is consistent
with CRLF versus LF line endings.

## Policy

Factory provenance hashes are byte identities. Raw acquired CSVs and their manifests
must not be silently normalized by Git checkout. `.gitattributes` disables text/EOL
conversion for `data/mt5-acquisition/*.csv` and
`data/mt5-acquisition/*.manifest.json`.

Do not update a manifest hash merely to make a Windows checkout pass. Do not treat
matching row counts as proof of data completeness or correctness.

## Safe local verification after pulling the policy

1. Confirm the tracked files have no intentional content edits and retain any needed backup.
2. Check `git check-attr -a -- data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv`; it should report `text: unset`.
3. Compare the local file SHA-256 to the manifest's `artifact_sha256`.
4. If the working copy still has CRLF, and only after verifying/backup, restore that tracked CSV from Git under the new attributes so it is materialized byte-for-byte from the committed blob. Then recheck the SHA-256 and byte size.

## Scope

This policy only protects artifact bytes. It does not validate timestamps, OHLC values,
the 20 reported data gaps, broker-feed accuracy, tick/Bid/Ask availability, or Strategy A
execution semantics. Historical strategy evaluation remains blocked until those separate
checks and source/execution contracts are resolved.
