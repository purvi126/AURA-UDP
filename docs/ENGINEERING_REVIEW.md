# Engineering review

Reviewed initially on 2026-10-15; software and documentation checks were extended through 2026-10-17. The Packet Tracer alarm transition still needs direct observation.

## Corrections made

| Area | Finding | Correction |
|---|---|---|
| NS2 protocol | A critical alert could occupy a sender window slot after its deadline until the next retry timer fired. | Schedule an expiration event at the absolute deadline and skip expired queued alerts when admitting new traffic. |
| Analytics | Throughput and logical goodput used the last logged event, giving transports different observation windows. | Log a common simulation finish event and divide by the interval from first generation to finish. Legacy logs retain a documented fallback. |
| Analytics | Malformed or out-of-order event logs could silently produce plausible metrics. | Reject empty logs, missing columns, invalid times, unknown events, duplicate generation, changing classes, and events after finish. |
| Experiment runners | Invalid probabilities, negative timing, or a missing NS2 executable failed late or with a traceback. | Validate arguments before writing output and report actionable command-line errors. |
| Packet Tracer evidence | PC3 and Server0 share a LAN, so their HTTP exchange had been mislabeled as routed. | Load the page from sensor-side PC0 across both routers, update Server0's saved page and the editable topology, and add a new capture. |
| Visuals | The original chart could not show the full 30-seed sweep. The README embedded tiny Packet Tracer screenshots. | Render both sample and full-sweep SVG plots with explicit scales; use a readable vector evidence guide and link the original captures. |
| Local review | The README's server command listened on all interfaces by default. | Bind the review server to 127.0.0.1 in the documented command. |
| Research logic | Reliability alone could hide missed alert deadlines or wasted late retries. | Keep every generated critical alert in the DDR denominator; log sender `abandon` decisions and compare with a no-feasibility ablation. |
| Traffic impact | A critical-first sender could obscure starvation of routine traffic or effects on the CBR competitor. | Track routine PDR, class delivery balance, and received CBR goodput; disclose the tight-deadline degradation. |
| Reproducibility | One shared RNG could couple data and ACK loss draws. | Give the two packet-error models separately seeded RNG streams and pair runs by NS2 substream index. |
| Arrival sensitivity | A regular 128 Kb/s workload concealed how late alerts in a burst change queueing and deadline delivery. | Cross two arrival spacings with two alert positions and two link rates, then save 1,440 fresh-seed runs with paired schedule and transport intervals. |

## Security and performance

The dashboard is static, has no account or database, and inserts CSV text through DOM text nodes rather than HTML markup. Its data paths and JavaScript syntax are checked in CI. The Packet Tracer HTTP page is a lab connectivity demonstration; its gateway login and wireless setup are not a production security design. No credentials are required by the NS2 or Python scripts.

The workload is intentionally finite: 30 or 120 generated messages per NS2 run, at most five sends per reliable message, and 3,540 checked-in measured runs across the short, held-out, robustness, reservation, and sensitivity studies. The Python scripts process one event log at a time. No long-lived worker, listener, or retained browser subscription is part of this project. Larger traces would warrant streaming the metrics parser and benchmarking memory use before claiming scale.

## Verification and limits

Run `python3 -m unittest discover -s tests -v` under WSL with NS2 and `node scripts/check_dashboard.mjs` from the repository root. Reproduce the full sweeps with the commands in [VALIDATION.md](VALIDATION.md). The CI workflow checks NS2 integration, dashboard assets, and short smoke sweeps for the multi-seed experiment runners on each push. The 2026-10-17 local check passed 24 tests; [CI run 39009613371](https://github.com/purvi126/AURA-UDP/actions/runs/39009613371) passed for the new dashboard panel.

Packet Tracer 9.0 was inspected with the editable topology open: the two routers, two switches, monitoring server, gateway, tablet, Temperature Monitor, and Smoke Detector are present. The saved evidence verifies routed HTTP and gateway registration. A triggered smoke alarm was not verified, and Packet Tracer does not execute the AURA transport. The 30-seed NS2 results cover selected synthetic conditions; they are not a general performance guarantee. The feasibility ablation does not show a DDR gain. The reservation and burst studies show condition-dependent alert gains alongside lower routine delivery. The 80 ms RTO floor and bounded window are lab heuristics, not a complete UDP congestion controller. NAM remains optional and was not changed. The new dashboard panel has passed static checks but still needs the [visual check](PENDING_DESKTOP_CHECKS.md) when the desktop is available.
