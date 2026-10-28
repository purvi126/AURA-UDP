# Checks reserved for a Packet Tracer desktop session

The software experiments can run in the background. The following observations need an uninterrupted Packet Tracer window, so they are deliberately **not marked complete** in the validation record. The saved starting point is [AURA-UDP-campus.pkt](../packet_tracer/topology/AURA-UDP-campus.pkt); use a copy for the experiment and keep the original as a rollback point.

## 1. Verify the smoke detector threshold

1. Open the topology in Packet Tracer 9.0. In Physical view, confirm `SMOKE-SENSOR` and `SMOKE-TRIGGER-CAR` are in the same container. The current container is Corporate Office.
2. Record the detector's starting `level` and `state` in Attributes, and its fields on Tablet PC0 at `http://192.168.25.1`. The last observed state was `level 0, state 0`, even while the car showed `state 1`.
3. In the Environment dialog, use Advanced Settings → Manual Adjustment to raise **Smoke** in the detector's container above 40%. Record the environment value, detector `level/state`, and gateway display before and after. This isolates whether the detector and gateway respond to smoke; it does **not** establish that the car generated it.
4. Restore the original environment value and confirm the detector returns to the inactive state. If it does not, record the actual state rather than treating the threshold test as passed.

## 2. Verify the Old Car stimulus separately

1. In a disposable topology copy, place the car and detector in the same **small** physical room or closet. Confirm their location from Physical view, not only their Logical view positions.
2. Start with smoke below the alarm threshold. Alt-click the car to turn it on, advance the **environment** clock, and observe whether the container's Smoke value rises. Packet Tracer's installed help states a 3% per simulated hour rise in a 100,000 cm³ container; the large Corporate Office may dilute the effect.
3. Record the detector's transition to `state 1` and the gateway's changed device fields. Then turn the car off and check whether the smoke level and alarm recover as expected. If either transition cannot be observed, document that limitation and the measured values.
4. Save the revised `.pkt` only when the behavior is reproducible. Capture full-resolution screenshots of Physical view (shared container), detector Attributes before/after, the gateway device page, and the environment setting. Do not upscale a small Packet Tracer capture for the README.

## 3. Recheck connectivity after moving devices

- On Tablet PC0, confirm association with HomeGateway0 and that both `TEMP-SENSOR` and `SMOKE-SENSOR` still appear at `http://192.168.25.1`.
- On sensor-side PC0, reload `http://10.10.30.10` and show the address bar plus page title in one native-resolution capture. This is the routed HTTP path across Router0 and Router1.
- If the physical move breaks wireless registration, restore association and static addresses as specified in the [build guide](../packet_tracer/documentation/BUILD_GUIDE.md), then repeat the observations.

## 4. Update evidence and release only after the checks

Record the Packet Tracer version, date, observed readings, and exact outcome in [VALIDATION.md](VALIDATION.md). Replace or supplement the small [routed HTTP screenshot](../packet_tracer/documentation/media/routed-http-pc0.jpg) with a native-resolution capture and update the README evidence captions. Commit the validated `.pkt` and captures, rerun the software test suite and CI, then publish a release if the smoke transition and connectivity gates pass. A failed or inconclusive alarm test should remain visible in the README and should not be presented as complete.

The step 05 dashboard chart has now been exercised in Chrome at desktop and mobile widths across all 16 control combinations; the exact scope is recorded in [VALIDATION.md](VALIDATION.md). The remaining release gate in this file is the Packet Tracer smoke transition and connectivity evidence above.
