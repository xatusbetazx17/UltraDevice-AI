# UltraDevice AI — working reference prototype

**Author: Marcelo Collado · MIT license · Python 3.10+**

UltraDevice AI turns the energy management and mode-control ideas on `main` into
an installable simulator, a desktop device demo, and source code for a Raspberry Pi
Pico bench prototype. The original inspiration is a futuristic multi-form wearable.

**This is a software-tested engineering reference, not a finished wearable product.**
Physical transformation, optical camouflage, self-repairing materials and an unlimited
energy source are not implemented. No physical board was available for validation.
See the [capability matrix](docs/capabilities.md) for every original requirement and
its actual implementation status.

## Start without hardware

```bash
git clone --branch codex/working-device-reference https://github.com/xatusbetazx17/UltraDevice-AI.git
cd UltraDevice-AI
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
ultradevice doctor
ultradevice demo --seconds 95 --out outputs/demo.jsonl
ultradevice check-log --input outputs/demo.jsonl
```

The demo runs 95 **virtual** seconds immediately. It exercises normal operation,
a startup cooldown, a ten-second boost, cooldown rejection, stealth and shutdown.
All demo sensor values are labeled `simulated`. Logs remain local.

## Simulate a proposed design

```bash
ultradevice validate-scenario --scenario examples/scenarios/day_walk.json
ultradevice simulate-physics --scenario examples/scenarios/day_walk.json --out outputs/day.csv
ultradevice report --csv outputs/day.csv --out outputs/day.md
python -m pip install '.[plot]'
ultradevice plot --csv outputs/day.csv --out outputs/day.png
```

Plots are `day_soc.png`, `day_load.png`, and `day_harvest.png`. The original scenario
has illustrative high loads: **it does not demonstrate all-day operation**. Reports
show unserved energy when depletion, current limits or heat reduce delivered power.
Use [the low-power example](examples/scenarios/bench_reference.json) as an editable
budget, then replace assumptions with measured data. Relative CSV paths are resolved
beside the scenario; `data/*.csv` sample profiles also ship inside the Python wheel.

## Connect a real prototype

Follow the [parts, wiring and firmware guide](hardware/README.md). The implemented
hardware target is the original **RP2040 Pico/Pico H, non-W**, powered through USB.
It measures chip temperature (or an optional TMP117 sensor) and controls the onboard
LED to demonstrate modes. It does not drive heaters, motors or biological hardware.

```bash
ultradevice device --port /dev/ttyACM0 --seconds 60 --out outputs/device.jsonl
# Windows: use the board's COM port, and first install .[hardware].
```

The board has no fuel gauge or power monitor in the baseline assembly. It reports
`battery_soc`, `load_w` and `harvest_w` as `null`; the host conserves power and refuses
boost with unknown battery state. Predictions require actual measurements.

## Included

- Correct package layout, command-line interface, wheel packaging and offline demo.
- Validated scenarios; solar, motion, ambient, cloud, external and thermal-harvest inputs.
- Recharge, finite storage, discharge-rate limits, exact boost timing and cooldowns.
- Stable thermal RC integration, losses, interval telemetry and energy reports.
- Host mode controller with hysteresis, sample freshness checks and latched faults.
- Bounded USB protocol, Pico firmware, watchdog, stop-button input and TMP117 driver.
- Local power-history predictor; no trained model, cloud service or API key required.
- Hash-linked logs, JSON schemas, tests, CI configuration and integration documentation.

```bash
python -m pip install -e '.[dev,plot]'
python -m unittest discover -s tests -v
python -m build
```

`python -m ultradevice` and `ultradevice` expose the same commands. Historical command
names such as `simulate_physics`, `size_battery` and `validate_scenario` remain aliases.

## For builders and companies

The original [MIT license](LICENSE) is retained, including permission to use, modify
and distribute the code with its notices. Start with the [integration guide](docs/integration.md),
[protocol](docs/protocol.md), [model assumptions](docs/models.md) and
[validation record](docs/validation.md). The [remaining work](docs/roadmap.md) covers
physical validation and product engineering. Software test success does not certify
battery safety, skin-contact temperatures, radio behavior or a manufactured device.

[Español](README.es.md) · [CLI examples](examples/usage_cli.md) · [Contributing](CONTRIBUTING.md)
