# Simulation and policy models

All example powers, thermal constants and battery parameters are assumptions.
`day_walk.json` preserves the main branch's illustrative load profile. The lower-power
`bench_reference.json` is another design budget, not a measured Pico consumption claim.

## Units and intervals

- Power: W; energy: Wh; temperatures: °C; current: A; resistance: Ω.
- Scenario `duration_minutes` is 1..1440; output `dt_minutes` is 1..60.
- `t_min` is interval **start**; `dt_min` is actual interval length.
- `soc_wh`, `soc` and `temp_c` are interval-end state. Load/harvest are interval averages.
- `max_temp_c` is the peak during the interval. The final interval may be shorter.

Integration uses at most one-second internal steps, split at event boundaries and
hour changes. Every boost is considered once, lasts its specified seconds, and is
blocked or canceled if reserves or thermal conditions no longer permit it. Scenario
validation rejects overlapping boosts and cooldown violations. This finite-step
model can overshoot a threshold slightly; it is not a hardware timing guarantee.

## Energy

The ideal `simulate` mode uses unity conversion efficiency and no thermal model.
`simulate-physics` uses:

```text
battery terminal demand = load / eff_out - raw_harvest * eff_harv
```

Positive terminal demand discharges storage; negative demand charges it. Storage
never exceeds capacity or drops below zero. Finite available energy and the battery
C-rate limit constrain **delivered power**. Unsatisfied demand appears as `unserved_w`;
no imaginary power is supplied after depletion. Positive harvest can directly supply
load even when the battery is empty.

The lumped discharge factor includes energy efficiency (historically named
`coulombic_eff`), an optional high-current empirical capacity factor, and approximate
I²R loss using nominal voltage. Charge efficiency and charge power are also bounded.
This is not a nonlinear voltage-versus-SoC, cell balancing or chemistry model. One
C-rate limit is used for both directions; actual packs may need different limits.

Check storage conservation with:

```text
end_soc_wh = start_soc_wh + sum(battery_charge_wh) - sum(battery_draw_wh)
```

`spilled_wh` is unused energy at the converted harvesting bus. Reports distinguish
raw-harvest/load net energy from battery-side draw/charge, which include losses.
Battery aging is an optional separate `BatteryAging` utility; pass its estimated
capacity to `Battery` explicitly if you choose to use it. Aging constants are uncalibrated.

## Thermal

The exact constant-input step is:

```text
T_end = T_ambient + P_heat*R + (T_start - T_ambient - P_heat*R)*exp(-dt_seconds/(R*C))
```

All delivered load power and modeled conversion/chemical losses heat one lump.
Derating begins at the configured threshold and requests zero modeled load at the
limit. Ambient heat can keep the device above the limit even after load shutdown.
There is no active cooler or skin-contact model. Do not interpret 39/42 °C example
settings as validated comfort, cell or product safety limits.

## Environmental profiles

A profile contains exactly 24 unique hourly values (0..23), held constant for each
hour. Negative irradiance/motion and non-finite numbers are rejected. Cloudiness is
actually a **solar transmission factor** from 0 (no transmitted irradiance) to 1
(clear). Ambient is bounded −40..85 °C. Relative CSV paths resolve beside the
scenario, with packaged `data/NAME.csv` examples as a fallback.

`thermal_w` and `external_w` are explicit raw input powers. They are never assumed
unless configured. Solar scale represents effective panel area × efficiency if its
input is W/m². Kinetic scale maps a normalized motion trace to W. Characterize these
against a real harvester; the supplied demo coefficients are not product ratings.

## Predictive policy

`PolicyLearner` retains at most 100 valid power observations. Its forecast divides
remaining battery energy by mean net load. With no samples or nonpositive net draw,
it returns `None`, not an invented infinite-life promise. The runtime can select
conserve when a forecast is below a remaining target, given measured power/SoC and
configured capacity. It does not learn a person's schedule, provide conversation,
or improve performance through a trained model.
