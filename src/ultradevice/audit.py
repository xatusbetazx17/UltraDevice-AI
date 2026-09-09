"""Local hash-linked JSONL logs. Detect edits; not authenticated or immutable."""
import hashlib
import json
from pathlib import Path


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


class AuditLog:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file = path.open("w", encoding="utf-8")
        self.previous = "0" * 64
        self.index = 0

    def append(self, kind, data):
        record = {"index": self.index, "previous": self.previous, "kind": kind, "data": data}
        record["sha256"] = _hash(record)
        self.file.write(json.dumps(record, allow_nan=False) + "\n")
        self.file.flush()
        self.previous = record["sha256"]
        self.index += 1

    def close(self):
        self.file.close()


def verify_log(path):
    previous = "0" * 64
    count = 0
    with open(path, encoding="utf-8") as file:
        for count, line in enumerate(file, 1):
            record = json.loads(line)
            digest = record.pop("sha256")
            if record["index"] != count - 1 or record["previous"] != previous or _hash(record) != digest:
                raise ValueError(f"Audit chain mismatch at line {count}")
            previous = digest
    if not count:
        raise ValueError("Empty audit log")
    return {"records": count, "head_sha256": previous}
