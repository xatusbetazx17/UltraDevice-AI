from __future__ import annotations
from .config import Scenario

def validate_scenario(scn: Scenario) -> list[str]:
    errs = []
    if scn.battery_wh <= 0: errs.append("battery_wh must be > 0")
    if scn.base_load_w < 0: errs.append("base_load_w must be >= 0")
    if scn.dt_minutes <= 0 or scn.dt_minutes > 60: errs.append("dt_minutes must be in 1..60")
    for k, f in scn.features.items():
        if f.w < 0: errs.append(f"feature {k} has negative power")
    return errs
