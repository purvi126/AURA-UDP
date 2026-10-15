# Implementation status

Updated 2026-10-15.

## Working

- NS2 2.35 runs baseline, fixed Selective Repeat, and deadline-aware AURA over live data and ACK paths.
- The Python analysis computes unique delivery, timely critical delivery, routine delivery, class balance, received competing-flow goodput, delay, logical goodput, retry overhead, and sender abandonments. Unsent generated messages do not produce negative retry overhead.
- The checked-in 30-seed sweep covers moderate loss, tight deadlines, and higher message rate: 270 runs. A second 360-run ablation isolates retry feasibility and window decisions. Raw per-run, aggregate, paired, and configuration CSV/JSON files are under experiments/results/multiseed and experiments/results/ablation.
- The dashboard compares the sweep and lets a reader step through actual sample message events. A dependency-free Node check validates its script, element references, and data paths in CI.
- The Packet Tracer 9.0 file has two routed LANs, a transit link, four PCs, Server0, a DLC100 Home Gateway, native Temperature Monitor, Smoke Detector, and a wireless monitoring tablet. Both native sensors are registered and visible in the gateway's Devices page. Static internal addresses were assigned after DHCP failed.
- PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. PC1 and PC2 each received four of four server ping replies; PC3 received four of four replies from PC2. PC0 loaded the updated custom HTTP page from Server0 across both routers. PC3's earlier HTTP check was on the same server LAN and is labeled accordingly.
- The sender now checks whether a critical retry is estimated to arrive before its absolute deadline, admits critical alerts by earliest deadline, reserves an opening for routine traffic after three critical admissions, and records bounded 4–6-message window changes. The 30-seed sweeps were regenerated for this implementation. The results show a retry-cost reduction from the feasibility rule under high load but no demonstrated DDR gain from that rule; see [the research evaluation](RESEARCH_EVALUATION.md).

## Release

Core connectivity, native IoT registration, HTTP, automated tests, and the multi-seed reproduction checks have passed. The [validation record](VALIDATION.md) lists direct observations and remaining limits. The [v1.1.0 verified engineering release](https://github.com/purvi126/AURA-UDP/releases/tag/v1.1.0) is published from the CI-validated `f314c59` commit with the editable `.pkt` file, current measured CSVs, and evidence visuals attached.

The sweep is descriptive. AURA improved mean deadline delivery in moderate and high-rate cases, but did not beat baseline in the tight-deadline case; fixed SR retained higher PDR. Throughput and logical goodput use a common configured observation window. The v1.0.0 release remains a frozen prior checkpoint.

## GitHub and recovery

The repository is [purvi126/AURA-UDP](https://github.com/purvi126/AURA-UDP) on `main`. Pushed milestones include `84ba5af` (30-seed evaluation), `5672b20` (native IoT topology), `7727f9c` (first review release), and `f314c59` (corrected protocol, measurements, visuals, and CI). The `checkpoint-2026-10-13-evaluation`, `checkpoint-2026-10-13-iot`, `v1.0.0`, and `v1.1.0` tags allow inspection of those stages. See [ROLLBACK.md](ROLLBACK.md) for non-destructive recovery.
