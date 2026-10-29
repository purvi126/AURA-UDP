# Packet Tracer evidence for the project review

These are direct, native-size Cisco Packet Tracer 9.0 captures from 2026-10-29. Use the linked JPEGs in a report with their captions. The two smoke tests used different stimuli; the manual adjustment is not evidence that the car produced smoke.

| Proof | Before | After | What was observed |
|---|---|---|---|
| Old Car, physical **Interact**, with car and detector in the same 1 m³ chamber | [Gateway: Alarm red, Level about 0.000073422](media/smoke-chamber-gateway-before-car-2026-10-29.jpg) | [Gateway: Alarm green, Level 100](media/smoke-chamber-gateway-after-car-2026-10-29.jpg) | The car emitted visible exhaust and the detector reached `level 100, state 1`. The car was then switched off. |
| Separate Main Wiring Closet Smoke Manual Adjustment test | [Gateway: Alarm red, Level 3.08169](media/smoke-manual-gateway-before-2026-10-29.jpg) | [Gateway: Alarm green, Level about 48.18 in the saved frame](media/smoke-manual-gateway-after-2026-10-29.jpg) | Smoke Manual Adjustment was set to 100. The live gateway was also observed at about 66.87 during the test, but the saved after frame shows a later, lower reading. |
| Routed HTTP | — | [PC0 browser at `http://10.10.30.10`](media/routed-http-after-chamber-2026-10-29.jpg) | The custom AURA page loaded from Server0 across Router0 and Router1. |

The paired images show the gateway's **Alarm** indicator changing from red to green. Packet Tracer's green indicator is the active alarm state in this lab. The detector's own [car-off](media/smoke-chamber-detector-before-2026-10-29.jpg) and [car-on](media/smoke-chamber-car-triggered-alarm-2026-10-29.jpg) Attributes captures provide the separate `level` and `state` readings. The [visible exhaust](media/smoke-chamber-visible-car-exhaust-2026-10-29.jpg) frame documents physical car activation.

## Limits of these captures

- The four gateway images include the simulator mouse pointer. The underlying readings and alarm colors are unedited; do not describe these files as pointer-free.
- The old closet attempt, in which the car's Attributes `state` was changed instead of using **Interact**, did not produce an alarm. Its [failed-test capture](media/car-on-detector-no-alarm-2026-10-29.jpg) is retained so the two methods are not conflated.
- The detector's built-in Specifications page says an alarm occurs at 30% Smoke, yet a later live closet reading near 34.18 showed `state 0` and a red gateway Alarm. No editable native threshold setting was found in Config, Programming, or Thing Editor. Do not claim the detector's threshold was changed from 40 to 30.
- The GitHub `main` topology was manually updated after the paired chamber test. Inspect its current physical placement before presenting the live car demonstration. The captured chamber test is valid evidence of that session, not proof that every later saved topology opens in the same arrangement.
- Packet Tracer demonstrates the simulated IoT scenario; the AURA transport is implemented and measured separately in NS2.
