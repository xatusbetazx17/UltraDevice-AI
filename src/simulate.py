from __future__ import annotations
from typing import List, Dict, Any
from .config import Scenario
from .profiles import load_hourly_csv
from .policy import PolicyEngine
from .power import reserve_boost

def _interp_hourly(hourly, hour):
    for h, v in hourly:
        if h == hour:
            return v
    return 0.0

def simulate(scn: Scenario) -> List[Dict[str, Any]]:
    # Load profiles
    solar_hourly = load_hourly_csv(scn.harvest.solar.irradiance_csv) if scn.harvest.solar else []
    motion_hourly = load_hourly_csv(scn.harvest.kinetic.motion_csv) if scn.harvest.kinetic else []

    # Pre-index boosts by hour
    boost_by_hour = {}
    for b in scn.boosts:
        boost_by_hour.setdefault(b.hour, []).append(b)

    soc_wh = scn.battery_wh
    soc_max = scn.battery_wh
    t = 0
    results: List[Dict[str, Any]] = []
    policy = PolicyEngine()

    for hour in range(24):
        for m in range(0, 60, scn.dt_minutes):
            # Harvest
            solar_w = (_interp_hourly(solar_hourly, hour) * scn.harvest.solar.scale) if scn.harvest.solar else 0.0
            kinetic_w = (_interp_hourly(motion_hourly, hour) * scn.harvest.kinetic.scale) if scn.harvest.kinetic else 0.0
            harvest_w = solar_w + kinetic_w

            # Features + policy
            features_w = sum(f.w for f in scn.features.values() if f.on)
            soc = soc_wh / soc_max if soc_max > 0 else 0.0
            pol = policy.decide(soc)
            if "radio" in scn.features:
                features_w -= scn.features["radio"].w * (1 - pol["radio_duty"])
            if "ui" in scn.features:
                features_w -= scn.features["ui"].w * (1 - pol["ui_duty"])

            load_w = scn.base_load_w + features_w

            # Burst boost at this hour if allowed
            if hour in boost_by_hour and pol["allow_boost"]:
                for b in boost_by_hour[hour]:
                    step_sec = scn.dt_minutes * 60
                    soc_wh = reserve_boost(soc_wh, b.burst_w, min(b.burst_sec, step_sec))

            # Net energy for this step
            net_w = max(load_w - harvest_w, 0.0)
            step_h = scn.dt_minutes / 60.0
            soc_wh = max(0.0, min(soc_max, soc_wh - net_w * step_h))

            results.append({
                "t_min": t,
                "hour": hour,
                "minute": m,
                "load_w": round(load_w, 3),
                "harvest_w": round(harvest_w, 3),
                "soc_wh": round(soc_wh, 3),
                "soc": round(soc_wh / soc_max if soc_max>0 else 0.0, 4),
            })
            t += scn.dt_minutes
    return results


# Thermal and battery-aware simulate wrapper
from .battery import Battery
from .thermal import ThermalModel

def simulate_physics(scn, battery: Battery | None = None, thermal: ThermalModel | None = None):
    rows = simulate(scn)
    if battery is None and thermal is None:
        return rows

    # Re-apply physics step using rows' load & harvest; overwrite SoC using battery model;
    # apply thermal derate by scaling load when hot.
    soc_max = scn.battery_wh if battery is None else battery.capacity_wh
    soc_wh = soc_max
    t_prev = 0
    t_c = thermal.t_ambient_c if thermal else 25.0
    out = []
    for r in rows:
        dt_h = (r["t_min"] - t_prev)/60.0
        t_prev = r["t_min"]
        load = r["load_w"]
        harv = r["harvest_w"]

        # Thermal derate
        if thermal:
            der = thermal.derate_factor(t_c)
            load = load * der
            t_c = thermal.step(t_c, load, dt_h)

        net_w = max(load - harv, 0.0)
        if battery:
            soc_wh = battery.step_discharge(soc_wh, net_w, dt_h)
        else:
            soc_wh = max(0.0, soc_wh - net_w*dt_h)

        r2 = dict(r)
        r2["load_w"] = round(load,3)
        r2["soc_wh"] = round(soc_wh,3)
        r2["soc"] = round(soc_wh/soc_max if soc_max>0 else 0.0,4)
        r2["temp_c"] = round(t_c,2)
        out.append(r2)
    return out
