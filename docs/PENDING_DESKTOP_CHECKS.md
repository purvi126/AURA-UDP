# Remaining Packet Tracer desktop checks

Packet Tracer 9.0 was retested on 2026-10-29 using the main [saved topology](../packet_tracer/topology/AURA-UDP-campus.pkt). The Old Car and Smoke Detector now share Corporate Office → `SMOKE-TEST-CHAMBER`, a 1 m × 1 m × 1 m physical container. The main file was saved with the car off (`state 0`). See [VALIDATION.md](VALIDATION.md) for measurements and native screenshots.

## Completed observations

- **Manual threshold, Main Wiring Closet:** With the car off, detector `level 10.048500061035156, state 0` rose to `level 69.21540069580078, state 1` after setting Smoke Manual Adjustment to `100` and advancing the environment clock. After removing the adjustment it returned to `level 36.340999603271484, state 0`. Gateway fields could not be read at that moment because the tablet showed its login page.
- **Car stimulus, small chamber:** Merely changing Old Car's Attributes `state` to `1` did not raise smoke. Using the car's physical **Interact** control produced visible exhaust. The detector changed from `level 0.00011444099083227316, state 0` before activation to `level 100, state 1` afterward. The car was turned off; the detector later recovered to `level 0.2446289066696716, state 0`. This is a car-caused local detector alarm, separate from the manual threshold test.
- **Gateway:** While the car-caused detector alarm was active, Tablet PC0's Devices page displayed `SMOKE-SENSOR` with Level `100` and a green Alarm indicator. A previous post-closet page displayed Level `34.1754` and a red Alarm indicator. These are observations at different test stages; a same-chamber, same-session before/after gateway capture is still needed. The tablet returned to the gateway login page during a later refresh.
- **Routed HTTP:** After the chamber change, PC0 loaded the custom AURA page at `http://10.10.30.10` across Router0 and Router1. Tablet PC0 reached `http://192.168.25.1` and earlier listed both registered sensors.

## Remaining before a new release

1. Sign into Tablet PC0's gateway browser manually, then capture its Smoke Level and Alarm indicator with the car off and again after activating the car physically. Capture the requested gateway display before and after the manual Smoke adjustment as a separate test if possible. The chamber is not listed in Packet Tracer's Environment Location menu, so its independent Smoke environment value could not be read; detector level and state were captured.
2. Rerun the repository tests and confirm CI on the final pushed commit. Publish a release only if the smoke transition, connectivity, and CI checks pass and the evidence above is complete.
