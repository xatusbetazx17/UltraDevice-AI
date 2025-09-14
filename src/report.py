from __future__ import annotations
import csv
from typing import Dict, Any

def summarize(csv_path: str) -> Dict[str, Any]:
    n = 0
    min_soc = 1.0
    max_soc = 0.0
    e_load = 0.0
    e_harv = 0.0
    last_min = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
    for i, row in enumerate(rows):
        t_min = int(row["t_min"])
        soc = float(row["soc"])
        load = float(row["load_w"])
        harv = float(row["harvest_w"])
        if i > 0:
            dt_h = (t_min - last_min)/60.0
            e_load += load*dt_h
            e_harv += harv*dt_h
        last_min = t_min
        min_soc = min(min_soc, soc)
        max_soc = max(max_soc, soc)
        n += 1
    return {
        "samples": n,
        "min_soc": round(min_soc,4),
        "max_soc": round(max_soc,4),
        "energy_load_Wh": round(e_load,3),
        "energy_harvest_Wh": round(e_harv,3),
        "net_Wh": round(e_load - e_harv,3),
        "hours": round(last_min/60.0,2)
    }

def write_markdown(summary: Dict[str, Any], out_md: str):
    md = f"""# Simulation Report
- Samples: {summary['samples']}
- Duration (h): {summary['hours']}
- Min SoC: {summary['min_soc']}
- Max SoC: {summary['max_soc']}
- Load energy (Wh): {summary['energy_load_Wh']}
- Harvest energy (Wh): {summary['energy_harvest_Wh']}
- Net energy (Wh): {summary['net_Wh']}
"""
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
