# Validation record

Packet Tracer connectivity was checked on 2026-10-13 with Packet Tracer 9.0 on Windows. The software checks were refreshed on 2026-10-15 with NS2 2.35 under Ubuntu WSL. These observations refer to the saved topology and experiment configuration.

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
| Smoke stimulus device | On 2026-10-16, an Old Car named `SMOKE-TRIGGER-CAR` was added beside `SMOKE-SENSOR` in the saved topology. Packet Tracer's device specifications identify the Old Car as a smoke source and Alt-click as its control. The sensor alarm transition remains unverified. |
| Python and NS2 tests | Twenty-one tests passed locally on 2026-10-16, including the original transport checks plus a 120-message, two-flow NS2 integration run and received-flow fairness calculation |
| Transport sweep | 30 seeds × 3 conditions × 3 modes = 270 NS2 runs; a second full sweep reproduced `runs.csv`, `summary.csv`, and `paired.csv` byte for byte |
| AURA ablation | 30 seeds × 3 conditions × 4 policies = 360 NS2 runs; a second full sweep reproduced `runs.csv`, `summary.csv`, and `paired.csv` byte for byte |
| Fresh-seed validation | Seed indices 31–60 repeated the 270-run transport sweep and 360-run ablation; a second execution reproduced the held-out `runs.csv` and `paired.csv` byte for byte |
| Long-workload robustness | Seed indices 61–90 produced 480 additional runs across four 120-message conditions, including two conditions with two CBR flows and a six-packet queue. The generated count, variant keys, DDR bounds, and two-flow fairness fields were checked. |
| Dashboard | Node asset and element check passed after adding the long-workload results panel |
| CI | The project workflow installs NS2, runs the tests, checks dashboard syntax/data paths, and executes three-seed smoke sweeps for both comparison and ablation on push |

The new [routed HTTP capture](../packet_tracer/documentation/media/routed-http-pc0.jpg) shows PC0's page load from the sensor LAN across both routers. The older [PC3 HTTP capture](../packet_tracer/documentation/media/server-http.jpg) is a same-LAN check. The [gateway screenshot](../packet_tracer/documentation/media/gateway-devices.jpg) shows both registered sensors and their displayed fields. Sensor readings reflect one simulator instant and are not experimental performance data.

Reproduce the software checks from `/mnt/d/projects/AURA-UDP`:

```bash
python3 -m unittest discover -s tests -v
node scripts/check_dashboard.mjs
python3 scripts/multiseed.py --output /tmp/aura-check
python3 scripts/ablation.py --output /tmp/aura-ablation-check
python3 scripts/multiseed.py --first-seed 31 --output /tmp/aura-heldout-check
python3 scripts/ablation.py --first-seed 31 --output /tmp/aura-heldout-ablation-check
python3 scripts/robustness.py --output /tmp/aura-robustness-check
cmp experiments/results/multiseed/runs.csv /tmp/aura-check/runs.csv
cmp experiments/results/multiseed/summary.csv /tmp/aura-check/summary.csv
cmp experiments/results/multiseed/paired.csv /tmp/aura-check/paired.csv
cmp experiments/results/ablation/runs.csv /tmp/aura-ablation-check/runs.csv
cmp experiments/results/ablation/summary.csv /tmp/aura-ablation-check/summary.csv
cmp experiments/results/ablation/paired.csv /tmp/aura-ablation-check/paired.csv
cmp experiments/results/holdout/multiseed/runs.csv /tmp/aura-heldout-check/runs.csv
cmp experiments/results/holdout/ablation/runs.csv /tmp/aura-heldout-ablation-check/runs.csv
cmp experiments/results/robustness/runs.csv /tmp/aura-robustness-check/runs.csv
```

The 30-seed sweeps are descriptive for three short and four longer synthetic scenarios. The feasibility rule saved retry traffic under high message rate and two-flow congestion but did not demonstrate a DDR gain. In both two-flow conditions, one-shot delivery exceeded AURA's deadline delivery. The results do not establish broad performance superiority or Internet-safe congestion fairness. Packet Tracer confirms routing, HTTP, and IoT registration; it does not run the custom transport. The gateway WAN address did not serve its device page from PC3. DHCP failed for the IoT clients in this lab, so the saved topology uses static internal addresses. A smoke alarm transition was not verified. The gateway's lab HTTP interface and wireless settings should be treated as a demonstration configuration, not a production security design.
