from __future__ import annotations
import csv
from pathlib import Path
from typing import List, Tuple

def load_hourly_csv(path: str | Path) -> List[Tuple[int, float]]:
    rows: List[Tuple[int, float]] = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        fieldnames = r.fieldnames or ["hour", "value"]
        if len(fieldnames) < 2:
            raise ValueError("CSV needs at least two columns")
        hour_key, val_key = fieldnames[0], fieldnames[1]
        for row in r:
            rows.append((int(float(row[hour_key])), float(row[val_key])))
    return rows
