# Remaining work

The desktop software and reference source are delivered in this branch. This is the
remaining engineering work, in dependency order:

1. **Bench validation:** flash a real Pico, verify USB timing, TMP117 readings, recovery,
   timeout and LED behavior using the provided acceptance template.
2. **Measured portable prototype:** choose power hardware, add a calibrated fuel gauge
   and power monitor, characterize harvesting, and establish thermal limits. No raw-cell
   charger or battery protection design is implemented here.
3. **Useful wearable functions:** select actual IMU/display/radio/camera parts and add
   their drivers and tests. Define the user task before choosing trained AI models.
4. **Product engineering:** design PCB/enclosure, secure boot/update process, production
   tests, reliability and any applicable compliance work for the chosen product.
5. **Research-only concepts:** optical camouflage, self-repairing structures and
   physical transformation have no implementation path established by this repository.

Completing software does not complete these physical and research stages. The
[capability matrix](capabilities.md) is the authoritative feature-status list.
