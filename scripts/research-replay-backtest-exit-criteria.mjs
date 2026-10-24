#!/usr/bin/env node

const criteria = [
  [1, "Chronology"],
  [2, "No look-ahead"],
  [3, "Signal accounting"],
  [4, "Identity"],
  [5, "Pending lifecycle"],
  [6, "Intrabar ambiguity"],
  [7, "Input integrity"],
  [8, "Ledger/metrics"],
  [9, "Manifest"],
  [10, "Scope Guard"],
  [11, "Fixture coverage"],
  [12, "CI"],
  [13, "Clean boundary"],
  [14, "Documentation"],
];

const missing = criteria.filter(([, name]) => process.env[`EXIT_${name.toUpperCase().replaceAll(/[^A-Z0-9]+/g, "_")}`] !== "PASS");

console.log("Replay/Backtest Audit Exit Criteria");
for (const [id, name] of criteria) console.log(`${id}. ${name}`);

if (process.argv.includes("--check")) {
  if (missing.length > 0) {
    console.error(`AUDIT-OPEN: ${missing.length} exit criteria remain unproven.`);
    process.exit(1);
  }
  console.log("AUDIT-CLOSED: all exit criteria explicitly marked PASS.");
}
