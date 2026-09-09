# Power Budget

> Original design goals, not implemented capabilities. See the [current capability matrix](../docs/capabilities.md) and [model definitions](../docs/models.md) before building.

Let:
- `B` = battery capacity (Wh)
- `P_load` = average load (W)
- `P_harvest` = average harvest (W)

Then net draw `P_net = max(P_load - P_harvest, 0)` and ideal runtime `T = B / P_net` hours.
Reserve-boost: short bursts `P_burst` for duration `t_burst` subject to cooldown `t_cooldown`.
