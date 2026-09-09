# Implementation history

## 0.3.0 — working-device-reference branch

Based on main `0abd854d1c0c64236ed9353244846018f0683fed`.

Repair package/test layout and command entry points. Correct simulation time and
energy accounting, add charging/current limits/stable thermal integration, and expose
unserved energy. Add a host controller, USB protocol, local predictor/logs, Pico firmware,
TMP117 support, schemas, examples, tests, packaging and physical bring-up documentation.

Keep the MIT license. Distinguish tested software from hardware-unverified source and
unimplemented conceptual features. Retire the old destructive ZIP-import helpers.
