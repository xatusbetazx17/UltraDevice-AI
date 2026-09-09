import csv
import math
from pathlib import Path


def summarize(csv_path):
    with open(csv_path, encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows or "dt_min" not in rows[0]:
        raise ValueError("Telemetry must include explicit dt_min intervals; regenerate old CSVs")
    load = harvest = requested = duration = unserved = 0.0
    previous_end = None
    for row in rows:
        time, dt = float(row["t_min"]), float(row["dt_min"])
        values = [time, dt, float(row["load_w"]), float(row["harvest_w"]), float(row["soc"])]
        if not all(math.isfinite(v) for v in values) or dt <= 0 or time < 0:
            raise ValueError("Invalid telemetry interval")
        if previous_end is not None and not math.isclose(time, previous_end):
            raise ValueError("Telemetry intervals must be contiguous")
        previous_end = time + dt
        hours = dt / 60
        duration += hours
        load += float(row["load_w"]) * hours
        harvest += float(row["harvest_w"]) * hours
        requested += float(row.get("requested_load_w", row["load_w"])) * hours
        unserved += float(row.get("unserved_w", 0)) * hours
    result = {
        "samples": len(rows), "hours": duration,
        "min_soc": min(float(row["soc"]) for row in rows),
        "max_soc": max(float(row["soc"]) for row in rows),
        "energy_load_Wh": load, "energy_requested_Wh": requested,
        "energy_harvest_Wh": harvest, "energy_unserved_Wh": unserved,
        "net_Wh": load - harvest,
        "battery_draw_Wh": sum(float(r.get("battery_draw_wh", 0)) for r in rows),
        "battery_charge_Wh": sum(float(r.get("battery_charge_wh", 0)) for r in rows),
    }
    if "max_temp_c" in rows[0]:
        result["peak_temperature_c"] = max(float(row["max_temp_c"]) for row in rows)
    return result


def write_markdown(summary, out_md):
    target = Path(out_md)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Simulation report", "", "Model estimates; hardware measurements are required.", "",
             "| Metric | Value |", "| --- | ---: |"]
    lines += [f"| {key} | {value:.6g} |" for key, value in summary.items()]
    lines += ["", "Load is delivered power; unserved energy exposes depletion, rate limits and thermal derating.",
              "net_Wh is load minus raw harvest; battery draw/charge include modeled losses.", ""]
    target.write_text("\n".join(lines), encoding="utf-8")
