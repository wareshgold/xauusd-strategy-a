# Twelve Data XAU/USD Pagination Experiment

## Purpose

This experiment is deliberately bounded. It validates the mechanics needed for a future historical downloader before any bulk acquisition:

- dedicated `earliest_timestamp` endpoint;
- one maximum-size M1 page (`outputsize=5000`);
- backward paging with `end_date` at the previous page boundary;
- overlap at the boundary;
- a tiny combined `start_date` + `end_date` window;
- OHLC validity and 1-minute continuity;
- API credit headers when exposed by the provider.

Twelve Data documents a maximum of 5,000 data points per request and documents `start_date`/`end_date` as the mechanism for bounded historical windows. When both are supplied, `outputsize` should be omitted so the date boundaries control the response. citeturn0search0turn0search1

## Run

After pulling the branch:

```powershell
python scripts/data/pagination_experiment.py
```

The experiment attempts at most **5 requests** and writes no market data to disk.

## Credit safety

The Basic plan currently advertises 8 API credits per minute and 800 per day. Twelve Data states that each API response exposes `api-credits-used` and `api-credits-left` headers, and that the Basic daily quota resets at 00:00 UTC. citeturn0search2turn0search6

The script prints those headers when available, but never prints the API key.

## Important non-conclusions

A passing experiment does **not** prove:

- complete 2020-present XAU/USD M1 coverage;
- absence of historical gaps outside tested pages;
- broker/feed equivalence;
- that Twelve Data should be the final source of truth;
- that bulk extraction should begin immediately.

The next step after a successful run is a small, credit-bounded acquisition sample with persisted provenance and explicit checkpoint semantics. Only after that should we estimate the full historical extraction cost.
