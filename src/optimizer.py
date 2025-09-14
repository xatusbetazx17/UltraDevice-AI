from __future__ import annotations
from typing import Dict, Any

def optimize_duty(target_hours: float, battery_wh: float, P_hi: float, P_lo: float, harvest_w: float) -> Dict[str, Any]:
    # Greedy solve for a single uniform duty fraction across the day
    denom_hi = max(P_hi - harvest_w, 1e-9)
    denom_lo = max(P_lo - harvest_w, 1e-9)
    X = battery_wh / max(target_hours, 1e-9)
    f = (X - denom_lo) / max(denom_hi - denom_lo, 1e-9)
    f = max(0.0, min(1.0, f))
    # Build a trivial schedule with this duty across hours
    schedule = {str(h): f for h in range(24)}
    return {"duty_fraction": f, "schedule": schedule}
