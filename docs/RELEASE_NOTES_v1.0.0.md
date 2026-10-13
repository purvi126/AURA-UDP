# AURA-UDP v1.0.0 — review release

This document describes the frozen v1.0.0 release. The current branch later corrected critical-alert expiration timing and the throughput observation window, then reran the measured datasets. Use the current README and CSVs for results from current source.

This release provides a reproducible NS2 2.35 comparison of one-shot datagrams, fixed Selective Repeat, and deadline-aware AURA transport, plus an editable Cisco Packet Tracer 9.0 smart-campus demonstration.

## Verified in this release

- Application messages and ACKs traverse NS2 agents and links. AURA uses critical-first queue admission, message deadlines, RTT-based timeout updates, Karn's rule, and retry backoff.
- Nine Python/NS2 tests pass, covering delivery, loss, ACK loss, duplicate suppression, out-of-order arrival, deadline expiration, adaptive timeout, and critical-first admission.
- The 30-seed comparison covers three conditions and 270 actual simulation runs. A fresh run reproduced the checked-in run, summary, and paired CSV files byte for byte.
- The Packet Tracer topology has two routed LANs, a monitor server, a Home Gateway, and registered native temperature and smoke sensors. The tablet displayed both sensors and their fields. Three remaining PC route checks each returned four replies with zero loss. The operations PC loaded the custom AURA HTTP page.
- GitHub Actions installs NS2 and runs the integration tests and a three-seed sweep on each push.

## Start here

Open the [README](https://github.com/purvi126/AURA-UDP/blob/v1.0.0/README.md) for setup and demonstration commands. The [validation record](https://github.com/purvi126/AURA-UDP/blob/v1.0.0/docs/VALIDATION.md) lists observed checks, and the [Packet Tracer guide](https://github.com/purvi126/AURA-UDP/blob/v1.0.0/packet_tracer/documentation/BUILD_GUIDE.md) has the address plan. Download the editable `.pkt` topology from the source archive or repository.

## Interpretation and limits

The sweep is descriptive for short synthetic scenarios. AURA had higher mean deadline delivery in moderate-loss and high-rate settings, tied Selective Repeat and trailed baseline in the tight-deadline setting, and had lower PDR than fixed Selective Repeat in all three. These results do not establish general superiority. Packet Tracer verifies campus routing, HTTP, and gateway registration; it does not run the AURA transport. DHCP failed for the IoT clients in this lab, so their saved addresses are static. A triggered smoke alarm transition was not verified.

The [rollback guide](https://github.com/purvi126/AURA-UDP/blob/v1.0.0/docs/ROLLBACK.md) explains the checkpoint tags and how to restore this release without rewriting history.
