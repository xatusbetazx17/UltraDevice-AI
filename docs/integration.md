# Integration guide for developers and manufacturers

## Reproduce the reference

1. Clone `codex/working-device-reference` and record the exact commit.
2. Install the Python package and run the desktop demo, tests and scenario report.
3. Build the [USB Pico assembly](../hardware/README.md); retain a physical acceptance record.
4. Compare its actual sensor readings and power measurements with your proposed budget.
5. Introduce one peripheral at a time and repeat disconnect, missing-sensor and shutdown tests.

The core package depends only on Pydantic. Plotting and Windows serial support use
optional extras. Linux/macOS serial uses a bounded standard-library TTY implementation.
The original MIT notice is preserved. Third-party dependencies, the MicroPython
runtime and purchased modules retain their own licenses/documentation.

## Software interfaces

A device adapter provides:

```python
sample() -> ultradevice.controller.Reading
set_mode(mode: str) -> str  # actual acknowledged mode
close() -> None
```

The host loop accepts this interface in `ultradevice.device.run_session`. A controller
can be embedded separately using `DeviceController.step(reading, monotonic_seconds)`.
Use one instance per device session. Do not replace measured SoC with a guessed value
just to enable boost. Schema exports are in `schemas/` and can be regenerated using
`ultradevice schema --kind reading --out FILE` (also `scenario` and `controller`).

Connect real power monitors, fuel gauges and peripheral drivers through an adapter.
Keep on-device maximum current, temperature and run-time enforcement independent of
the host. Host `radio_duty`/`ui_duty` currently describe desired budgets; integrations
must implement and confirm the corresponding physical behavior.

`examples/controller.json` contains host limits. The host can be configured more
conservatively. The Pico's separate hardcoded demo limits remain authoritative and
cannot be relaxed over USB. A custom board needs reviewed limits matched to its
components; this reference is not a safety-critical controller.

## Physical product work still required

| Area | Deliverable before a product claim |
| --- | --- |
| Electrical | Reviewed schematic, exact BOM, PCB layout, power rails and connector definitions |
| Portable power | Selected protected pack, compatible charge circuit, fuel gauge, independently enforced current and temperature limits |
| Harvesting | Selected solar/kinetic/thermal modules, power-path design and measured net output |
| Mechanical | Dimensioned enclosure, mounting, cable strain relief, material and surface-temperature evaluation |
| Sensors | Calibration, sampling/freshness limits, fault detection, placement and environmental testing |
| Compute and AI | Selected SoC and runtime, trained model(s), measured accuracy, inference latency and power |
| Wireless | Selected radio stack, pairing, authenticated protocol and verified delivery behavior |
| Security | Threat model, signed updates, rollback policy, key lifecycle and appropriate hardware root of trust |
| Manufacturing | Test fixtures, serial/lot traceability, assembly instructions, quality checks and support/recovery plan |

No PCB Gerbers, certified enclosure, battery schematic, trained AI model, radio stack
or production secure boot image are supplied. Those require specific physical design
choices and measured validation, and cannot be certified from this chat or simulator.

## Release workflow

Run tests, package the source/wheel, verify the firmware manifest, then retain measured
acceptance evidence with the exact commit. The GitHub workflow defines Linux, Windows
and macOS checks for Python 3.10/3.12; examine its actual results before asserting that
a particular release passed that matrix. Do not merge generated claims of hardware
success without lab records. [Validation](validation.md) records the current evidence.
