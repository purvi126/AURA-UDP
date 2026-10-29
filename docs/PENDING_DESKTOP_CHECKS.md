# Remaining Packet Tracer desktop checks

Packet Tracer 9.0 was retested on 2026-10-29. The active topology is `packet_tracer/topology/AURA-UDP-campus.pkt`; a validated snapshot also exists at `packet_tracer/topology/AURA-UDP-campus-validated.pkt`. Both paired gateway tests were completed: physical car activation and manual smoke adjustment. Afterward, the car was switched OFF and the detector recovered. The validated snapshot was reopened with both devices in Main Wiring Closet, car OFF and detector inactive. A later manual GitHub commit changed the main topology, so its current physical placement must be checked before a live replay.

## Completed observations

- **Manual threshold, Main Wiring Closet:** With the car off, detector `level 10.048500061035156, state 0` rose to `level 69.21540069580078, state 1` after setting Smoke Manual Adjustment to `100` and advancing the environment clock. After removing the adjustment it returned to `level 36.340999603271484, state 0`. Gateway fields could not be read at that moment because the tablet showed its login page.
- **Car stimulus, small chamber:** Merely changing Old Car's Attributes `state` to `1` did not raise smoke. Using the car's physical **Interact** control produced visible exhaust. The detector changed from `level 0.00011444099083227316, state 0` before activation to `level 100, state 1` afterward. The car was turned off; the detector later recovered to `level 0.2446289066696716, state 0`. This is a car-caused local detector alarm, separate from the manual threshold test.
- **Gateway:** Paired before-and-after gateway screenshots were captured for both physical car activation and manual smoke adjustment. The car test showed Smoke Level increasing from approximately `0.000073422` (Alarm red) to `100` (Alarm green). The manual test showed `3.08169` (Alarm red) before and about `48.18` (Alarm green) in the saved after screenshot; a higher live reading around `66.87` was seen before that frame. See the [evidence guide](../packet_tracer/documentation/EVIDENCE_GUIDE.md).
- **Routed HTTP:** After the chamber change, PC0 loaded the custom AURA page at `http://10.10.30.10` across Router0 and Router1. Tablet PC0 reached `http://192.168.25.1` and earlier listed both registered sensors.
- **Software and CI:** All 24 NS2/Python tests, the dashboard check, and `git diff --check` passed locally. [CI for the chamber evidence commit `ddeeb95`](https://github.com/purvi126/AURA-UDP/actions/runs/40802214901) and [CI for the follow-up documentation commit `a06c1e0`](https://github.com/purvi126/AURA-UDP/actions/runs/40802509644) both passed.

## Final desktop validation — completed 2026-10-29

The previously pending paired gateway checks have now been completed.

### Completed gateway checks

1. **Physical car smoke test — PASSED**
   - Car OFF: Gateway Smoke Level approximately `0.000073422`; Alarm red.
   - Car activated using the physical Interact control: Smoke Level `100`; Alarm green.
   - Before-and-after screenshots saved in `packet_tracer/documentation/media/`.

2. **Manual smoke adjustment test — PASSED**
   - Baseline: Gateway Smoke Level approximately `3.08169`; Alarm red.
   - Smoke Manual Adjustment set to `100`: Gateway Smoke Level rose to about `66.87` live; the saved after frame reads about `48.18` with Alarm green.
   - Before-and-after screenshots saved in `packet_tracer/documentation/media/`.

3. **Recovery and saved topology**
   - The car was switched OFF after testing.
   - The detector subsequently returned to a near-zero reading with `state 0`.
   - The validated simulation was saved as `packet_tracer/topology/AURA-UDP-campus-validated.pkt`.

### Remaining review and release requirements

- Capture pointer-free evidence images if they are required in the report. The current native gateway pair includes a visible simulator cursor; the readings are unedited.
- Verify that the current main topology has the car and detector together in the 1 m³ chamber before demonstrating a car-caused alarm live. The later manual GitHub topology change may have moved them.
- Resolve the native detector threshold question. Its Specifications page says 30% but the live closet showed Alarm off near Level 34.18; no editable 40-to-30 control has been identified. Do not claim this adjustment is implemented.
- Recheck PC0 routed HTTP and Tablet gateway Devices after the final topology edit, run local tests, push the proof update, and verify CI before publishing another release.

**Scope clarification:** Packet Tracer demonstrates the simulated IoT network and smoke-response behavior. The AURA transport protocol is implemented and evaluated separately in NS2.
