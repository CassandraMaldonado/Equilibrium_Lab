# Checks before making a recommendation.

import numpy as np
from .simulation import MarketplacePanel

def assignment_checks(panel: MarketplacePanel) -> dict:
    share = float(np.mean(panel.treatment))
    by_zone = [float(np.mean(panel.treatment[panel.zone == z])) for z in np.unique(panel.zone)]
    first_week = panel.hour < 7 * 24
    early_gap = float(np.mean(panel.requests[first_week & panel.treatment]) - np.mean(panel.requests[first_week & ~panel.treatment]))
    return {
        "treatment_share": share,
        "max_zone_imbalance": float(max(abs(value - 0.5) for value in by_zone)),
        "early_request_gap": early_gap,
        "passed": abs(share - 0.5) < 0.02 and max(abs(value - 0.5) for value in by_zone) < 0.03,
    }


def access_gap(effect_by_group: dict[str, float]) -> dict:
    limited = effect_by_group["limited"]
    standard = effect_by_group["standard"]
    gap = limited - standard
    return {"limited_effect": limited, "standard_effect": standard, "gap": gap, "passed": gap > -0.025}
