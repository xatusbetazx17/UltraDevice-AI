# USB protocol version 1

Transport: USB CDC serial, UTF-8 newline-delimited JSON. Nominal host line settings
are 115200 baud, 8N1; USB transport is still packet-based. One request is outstanding
at a time. Maximum frame is 4096 bytes including the newline. The host uses a
2-second transaction deadline. This is a local, unauthenticated bench protocol.

Request IDs correlate responses; they are not authentication or replay protection.
The host separately rejects repeated/non-increasing sample sequence numbers and
uptime, unknown versions, missing temperatures and expired samples. A device reset
requires restarting the host session. Do not bridge this port directly to a network.

## Requests

```json
{"v":1,"id":1,"op":"sample"}
{"v":1,"id":2,"op":"set_mode","mode":"stealth"}
{"v":1,"id":3,"op":"reset_fault"}
```

Accepted modes: `normal`, `conserve`, `stealth`, `boost`, `reserve`, `shutdown`, `fault`.
Unexpected request keys and operations are rejected. Modes cannot change thermal,
watchdog or boost limits through this protocol. The firmware may acknowledge a
more restrictive mode; the host logs the actual acknowledgment.

## Responses

```json
{"v":1,"id":1,"ok":true,"sample":{"seq":1,"uptime_ms":1000,"temp_c":26.5,"temp_source":"die","battery_soc":null,"load_w":null,"harvest_w":null,"device_mode":"conserve","sensor_ok":true}}
{"v":1,"id":2,"ok":true,"mode":"stealth"}
{"v":1,"id":3,"ok":false,"error":"Reset requires a valid cool sensor"}
```

`temp_source` distinguishes `die`, `tmp117` and `simulated`. Battery SoC is a fraction
0..1 when a future calibrated adapter supplies it. Unknown quantities are JSON `null`.
The reference board has no battery monitor. Invalid temperature is reported as null
with `sensor_ok=false`, and the board latches a fault. Samples are not medical data.

The local firmware enforces LED shutdown without host cooperation for invalid
sensors, high temperature, the stop input and host-command timeout. A boost request
cannot extend an already active ten-second boost. Cooldowns persist across host
reconnections while the board is powered; reboot starts another sixty-second lockout.

The host polls based on its mode decision and sends `set_mode` each cycle as the
heartbeat. Always close a session cleanly; on an error it attempts shutdown and
closes the serial handle. If shutdown cannot be confirmed, the log records that
condition and the firmware timeout is the fallback.

## Logs

Every local JSONL record contains an index, previous hash, kind, payload and SHA-256.
`ultradevice check-log --input FILE` checks the chain. This detects ordinary edits,
reordering and malformed/incomplete records. A party able to rewrite the entire log
can recompute hashes, and deleting a complete suffix is not detectable without a
separately trusted final hash. Logs are not encrypted, signed, immutable or uploaded.
A session overwrites its chosen output path; use a new filename to retain older runs.
