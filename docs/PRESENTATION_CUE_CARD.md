# AURA-UDP presentation cue card

Keep this page open during the review. Show one result from each tool and explain what it proves.

## Before speaking

Open `ns2/run.tcl`, `python/analysis/metrics.py`, the [robustness chart](../experiments/plots/robustness.svg), the [main topology](../packet_tracer/topology/AURA-UDP-campus.pkt), the [evidence guide](../packet_tracer/documentation/EVIDENCE_GUIDE.md), and the [green CI run](https://github.com/purvi126/AURA-UDP/actions/runs/40938626417). Keep the car OFF until the live smoke demonstration.

## Ten-minute order

| Time | Show | Say |
|---|---|---|
| 0–1 min | Project title | “A critical alert is useful only if it arrives before its deadline. We measure timely delivery, not just eventual arrival.” |
| 1–4 min | `run.tcl`: `generate`, `pump`, `transmit`, `timeout`, `on_ack`, `recv` | “AURA queues messages, gives critical alerts deadlines, retries when useful, and adapts its timer and sender window from ACK feedback.” |
| 4–5 min | `metrics.py`: `calculate` | “DDR is on-time critical alerts divided by *all generated* critical alerts. PDR counts eventual unique deliveries.” |
| 5–6 min | One-run output, then robustness chart | “One run illustrates the code. The saved multi-seed results support the comparison. AURA helps in moderate loss but loses to one-shot in some tight or congested cases.” |
| 6–8 min | Packet Tracer PC0 and Tablet PC0 | “PC0 reaches `http://10.10.30.10` through the two routers. The tablet reaches the Home Gateway at `http://192.168.25.1` and shows registered sensors.” |
| 8–9 min | Car **Interact** and gateway, or clean evidence pair | “In the small chamber, physical car activation produced exhaust, detector Level 100/state 1, and an active gateway alarm.” |
| 9–10 min | CI and release | “The code, experiments, tests, and topology are available in the repository and v1.3.0 release.” |

## Commands to prepare in WSL

```bash
cd /mnt/d/projects/AURA-UDP
python3 scripts/demo_ns2_pipeline.py
ns ns2/run.tcl aura 0.15 40 80 300 7 /tmp/aura-review
python3 python/analysis/metrics.py /tmp/aura-review/events.csv
head -n 12 /tmp/aura-review/events.csv
head -n 12 /tmp/aura-review/control.csv
```

`events.csv` records what happened to each message; `control.csv` records sender decisions. If the live simulator or gateway is slow, show the saved [pointer-free car and HTTP captures](../packet_tracer/documentation/EVIDENCE_GUIDE.md) and identify them as recorded tests.

The first command is the clearest proof of the runtime connection: it displays NS2's own completion output, the CSV it produced, and Python's result from that CSV in one terminal view. There is no separate NS2 client/server application window; `ns2.nam` is an optional graphical packet animation.

## Boundaries to state plainly

- NS2 evaluates the application-level transport; Packet Tracer demonstrates campus routing and native IoT response. They are separate.
- AURA reached 93.3% DDR versus 81.7% for one-shot under the original moderate-loss workload. Under the original tight deadline, AURA reached 10.4% versus 12.9% for one-shot.
- The detector's 30% Specifications text conflicts with an earlier Alarm-off reading near Level 34.18. No threshold change was verified. The chamber car test triggered at Level 100.
- The submitted PDF describes an earlier Main Wiring Closet saved arrangement. The later [v1.3.0 topology](https://github.com/purvi126/AURA-UDP/releases/tag/v1.3.0) places the car and detector together in `SMOKE-TEST-CHAMBER` for the verified physical-car test.
