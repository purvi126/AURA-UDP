# Remaining Packet Tracer desktop checks

Packet Tracer 9.0 was retested on 2026-10-29. The project retains its original topology at `packet_tracer/topology/AURA-UDP-campus.pkt`, while the final validated session was saved separately as `packet_tracer/topology/AURA-UDP-campus-validated.pkt`. Both paired gateway tests were completed successfully: physical car activation and manual smoke adjustment. The car was switched OFF after testing, and the Smoke Detector subsequently recovered to a near-zero reading with `state 0`. The validated topology was reopened and inspected: both devices are located in Main Wiring Closet, with the car OFF (state 0) and the Smoke Detector recovered (level 0, state 0). The separate SMOKE-TEST-CHAMBER is empty in this saved version.

## Completed observations

- **Manual threshold, Main Wiring Closet:** With the car off, detector `level 10.048500061035156, state 0` rose to `level 69.21540069580078, state 1` after setting Smoke Manual Adjustment to `100` and advancing the environment clock. After removing the adjustment it returned to `level 36.340999603271484, state 0`. Gateway fields could not be read at that moment because the tablet showed its login page.
- **Car stimulus, small chamber:** Merely changing Old Car's Attributes `state` to `1` did not raise smoke. Using the car's physical **Interact** control produced visible exhaust. The detector changed from `level 0.00011444099083227316, state 0` before activation to `level 100, state 1` afterward. The car was turned off; the detector later recovered to `level 0.2446289066696716, state 0`. This is a car-caused local detector alarm, separate from the manual threshold test.
- **Gateway:** During the earlier chamber test, Tablet PC0 displayed `SMOKE-SENSOR` at Level `100` with a green Alarm indicator. A separate earlier observation showed Level `34.1754` with a red Alarm indicator; these readings came from different test stages. On 2026-10-29, paired before-and-after gateway screenshots were successfully captured for both physical car activation and manual smoke adjustment. The physical car test showed Smoke Level increasing from approximately `0.000073422` (Alarm red) to `100` (Alarm green). The manual adjustment test showed an increase from approximately `3.08169` (Alarm red) to `66.8725` (Alarm green). See [VALIDATION.md](VALIDATION.md) for the corresponding evidence.
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
   - Smoke Manual Adjustment set to `100`: Gateway Smoke Level increased to approximately `66.8725`; Alarm green.
   - Before-and-after screenshots saved in `packet_tracer/documentation/media/`.

3. **Recovery and saved topology**
   - The car was switched OFF after testing.
   - The detector subsequently returned to a near-zero reading with `state 0`.
   - The validated simulation was saved as `packet_tracer/topology/AURA-UDP-campus-validated.pkt`.

### Remaining release requirements

- Commit and push the validated topology, evidence screenshots, and updated documentation.
- Verify that GitHub Actions passes for the final pushed commit.
- Publish a release only after the final CI verification succeeds.

**Scope clarification:** Packet Tracer demonstrates the simulated IoT network and smoke-response behavior. The AURA transport protocol is implemented and evaluated separately in NS2.
