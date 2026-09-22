import asyncio
import os
import statistics
import time

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_URL = "http://127.0.0.1:22346/mcp"
SYMBOL = "XAUUSD.ecn"
HEADERS = {
    "Authorization": f"Bearer {os.environ['MT5_MCP_API_KEY']}",
    "MCP-Protocol-Version": "2025-06-18",
}


def stats(values):
    values = sorted(values)
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "p95": values[max(0, int(0.95 * len(values)) - 1)],
        "stdev": statistics.stdev(values) if len(values) >= 2 else 0.0,
    }


async def timed_call(session, tool_name, arguments):
    started = time.perf_counter()
    result = await session.call_tool(tool_name, arguments)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return result, elapsed_ms


async def benchmark_tool(session, label, tool_name, arguments, count=20):
    values = []
    failures = 0

    print(f"\n=== {label} ===")

    for i in range(1, count + 1):
        try:
            result, elapsed = await timed_call(session, tool_name, arguments)
            ok = bool(result.content)
            if ok:
                values.append(elapsed)
            else:
                failures += 1
            print(f"{i:02d}: {elapsed:8.2f} ms  {'OK' if ok else 'EMPTY'}")
        except Exception as exc:
            failures += 1
            print(f"{i:02d}: FAILED {type(exc).__name__}: {exc}")

    if values:
        s = stats(values)
        print(
            f"SUMMARY: success={len(values)}/{count} failed={failures} "
            f"min={s['min']:.2f} median={s['median']:.2f} "
            f"mean={s['mean']:.2f} p95={s['p95']:.2f} "
            f"max={s['max']:.2f} stdev={s['stdev']:.2f} ms"
        )
    else:
        print(f"SUMMARY: success=0/{count} failed={failures}")

    return values


async def benchmark_state_cycle(session, count=20):
    values = []
    failures = 0

    print("\n=== ACCOUNT + OPEN POSITIONS CYCLE ===")

    for i in range(1, count + 1):
        started = time.perf_counter()
        try:
            account = await session.call_tool(
                "get_trading_account_info", {}
            )
            positions = await session.call_tool(
                "get_trading_open_positions", {}
            )
            elapsed = (time.perf_counter() - started) * 1000
            ok = bool(account.content) and bool(positions.content)

            if ok:
                values.append(elapsed)
            else:
                failures += 1

            print(f"{i:02d}: {elapsed:8.2f} ms  {'OK' if ok else 'EMPTY'}")
        except Exception as exc:
            failures += 1
            elapsed = (time.perf_counter() - started) * 1000
            print(
                f"{i:02d}: {elapsed:8.2f} ms  "
                f"FAILED {type(exc).__name__}: {exc}"
            )

    if values:
        s = stats(values)
        print(
            f"SUMMARY: success={len(values)}/{count} failed={failures} "
            f"min={s['min']:.2f} median={s['median']:.2f} "
            f"mean={s['mean']:.2f} p95={s['p95']:.2f} "
            f"max={s['max']:.2f} stdev={s['stdev']:.2f} ms"
        )

    return values


async def main():
    print("SP2L MT5 MCP READ-ONLY BENCHMARK SUITE")
    print("No trading tools are called.")

    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as http_client:
        async with streamable_http_client(
            MCP_URL,
            http_client=http_client,
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                await benchmark_tool(
                    session,
                    "MARKETWATCH XAUUSD.ecn",
                    "get_marketwatch_symbols",
                    {
                        "symbol": SYMBOL,
                        "include_hidden": True,
                        "limit": 1,
                    },
                )

                await benchmark_tool(
                    session,
                    "M1 CHART HISTORY XAUUSD.ecn / 10 CANDLES",
                    "get_chart_history",
                    {
                        "symbol": SYMBOL,
                        "period": "M1",
                        "datetime_from": "2026-09-22T14:00:00Z",
                        "datetime_to": "2026-09-22T14:10:00Z",
                        "limit": 10,
                    },
                )

                await benchmark_tool(
                    session,
                    "ACCOUNT INFO",
                    "get_trading_account_info",
                    {},
                )

                await benchmark_tool(
                    session,
                    "OPEN POSITIONS",
                    "get_trading_open_positions",
                    {},
                )

                await benchmark_state_cycle(session)

    print("\n=== SUITE COMPLETE ===")
    print("Trading tools were not called.")


if __name__ == "__main__":
    asyncio.run(main())
