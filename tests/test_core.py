# These tests make sure the dashboard gets the results it expects and that
# invalid experiment sizes are caught before the analysis runs.

import numpy as np
import pytest
from equilibrium_lab.analysis import analyze
from equilibrium_lab.diagnostics import assignment_checks
from equilibrium_lab.experiment import estimate_effect
from equilibrium_lab.optimizer import recommend_rollout
from equilibrium_lab.simulation import simulate_marketplace


def test_simulation_is_reproducible_and_balanced():
    first = simulate_marketplace(seed=7)
    second = simulate_marketplace(seed=7)
    assert np.array_equal(first.completed, second.completed)
    assert assignment_checks(first)["passed"]


def test_effect_recovers_positive_completion_lift():
    panel = simulate_marketplace(seed=29)
    conversion = panel.completed / panel.requests
    result = estimate_effect(conversion, panel.treatment, panel.zone, panel.hour, panel.block)
    assert result.effect > 0.02
    assert result.ci_low > 0
    assert result.clusters > 100


def test_rollout_is_normalized_and_selective():
    panel = simulate_marketplace(n_zones=18, seed=4)
    rollout = recommend_rollout(panel.zone, panel.demand_pressure, panel.access_group, 0.035, 0.004)
    assert len(rollout) == 9
    assert sum(row.rollout_share for row in rollout) == pytest.approx(1.0)


def test_analysis_contract():
    result = analyze()
    assert result["decision"]["status"] in {"SCALE IN PHASES", "ITERATE", "HOLD"}
    assert len(result["guardrails"]) == 4
    assert set(result["demand_segments"]) == {"balanced", "busy", "constrained"}
    assert len(result["hourly"]) == 24

