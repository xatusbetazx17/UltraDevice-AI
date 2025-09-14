from .models import PowerProfile

def net_power_w(profile: PowerProfile) -> float:
    return max(profile.avg_load_w - profile.harvest_w, 0.0)

def ideal_runtime_hours(profile: PowerProfile) -> float:
    p = net_power_w(profile)
    if p == 0:
        return float('inf')
    return profile.battery_wh / p

def reserve_boost(battery_wh: float, burst_w: float, burst_sec: float) -> float:
    # energy used in Wh = W * s / 3600
    return max(battery_wh - (burst_w * burst_sec / 3600.0), 0.0)

def duty_fraction_for_target(battery_wh: float, P_hi: float, P_lo: float, P_h: float, target_hours: float) -> float:
    # Solve B / ( f*(P_hi-P_h) + (1-f)*(P_lo-P_h) ) = T*
    denom_hi = max(P_hi - P_h, 1e-9)
    denom_lo = max(P_lo - P_h, 1e-9)
    X = battery_wh / max(target_hours, 1e-9)
    f = (X - denom_lo) / max(denom_hi - denom_lo, 1e-9)
    return max(0.0, min(1.0, f))
