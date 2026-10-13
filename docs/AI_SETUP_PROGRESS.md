# Implementation status

Updated 2026-10-13.

## Working

- NS2 2.35 runs baseline, fixed Selective Repeat, and deadline-aware AURA over live data and ACK paths.
- The Python analysis computes unique delivery, timely critical delivery, delay, logical goodput, and retry overhead. Unsent generated messages no longer produce negative retry overhead.
- The checked-in 30-seed sweep covers moderate loss, tight deadlines, and higher message rate: 270 runs. Raw per-run, aggregate, paired, and configuration CSV/JSON files are under experiments/results/multiseed.
- The dashboard compares the sweep and lets a reader step through actual sample message events.
- The Packet Tracer 9.0 file has two routed LANs, a transit link, four PCs, Server0, a DLC100 Home Gateway, native Temperature Monitor, Smoke Detector, and a wireless monitoring tablet. The IoT devices show wireless association and select Home Gateway as their IoT server. Static internal addresses were assigned after DHCP failed.
- PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. Server0 HTTP was On, and PC3 loaded its page at 10.10.30.10.
- Eight WSL integration/unit tests pass.

## Open verification

1. Recheck that TEMP-SENSOR and SMOKE-SENSOR appear in the gateway's registered-device list from Tablet PC0, which can load the gateway's login page. The list was empty before static sensor addressing. The gateway Internet address timed out from PC3.
2. Verify PC1 and PC2 to Server0 and PC3 to the sensor LAN, allowing for initial ARP resolution.
3. Recheck the saved Packet Tracer file after those steps.
4. Publish a release only when those checks and project tests pass. No release has been published.

The sweep is descriptive. AURA improved mean deadline delivery in moderate and high-rate cases, but did not improve it in the tight-deadline case; fixed SR retained higher PDR.
