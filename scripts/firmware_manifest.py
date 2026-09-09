"""Create or check firmware source hashes; these are not signatures or secure boot."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "hardware" / "firmware-manifest.json"


def manifest():
    paths = sorted((ROOT / "firmware" / "pico").glob("*.py"))
    return {
        "format_version": 1,
        "target": "Raspberry Pi Pico/Pico H RP2040 non-W",
        "hardware_validation": "not executed",
        "micropython_version": "must be recorded by the physical builder",
        "integrity_only": True,
        "files": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = manifest()
    if args.check:
        if not TARGET.exists() or json.loads(TARGET.read_text()) != expected:
            raise SystemExit("Firmware manifest mismatch; regenerate after reviewing changes")
        print("Firmware source hashes match; physical operation still requires validation")
    else:
        TARGET.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
        print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
