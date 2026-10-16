# Implementation status

Updated 2026-10-16.

## Working

- NS2 2.35 runs baseline, fixed Selective Repeat, and deadline-aware AURA over live data and ACK paths.
- The Python analysis computes unique delivery, timely critical delivery, routine delivery, class balance, received competing-flow goodput, delay, logical goodput, retry overhead, and sender abandonments. Unsent generated messages do not produce negative retry overhead.
- The checked-in 30-seed sweep covers moderate loss, tight deadlines, and higher message rate: 270 runs. A second 360-run ablation isolates retry feasibility and window decisions. Fresh seed indices 31–60 repeat both sweeps, for 1,260 total runs. Raw per-run, aggregate, paired, and configuration CSV/JSON files are under experiments/results/multiseed, experiments/results/ablation, and experiments/results/holdout.
- A further 480-run sweep uses 120 messages, fresh seed indices 61–90, and four longer conditions. Two conditions have two competing CBR senders and a six-packet bottleneck queue. Per-flow received rates and their Jain index are recorded. The full project now has 1,740 measured runs; see [the robustness results](../experiments/results/robustness/summary.csv).
- The dashboard compares the sweep and lets a reader step through actual sample message events. A dependency-free Node check validates its script, element references, and data paths in CI.
- The dashboard now has a separate long-workload stress panel. A fixed-scale [SVG chart](../experiments/plots/robustness.svg) keeps both positive and negative DDR results legible on GitHub.
- The Packet Tracer 9.0 file has two routed LANs, a transit link, four PCs, Server0, a DLC100 Home Gateway, native Temperature Monitor, Smoke Detector, and a wireless monitoring tablet. Both native sensors are registered and visible in the gateway's Devices page. Static internal addresses were assigned after DHCP failed.
- An Old Car named `SMOKE-TRIGGER-CAR` was added beside the Smoke Detector. Its Packet Tracer specification identifies Alt-click as the control and smoke increase as its effect. The full sensor alarm transition is still unverified.
- PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. PC1 and PC2 each received four of four server ping replies; PC3 received four of four replies from PC2. PC0 loaded the updated custom HTTP page from Server0 across both routers. PC3's earlier HTTP check was on the same server LAN and is labeled accordingly.
- The sender now checks whether a critical retry is estimated to arrive before its absolute deadline, admits critical alerts by earliest deadline, reserves an opening for routine traffic after three critical admissions, and records bounded 4–6-message window changes. The 30-seed sweeps were regenerated for this implementation. The results show a retry-cost reduction from the feasibility rule under high load but no demonstrated DDR gain from that rule; see [the research evaluation](RESEARCH_EVALUATION.md).
- The longer experiments show a material limitation: under two competing flows, one-shot delivery beats AURA on critical-alert DDR. The feasibility decision saves some retry traffic but still has no demonstrated DDR gain. See the [research evaluation](RESEARCH_EVALUATION.md) before making performance claims.

## Release

Core connectivity, native IoT registration, HTTP, automated tests, and the original multi-seed reproduction checks have passed. The [validation record](VALIDATION.md) lists direct observations and remaining limits. The [v1.2.0 research evaluation release](https://github.com/purvi126/AURA-UDP/releases/tag/v1.2.0) is a stable checkpoint with the first 1,260 runs. The newer long-workload results and smoke stimulus are on `main` and have not been released as a new version.

The sweeps are descriptive. AURA improved mean deadline delivery in some moderate and high-rate cases, but underperformed one-shot delivery in the new two-flow cases. Throughput and logical goodput use a common configured observation window within each condition. The v1.0.0 and v1.1.0 releases remain earlier checkpoints.

## GitHub and recovery

The repository is [purvi126/AURA-UDP](https://github.com/purvi126/AURA-UDP) on `main`. The long-workload simulation, measured results, dashboard, and Packet Tracer smoke stimulus were pushed in separate commits so each change can be inspected or reversed. The `v1.0.0`, `v1.1.0`, and `v1.2.0` tags remain published checkpoints. See [ROLLBACK.md](ROLLBACK.md) for non-destructive recovery.
