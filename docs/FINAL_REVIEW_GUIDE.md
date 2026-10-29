# Final review: AURA-UDP

**Project:** Deadline-Aware Adaptive Reliable Transport for Critical IoT Communication Using NS2 and Cisco Packet Tracer  
**Team:** Purvi Valmeti (24BCE2191) and M Harshita Sri (24BCE2471)  
**Repository:** https://github.com/purvi126/AURA-UDP

## One-minute explanation

Imagine a campus smoke detector sending an urgent alert while routine sensor readings and other network traffic share a slow, lossy link. A packet can arrive eventually yet miss the alert's deadline. AURA-UDP asks whether a sender that tracks deadlines, retries selectively, adapts its timer, and reserves capacity for alerts can improve **timely** delivery. NS2 runs and measures that transport experiment. Cisco Packet Tracer separately shows the campus network, a routed HTTP path, a Home Gateway, and native temperature and smoke devices. The two tools are complementary demonstrations; there is no live data bridge between them.

## What the assignment PDF means for this project

The LMS PDF lists **possible** NS-2/NS-3 network simulation topics and shows Packet Tracer examples. Its large network images are examples, not a required device count or topology. AURA fits the IoT communication and network performance area through a custom application-level datagram policy, loss/load experiments, and a separate Packet Tracer IoT campus. The project does not claim an MQTT-versus-CoAP comparison, native TCP Reno study, or NS3 implementation. Keep the scope specific when presenting it.

## Five-minute demonstration order

| Time | Show | Say |
|---|---|---|
| 0:00–0:45 | This page and the [README architecture](../README.md#architecture) | The alert must arrive before its deadline; NS2 measures this, Packet Tracer illustrates the campus. |
| 0:45–1:45 | [`ns2/run.tcl`](../ns2/run.tcl) and a fresh one-run trace | Show generation, send, receive, delivery, and ACK events. Use the second command below to show a verified `abandon` decision; `control.csv` records window/RTO changes. |
| 1:45–2:45 | [Multi-seed chart](../experiments/plots/multiseed.svg) and [evaluation table](RESEARCH_EVALUATION.md#three-mode-results) | Explain DDR denominator, baseline/SR/AURA, and the tight-deadline failure. |
| 2:45–3:30 | [Four-schedule chart](../experiments/plots/sensitivity.svg) or dashboard step 05 | Show how burst timing and alert position are varied separately; discuss routine-delivery cost. |
| 3:30–4:30 | [Packet Tracer topology](../packet_tracer/topology/AURA-UDP-campus.pkt) | On PC0 load `http://10.10.30.10`; on Tablet PC0 show both registered devices at `http://192.168.25.1`. |
| 4:30–5:00 | [Packet Tracer evidence guide](../packet_tracer/documentation/EVIDENCE_GUIDE.md) | Show the paired gateway screenshots: car OFF versus ON and manual smoke adjustment before versus after. Explain that the two triggers were tested separately. |
If the reviewer asks for only one graph, use the [fixed-scale 120-message robustness chart](../experiments/plots/robustness.svg): it includes the conditions in which one-shot delivery beats original AURA. An honest failure case makes the conclusion defensible.

## Commands to prepare before opening Packet Tracer

From the repository root in Ubuntu WSL, with NS2 2.35 on `PATH`:

```bash
python3 -m unittest discover -s tests -v
ns ns2/run.tcl aura 0.15 40 80 300 7 /tmp/aura-final-demo
python3 python/analysis/metrics.py /tmp/aura-final-demo/events.csv
head -n 15 /tmp/aura-final-demo/events.csv
head -n 15 /tmp/aura-final-demo/control.csv
ns ns2/run.tcl aura 0.15 40 120 300 1 /tmp/aura-final-abandon 60 full
grep abandon /tmp/aura-final-abandon/events.csv
```

The single run is **illustration**, not proof of an average advantage. For aggregate results, use the saved 30-seed CSVs and [reproduction commands](RESEARCH_EVALUATION.md#reproduce-and-inspect). The dashboard is a static viewer for saved data; start a local server from the repository root with `python3 -m http.server 8000 --bind 127.0.0.1` if you want to show it. Keep that terminal running while the page is open.

## Claims to make precisely

| Safe statement | Boundary |
|---|---|
| The project has 3,540 checked-in NS2 runs across short, held-out, robustness, reservation, and sensitivity studies. | This counts runs, not independent real-world networks or a performance guarantee. |
| AURA reached 93.3% mean DDR in the original moderate-loss scenario versus 81.7% for one-shot. | In the original tight-deadline scenario it reached only 10.4% versus 12.9% for one-shot. |
| The retry-feasibility decision can reduce extra sends. | Its ablation has not established an improvement in DDR. |
| The reserved-alert candidate reduces alert starvation under some crowded loads. | It can lower routine PDR and does not consistently beat one-shot. |
| Packet Tracer routed HTTP, native IoT registration, and paired smoke-response gateway tests were observed. | Both physical car activation and manual smoke adjustment produced gateway alarm transitions. Packet Tracer does not execute the AURA transport protocol. |
See [academic review notes](ACADEMIC_REVIEW.md) for likely questions and [protocol details](PROTOCOL.md) for the exact sender rules. Avoid calling the NS2 `Agent/Message` implementation a deployed UDP stack or a new UDP packet header.

## Before the review

1. Confirm the live LMS has a **submitted** file and the correct assignment status. A PDF capture dated 26 October showed no submission at that moment; it cannot establish the current state. If submission is blocked, contact the course instructor promptly with the repository and report link.
2. Keep the [main Packet Tracer topology](../packet_tracer/topology/AURA-UDP-campus.pkt), the [historical Review 2 PDF and DOCX](reviews/README.md), and this guide ready. The Review 2 report is dated 15 October and should be labeled as a **past progress snapshot**. The main `.pkt` was updated after the manual GitHub edit to put the car and detector together in `SMOKE-TEST-CHAMBER`, with the car OFF; verify that placement when opening it for review.
3. Review the [Packet Tracer desktop status](PENDING_DESKTOP_CHECKS.md), [evidence guide](../packet_tracer/documentation/EVIDENCE_GUIDE.md), and [validation record](VALIDATION.md). The new car OFF/ON/recovery gateway images and routed HTTP image are pointer-free. The historical manual-smoke pair still shows a cursor. Confirm saved topology placement and CI before claiming the release is ready.
4. If time permits, visually reopen dashboard step 05. Desktop and narrow browser checks already passed on 2026-10-28 for all 16 control combinations.
5. Open the key files and commands before the session. If Packet Tracer or the dashboard cannot launch during review, use the saved topology, native screenshots, run logs, and CSVs while clearly identifying which checks were previously observed.
