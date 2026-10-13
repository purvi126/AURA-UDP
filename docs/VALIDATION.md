# Validation record

Checked on 2026-10-13 with Packet Tracer 9.0 on Windows and NS2 2.35 under Ubuntu WSL. These observations refer to the committed topology and experiment configuration.

| Check | Observation |
|---|---|
| Routed packet, PC0 to Server0 | Simple ICMP PDU successful after address resolution |
| PC1 to Server0 (`10.10.30.10`) | Four replies, zero lost |
| PC2 to Server0 (`10.10.30.10`) | Four replies, zero lost |
| PC3 to PC2 (`10.10.10.13`) | Four replies, zero lost |
| PC3 HTTP to Server0 | `http://10.10.30.10` rendered the custom AURA campus page |
| Native IoT registration | Tablet PC0 opened Home Gateway at `192.168.25.1`; Devices listed both `TEMP-SENSOR` and `SMOKE-SENSOR` |
| IoT telemetry view | Temperature and smoke alarm/level fields appeared on the gateway page |
| Python and NS2 tests | Nine tests passed locally, including critical-first admission and no critical send after its deadline |
| Seed sweep | 30 seeds x 3 conditions x 3 modes = 270 NS2 runs; fresh `runs.csv`, `summary.csv`, and `paired.csv` matched the committed files byte for byte |
| CI | The project workflow installs NS2, runs the nine tests, and executes a three-seed smoke sweep on push |

The saved [HTTP screenshot](../packet_tracer/documentation/media/server-http.jpg) shows PC3's routed page load. The [gateway screenshot](../packet_tracer/documentation/media/gateway-devices.jpg) shows both registered sensors and their displayed fields. Sensor readings reflect one simulator instant and are not experimental performance data.

Reproduce the software checks from `/mnt/d/projects/AURA-UDP`:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/multiseed.py --output /tmp/aura-check
cmp experiments/results/multiseed/runs.csv /tmp/aura-check/runs.csv
cmp experiments/results/multiseed/summary.csv /tmp/aura-check/summary.csv
cmp experiments/results/multiseed/paired.csv /tmp/aura-check/paired.csv
```

The 30-seed sweep is descriptive for three short synthetic scenarios. It does not establish statistical significance or broad performance superiority. Packet Tracer confirms routing, HTTP, and IoT registration; it does not run the custom transport. The gateway WAN address did not serve its device page from PC3. DHCP failed for the IoT clients in this lab, so the saved topology uses static internal addresses. A smoke alarm transition was not verified.
