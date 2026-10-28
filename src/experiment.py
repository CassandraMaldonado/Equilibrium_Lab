# This is where I estimate the actual impact of the policy. 
# I account for differences between zones and times of day, then group related observations together so I do not treat repeated marketplace activity as completely independent.

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Effect:
    control_mean: float
    treatment_mean: float
    effect: float
    relative_effect: float
    standard_error: float
    ci_low: float
    ci_high: float
    p_value: float
    clusters: int


def residualize(outcome: np.ndarray, zone: np.ndarray, hour: np.ndarray) -> np.ndarray:
    """Remove additive zone and hour-of-day effects."""
    y = np.asarray(outcome, dtype=float)
    result = y.copy()
    grand = np.mean(y)
    for value in np.unique(zone):
        mask = zone == value
        result[mask] -= np.mean(y[mask]) - grand
    for value in np.unique(hour % 24):
        mask = hour % 24 == value
        result[mask] -= np.mean(result[mask]) - grand
    return result


def estimate_effect(
    outcome: np.ndarray,
    treatment: np.ndarray,
    zone: np.ndarray,
    hour: np.ndarray,
    block: np.ndarray,
) -> Effect:
    adjusted = residualize(outcome, zone, hour)
    effect = float(np.mean(adjusted[treatment]) - np.mean(adjusted[~treatment]))
    control_mean = float(np.mean(outcome[~treatment]))
    treatment_mean = float(np.mean(outcome[treatment]))
    residual = adjusted - np.where(treatment, np.mean(adjusted[treatment]), np.mean(adjusted[~treatment]))
    cluster_id = zone.astype(np.int64) * (int(np.max(block)) + 1) + block.astype(np.int64)
    unique_clusters = np.unique(cluster_id)
    score = np.array([np.sum((treatment[cluster_id == c].astype(float) - np.mean(treatment)) * residual[cluster_id == c]) for c in unique_clusters])
    denom = np.sum((treatment.astype(float) - np.mean(treatment)) ** 2)
    variance = len(unique_clusters) / (len(unique_clusters) - 1) * np.sum(score**2) / denom**2
    se = float(np.sqrt(variance))
    dof = len(unique_clusters) - 1
    critical = float(stats.t.ppf(0.975, dof))
    p_value = float(2 * stats.t.sf(abs(effect / se), dof)) if se else 1.0
    return Effect(control_mean, treatment_mean, effect, effect / control_mean if control_mean else 0.0, se, effect - critical * se, effect + critical * se, p_value, len(unique_clusters))

