# AURA-UDP

[![Python and NS2 checks](https://github.com/purvi126/AURA-UDP/actions/workflows/python.yml/badge.svg)](https://github.com/purvi126/AURA-UDP/actions/workflows/python.yml)

**Deadline-Aware Adaptive Reliable Transport for Critical IoT Communication Using NS2 and Cisco Packet Tracer**

This Computer Networks Lab project studies whether application-layer reliability and deadline awareness help safety alerts in a smart-campus network. It compares one-shot datagrams, fixed Selective Repeat, and an adaptive deadline-aware variant in **NS2 2.35**. A separate [Packet Tracer build guide](packet_tracer/documentation/BUILD_GUIDE.md) explains a campus connectivity demonstration. Packet Tracer does not implement AURA.

## Architecture

```mermaid
flowchart LR
  S[Sensor and alert source] --> R[NS2 router<br/>128 Kb/s bottleneck] --> D[Monitoring receiver]
  B[Background CBR source] --> R
  D -- ACKs, SR and AURA --> S
  D --> E[Application event CSV] --> M[Python metrics and SVG plot]
```

Numbered datagrams and ACKs are carried by real NS2 `Agent/Message` instances. The sender controls a four-message window, retries individually and suppresses duplicate delivery. AURA adds critical-first admission, absolute deadlines, RTT-based RTO, Karn's rule and timeout backoff. See [protocol details](docs/PROTOCOL.md). The novelty here is the *combination and evaluation* of established mechanisms in this lab scenario; no claim of a new transport standard is made.

## Requirements and quick start

- Ubuntu WSL with NS2 2.35 (`ns` on `PATH`)
- Python 3.10 or newer, standard library only
- Cisco Packet Tracer 9.0 for the separate topology demonstration

From `/mnt/d/projects/AURA-UDP`:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/experiments.py --output experiments/results/sample
python3 scripts/multiseed.py
python3 python/analysis/plot.py experiments/results/sample/summary.csv experiments/plots/sample.svg
python3 -m http.server 8000
```

Run a single mode:

```bash
ns ns2/run.tcl aura 0.15 40 80 300 7 /tmp/aura-demo
python3 python/analysis/metrics.py /tmp/aura-demo/events.csv
```

Open `http://localhost:8000/python/dashboard/` to explore the measured CSVs. The NS2 command arguments are `mode loss_probability delay_ms background_kbps deadline_ms seed output_directory [interval_ms]`. The output contains `events.csv`, `ns2.tr`, and `ns2.nam`. NAM is optional for analysis. Modify the arguments to vary loss, delay, congestion, message rate and deadlines. Each mode uses the same configured topology, traffic schedule and initial seed.

## Measured sample

The checked-in sample comes from `loss=0.15`, `delay=40 ms`, `background=80 Kb/s`, `deadline=300 ms`, `seed=7`. It is a single short run and supports no broad performance claim. Open [sample results](experiments/results/sample/summary.csv) and [the plot](experiments/plots/sample.svg). Re-run to regenerate them. Under a stronger scenario, `loss=0.3`, `delay=80 ms`, `background=180 Kb/s`, `deadline=120 ms`, `seed=11`, AURA did **not** improve DDR over the other modes; [stress results](experiments/results/stress/summary.csv) and [stress plot](experiments/plots/stress.svg) show the limitation.

## Demonstration

1. Run the tests and experiments above. Compare PDR, DDR, delay, retransmission overhead and goodput in the CSV and SVG.
2. Inspect `events.csv` for `generate`, `send`, `timeout`, `receive`, `duplicate`, `deliver`, `late`, `ack`, and `expire` transitions.
3. Optionally open `ns2.nam` with NAM if installed; no result calculation depends on NAM.
4. Open the editable [Packet Tracer campus topology](packet_tracer/topology/AURA-UDP-campus.pkt). From PC3, browse to `http://10.10.30.10` to see the AURA campus page. From Tablet PC0, browse to `http://192.168.25.1`, sign in to the lab gateway, and inspect the registered temperature and smoke devices. The [build guide](packet_tracer/documentation/BUILD_GUIDE.md) has the full address plan.

| Routed HTTP page | Registered native IoT devices |
|---|---|
| ![Custom AURA page loaded from PC3](packet_tracer/documentation/media/server-http.jpg) | ![Gateway page showing both sensors and telemetry fields](packet_tracer/documentation/media/gateway-devices.jpg) |

## Current validation and limits

The [30-seed sweep](experiments/results/multiseed/summary.csv) covers moderate loss, tight deadlines, and twice the message rate: 270 NS2 runs. In moderate loss, mean DDR was 0.917 for AURA, 0.867 for fixed SR, and 0.863 for baseline. At the high message rate, it was 0.892, 0.658, and 0.883. With a tight deadline, AURA and SR both reached 0.121, below baseline's 0.163. AURA's PDR remained below fixed SR in all three conditions. See the [per-run results](experiments/results/multiseed/runs.csv), [paired differences](experiments/results/multiseed/paired.csv), and [settings](experiments/results/multiseed/config.json). These descriptive comparisons do not establish general superiority.

The Packet Tracer file includes a DLC100 Home Gateway, native Temperature Monitor, and Smoke Detector. Both sensors have wireless links and appear by name in the gateway's device list on Tablet PC0. The tablet showed their temperature and smoke-level fields. PC1 and PC2 each received four of four replies from Server0; PC3 received four of four replies from PC2. PC3 loaded the custom AURA HTTP page from Server0. See the [validation record](docs/VALIDATION.md). These are connectivity observations in Packet Tracer, not transport performance measurements.

## Limits

No adaptive window sizing, router queue priority, custom C++ UDP header, or statistical significance test is implemented. The logical 64-byte goodput assumption is documented. See [progress](docs/AI_SETUP_PROGRESS.md).

MIT licensed; see [LICENSE](LICENSE).

For a published checkpoint or safe recovery, see the [rollback guide](docs/ROLLBACK.md).
