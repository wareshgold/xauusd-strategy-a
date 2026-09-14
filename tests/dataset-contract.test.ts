import { describe, expect, it } from "vitest";
import {
  buildDatasetContract,
  canonicalizeDatasetRows,
  fingerprintDatasetRows,
  type DatasetRow,
} from "../src/data/dataset-contract.js";

const rows: readonly DatasetRow[] = [
  {
    timestamp: "2026-01-01T00:00:00.000Z",
    open: 100,
    high: 101,
    low: 99,
    close: 100.5,
  },
  {
    timestamp: "2026-01-01T00:01:00.000Z",
    open: 100.5,
    high: 102,
    low: 100,
    close: 101.5,
  },
];

describe("dataset contract", () => {
  it("canonicalizes identical rows deterministically", () => {
    expect(canonicalizeDatasetRows(rows)).toBe(
      "2026-01-01T00:00:00.000Z,100,101,99,100.5\n2026-01-01T00:01:00.000Z,100.5,102,100,101.5",
    );
    expect(fingerprintDatasetRows(rows)).toBe(fingerprintDatasetRows([...rows]));
  });

  it("changes the fingerprint when dataset content changes", () => {
    const mutated = rows.map((row, index) =>
      index === 1 ? { ...row, close: 101.6 } : row,
    );
    expect(fingerprintDatasetRows(mutated)).not.toBe(fingerprintDatasetRows(rows));
  });

  it("builds an auditable contract from metadata and rows", () => {
    const contract = buildDatasetContract(
      {
        datasetId: "xauusd-test",
        datasetVersion: "fixture-v1",
        source: "synthetic-fixture",
        schemaVersion: "ohlc-v1",
        symbol: "XAUUSD",
        timeframe: "1m",
        timezone: "UTC",
        timestampConvention: "ISO-8601 UTC candle-open timestamps",
      },
      rows,
    );

    expect(contract.rowCount).toBe(2);
    expect(contract.firstTimestamp).toBe(rows[0].timestamp);
    expect(contract.lastTimestamp).toBe(rows[1].timestamp);
    expect(contract.contentFingerprint).toHaveLength(64);
  });

  it("rejects an empty dataset", () => {
    expect(() =>
      buildDatasetContract(
        {
          datasetId: "empty",
          datasetVersion: "v1",
          source: "test",
          schemaVersion: "ohlc-v1",
          symbol: "XAUUSD",
          timeframe: "1m",
          timezone: "UTC",
          timestampConvention: "ISO-8601 UTC candle-open timestamps",
        },
        [],
      ),
    ).toThrow("Dataset must contain at least one row");
  });
});
