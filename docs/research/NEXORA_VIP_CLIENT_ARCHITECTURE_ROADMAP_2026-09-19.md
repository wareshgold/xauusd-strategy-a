# Nexora Client / VIP Distribution Architecture — Future Plan

## Status

**PLANNED / NON-OPERATIONAL**

This document records a future product architecture only. It does not authorize live trading, does not change Strategy A geometry, and does not activate any client, installer, auto-update, VIP authentication, or automated order-generation path.

## Purpose

Future goal: allow an authorized user with a valid VIP code to install a Nexora client on their own Windows computer, connect the client to their locally running MT5 terminal, and receive the currently approved Nexora system release without manually managing Python environments or cloning the research repository.

The public product identity is **Nexora**. The underlying strategy name must not be exposed in public-facing client/Telegram UI.

## Planned layers

### Layer 1 — Installer / Client Shell

A future Windows installer will provide a self-contained Nexora client environment.

Responsibilities:
- install required runtime components;
- create local application directories;
- provide Start / Stop / Status controls;
- keep research repository internals hidden from normal users;
- never contain broker credentials or hard-coded secrets.

Status: **DESIGN ONLY**.

### Layer 2 — Release / Update Manager

The client will later obtain only an explicitly approved release from the authoritative GitHub repository/release channel.

Responsibilities:
- identify installed client version;
- check the approved release manifest;
- download updates;
- verify revision/integrity before activation;
- retain a rollback-safe previous version;
- refuse untrusted or incomplete releases.

Important constraint: GitHub source changes must not automatically become live trading authority. A release must pass the project's research and approval gates first.

Status: **DESIGN ONLY**.

### Layer 3 — VIP Authorization

A future VIP service will authenticate a user's entitlement without exposing internal research rules.

Responsibilities:
- validate VIP code / entitlement;
- associate entitlement with an authorized client/device policy if later required;
- support expiration/revocation;
- prevent the VIP code itself from being treated as a trading signal.

Exact licensing, device limits, server architecture, and cryptographic protocol remain **UNRESOLVED** and must not be invented yet.

Status: **DESIGN ONLY**.

### Layer 4 — MT5 Discovery / Connection Adapter

The future client will discover compatible locally installed MT5 terminals and validate the selected terminal/account environment.

Expected checks:
- MT5 terminal detected;
- terminal connection available;
- broker/server identity readable;
- required symbol available;
- trading permissions/status readable;
- market data accessible.

The client must not assume that terminal timestamps are UTC. Existing MT5 timestamp/session findings remain observations until historically verified.

Status: **DESIGN ONLY**.

### Layer 5 — Strategy Runtime Boundary

The strategy runtime will consume only the canonical, approved Strategy A release once the research gates are complete.

Critical boundary:
- the client must not invent unresolved P-Gap geometry;
- must not invent AB=CD anchors/tolerance;
- must not invent fill semantics;
- must not promote Leg1=Leg2 equality without source confirmation;
- must not tune parameters automatically in production;
- must not generate production BUY/SELL decisions before explicit project authorization.

Status: **DESIGN ONLY / CURRENTLY BLOCKED BY RESEARCH GATES**.

### Layer 6 — Execution Gateway

The existing guarded scripts/live_mt5_gateway.py remains the authoritative execution boundary.

Future client integration must preserve:
- explicit approved-signal contract;
- LIVE_TRADING_ENABLE=false until separately authorized;
- position limits and duplicate-signal protection;
- journaling and reconciliation;
- Nexora public branding;
- separation between strategy generation and execution.

No new execution implementation is authorized by this document.

Status: **EXISTING GUARDED INFRASTRUCTURE; FUTURE CLIENT INTEGRATION ONLY**.

### Layer 7 — Observability / Support

Future client diagnostics may expose safe operational state such as:
- client version;
- approved release revision;
- MT5 connection state;
- symbol availability;
- last market-data timestamp;
- runtime health;
- signal/execution journal status.

Sensitive credentials, internal source evidence, and private research artifacts must not be exposed through normal VIP UI.

Status: **DESIGN ONLY**.

## Planned trust boundary

GitHub main is a source/release input, not an unconditional trading authority.

VIP authorization grants access to an approved client/release; it does not define Strategy A rules.

MT5 supplies the broker connection, account context, and market data.

Execution Gateway is the final guarded order boundary.

## Current project gates

As of 2026-09-19:

- Frozen Geometry: **BLOCKED**
- Parameter Stability: **INCONCLUSIVE — NO PASS / NO FAIL**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Live Trading: **DISABLED**

Therefore this architecture is a **future roadmap only**. No layer described here should be interpreted as operational authorization.

## Future activation order

When the research program eventually permits production, activation should proceed only through an explicit release/authorization gate:

1. Source/Frozen Geometry becomes resolved and frozen.
2. Untouched validation completes.
3. Robustness/stability requirements are satisfied under the project's pre-registered criteria.
4. Fresh Holdout completes without rule or parameter changes.
5. Production authorization is explicitly recorded.
6. Only then may the approved Strategy A release be connected to the guarded execution gateway.
7. VIP distribution and client auto-update can then distribute that approved release.

No step in this document bypasses those gates.
