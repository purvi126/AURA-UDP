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
| Connectivity retest, 2026-10-29 | After moving the car and detector, PC0 loaded the AURA campus page at `http://10.10.30.10` over the routed path. Tablet PC0 loaded the Home Gateway at `http://192.168.25.1`; after a manual lab login, the refreshed Devices page listed `TEMP-SENSOR` only. `SMOKE-SENSOR` was absent. The earlier two-device observation above remains historical evidence. |
| Local software checks, 2026-10-29 | Under Ubuntu WSL with NS2 installed, `python3 -m unittest discover -s tests -q` passed all 24 tests. `node scripts/check_dashboard.mjs` passed, and `git diff --check` found no whitespace errors. |
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

The [2026-10-29 routed HTTP capture](../packet_tracer/documentation/media/routed-http-postmove-2026-10-29.jpg) shows PC0's page load from the sensor LAN across both routers. The [shared-closet capture](../packet_tracer/documentation/media/shared-closet-2026-10-29.jpg), [manual alarm capture](../packet_tracer/documentation/media/smoke-manual-threshold-passed-2026-10-29.jpg), [car-off baseline](../packet_tracer/documentation/media/car-off-detector-baseline-2026-10-29.jpg), [car-on state](../packet_tracer/documentation/media/car-on-state-2026-10-29.jpg), and [car-on detector reading](../packet_tracer/documentation/media/car-on-detector-no-alarm-2026-10-29.jpg) are native Packet Tracer captures. The [post-move gateway Devices capture](../packet_tracer/documentation/media/gateway-devices-postmove-2026-10-29.jpg) shows only `TEMP-SENSOR`; the older [Devices screenshot](../packet_tracer/documentation/media/gateway-devices.jpg) shows both sensors in an earlier session. No gateway smoke fields were available during the manual or car tests. Sensor readings reflect simulator instants, not transport performance data.

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

The 30-seed sweeps are descriptive for three short, four longer, and 16 arrival/link-rate synthetic scenarios. The feasibility rule saved retry traffic under high message rate and two-flow congestion but did not demonstrate a DDR gain. In both original two-flow conditions, one-shot delivery exceeded original AURA's deadline delivery. Alert-slot reservation improved crowded results at the cost of routine delivery; it still fell below one-shot in the original tight case. In the four-schedule study, moving the alert from first to last within a 128 Kb/s crowded burst reduced one-shot DDR by 43.6 points and reserved AURA DDR by 15.2 points. Reservation beat one-shot under the tested 128 Kb/s late-alert bursts, but several other tight-case paired differences from one-shot spanned zero. The results do not establish broad performance superiority or Internet-safe congestion fairness. Packet Tracer confirms the current routed HTTP page, but it does not run the custom transport. The gateway WAN address did not serve its device page from PC3. DHCP failed for the IoT clients in this lab, so the saved topology uses static internal addresses. The detector responded to a manual smoke increase, but the Old Car did not produce an observed alarm in Main Wiring Closet. The post-move gateway Devices page listed only `TEMP-SENSOR`, so smoke registration and gateway telemetry need repair. Packet Tracer's installed Environment help says the car's smoke output depends on physical container volume; the closet may still dilute it, but the cause of the failed car test was not established. The [remaining desktop checks](PENDING_DESKTOP_CHECKS.md) state the release gates. The gateway's lab HTTP interface and wireless settings should be treated as a demonstration configuration, not a production security design.
