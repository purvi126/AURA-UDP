# AI setup progress

Updated 2026-10-12.

## Completed

- Initialized a new local Git repository on `main` at `D:\projects\AURA-UDP`.
- Implemented live NS2 2.35 datagram simulations for baseline UDP-like one-shot delivery, fixed Selective Repeat, and AURA.
- Added independently lossy data/ACK paths, background CBR load, variable delay, deadline, loss probability, message interval and documented seed.
- Added CSV event metrics, measured sample and stress scenarios, SVG comparison charts, and a local CSV-backed interactive dashboard.
- Created editable Packet Tracer 9.0 `.pkt` topology with two routers, two switches, four PCs and a monitoring server. Configured router interfaces, static routes and all host addresses. A PC0-to-Server0 simple ICMP PDU succeeded after ARP learning. The guide covers adding a Home Gateway, Temperature Meter and Smoke Detector; these native IoT devices and registration are not yet in the `.pkt` file.
- Added protocol, academic review, README, license, and Python CI workflow.

## Validation

- `python3 -m unittest discover -s tests -v`: 7 tests passed in WSL with NS2 2.35.
- `python3 scripts/experiments.py --output experiments/results/sample`: passed with seed 7.
- Stress run: loss .3, delay 80 ms, background 180 Kb/s, deadline 120 ms, seed 11: passed. DDR was .125 for all three modes; no AURA improvement is claimed.
- NAM visualization has not been opened or validated; trace output is produced.
- Packet Tracer ICMP check: first two PC0-to-Server0 simple PDUs failed during address resolution; a subsequent PDU succeeded. HTTP and native IoT registration have not been verified.

## Git and publication

- Commits: `cc746c0` repository and CI; `02bb2d8` NS2 transports; `f37b704` analytics, runs, tests; `0be014d` documentation; `6772261` expanded protocol tests and Packet Tracer guide.
- GitHub CLI 2.102.0 was installed through winget and authenticated as `purvi126`. Created and pushed the public repository at <https://github.com/purvi126/AURA-UDP>; `main` tracks `origin/main`. GitHub Actions Python checks passed on the initial push.
- `7825c72` added the CSV-backed dashboard and stress plot before the initial push.

## Next actions

1. Add Home Gateway, Temperature Meter and Smoke Detector to the editable Packet Tracer topology and verify registration.
2. Verify HTTP service and all endpoint paths in Packet Tracer.
3. Run broader multi-seed and traffic-intensity sweeps before drawing performance conclusions.
4. Prepare a release only after the remaining Packet Tracer criteria are satisfied.
