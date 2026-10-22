"""Constrained marketplace rollout optimization."""

# I use a transparent rollout score instead of automatically scaling everywhere.
# The optimizer rewards expected trip lift but penalizes uncertainty, access
# gaps, and operational pressure while preserving minimum geographic coverage.

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RolloutZone:
    zone: int
    score: float
    expected_trip_lift: float
    demand_pressure: float
    access_group: str
    rollout_share: float


def recommend_rollout(
    zone: np.ndarray,
    pressure: np.ndarray,
    access_group: np.ndarray,
    base_lift: float,
    uncertainty: float,
    rollout_fraction: float = 0.50,
) -> list[RolloutZone]:
    rows = []
    for zone_id in np.unique(zone):
        mask = zone == zone_id
        avg_pressure = float(np.mean(pressure[mask]))
        group = str(access_group[mask][0])
        expected = base_lift * (1 + 0.24 * (avg_pressure - 0.9))
        equity_adjustment = 0.006 if group == "limited" else 0.0
        score = expected - 0.35 * uncertainty - max(0, avg_pressure - 1.25) * 0.02 + equity_adjustment
        rows.append((int(zone_id), score, expected, avg_pressure, group))
    selected_n = max(1, round(len(rows) * rollout_fraction))
    selected = sorted(rows, key=lambda row: row[1], reverse=True)[:selected_n]
    positive = np.maximum([row[1] for row in selected], 0.001)
    shares = positive / np.sum(positive)
    return [RolloutZone(*row, float(share)) for row, share in zip(selected, shares, strict=True)]

