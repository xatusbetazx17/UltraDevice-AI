from __future__ import annotations
from typing import Dict

def battery_wh_for_runtime(target_hours: float, avg_load_w: float, harvest_w: float, eff_out: float = 0.9) -> float:
    net = max(avg_load_w/eff_out - harvest_w, 0.0)
    return target_hours * net

def battery_mass_kg(wh: float, energy_density_wh_per_kg: float = 240.0) -> float:
    if energy_density_wh_per_kg <= 0:
        energy_density_wh_per_kg = 240.0
    return wh / energy_density_wh_per_kg

def size_pack(target_hours: float, avg_load_w: float, harvest_w: float) -> Dict[str, float]:
    wh = battery_wh_for_runtime(target_hours, avg_load_w, harvest_w)
    mass = battery_mass_kg(wh)
    return {"battery_wh": round(wh,2), "approx_mass_kg": round(mass,3)}
