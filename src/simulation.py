# I use synthetic data so the full marketplace experiment can be reproduced
# without exposing customer or driver information. The simulation includes
# zone differences, demand cycles, supply constraints, and treatment spillover.

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MarketplacePanel:
    zone: np.ndarray
    hour: np.ndarray
    block: np.ndarray
    treatment: np.ndarray
    access_group: np.ndarray
    demand_pressure: np.ndarray
    requests: np.ndarray
    completed: np.ndarray
    pickup_minutes: np.ndarray
    cancellations: np.ndarray
    driver_utilization: np.ndarray
    driver_earnings: np.ndarray
    contribution: np.ndarray


def simulate_marketplace(n_zones: int = 18, days: int = 28, seed: int = 29) -> MarketplacePanel:
    """Create an hourly panel with randomized four-hour switchback blocks."""
    if n_zones < 8 or days < 14:
        raise ValueError("Use at least 8 zones and 14 days")
    rng = np.random.default_rng(seed)
    hours = np.arange(days * 24)
    zone_ids = np.repeat(np.arange(n_zones), len(hours))
    time_ids = np.tile(hours, n_zones)
    blocks = time_ids // 4
    zone_effect = rng.normal(0, 0.18, n_zones)
    access_by_zone = np.where(np.arange(n_zones) % 4 == 0, "limited", "standard")
    access_group = access_by_zone[zone_ids]

    # Alternate assignment within each zone, with a random phase to avoid a
    # systematic relationship between treatment and time of day.
    phase = rng.integers(0, 2, n_zones)
    treatment = ((blocks + phase[zone_ids]) % 2).astype(bool)
    hour_of_day = time_ids % 24
    weekend = (time_ids // 24) % 7 >= 5
    peak = ((hour_of_day >= 7) & (hour_of_day <= 9)) | ((hour_of_day >= 16) & (hour_of_day <= 19))
    pressure = 0.72 + 0.55 * peak + 0.16 * weekend + zone_effect[zone_ids] + rng.normal(0, 0.11, len(zone_ids))
    demand_pressure = np.clip(pressure, 0.35, 1.75)
    requests = rng.poisson(62 * demand_pressure).astype(float)

    # The new policy helps most when the market is moderately constrained. It
    # helps access-limited zones too, but less, making equity visible.
    access_penalty = (access_group == "limited") * 0.018
    conversion_base = 0.70 - 0.12 * (demand_pressure - 0.8) - access_penalty
    conversion_lift = treatment * (0.036 + 0.018 * (demand_pressure > 1.05) - 0.010 * (access_group == "limited"))
    conversion = np.clip(conversion_base + conversion_lift, 0.42, 0.90)
    completed = rng.binomial(requests.astype(int), conversion).astype(float)
    cancellations = requests - completed
    pickup_minutes = np.maximum(
        2.5,
        7.9 + 3.1 * (demand_pressure - 0.8) - treatment * 0.72 + access_penalty * 34 + rng.normal(0, 0.48, len(zone_ids)),
    )
    driver_utilization = np.clip(0.58 + 0.19 * demand_pressure + treatment * 0.026 + rng.normal(0, 0.025, len(zone_ids)), 0, 0.98)
    driver_earnings = 22.5 + 8.2 * demand_pressure + treatment * 0.68 + rng.normal(0, 1.1, len(zone_ids))
    contribution = completed * (5.1 + 0.35 * demand_pressure) - treatment * requests * 0.08
    return MarketplacePanel(
        zone_ids,
        time_ids,
        blocks,
        treatment,
        access_group,
        demand_pressure,
        requests,
        completed,
        pickup_minutes,
        cancellations,
        driver_utilization,
        driver_earnings,
        contribution,
    )

