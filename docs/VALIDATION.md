# Validation record

Packet Tracer connectivity was checked on 2026-10-13 and retested on 2026-10-29 with Packet Tracer 9.0 on Windows. Software and browser checks were refreshed on 2026-10-16 with NS2 2.35 under Ubuntu WSL and the local dashboard; NS2 tests and experiments were extended on 2026-10-17. A final review preparation pass was performed on 2026-10-28. These observations refer to the saved topology and experiment configuration.

| Check | Observation |
|---|---|
| Routed packet, PC0 to Server0 | Simple ICMP PDU successful after address resolution |
| PC1 to Server0 (`10.10.30.10`) | Four replies, zero lost |
| PC2 to Server0 (`10.10.30.10`) | Four replies, zero lost |
| PC3 to PC2 (`10.10.10.13`) | Four replies, zero lost |
| PC0 HTTP to Server0 across Router0 and Router1 | `http://10.10.30.10` rendered the custom AURA campus page after the page text was updated |
| PC3 HTTP to Server0 on the same LAN | `http://10.10.30.10` rendered the custom AURA campus page; this is not a routed path |
| Native IoT registration | Tablet PC0 opened Home Gateway at `192.168.25.1`; Devices listed both `TEMP-SENSOR` and `SMOKE-SENSOR` |
| IoT telemetry view | Temperature and smoke alarm/level fields appeared on the gateway page |
| Smoke stimulus device | On 2026-10-16, an Old Car named `SMOKE-TRIGGER-CAR` was added beside `SMOKE-SENSOR`. On 2026-10-17, Packet Tracer's physical view showed both devices inside Corporate Office, as required by the car specification. The car's Attributes tab showed `state 1`, but the detector's Attributes tab still showed `level 0, state 0`. No smoke alarm transition was observed. |
| Manual smoke threshold, 2026-10-29 | Both devices were moved into Corporate Office → Main Wiring Closet. With the car off, the detector read `level 10.048500061035156, state 0`. Setting the closet's Smoke Manual Adjustment to `100` and advancing the environment clock produced `level 69.21540069580078, state 1` (above the 40% threshold). With the adjustment removed and the clock advanced, the detector returned to `level 36.340999603271484, state 0`. This is a detector response, not evidence that the car emitted smoke. The Home Gateway showed its login page before/after; its Devices fields were unavailable without signing in. |
| Old Car stimulus, 2026-10-29 | With the detector and car visibly together in Main Wiring Closet, the car's Attributes showed `state 1`. The detector read `level 34.29800033569336, state 0` and later `level 34.18050003051758, state 0` after the environment clock had advanced beyond 1:47:30. The level did not rise past the threshold and no car-caused alarm was observed. The car was set back to `state 0` before the main `.pkt` was saved. Container volume and Smoke environment reading during this car test were not captured. |
| Small-chamber car retest, 2026-10-29 | A new physical `SMOKE-TEST-CHAMBER` measured 1 m × 1 m × 1 m (1 m³), the minimum Packet Tracer accepted. The car and detector were placed together inside it. With the car off, detector `level 0.00011444099083227316, state 0`. Setting the car's Attributes `state` to `1` alone left the detector at `level 0.000011444099982327316, state 0` after the environment clock advanced. The car's physical **Interact** control then produced visible exhaust; after the clock advanced, detector `level 100, state 1`. After Interact turned the car off, the detector recovered to approximately `level 0.2446, state 0`. The new chamber was absent from the Environment dialog's Location menu, so its independent Smoke environment value could not be read. The main topology was saved with the car off. |
| Gateway during car alarm, 2026-10-29 | Tablet PC0's refreshed `http://192.168.25.1/home.html` Devices page listed both sensors and displayed Smoke Level `100` with a green Alarm indicator while the detector read `state 1`. The earlier post-closet page displayed Level `34.1754` with a red Alarm indicator. These are different test stages, so a same-chamber gateway before/after pair has not been captured. A later refresh returned the tablet to the Home Gateway login page; authentication must be performed by the user. |
| Post-chamber connectivity, 2026-10-29 | PC0 loaded the AURA campus page at `http://10.10.30.10` across Router0 and Router1 after the small-chamber move. The gateway address remained reachable from Tablet PC0, but its login page blocked another Devices reading after the session expired. |
| Connectivity retest, 2026-10-29 | After moving the car and detector, PC0 loaded the AURA campus page at `http://10.10.30.10` over the routed path. Tablet PC0 loaded the Home Gateway at `http://192.168.25.1`; after manual lab login, the refreshed Devices page initially listed only `TEMP-SENSOR`. Toggling `SMOKE-SENSOR`'s IoT Server setting from None back to Home Gateway restored registration. The refreshed page then listed both sensors and displayed Smoke Level `34.1754` with an Alarm field. No gateway alarm transition was captured. The main `.pkt` was saved after reconnection. |
| Local software checks, 2026-10-29 | Under Ubuntu WSL with NS2 installed, `python3 -m unittest discover -s tests -q` passed all 24 tests. `node scripts/check_dashboard.mjs` passed, and `git diff --check` found no whitespace errors. |
| Final chamber commit checks, 2026-10-29 | After the small-chamber topology and documentation changes, the same 24 NS2/Python tests, dashboard check, and `git diff --check` passed locally. [CI run 40802067252](https://github.com/purvi126/AURA-UDP/actions/runs/40802067252) passed for commit `2367eec`, including NS2 installation, tests, chart regeneration checks, and short experiment sweeps. |
| Python and NS2 tests | Twenty-four tests passed locally on 2026-10-17, including crowded alert admission, received-flow fairness, rejection of incomplete simulation logs, and an integration check that holds generation times fixed while alert order changes |
| Transport sweep | 30 seeds × 3 conditions × 3 modes = 270 NS2 runs; a second full sweep reproduced `runs.csv`, `summary.csv`, and `paired.csv` byte for byte |
| AURA ablation | 30 seeds × 3 conditions × 4 policies = 360 NS2 runs; a second full sweep reproduced `runs.csv`, `summary.csv`, and `paired.csv` byte for byte |
| Fresh-seed validation | Seed indices 31–60 repeated the 270-run transport sweep and 360-run ablation; a second execution reproduced the held-out `runs.csv` and `paired.csv` byte for byte |
| Long-workload robustness | Seed indices 61–90 produced 480 additional runs across four 120-message conditions, including two conditions with two CBR flows and a six-packet queue. The generated count, variant keys, DDR bounds, and two-flow fairness fields were checked. |
| Alert-slot reservation study | Seed indices 121–150 produced 360 runs across the same four 120-message conditions. A second execution reproduced `runs.csv`, `summary.csv`, and `paired.csv` byte for byte. The candidate reduced the original AURA DDR deficit in both crowded cases; routine delivery fell, and one-shot still won the tight case. |
| Arrival and link-rate sensitivity | Seed indices 181–210 produced 1,440 runs across 16 conditions: two workloads × regular/burst spacing × alert first/last × 128/256 Kb/s, each with one-shot, original AURA, and reserved AURA. All 48 scenario/variant groups have 30 runs; each run generated 120 messages and DDR stayed within [0, 1]. A second execution reproduced `runs.csv`, `summary.csv`, `paired.csv`, `schedule_pairs.csv`, and `config.json` byte for byte. The first 720 runs match the earlier two-schedule dataset exactly, and the default NS2 sample `events.csv` matches its checked-in baseline, SR, and AURA traces. |
| Final review preparation | On 2026-10-28, the 24-test NS2/Python suite and dashboard static check passed. A fresh one-run AURA trace generated metrics and window/RTO events; a separate trace showed two `abandon` events under the documented configuration. The sensitivity SVG was generated from the saved CSV, rendered headlessly, and visually inspected for legible labels, scales, and values. Local links in the README and new review notes resolved. This did not test Packet Tracer. |
| Dashboard browser check | On 2026-10-28, an isolated local HTTP server and headless Chrome loaded the dashboard at 1440 × 900 and 390 × 844. Browser automation changed all three step 05 controls through all 16 workload/schedule/rate combinations at each viewport. For each combination, the three displayed deadline-delivery chart values matched `experiments/results/sensitivity/summary.csv` after one-decimal rounding. Neither viewport had page-level horizontal overflow or JavaScript exceptions. Screenshots of the step 05 panel were visually inspected. This check did not verify every table cell, keyboard focus behavior, or Packet Tracer. |
| CI | [Run 40715470548](https://github.com/purvi126/AURA-UDP/actions/runs/40715470548) passed for commit `fbaeb78`. The workflow installed NS2, ran tests, checked dashboard syntax/data paths, regenerated the ablation, robustness, and new sensitivity SVGs without a diff, and executed short smoke sweeps for comparison, ablation, robustness, reservation, sensitivity, and paired schedule contrasts. |

The [current routed HTTP capture](../packet_tracer/documentation/media/routed-http-after-chamber-2026-10-29.jpg) shows PC0's page load from the sensor LAN across both routers. Earlier native captures document the [shared closet](../packet_tracer/documentation/media/shared-closet-2026-10-29.jpg), [manual threshold alarm](../packet_tracer/documentation/media/smoke-manual-threshold-passed-2026-10-29.jpg), and [failed closet car test](../packet_tracer/documentation/media/car-on-detector-no-alarm-2026-10-29.jpg). The small-chamber test has separate [detector baseline](../packet_tracer/documentation/media/smoke-chamber-detector-before-2026-10-29.jpg), [visible car exhaust](../packet_tracer/documentation/media/smoke-chamber-visible-car-exhaust-2026-10-29.jpg), [car-on state](../packet_tracer/documentation/media/smoke-chamber-car-on-2026-10-29.jpg), [car-caused detector alarm](../packet_tracer/documentation/media/smoke-chamber-car-triggered-alarm-2026-10-29.jpg), [gateway Level 100 display](../packet_tracer/documentation/media/smoke-chamber-gateway-car-level100-2026-10-29.jpg), and [recovered detector](../packet_tracer/documentation/media/smoke-chamber-car-off-recovered-2026-10-29.jpg). The [earlier restored gateway capture](../packet_tracer/documentation/media/gateway-devices-restored-2026-10-29.jpg) shows both devices at Smoke Level `34.1754`. All captures are native Packet Tracer window resolution. Sensor readings reflect simulator instants, not transport performance data.

Reproduce the software checks from `/mnt/d/projects/AURA-UDP`:

```bash
python3 -m unittest discover -s tests -v
node scripts/check_dashboard.mjs
python3 scripts/multiseed.py --output /tmp/aura-check
python3 scripts/ablation.py --output /tmp/aura-ablation-check
python3 scripts/multiseed.py --first-seed 31 --output /tmp/aura-heldout-check
python3 scripts/ablation.py --first-seed 31 --output /tmp/aura-heldout-ablation-check
python3 scripts/robustness.py --output /tmp/aura-robustness-check
python3 scripts/reservation_study.py --output /tmp/aura-reservation-check
python3 scripts/sensitivity.py --output /tmp/aura-sensitivity-check
python3 scripts/sensitivity_contrasts.py --input /tmp/aura-sensitivity-check
cmp experiments/results/multiseed/runs.csv /tmp/aura-check/runs.csv
cmp experiments/results/multiseed/summary.csv /tmp/aura-check/summary.csv
cmp experiments/results/multiseed/paired.csv /tmp/aura-check/paired.csv
cmp experiments/results/ablation/runs.csv /tmp/aura-ablation-check/runs.csv
cmp experiments/results/ablation/summary.csv /tmp/aura-ablation-check/summary.csv
cmp experiments/results/ablation/paired.csv /tmp/aura-ablation-check/paired.csv
cmp experiments/results/holdout/multiseed/runs.csv /tmp/aura-heldout-check/runs.csv
cmp experiments/results/holdout/ablation/runs.csv /tmp/aura-heldout-ablation-check/runs.csv
cmp experiments/results/robustness/runs.csv /tmp/aura-robustness-check/runs.csv
cmp experiments/results/reservation/runs.csv /tmp/aura-reservation-check/runs.csv
cmp experiments/results/sensitivity/runs.csv /tmp/aura-sensitivity-check/runs.csv
cmp experiments/results/sensitivity/summary.csv /tmp/aura-sensitivity-check/summary.csv
cmp experiments/results/sensitivity/paired.csv /tmp/aura-sensitivity-check/paired.csv
cmp experiments/results/sensitivity/schedule_pairs.csv /tmp/aura-sensitivity-check/schedule_pairs.csv
```

The 30-seed sweeps are descriptive for three short, four longer, and 16 arrival/link-rate synthetic scenarios. The feasibility rule saved retry traffic under high message rate and two-flow congestion but did not demonstrate a DDR gain. In both original two-flow conditions, one-shot delivery exceeded original AURA's deadline delivery. Alert-slot reservation improved crowded results at the cost of routine delivery; it still fell below one-shot in the original tight case. In the four-schedule study, moving the alert from first to last within a 128 Kb/s crowded burst reduced one-shot DDR by 43.6 points and reserved AURA DDR by 15.2 points. Reservation beat one-shot under the tested 128 Kb/s late-alert bursts, but several other tight-case paired differences from one-shot spanned zero. The results do not establish broad performance superiority or Internet-safe congestion fairness. Packet Tracer confirms the routed HTTP page and registered sensor telemetry, but it does not run the custom transport. The gateway WAN address did not serve its device page from PC3. DHCP failed for the IoT clients in this lab, so the saved topology uses static internal addresses. The detector responded both to manual Smoke adjustment in Main Wiring Closet and to the physically activated Old Car in the small chamber. The gateway displayed Level 100 during the car alarm, but a paired same-chamber gateway before/after capture remains pending after the login expired. Packet Tracer's Environment menu did not expose the new chamber, so its independent Smoke value was not recorded. The [remaining desktop checks](PENDING_DESKTOP_CHECKS.md) state the release gates. The gateway's lab HTTP interface and wireless settings are demonstration configuration, not a production security design.

## Final paired gateway validation — 2026-10-29

Two paired smoke-response tests were completed using Cisco Packet Tracer 9.0.

### Test 1: Physical car smoke stimulus

- Baseline: Car OFF; gateway Smoke Level approximately 0.000073422; Alarm indicator red.
- Trigger: The Old Car was physically activated using Packet Tracer's Interact control.
- Result: Gateway Smoke Level increased to 100; Alarm indicator changed to green.
- Detector response: Smoke Detector reached level 100, state 1.
- Outcome: PASSED.

Evidence:
- packet_tracer/documentation/media/smoke-chamber-gateway-before-car-2026-10-29.jpg
- packet_tracer/documentation/media/smoke-chamber-gateway-after-car-2026-10-29.jpg

### Test 2: Manual Smoke adjustment

- Baseline: Gateway Smoke Level approximately 3.08169; Alarm indicator red.
- Trigger: Main Wiring Closet Smoke Manual Adjustment was set to 100.
- Result: Gateway Smoke Level increased to approximately 66.8725 during the test; the Alarm indicator changed to green.
- The level subsequently decreased after the adjustment was removed.
- Outcome: PASSED.

Evidence:
- packet_tracer/documentation/media/smoke-manual-gateway-before-2026-10-29.jpg
- packet_tracer/documentation/media/smoke-manual-gateway-after-2026-10-29.jpg

### Final topology

- The car was switched OFF.
- The detector recovered to a near-zero smoke reading.
- A validated topology copy was saved as:
  packet_tracer/topology/AURA-UDP-campus-validated.pkt

Both paired gateway tests passed. These Packet Tracer observations validate simulated IoT smoke detection and gateway response, not execution of the AURA transport protocol. Transport performance is evaluated separately in NS2.

### Final saved topology verification — 2026-10-29

The saved `AURA-UDP-campus-validated.pkt` topology was reopened in Cisco Packet Tracer 9.0 and inspected.

- `SMOKE-TRIGGER-CAR` (Old Car) is located in Main Wiring Closet with `state = 0` (OFF).
- `SMOKE-SENSOR` (Smoke Detector) is located in Main Wiring Closet with `level = 0` and `state = 0`.
- The separate `SMOKE-TEST-CHAMBER` is present but empty in this saved version.
- Both devices are in their recovered, inactive states.

The paired gateway screenshots document the successful smoke-response tests performed earlier. The saved topology represents the recovered state after testing.
