# Math Models (Simplified)

- Runtime: `T = B / max(P_load - P_harvest, 0)`
- Duty cycle to reach target runtime `T*`:
  - Let high-power `P_hi`, low-power `P_lo`, harvest `P_h`.
  - Find fraction `f` in high mode so that `B / (f*(P_hi-P_h) + (1-f)*(P_lo-P_h)) = T*`.
  - Solve for `f` in [0,1].
- Thermal cap (not modeled in detail): enforce `P_load <= P_max(T_env)`.
