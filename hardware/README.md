# Pico bench prototype: parts, wiring and bring-up

Status: reference source written and tested using emulated inputs; **not board-tested**.
This build makes a temperature-aware USB device with visible modes. It is the first
physical implementation of the controller, not the entire futuristic wearable.

## Supported assembly

| Qty | Item | Requirement |
| ---: | --- | --- |
| 1 | Raspberry Pi Pico H or Pico with fitted headers | Original RP2040, non-W; onboard LED is GP25 |
| 1 | USB data cable | Micro-USB at Pico; host connector to match your computer |
| 1 | Computer | Python 3.10+; Linux/macOS USB TTY or Windows COM port |
| 1 | Breadboard | Optional for stop button and external sensor |
| 1 | Normally-open momentary button | Optional, connects GP2 to GND when pressed |
| 2 | Jumper wires | For the button |
| 1 | TMP117 breakout | Optional; 3.3 V logic, address 0x48, fitted I2C pull-ups and decoupling |
| 4 | Jumper wires | For the optional TMP117 |
| 1 | Multimeter / USB power meter | For continuity, supply checks and measured energy budgets |

Use USB power from the host for this reference build. A custom raw-cell battery circuit,
charger, solar wiring, load switches and a production enclosure are not included.
Do not connect a raw battery or 5 V to GPIO/ADC pins. Component ratings and final
surface-temperature limits must be established for a different assembly.

## Wiring

With power disconnected, identify pins using the [official Pico pinout](https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf).
Physical pin numbers below refer to the original Pico, viewed from the component side.

| Pico signal | Physical pin | Destination |
| --- | ---: | --- |
| GP0 / I2C0 SDA | 1 | TMP117 SDA |
| GP1 / I2C0 SCL | 2 | TMP117 SCL |
| GND | 3 | TMP117 GND and one button terminal |
| GP2 | 4 | Other button terminal; internal pull-up is enabled |
| 3V3 OUT | 36 | TMP117 3.3 V / V+ input |
| GP25 | Onboard | Existing onboard LED; no external wiring |

The breakout must pull SDA/SCL up to **3.3 V**. Use the breakout maker's 3.3 V supply
pin, not an ambiguous pin assumed from another manufacturer's board. Verify default
address 0x48 (TMP117 ADD0 tied to GND). No additional pull-ups are required if the
chosen breakout already supplies them.

The [TMP117 datasheet](https://www.ti.com/lit/ds/symlink/tmp117.pdf) specifies temperature
register 0x00 (signed 16-bit, 1/128 °C units) and device ID register 0x0F. The driver
checks the ID and rejects invalid readings. Its bounded range here is −40 to 125 °C.
An external sensor measures its mounting location; neither it nor chip temperature
alone establishes skin-contact safety.

## Firmware installation

1. Download a **stable** UF2 for [RPI_PICO from MicroPython](https://micropython.org/download/RPI_PICO/).
   Record its exact version/filename in your build record. This repository does not
   redistribute a UF2 or claim a board-tested MicroPython version.
2. Hold BOOTSEL while connecting USB, then copy that UF2 onto the RPI-RP2 drive.
   Wait for the board to restart. Use a USB data cable.
3. On the computer, install the official transfer tool: `python -m pip install mpremote`.
4. If you wired the TMP117, change `USE_TMP117 = True` in `firmware/pico/main.py`.
   If not, leave it `False`: telemetry explicitly identifies the sensor as `die`.
5. Identify the port with `mpremote connect list`. Substitute that port below.
6. Copy dependency files first, `main.py` last:

```bash
mpremote connect /dev/ttyACM0 fs cp firmware/pico/safety.py :safety.py
mpremote connect /dev/ttyACM0 fs cp firmware/pico/sensors.py :sensors.py
mpremote connect /dev/ttyACM0 fs cp firmware/pico/service.py :service.py
mpremote connect /dev/ttyACM0 fs cp firmware/pico/main.py :main.py
mpremote connect /dev/ttyACM0 reset
```

Close mpremote/Thonny before opening the port with the host program. On Windows,
substitute the actual `COM` port and install the package's `hardware` extra.

```bash
python -m pip install .
ultradevice device --port /dev/ttyACM0 --seconds 60 --out outputs/pico.jsonl
ultradevice check-log --input outputs/pico.jsonl
```

Expected: valid temperature samples, `source=usb`, `temp_source=die` or `tmp117`,
unknown (`null`) battery/load/harvest values, host mode `conserve`, and a shutdown
acknowledgment at exit. Unknown battery state prevents a host boost. No radio is present.
To see a real LED mode change, run again with `--mode stealth`: the LED stays off.

## Local protection and recovery

The firmware checks temperature every 250 ms, turns the LED off when the stop button
is held, limits LED boosts to ten seconds with sixty-second cooldowns, and starts
with a sixty-second boost lockout. A 3-second host-command timeout shuts down outputs;
a 5-second [hardware watchdog](https://docs.micropython.org/en/latest/library/machine.WDT.html)
resets a stalled loop. These are demo protections, not a certified safety subsystem.
The reference controls only the onboard LED; GPIOs are not general power outputs.

A missing configured TMP117 causes a latched fault, without falling back to invented
data. After correcting the connection, restart with `--reset-fault`; the firmware
accepts a reset only with a valid sensor below its derating threshold.

For firmware maintenance, hold the stop button (GP2 to GND) while powering up. The
application stays at the REPL without starting its watchdog. Upload changes, release
the button, and reset. Without that boot recovery, interrupting the loop leaves the
hardware watchdog active and the board may restart during an upload.

## Acceptance record to complete on your board

Copy [acceptance-template.md](acceptance-template.md) for each build. Record:

1. Board revision, sensor breakout, MicroPython release and firmware SHA-256 hashes.
2. Continuity checks before power, then measured 3.3 V supply and USB current.
3. Repeated USB connect/disconnect and clean shutdown acknowledgments.
4. Stop-button LED override, interrupted-host timeout and power-cycle default behavior.
5. Optional sensor unplug/reconnect and explicit fault reset. Use injected test readings
   for temperature thresholds; do not heat a worn device to test shutdown.
6. Sensor comparison with a reference instrument at known stable temperatures.
7. Long-session logs, actual average current, enclosure temperature and recovery behavior.

Do not mark these tests passed from desktop test results. Finish physical validation
before attaching a battery, adding actuators or treating this as wearable hardware.
