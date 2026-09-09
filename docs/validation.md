# Validation record — 2026-09-09

Baseline: main commit `0abd854d1c0c64236ed9353244846018f0683fed`.
Environment: Linux, CPython 3.12.14. No Pico, battery, harvester or sensor was connected.

## Software evidence

- Ruff checks and Python syntax compilation passed.
- **66 automated tests passed**, using `python -m unittest discover -s tests -v`.
- Battery, sizing, schema and thermal tests preserve original main-branch coverage
  and add current limits, stable RC behavior, invalid-input rejection and feasibility.
- Simulation tests verify exact one-shot/fractional-duration boosts, charging,
  depleted-load behavior, disabled features, partial intervals and storage conservation.
- Controller and firmware-policy tests cover cooldowns, stale/replayed samples,
  unknown battery state, fault latching, temperature hysteresis and stop overrides.
- Host/firmware integration tests exchange the real firmware service's JSON messages;
  Linux pseudo-terminal tests exercise actual TTY framing and fragmented responses.
- CLI tests exercise commands from outside the repository and plain output filenames,
  schema export, reports, plots, invalid inputs and module-entry-point aliases.
- The virtual demo traverses normal, boost, conserve and stealth, verifies its log,
  and finishes with a shutdown acknowledgment.

The Python wheel and source distribution are built locally. The wheel is additionally
installed into an isolated virtual environment (using available dependencies) and
smoked from an unrelated working directory. Bundled profile loading is checked there.
Firmware files are syntax-compiled under CPython and hashed in
`hardware/firmware-manifest.json`; MicroPython machine/USB operations still need a board test.

## Main-branch defects corrected

The original package files lived directly under `src/`, while its entry point imported
`ultradevice`; tests also lived under `test/` while configuration selected `tests/`.
The CLI's module-entry call preceded several command definitions. These prevented the
documented execution paths from working reliably.

Boost energy was applied repeatedly throughout its hour; the physics wrapper then
lost that boost accounting and skipped the first interval. Surplus harvesting could
not recharge storage. Disabled radio/UI features could be subtracted from load anyway.
Empty batteries still appeared to deliver power, current clamping did not limit actual
energy draw, the thermal Euler equation was unstable, and reports omitted the first
interval. These behaviors now have regression coverage.

The old ZIP-import scripts could replace repository contents and push the default
branch. They have been retired; use normal clone/build/feature-branch workflows.

## Evidence still missing

- Physical Pico execution, MicroPython USB timing and sensor calibration.
- Actual current, runtime, harvesting efficiency or wearable surface temperatures.
- PCB, enclosure, battery pack, reliability and manufacturing verification.
- Radio/mesh, trained AI, vision, voice, secure boot or signed-update validation;
  those features are not implemented.
- Docker and MkDocs recipes have not been executed in this environment.
- GitHub CI results are separate from local test results; check the workflow's actual
  runs for Windows, macOS and alternate Python versions before claiming they passed.

Use the physical acceptance template for hardware evidence. **Software test success
is not a certificate that the original futuristic device exists or is safe to wear.**
