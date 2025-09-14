# 🧠 UltraDevice AI — Concept & Tiny Simulator

![CI](https://github.com/xatusbetazx17/UltraDevice-AI/actions/workflows/ci.yml/badge.svg)

<p align='center'><img src='assets/logo.svg' width='520' alt='UltraDevice AI logo'/></p>

**Author:** Marcelo Collado (GitHub: [@xatusbetazx17](https://github.com/xatusbetazx17))  
**License:** MIT  
**Status:** Fictional R&D concept with a small Python simulator for power & thermal-adjacent budgets.

## 📖 Overview
UltraDevice AI is a **futuristic wearable** inspired by multi‑form devices (Omnitrix‑style), turned into something **engineering‑grounded**:

- Hybrid power: safe, compact baseline + **environmental harvesting** (solar/kinetic/thermal).
- Bio‑inspired compute (concept) → implemented as **policies & constraints** (no biology here).
- Robust materials (concept) → documented in specs; simulator models **power trade‑offs**.
- Intelligence: **predictive/policy AI**, environment sensing toggles, learning profile.
- Modes: **stealth/camouflage** (mode flag), **emergency boost** (short bursts + cooldown), **reserve** power.
- Comms (concept) → modeled as power toggles (radio duty).
- Constraints: needs **recharge cycles**; boosts limited; **safety‑first** guardrails.

> ⚠️ **This repo is safe**: code models power/harvest/duty only. No hazardous, genetic, or nuclear instructions.

---

## 📂 Structure
```
UltraDevice-AI/
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── Makefile
├── Dockerfile
├── docs/ … narrative docs
├── specs/ … technical specs (power budget math, sensors, policies, etc.)
├── data/ … simple hourly irradiance & motion profiles
├── examples/
│   └── scenarios/ … scenario JSONs for simulator
├── src/ultradevice/ … simulator & CLI
├── tests/ … unit tests
└── .github/ … CI & templates
```

---

## 🧪 Tiny Simulator (CLI)

### Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Usage
```bash
# Help
ultradevice --help

# Quick budgets
ultradevice runtime --battery-wh 12 --avg-load-w 2.8 --solar-w 0.6 --kinetic-w 0.2
ultradevice boost --battery-wh 12 --burst-w 10 --burst-sec 60
ultradevice duty --battery-wh 12 --avg-load-w 3.0 --target-hours 8

# Time-series simulation + plots
ultradevice simulate --scenario examples/scenarios/day_walk.json --out outputs/day_walk.csv
ultradevice plot --csv outputs/day_walk.csv --out outputs/day_walk.png
```

You’ll get:
- `outputs/day_walk.csv` (telemetry)
- `outputs/day_walk_soc.png`, `outputs/day_walk_load.png`, `outputs/day_walk_harvest.png`

---

## 🎯 Realism upgrades
- **Time-series simulator** (5‑min steps) with base load, features, **harvest** and **policy** decisions
- **Scenario JSONs** so you can vary loads/features/boosts without editing code
- **Rule-based policy** reduces radio/UI duty when battery is low; blocks boosts at very low SoC
- **CSV telemetry** + **Matplotlib plots** (SoC, Load, Harvest)
- **CI, Dependabot, templates, Devcontainer, Dockerfile**
- **Spanish README** (`README.es.md`) & simple **logo**

> Note: Real wearables usually harvest **milliwatts**; values here are illustrative for demos.

---

## 🧭 Roadmap
- Thermal limit curve & heat‑driven derating
- Randomized weather/light/activity generators
- Sensor‑fusion policy experiments
- Jupyter demo notebook

---

## 🙏 Credits
Concept: **Marcelo Collado** ([@xatusbetazx17](https://github.com/xatusbetazx17)) + ChatGPT  
License: MIT


---

## 🔬 Physics mode (battery + thermal)
Run the simulator with simple **battery** and **thermal** models:
```bash
ultradevice simulate_physics --scenario examples/scenarios/day_walk.json --out outputs/sim_physics.csv
ultradevice report --csv outputs/sim_physics.csv --out outputs/report.md
ultradevice plot --csv outputs/sim_physics.csv --out outputs/plot.png
```

## 🧮 Optimizer
Suggest a uniform high-power duty cycle to hit a target runtime:
```bash
ultradevice optimize --battery-wh 12 --P_hi 6 --P_lo 1.2 --harvest-w 0.5 --target-hours 8 --out outputs/optimized.json
```


---

## 🧰 Engineering utilities
- **Battery sizing:** estimate required Wh & mass for a target runtime.
  ```bash
  ultradevice size_battery --target-hours 8 --avg-load-w 3.0 --harvest-w 0.5
  ```
- **Scenario validator:** ensure JSON is sane.
  ```bash
  ultradevice validate_scenario --scenario examples/scenarios/day_walk.json
  ```
- **Random scenario generator:** create a new scenario to stress-test.
  ```bash
  ultradevice randomize --out examples/scenarios/random_day.json --seed 42
  ```
- **Ambient & clouds:** simulator reads `data/ambient_summer.csv` and `data/cloudiness.csv` to adjust thermal & solar.
- **Powertrain efficiencies:** battery sees `load/eff_out - harvest*eff_harv` by default (0.90 / 0.80).
