# Security and device boundary

The reference protocol is for a local USB connection. It provides input validation,
framing limits and deadlines, but no peer authentication, encryption or authorization
against a hostile USB host. Do not expose it to a network without a designed secure
transport. The controller is not a safety-critical or medical control system.

Telemetry is opt-in through a selected local output file. Its hash chain can expose
edits, but is not signed or immutable, and cannot detect a removed complete suffix
without a trusted final hash. Firmware SHA-256 manifests provide integrity comparison,
not secure boot or publisher authentication. The Pico bootloader remains writable.

Report reproducible issues through the repository's reporting facilities without
publishing credentials or personal logs. Security-sensitive product integrations need
a threat model, signed update/key lifecycle and independent hardware protections.
