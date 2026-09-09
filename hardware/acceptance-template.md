# Physical build acceptance record

Status: NOT EXECUTED. Fill in actual measurements; do not infer them from simulation.

| Field | Recorded value |
| --- | --- |
| Build identifier / date / tester | |
| Repository commit | |
| Pico model and PCB revision | |
| MicroPython UF2 version and hash | |
| Firmware file hashes | |
| TMP117 breakout and mounting position | |
| Supply / cable / instrument identifiers | |
| Measured supply voltage and current | |
| Temperature calibration and uncertainty | |

| Test | Expected result | Observed result / evidence | Pass? |
| --- | --- | --- | --- |
| Boot / recovery | Outputs default off/conserve; button-at-boot keeps REPL | | |
| USB sample | Correct source, finite temperature, unknown power fields | | |
| Stealth | Onboard LED off | | |
| Button override | LED off while held, including during commands | | |
| Host disconnect | Output shutdown after 3-second timeout | | |
| Loop stall | Watchdog resets within configured timeout | | |
| Missing configured sensor | Latched fault; no synthetic fallback | | |
| Reset with cool valid sensor | Explicit reset accepted | | |
| Thermal threshold injection | Derate at 39 °C; shut down at 42 °C | | |
| Boost threshold injection | Maximum 10 s; minimum 60 s cooldown | | |
| Current and temperature budget | Within independently established component limits | | |
| Long run | No unexplained resets, stale data or output state | | |

Outstanding defects and disposition:

Tester sign-off and limitations:
