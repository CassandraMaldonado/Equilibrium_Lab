# It brings the experiment together. I calculate rider, driver and marketplace outcomes, also look for heterogeneous effects and turn it into a recommendation.

from dataclasses import asdict
import numpy as np
from .diagnostics import access_gap, assignment_checks
from .experiment import estimate_effect
from .optimizer import recommend_rollout
from .simulation import MarketplacePanel, simulate_marketplace


def _effect(panel: MarketplacePanel, outcome: np.ndarray, mask: np.ndarray | None = None) -> dict:
    mask = np.ones(len(panel.zone), dtype=bool) if mask is None else mask
    return asdict(estimate_effect(outcome[mask], panel.treatment[mask], panel.zone[mask], panel.hour[mask], panel.block[mask]))


def analyze(seed: int = 29, zones: int = 18) -> dict:
    panel = simulate_marketplace(n_zones=zones, seed=seed)
    conversion = np.divide(panel.completed, panel.requests, out=np.zeros_like(panel.completed), where=panel.requests > 0)
    completion = _effect(panel, conversion)
    pickup = _effect(panel, panel.pickup_minutes)
    utilization = _effect(panel, panel.driver_utilization)
    earnings = _effect(panel, panel.driver_earnings)
    cancellation = _effect(panel, np.divide(panel.cancellations, panel.requests, out=np.zeros_like(panel.cancellations), where=panel.requests > 0))
    contribution = _effect(panel, panel.contribution)

    demand_segments = {}
    for name, mask in {
        "balanced": panel.demand_pressure < 0.90,
        "busy": (panel.demand_pressure >= 0.90) & (panel.demand_pressure < 1.20),
        "constrained": panel.demand_pressure >= 1.20,
    }.items():
        demand_segments[name] = _effect(panel, conversion, mask)
    access_effects = {name: _effect(panel, conversion, panel.access_group == name) for name in ("limited", "standard")}
    access = access_gap({name: result["effect"] for name, result in access_effects.items()})
    assignment = assignment_checks(panel)

    guardrails = [
        {"name": "Pickup time", "passed": pickup["ci_high"] < 0, "value": pickup["effect"], "threshold": "95% CI below 0"},
        {"name": "Driver earnings", "passed": earnings["ci_low"] > 0, "value": earnings["effect"], "threshold": "95% CI above 0"},
        {"name": "Cancellation rate", "passed": cancellation["ci_high"] < 0, "value": cancellation["effect"], "threshold": "95% CI below 0"},
        {"name": "Access gap", "passed": access["passed"], "value": access["gap"], "threshold": "> -2.5 pp"},
    ]
    failed = [item for item in guardrails if not item["passed"]]
    if completion["ci_low"] > 0 and not failed and assignment["passed"]:
        decision = "SCALE IN PHASES"
    elif completion["ci_high"] <= 0 or len(failed) >= 2:
        decision = "HOLD"
    else:
        decision = "ITERATE"
    rollout = recommend_rollout(panel.zone, panel.demand_pressure, panel.access_group, completion["effect"], completion["standard_error"])
    hourly = []
    for hour in range(24):
        mask = panel.hour % 24 == hour
        hourly.append({"hour": hour, "control": float(np.mean(conversion[mask & ~panel.treatment])), "treatment": float(np.mean(conversion[mask & panel.treatment]))})
    return {
        "experiment": {"name": "Adaptive Matching Policy", "zones": zones, "days": 28, "observations": len(panel.zone), "design": "Four-hour zone switchback"},
        "decision": {"status": decision, "summary": f"Completed-trip conversion changed {completion['relative_effect']:+.1%} while pickup time changed {pickup['effect']:+.2f} minutes.", "next_action": "Expand gradually in the highest-scoring zones and keep switchback holdouts active."},
        "assignment": assignment,
        "metrics": {"completion": completion, "pickup_minutes": pickup, "driver_utilization": utilization, "driver_earnings": earnings, "cancellation_rate": cancellation, "contribution": contribution},
        "guardrails": guardrails,
        "demand_segments": demand_segments,
        "access": {"effects": access_effects, **access},
        "rollout": [asdict(row) for row in rollout],
        "hourly": hourly,
    }

