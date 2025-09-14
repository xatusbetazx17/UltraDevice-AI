from __future__ import annotations
import csv
from typing import Iterable, Dict, Any

def write_csv(path: str, rows: Iterable[Dict[str, Any]]):
    rows = list(rows)
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
