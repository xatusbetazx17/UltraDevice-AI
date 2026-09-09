from .powertrain import effective_net_draw
from .validation import number


def battery_wh_for_runtime(target_hours, avg_load_w, harvest_w, eff_out=0.9, eff_harv=0.8):
    number("target_hours", target_hours, positive=True)
    return target_hours * effective_net_draw(avg_load_w, harvest_w, eff_out, eff_harv)


def battery_mass_kg(wh, energy_density_wh_per_kg=240.0):
    number("wh", wh)
    number("energy_density_wh_per_kg", energy_density_wh_per_kg, positive=True)
    return wh / energy_density_wh_per_kg


def size_pack(target_hours, avg_load_w, harvest_w):
    wh = battery_wh_for_runtime(target_hours, avg_load_w, harvest_w)
    return {"battery_wh": round(wh, 2), "approx_mass_kg": round(battery_mass_kg(wh), 3)}
