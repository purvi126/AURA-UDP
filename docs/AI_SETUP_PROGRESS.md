# Implementation status

Updated 2026-10-13.

## Working

- NS2 2.35 runs baseline, fixed Selective Repeat, and deadline-aware AURA over live data and ACK paths.
- The Python analysis computes unique delivery, timely critical delivery, delay, logical goodput, and retry overhead. Unsent generated messages no longer produce negative retry overhead.
- The checked-in 30-seed sweep covers moderate loss, tight deadlines, and higher message rate: 270 runs. Raw per-run, aggregate, paired, and configuration CSV/JSON files are under experiments/results/multiseed.
- The dashboard compares the sweep and lets a reader step through actual sample message events.
- The Packet Tracer 9.0 file has two routed LANs, a transit link, four PCs, Server0, a DLC100 Home Gateway, native Temperature Monitor, Smoke Detector, and a wireless monitoring tablet. Both native sensors are registered and visible in the gateway's Devices page. Static internal addresses were assigned after DHCP failed.
- PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. PC1 and PC2 each received four of four server ping replies; PC3 received four of four replies from PC2. PC3 loaded the custom AURA page over HTTP from Server0.
- Nine WSL integration/unit tests pass, including direct priority and deadline assertions. A fresh 270-run sweep reproduced all three committed CSVs byte for byte.

## Release readiness

Core connectivity, native IoT registration, HTTP, automated tests, and the multi-seed reproduction checks have passed. The [validation record](VALIDATION.md) lists direct observations and remaining limits. Publish the review release after the final commit passes GitHub Actions.

The sweep is descriptive. AURA improved mean deadline delivery in moderate and high-rate cases, but did not improve it in the tight-deadline case; fixed SR retained higher PDR.

## GitHub and recovery

The repository is [purvi126/AURA-UDP](https://github.com/purvi126/AURA-UDP) on `main`. Earlier pushed milestones include `84ba5af` (30-seed evaluation and event trace), `5672b20` (native IoT topology), and `14868d2` (NS2 CI and rollback guide). The published `checkpoint-2026-10-13-evaluation` and `checkpoint-2026-10-13-iot` tags allow inspection of those stages. See [ROLLBACK.md](ROLLBACK.md) for non-destructive recovery. The remaining publication step is the review release after the final push's CI result is green.
