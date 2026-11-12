# Virtual ESP32 demonstration

Live project: https://wokwi.com/projects/480447773460293633

This actual Wokwi MicroPython ESP32 simulation was run and verified with the local MQTT bridge on 2026-11-12. It publishes a synthetic BPM every two seconds. The knob maps GPIO34 ADC values to 50–150 bpm. This is not a biological sensor.

## Run

1. Start `python backend/server.py` in this repository.
2. In another terminal, run `python tools/mqtt_bridge.py`.
3. Open http://127.0.0.1:8877 and enable five-second database refresh.
4. Open the Wokwi link and press the green Play triangle.
5. Wait for serial output `MQTT connected` and `PUBLISHED 75 bpm`.
6. Click the actual knob and press End to set 150 bpm. Wait roughly 10 seconds; confirm STORED messages in the bridge and a rule notice on the dashboard.
7. Click the knob and press Home to set 50 bpm; the elevated rule should clear after subsequent records.

If a slider label does not focus the knob, click the visible round dial itself. Home/End work only when the knob has keyboard focus. Only run one copy of this saved project during the demo, since it uses a fixed MQTT client ID.

The public MQTT broker and public Wokwi gateway carry only synthetic values. They are untrusted demonstration infrastructure and are not for medical records, secrets or production. The bridge filters topic, synthetic flag, bounds and receive rate. The bridge timestamps reception, not the original ADC sampling instant. No pip dependencies, Wokwi private gateway, tunnel or AWS login are required for this demo route.

The public GitHub Pages dashboard is separate: it does not read this computer's SQLite database. Use the local URL for the live Wokwi flow. Public Pages is used to share the standalone synthetic scenarios and report.

Sources: https://docs.wokwi.com/guides/esp32-wifi and https://docs.wokwi.com/parts/wokwi-potentiometer
