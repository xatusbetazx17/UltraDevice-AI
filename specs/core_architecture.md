# Core Architecture

> Original design goals, not implemented capabilities. See the [current capability matrix](../docs/capabilities.md) and [model definitions](../docs/models.md) before building.

- **Compute Module**: Efficient SoC with separate low-power controller.
- **Power Module**: Battery + baseline source + harvest controller.
- **I/O & Sensors**: Vision, IMU, environmental (temp, VOC proxy), proximity.
- **Materials**: Multilayer fabric with abrasion resistance + self-repair coating.
- **Safety Controller**: Enforces thermal and discharge limits.
