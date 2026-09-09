from .models import PowerProfile
from .validation import number


def net_power_w(profile: PowerProfile):
    return max(profile.avg_load_w - profile.harvest_w, 0.0)


def ideal_runtime_hours(profile: PowerProfile):
    net = net_power_w(profile)
    return profile.battery_wh / net if net else float("inf")


def reserve_boost(battery_wh, burst_w, burst_sec):
    for name, value in (("battery_wh", battery_wh), ("burst_w", burst_w), ("burst_sec", burst_sec)):
        number(name, value)
    return max(battery_wh - burst_w * burst_sec / 3600.0, 0.0)


def duty_fraction_for_target(battery_wh, P_hi, P_lo, P_h, target_hours):
    for name, value in (("battery_wh", battery_wh), ("P_hi", P_hi), ("P_lo", P_lo), ("P_h", P_h)):
        number(name, value)
    number("target_hours", target_hours, positive=True)
    if P_hi < P_lo:
        raise ValueError("P_hi must be >= P_lo")
    budget = battery_wh / target_hours + P_h
    if budget < P_lo:
        raise ValueError("Target is infeasible even at the low-power load")
    if P_hi == P_lo:
        return 1.0
    return min(1.0, max(0.0, (budget - P_lo) / (P_hi - P_lo)))
