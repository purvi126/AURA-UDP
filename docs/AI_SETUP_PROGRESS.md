# Implementation status

Updated 2026-10-13.

## Working

- NS2 2.35 runs baseline, fixed Selective Repeat, and deadline-aware AURA over live data and ACK paths.
- The Python analysis computes unique delivery, timely critical delivery, delay, logical goodput, and retry overhead. Unsent generated messages no longer produce negative retry overhead.
- The checked-in 30-seed sweep covers moderate loss, tight deadlines, and higher message rate: 270 runs. Raw per-run, aggregate, paired, and configuration CSV/JSON files are under experiments/results/multiseed.
- The dashboard compares the sweep and lets a reader step through actual sample message events. A dependency-free Node check validates its script, element references, and data paths in CI.
- The Packet Tracer 9.0 file has two routed LANs, a transit link, four PCs, Server0, a DLC100 Home Gateway, native Temperature Monitor, Smoke Detector, and a wireless monitoring tablet. Both native sensors are registered and visible in the gateway's Devices page. Static internal addresses were assigned after DHCP failed.
- PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. PC1 and PC2 each received four of four server ping replies; PC3 received four of four replies from PC2. PC0 loaded the updated custom HTTP page from Server0 across both routers. PC3's earlier HTTP check was on the same server LAN and is labeled accordingly.
- Fourteen WSL integration/unit tests pass, including direct priority and deadline assertions, fixed observation time, and plot layout. The 270-run sweep was regenerated after critical alerts began freeing their sender window at the exact deadline. Current CSVs and README figures use that corrected implementation.

## Release

Core connectivity, native IoT registration, HTTP, automated tests, and the multi-seed reproduction checks have passed. The [validation record](VALIDATION.md) lists direct observations and remaining limits. The [v1.0.0 review release](https://github.com/purvi126/AURA-UDP/releases/tag/v1.0.0) is published from the CI-validated `7727f9c` commit with the `.pkt` file and measured CSVs attached.

The sweep is descriptive. AURA improved mean deadline delivery in moderate and high-rate cases, but did not beat baseline in the tight-deadline case; fixed SR retained higher PDR. Throughput and logical goodput now use a common configured observation window. The v1.0.0 release is a frozen prior checkpoint; current branch results differ from it.

## GitHub and recovery

The repository is [purvi126/AURA-UDP](https://github.com/purvi126/AURA-UDP) on `main`. Pushed milestones include `84ba5af` (30-seed evaluation and event trace), `5672b20` (native IoT topology), `14868d2` (NS2 CI and rollback guide), `1214329` (final topology, evidence, and nine-test validation), and `7727f9c` (current CI actions). The `checkpoint-2026-10-13-evaluation`, `checkpoint-2026-10-13-iot`, and `v1.0.0` tags allow inspection of those stages. See [ROLLBACK.md](ROLLBACK.md) for non-destructive recovery.
