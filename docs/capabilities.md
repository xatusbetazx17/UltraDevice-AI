# Capability matrix against the original main branch

Original baseline: commit `0abd854d1c0c64236ed9353244846018f0683fed`.
This table describes delivered behavior, not predictions about future inventions.

| Original goal | What this branch implements | What remains |
| --- | --- | --- |
| Power budgets, duty and sizing | Validated CLI calculators; infeasible targets fail clearly | Measurements for a selected assembly; pack reserve/mass qualification |
| Solar, kinetic and thermal harvesting | Explicit input powers and CSV profiles, conversion losses, recharge and spill accounting | Actual harvesters, charge controller and measured curves |
| Continuous baseline power | Explicit `external_w` energy input | A specified physical supply; no energy source is invented |
| Battery and thermal behavior | Rate-limited finite storage, empirical losses, stable RC thermal integration | Cell characterization, surface calibration and hardware protection |
| Emergency boost / evolution | Duration, cooldown, battery and thermal checks; LED demo | No physical transformation, tissue change or material stiffening |
| Stealth / camouflage | Reduced model duty; Pico LED off in stealth | No optical camouflage or invisibility |
| Environment sensing | Pico die temperature and optional TMP117 driver | IMU, light, gas, proximity and camera drivers/validation |
| Environment adaptation | Mode changes, thermal derating, load shedding and profile inputs | Mechanical airflow or material actuation |
| Predictive assistant | Bounded local history, ideal runtime forecast, target-driven conserve choice when measurements exist | Trained models, voice/dialog, vision, user-schedule learning and model evaluation |
| Communications | Versioned USB request/response with framing limits, deadlines and acknowledgments | Radio, mesh, BLE, SOS delivery, authentication, pairing and interoperability |
| Security / immutable audit / signed firmware | Local hash-linked telemetry logs, verification, source hashes, strict frame checks | Authenticated/append-only audit, encrypted storage, secure boot, signed updates and key management |
| High-end compute and storage | Host Python package plus small Pico control loop | Selected application SoC, accelerators, TB storage and their drivers/power budgets |
| Wearable materials / self-repair | Requirements retained as concept specifications | Materials engineering and manufacturing; no self-repair implementation |
| DNA sequence storage | Original informational concept retained | No genome database, sequence processing or biological transformation implementation |
| Packaging, tests and automation | Installable wheel/sdist layout, unit/integration tests, GitHub CI definition, Docker recipe | Hardware acceptance; cross-platform/CI/container results must be measured in their environments |

The hardware build controls only its onboard LED. Host `radio_duty` and `ui_duty` are
policy outputs for future adapters; a USB-only Pico does not acquire a radio or display
because those values appear in telemetry. Host polling frequency changes, but the
firmware keeps its local temperature checks at 250 ms for independent shutdown.
