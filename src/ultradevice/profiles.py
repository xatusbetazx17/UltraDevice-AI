import csv
import math
from pathlib import Path


def resolve_profile(path, base=None):
    path = Path(path)
    candidates = [path] if path.is_absolute() else [Path(base or Path.cwd()) / path]
    if not path.is_absolute() and path.parts[:1] == ("data",) and len(path.parts) == 2:
        candidates.append(Path(__file__).parent / path)
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise ValueError(f"Profile not found: {path}; use a path relative to the scenario")


def load_hourly_csv(path, *, minimum=0.0, maximum=None):
    rows = []
    with resolve_profile(path).open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or len(reader.fieldnames) != 2 or reader.fieldnames[0] != "hour":
            raise ValueError(f"{path}: expected hour,value columns")
        for row in reader:
            try:
                hour = int(row["hour"])
                value = float(row[reader.fieldnames[1]])
            except (ValueError, TypeError) as error:
                raise ValueError(f"{path}: invalid profile row") from error
            if not 0 <= hour <= 23 or not math.isfinite(value) or value < minimum:
                raise ValueError(f"{path}: invalid hour or value")
            if maximum is not None and value > maximum:
                raise ValueError(f"{path}: value exceeds {maximum}")
            rows.append((hour, value))
    if sorted(h for h, _ in rows) != list(range(24)):
        raise ValueError(f"{path}: exactly one sample for each hour 0..23 is required")
    return sorted(rows)
