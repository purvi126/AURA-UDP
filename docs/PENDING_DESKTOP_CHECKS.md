# Remaining Packet Tracer desktop checks

Packet Tracer 9.0 was retested on 2026-10-29 using the main [saved topology](../packet_tracer/topology/AURA-UDP-campus.pkt). The Old Car and Smoke Detector now share Corporate Office → Main Wiring Closet. The main file was saved with the car off (`state 0`). See [VALIDATION.md](VALIDATION.md) for measurements and native screenshots.

## Completed observations

- **Manual threshold:** With the car off, the detector read `level 10.048500061035156, state 0`. Setting the closet Smoke Manual Adjustment to `100` and advancing the environment clock produced `level 69.21540069580078, state 1`. After the adjustment was removed and the clock advanced, the detector returned to `level 36.340999603271484, state 0`. This verifies the detector's local threshold response only.
- **Car stimulus:** With both devices in the Main Wiring Closet and the car set to `state 1`, the detector read `level 34.29800033569336, state 0` and later `level 34.18050003051758, state 0` after the environment clock advanced beyond 1:47:30. No car-caused alarm was observed. The car was returned to `state 0` before saving.
- **Routed HTTP:** PC0 loaded `http://10.10.30.10` after the physical move; the AURA campus page and address were visible.
- **Gateway Devices page:** Tablet PC0 reached `http://192.168.25.1`. At first the refreshed Devices page listed only `TEMP-SENSOR`. Toggling `SMOKE-SENSOR`'s IoT Server setting from None back to Home Gateway restored its registration. The [restored page](../packet_tracer/documentation/media/gateway-devices-restored-2026-10-29.jpg) lists both devices and shows Smoke Level `34.1754` with its Alarm field. The main topology was saved after reconnection.

## Still required for a new release

1. Establish an Old Car-caused Smoke rise and detector transition to `state 1` in the same physical container. Record the container Smoke value and detector readings before and after. The manual adjustment result does not satisfy this gate. Packet Tracer's installed Environment help says output is 3% per simulated hour in a 100,000 cm³ container; the Main Wiring Closet may still dilute the effect, but its volume was not measured.
2. Capture the gateway Smoke Level and Alarm field before and after a reproducible car-caused alarm. Both devices currently appear on Tablet PC0's Devices page after reconnection, but no gateway alarm transition has been observed.
3. Recheck PC0's routed HTTP page after any further topology edits, rerun tests and CI, and publish a new release only after all smoke, connectivity, and CI gates pass. Until then, keep the failed or incomplete alarm observation visible in the README.
