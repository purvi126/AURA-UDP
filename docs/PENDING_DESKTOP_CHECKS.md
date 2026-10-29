# Remaining Packet Tracer desktop checks

Packet Tracer 9.0 was retested on 2026-10-29. The active topology is `packet_tracer/topology/AURA-UDP-campus.pkt`. After the manual GitHub edit `6e13aa4` placed the car and detector in Main Wiring Closet, both were returned to the same 1 m³ `SMOKE-TEST-CHAMBER` in the main file. A new car OFF → ON → OFF run showed a gateway Alarm transition at Level 0 → 100 → about 0.057. The car was OFF when the main topology was saved. The older `AURA-UDP-campus-validated.pkt` remains a separate historical snapshot with both devices in the closet.

## Completed observations

- **Manual threshold, Main Wiring Closet:** With the car off, detector `level 10.048500061035156, state 0` rose to `level 69.21540069580078, state 1` after setting Smoke Manual Adjustment to `100` and advancing the environment clock. After removing the adjustment it returned to `level 36.340999603271484, state 0`. Gateway fields could not be read at that moment because the tablet showed its login page.
- **Car stimulus, small chamber:** Merely changing Old Car's Attributes `state` to `1` did not raise smoke. Using the car's physical **Interact** control produced visible exhaust. The detector changed from `level 0.00011444099083227316, state 0` before activation to `level 100, state 1` afterward. The car was turned off; the detector later recovered to `level 0.2446289066696716, state 0`. This is a car-caused local detector alarm, separate from the manual threshold test.
- **Gateway:** A new pointer-free car pair captured Smoke Level `0` (Alarm red) before physical activation and `100` (Alarm green) after it. A pointer-free recovery frame shows about `0.057` (Alarm red) after the car was turned off. The earlier separate manual pair showed `3.08169` (Alarm red) before and about `48.18` (Alarm green) in the saved after screenshot; a higher live reading around `66.87` was seen before that frame. See the [evidence guide](../packet_tracer/documentation/EVIDENCE_GUIDE.md).
- **Routed HTTP:** After restoring the chamber layout, PC0 refreshed the custom AURA page at `http://10.10.30.10` across Router0 and Router1. Tablet PC0 displayed both registered sensors at `http://192.168.25.1` throughout the new car test. Pointer-free captures of both pages were saved.
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
   - The main `packet_tracer/topology/AURA-UDP-campus.pkt` was saved with both devices in the small chamber and the car OFF. The older validated copy remains in its earlier closet state.

### Remaining review and release requirements

- The new car pair, recovery image, and routed HTTP image are pointer-free direct captures. The historical manual-smoke pair still has a visible cursor; recapture it if the report requires a fully pointer-free manual pair.
- The saved main `.pkt` was reopened: both devices remained in `SMOKE-TEST-CHAMBER`, the car showed no exhaust, and its Attributes `state` was `0`.
- Resolve the native detector threshold question. Its Specifications page says 30% but the live closet showed Alarm off near Level 34.18; no editable 40-to-30 control has been identified. Do not claim this adjustment is implemented.
- Run local tests, push the chamber and proof update, and verify CI before publishing another release.

**Scope clarification:** Packet Tracer demonstrates the simulated IoT network and smoke-response behavior. The AURA transport protocol is implemented and evaluated separately in NS2.
