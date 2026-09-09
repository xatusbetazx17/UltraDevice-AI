"""One-pass simulator with 1-second integration and interval-average telemetry."""
from .battery import Battery
from .policy import PolicyEngine
from .profiles import load_hourly_csv
from .thermal import ThermalModel
from .validate import validate_scenario


def _profile(path, default, minimum=0, maximum=None):
    return dict(load_hourly_csv(path, minimum=minimum, maximum=maximum)) if path else {h: default for h in range(24)}


def simulate(scn):
    return _run(scn, None, None)


def simulate_physics(scn, battery=None, thermal=None):
    battery = battery or Battery(scn.battery_wh)
    thermal = thermal or ThermalModel(t_ambient_c=scn.ambient_c)
    return _run(scn, battery, thermal)


def _run(scn, battery, thermal):
    errors = validate_scenario(scn)
    if errors:
        raise ValueError("; ".join(errors))
    solar_cfg, kinetic_cfg = scn.harvest.solar, scn.harvest.kinetic
    solar = _profile(solar_cfg.irradiance_csv if solar_cfg else None, 0)
    motion = _profile(kinetic_cfg.motion_csv if kinetic_cfg else None, 0)
    clouds = _profile(scn.cloudiness_csv, 1, 0, 1)
    ambient = _profile(scn.ambient_csv, scn.ambient_c, -40, 85)
    events = sorted(scn.boosts, key=lambda b: b.start_s)
    capacity = battery.capacity_wh if battery else scn.battery_wh
    energy = capacity * scn.initial_soc
    eff_out, eff_harv = (scn.eff_out, scn.eff_harv) if battery else (1.0, 1.0)
    temperature = ambient[0]
    engine = PolicyEngine()
    time_s = 0.0
    event_index = 0
    active_boost = None
    rows = []
    horizon = scn.duration_minutes * 60
    for output_start in range(0, horizon, scn.dt_minutes * 60):
        output_end = min(output_start + scn.dt_minutes * 60, horizon)
        seconds = output_end - output_start
        initial_energy = energy
        totals = {k: 0.0 for k in ("load", "requested", "harvest", "boost", "draw", "charge", "spill")}
        accepted = blocked = 0
        max_temperature = temperature
        while time_s < output_end:
            hour = min(23, int(time_s // 3600))
            soc = energy / capacity
            policy = engine.decide(soc)
            derate = thermal.derate_factor(temperature) if thermal else 1.0
            if active_boost and time_s >= active_boost.start_s + active_boost.burst_sec:
                active_boost = None
            if event_index < len(events) and time_s >= events[event_index].start_s:
                event = events[event_index]
                event_index += 1
                if soc > scn.reserve_soc and derate >= 1:
                    active_boost = event
                    accepted += 1
                else:
                    blocked += 1
            if soc <= scn.reserve_soc or derate < 1:
                active_boost = None
            stop = min(time_s + 1, output_end, (hour + 1) * 3600)
            if active_boost:
                stop = min(stop, active_boost.start_s + active_boost.burst_sec)
            if event_index < len(events):
                stop = min(stop, events[event_index].start_s)
            dt_h = (stop - time_s) / 3600
            harvest = (solar[hour] * solar_cfg.scale * clouds[hour] if solar_cfg else 0)
            harvest += motion[hour] * kinetic_cfg.scale if kinetic_cfg else 0
            harvest += scn.harvest.thermal_w + scn.harvest.external_w
            features = sum(f.w * policy.get(name + "_duty", 1) for name, f in scn.features.items() if f.on)
            boost = active_boost.burst_w if active_boost else 0.0
            requested = scn.base_load_w + features + boost
            # Derating and depleted storage must reduce delivered energy, not merely SoC.
            demand = requested * derate
            harvested_bus = harvest * eff_harv
            terminal_need = max(0.0, demand / eff_out - harvested_bus)
            terminal_cap = min(terminal_need, battery.max_power_w) if battery else terminal_need
            factor = battery.discharge_factor(terminal_cap) if battery else 1.0
            terminal_cap = min(terminal_cap, energy / (dt_h * factor))
            delivered = min(demand, (harvested_bus + terminal_cap) * eff_out)
            net = delivered / eff_out - harvested_bus
            before = energy
            if net > 0:
                energy = battery.step_discharge(energy, net, dt_h) if battery else max(0, energy - net * dt_h)
                totals["draw"] += before - energy
                chemical_loss = max(0, (before - energy) / dt_h - net)
                spill = 0.0
            else:
                energy = battery.step_charge(energy, -net, dt_h) if battery else min(capacity, energy - net * dt_h)
                totals["charge"] += energy - before
                charge_eff = battery.coulombic_eff if battery else 1.0
                accepted_charge = (energy - before) / (dt_h * charge_eff)
                spill = max(0, -net - accepted_charge)
                chemical_loss = accepted_charge * (1 - charge_eff)
            if thermal:
                # All delivered load and conversion/chemical loss heat this one lump.
                heat = delivered / eff_out + chemical_loss + harvest * (1 - eff_harv)
                temperature = thermal.step(temperature, heat, dt_h, ambient[hour])
                max_temperature = max(max_temperature, temperature)
            totals["load"] += delivered * dt_h
            totals["requested"] += requested * dt_h
            totals["harvest"] += harvest * dt_h
            totals["boost"] += boost * dt_h
            totals["spill"] += spill * dt_h
            time_s = stop
        hours = seconds / 3600
        row = {
            "t_min": output_start / 60,
            "dt_min": seconds / 60,
            "hour": output_start // 3600,
            "minute": (output_start % 3600) // 60,
            "initial_soc_wh": initial_energy,
            "load_w": totals["load"] / hours,
            "requested_load_w": totals["requested"] / hours,
            "unserved_w": max(0, totals["requested"] - totals["load"]) / hours,
            "harvest_w": totals["harvest"] / hours,
            "boost_w": totals["boost"] / hours,
            "battery_draw_wh": totals["draw"],
            "battery_charge_wh": totals["charge"],
            "spilled_wh": totals["spill"],
            "soc_wh": energy,
            "soc": energy / capacity,
            "boosts_accepted": accepted,
            "boosts_blocked": blocked,
        }
        if thermal:
            row.update(temp_c=temperature, max_temp_c=max_temperature)
        rows.append(row)
    return rows
