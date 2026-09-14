import { createHash } from "node:crypto";

export interface DatasetRow {
  readonly timestamp: string;
  readonly open: number;
  readonly high: number;
  readonly low: number;
  readonly close: number;
}

export interface DatasetContract {
  readonly datasetId: string;
  readonly datasetVersion: string;
  readonly source: string;
  readonly schemaVersion: string;
  readonly symbol: string;
  readonly timeframe: string;
  readonly timezone: string;
  readonly timestampConvention: string;
  readonly rowCount: number;
  readonly firstTimestamp: string;
  readonly lastTimestamp: string;
  readonly contentFingerprint: string;
}

/** Canonical row encoding used for reproducible dataset identity. */
export function canonicalizeDatasetRows(rows: readonly DatasetRow[]): string {
  return rows
    .map((row) =>
      [
        row.timestamp,
        row.open.toString(),
        row.high.toString(),
        row.low.toString(),
        row.close.toString(),
      ].join(","),
    )
    .join("\n");
}

/** SHA-256 fingerprint of canonical dataset content; this does not validate data quality. */
export function fingerprintDatasetRows(rows: readonly DatasetRow[]): string {
  return createHash("sha256")
    .update(canonicalizeDatasetRows(rows), "utf8")
    .digest("hex");
}

export function buildDatasetContract(
  metadata: Omit<
    DatasetContract,
    "rowCount" | "firstTimestamp" | "lastTimestamp" | "contentFingerprint"
  >,
  rows: readonly DatasetRow[],
): DatasetContract {
  if (rows.length === 0) {
    throw new Error("Dataset must contain at least one row");
  }

  return {
    ...metadata,
    rowCount: rows.length,
    firstTimestamp: rows[0].timestamp,
    lastTimestamp: rows[rows.length - 1].timestamp,
    contentFingerprint: fingerprintDatasetRows(rows),
  };
}
