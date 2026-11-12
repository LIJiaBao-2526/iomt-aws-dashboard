# Device integration boundary

Assigned owner: CHAN Ka Ming; authenticated backend integration: LI Jia Bao.

This delivery uses a Python HTTP publisher with explicitly synthetic readings. It is not an ESP32 emulator or a validated sensor. It sends finite numeric heart rates, a timezone-aware timestamp, `device_id=website-synthetic-demo` and `synthetic=true`.

The local receiver accepts only that reserved demonstration device. Identical replays are idempotent; conflicting duplicate timestamps are rejected. Engineering input bounds 20–250 bpm are not medical reference limits. The receiver is loopback-only and cannot receive directly from an ESP32 on the LAN.

To add hardware later, confirm exact board and sensor first. A separate authenticated TLS gateway, signal-quality checks, clock synchronization, retries and data isolation are required. Do not embed AWS or DeepSeek keys in firmware. Do not label real health data as synthetic to bypass this prototype's restrictions.

Hardware acceptance requires a circuit, successfully compiled firmware, observed readings, reference-device comparison, missing-signal tests and a repeatable upload test. These physical checks are outside the selected demonstration version and have not been claimed.
