from __future__ import annotations

from collections import Counter
from datetime import datetime
from statistics import mean
from typing import Iterable

from .models import Trade


def cluster_trades(trades: Iterable[Trade], *, max_gap_minutes: int = 30) -> list[list[Trade]]:
    """Group chronologically adjacent trades into deterministic activity clusters."""
    if max_gap_minutes < 0:
        raise ValueError("max_gap_minutes must be non-negative")
    ordered = sorted(trades, key=lambda t: t.entry_time)
    clusters: list[list[Trade]] = []
    for trade in ordered:
        if not clusters:
            clusters.append([trade])
            continue
        gap = (trade.entry_time - clusters[-1][-1].entry_time).total_seconds() / 60
        if gap <= max_gap_minutes:
            clusters[-1].append(trade)
        else:
            clusters.append([trade])
    return clusters


def summarize_clusters(trades: Iterable[Trade], *, max_gap_minutes: int = 30) -> dict:
    clusters = cluster_trades(trades, max_gap_minutes=max_gap_minutes)
    sizes = [len(c) for c in clusters]
    return {
        "clusterCount": len(clusters),
        "tradeCount": sum(sizes),
        "meanClusterSize": mean(sizes) if sizes else None,
        "maxClusterSize": max(sizes, default=0),
        "clusters": [
            {"start": c[0].entry_time.isoformat(), "end": c[-1].entry_time.isoformat(), "size": len(c)}
            for c in clusters
        ],
    }


def summarize_excursions(trades: Iterable[Trade]) -> dict:
    """Summarize MAE/MFE when values are supplied by the neutral backtest layer."""
    rows = list(trades)
    mae = [float(t.metadata["maeR"]) for t in rows if "maeR" in t.metadata]
    mfe = [float(t.metadata["mfeR"]) for t in rows if "mfeR" in t.metadata]
    return {
        "maeCount": len(mae),
        "mfeCount": len(mfe),
        "meanMaeR": mean(mae) if mae else None,
        "meanMfeR": mean(mfe) if mfe else None,
        "maxMaeR": max(mae, default=None),
        "maxMfeR": max(mfe, default=None),
    }
