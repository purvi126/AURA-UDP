# AI setup progress

Updated 2026-10-12.

## Completed

- Initialized a new local Git repository on `main` at `D:\projects\AURA-UDP`.
- Implemented live NS2 2.35 datagram simulations for baseline UDP-like one-shot delivery, fixed Selective Repeat, and AURA.
- Added independently lossy data/ACK paths, background CBR load, variable delay, deadline, loss probability, message interval and documented seed.
- Added CSV event metrics, measured sample and stress scenarios, and an SVG comparison chart.
- Added Packet Tracer 9.0 device, cabling, address, route and verification guide. Editable `.pkt` topology is not yet complete.
- Added protocol, academic review, README, license, and Python CI workflow.

## Validation

- `python3 -m unittest discover -s tests -v`: 5 tests passed in WSL with NS2 2.35.
- `python3 scripts/experiments.py --output experiments/results/sample`: passed with seed 7.
- Stress run: loss .3, delay 80 ms, background 180 Kb/s, deadline 120 ms, seed 11: passed. DDR was .125 for all three modes; no AURA improvement is claimed.
- NAM visualization has not been opened or validated; trace output is produced.

## Git and publication

- Local Git initialized; commit history and GitHub push status to be updated after commit.
- `gh` was initially absent. GitHub CLI installation was attempted via winget; authentication and remote publication are pending verification.

## Next actions

1. Verify local commits and GitHub authentication. Create or reuse public remote and push when available.
2. Build and verify an editable Packet Tracer topology if UI automation permits; otherwise retain the complete guide.
3. Run broader multi-seed and traffic-intensity sweeps before drawing performance conclusions.
4. Prepare a release only after Packet Tracer and remote publication criteria are satisfied.
