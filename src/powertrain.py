from __future__ import annotations

def effective_net_draw(load_w: float, harvest_w: float,
                       eff_out: float = 0.90, eff_harv: float = 0.80) -> float:
    """Compute battery net draw with DC/DC efficiencies.
    - eff_out applies to battery power delivered to load.
    - eff_harv applies to harvested power before offsetting the load.
    Battery draw P_batt = max( load/eff_out - harvest*eff_harv, 0 ).
    """
    load_from_batt = load_w / max(eff_out, 1e-6)
    harvest_effective = harvest_w * eff_harv
    return max(load_from_batt - harvest_effective, 0.0)
