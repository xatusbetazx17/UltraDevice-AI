# Overview

UltraDevice AI is an energy-aware device software reference by Marcelo Collado.
The repository contains three distinct execution layers:

| Layer | Input | Output |
| --- | --- | --- |
| Engineering simulator | Scenario and environmental profiles | Energy/temperature estimates, CSV and plots |
| Host controller | Validated sensor readings | Bounded mode requests and local audit logs |
| Pico firmware | Chip/TMP117 temperature, USB requests and stop button | Temperature samples and onboard LED modes |

The simulator does not flash firmware or power real peripherals. The firmware
independently limits its own outputs. Physical validation is still required.

Start with the root [README](../README.md), then review [capabilities](capabilities.md)
and the [integration guide](integration.md).
