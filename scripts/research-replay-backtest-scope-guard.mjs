#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { appendFileSync, writeFileSync } from "node:fs";

const base = process.env.BASE_SHA;
const head = process.env.HEAD_SHA ?? "HEAD";
if (!base) throw new Error("SCOPE_GUARD_MISSING_BASE_SHA");

const guardedPaths = [
  "src/replay/replay-runner.ts",
  "src/replay/backtest-runner.ts",
  "src/replay/execution-simulator.ts",
];

const sensitivePatterns = [
  /P[- ]?Gap/i,
  /AB\s*=?\s*CD/i,
  /ABCD/i,
  /geometry/i,
  /SP2L_FINAL_GEOMETRY/i,
  /SP2L_SOURCE_GEOMETRY/i,
  /VISUAL_GEOMETRY/i,
  /GEOMETRY_RESOLUTION/i,
];

const diff = execFileSync("git", [
  "diff", "--unified=0", `${base}...${head}`, "--", ...guardedPaths,
], { encoding: "utf8" });

const addedLines = diff
  .split("\n")
  .filter((line) => line.startsWith("+") && !line.startsWith("+++"));

const hits = [];
for (const line of addedLines) {
  for (const pattern of sensitivePatterns) {
    if (pattern.test(line)) {
      hits.push({ pattern: pattern.source, line: line.slice(0, 300) });
      break;
    }
  }
}

const output = hits.length === 0
  ? "## Replay/Backtest Scope Guard\n\nPASS — no sensitive Strategy A geometry terms detected in added lines within guarded replay/execution paths.\n"
  : [
      "## Replay/Backtest Scope Guard",
      "",
      "⚠️ **MANUAL REVIEW REQUIRED** — sensitive Strategy A geometry terms were detected in added lines inside guarded replay/execution paths.",
      "",
      "This guard is advisory. It does not decide whether the change is valid and does not make any rule canonical.",
      "",
      ...hits.map((hit) => `- pattern \`${hit.pattern}\`: \`${hit.line.replaceAll("`", "'")}\``),
      "",
      "Required review: confirm that the change is infrastructure-only and introduces no new Strategy A geometry or source meaning.",
      "",
    ].join("\n");

writeFileSync("scope-guard-report.md", `${output}\n`);
appendFileSync(process.env.GITHUB_STEP_SUMMARY ?? "/dev/null", `${output}\n`);

console.log(output);
// Advisory by design: never fail the build solely because the guard detects a term.
process.exit(0);
