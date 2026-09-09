from .power import duty_fraction_for_target


def optimize_duty(target_hours, battery_wh, P_hi, P_lo, harvest_w):
    fraction = duty_fraction_for_target(battery_wh, P_hi, P_lo, harvest_w, target_hours)
    return {
        "model": "ideal constant load/harvest; not a hardware runtime guarantee",
        "duty_fraction": fraction,
        "target_hours": target_hours,
        "average_load_w": fraction * P_hi + (1 - fraction) * P_lo,
        "schedule": {str(h): fraction for h in range(24)},
    }
