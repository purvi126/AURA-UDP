# AI setup progress

Updated 2026-10-12.

## Completed

- Initialized a new local Git repository on `main` at `D:\projects\AURA-UDP`.
- Implemented live NS2 2.35 datagram simulations for baseline UDP-like one-shot delivery, fixed Selective Repeat, and AURA.
- Added independently lossy data/ACK paths, background CBR load, variable delay, deadline, loss probability, message interval and documented seed.
- Added CSV event metrics, measured sample and stress scenarios, and an SVG comparison chart.
- Added Packet Tracer 9.0 device, cabling, address, route and verification guide, including supported Home Gateway, Temperature Meter and Smoke Detector. Editable `.pkt` topology is not yet complete; UI placement began but full configuration and connectivity could not be verified.
- Added protocol, academic review, README, license, and Python CI workflow.

## Validation

- `python3 -m unittest discover -s tests -v`: 7 tests passed in WSL with NS2 2.35.
- `python3 scripts/experiments.py --output experiments/results/sample`: passed with seed 7.
- Stress run: loss .3, delay 80 ms, background 180 Kb/s, deadline 120 ms, seed 11: passed. DDR was .125 for all three modes; no AURA improvement is claimed.
- NAM visualization has not been opened or validated; trace output is produced.

## Git and publication

- Commits: `cc746c0` repository and CI; `02bb2d8` NS2 transports; `f37b704` analytics, runs, tests; `0be014d` documentation; `6772261` expanded protocol tests and Packet Tracer guide.
- GitHub CLI 2.102.0 was installed through winget. Official GitHub device authentication was started, and the user was given the one-time login code. Remote publication remains pending authentication.

## Next actions

1. Verify local commits and GitHub authentication. Create or reuse public remote and push when available.
2. Build and verify an editable Packet Tracer topology if UI automation permits; otherwise retain the complete guide.
3. Run broader multi-seed and traffic-intensity sweeps before drawing performance conclusions.
4. Prepare a release only after Packet Tracer and remote publication criteria are satisfied.
