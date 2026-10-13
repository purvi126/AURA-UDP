# AURA-UDP v1.1.0 — verified engineering update

This release updates the NS2 implementation, measured results, dashboard checks, and editable Packet Tracer demonstration. It supersedes the v1.0.0 source and CSVs for current results; the earlier tag remains available as a rollback checkpoint.

## What changed

- Critical alerts now free the AURA sender window at their absolute deadline, including while queued.
- Every transport run logs a common finish event. Throughput and logical goodput use the same observation window within each condition.
- Event parsing rejects malformed or inconsistent logs, and experiment commands validate their inputs before writing output.
- Sample and 30-seed charts use clear scales; the dashboard and its data paths have a dependency-free CI check.
- The Packet Tracer Server0 page uses larger text. Sensor-side PC0 loaded it across Router0 and Router1, correcting the previous description of PC3's same-LAN HTTP check.
- The README includes a readable vector evidence guide, a fresh PC0 capture, current measurements, and an engineering review.

## Verification

- Fourteen Python and NS2 tests passed locally.
- The full 30-seed sweep ran 270 NS2 simulations; a second sweep reproduced the checked-in run, summary, and paired CSV files byte for byte.
- Packet Tracer 9.0 showed the routed PC0 HTTP page and registered Temperature Monitor and Smoke Detector on the Home Gateway.
- GitHub Actions runs the tests, dashboard check, and a three-seed NS2 smoke sweep on each push.

## Limits

The results describe three short synthetic NS2 conditions and do not establish general superiority. Packet Tracer demonstrates connectivity and native IoT registration; it does not run AURA transport. A triggered smoke alarm was not verified. NAM remains optional. The gateway's HTTP interface and wireless setup are lab settings, not a production security design.
