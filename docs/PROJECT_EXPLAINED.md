# AURA-UDP, explained without networking jargon

## The idea in one minute

Imagine a smart campus with a temperature monitor and a smoke detector. A normal reading can arrive a little late; a fire alert is useful only if it reaches the monitoring room quickly. A crowded or unreliable network can lose or delay either message.

This project asks: **can a sender give urgent alerts a better chance of arriving before a deadline, and what does that cost in extra transmissions?** It studies the question in a simulation. It is a lab demonstration, not a deployed emergency system.

## Why there are two programs

| Program | Job in this project | What it actually proves |
|---|---|---|
| **NS2** | Runs the baseline, Selective Repeat (SR), and AURA message-sending rules over simulated links with loss and competing traffic. | Measured delivery, timing, and retry results for the configured scenarios. |
| **Cisco Packet Tracer** | Opens an editable model of a campus with PCs, two routers, a monitoring server, a Home Gateway, and native temperature and smoke devices. | The saved campus routes packets, serves an HTTP page, and shows the two IoT devices registered on the gateway. |

**They do not exchange live data.** The Packet Tracer smoke detector does not feed the NS2 experiment, and the Packet Tracer web page does not run the AURA algorithm. The two programs illustrate the same campus story from different angles: NS2 measures message behavior; Packet Tracer shows the network and devices.

## What happens inside NS2

1. [The NS2 script](../ns2/run.tcl) builds a small network: an alert source, a router, a monitoring receiver, and one or two senders that add background traffic. The link to the receiver is deliberately slow and can drop packets.
2. It creates **30 messages in the original runs or 120 in the longer stress runs**. Every fourth message is marked critical and has a delivery deadline. The others are routine messages.
3. It runs one of three sending rules over NS2 message agents:
   - **Baseline:** send once, with no acknowledgment or retry.
   - **Selective Repeat:** keep up to four messages in flight, acknowledge delivered messages, and retry missing ones, up to five sends per message.
   - **AURA:** use acknowledgments and retries too, put the earliest-due alerts first, allow routine messages regular turns, adapt the retry timer and small sender window, and skip a retry when its estimated travel time exceeds the alert's remaining lifetime.
4. NS2 records each meaningful step in `events.csv`: generation, sending, receiving, delivery, acknowledgment, retry, expiration, abandonment, or late arrival. `control.csv` records sender decisions; `background.csv` records how much traffic reached the competing flow. NS2 also writes packet traces and optional NAM animation files.
5. [The metrics code](../python/analysis/metrics.py) counts each message only once. The original [transport comparison](../scripts/multiseed.py), [policy ablation](../scripts/ablation.py), and fresh-seed repeats make **1,260 short runs**. A [long-workload sweep](../scripts/robustness.py) adds **480 runs**, an [alert-reservation study](../scripts/reservation_study.py) adds **360**, and an [arrival/link-rate study](../scripts/sensitivity.py) adds **1,440**: **3,540 measured runs** in total. [The charts](../experiments/plots/robustness.svg) and [dashboard](../python/dashboard/index.html) display selected saved results. Opening the dashboard does not rerun NS2.

Two useful measurements are **PDR**, the fraction of all generated messages that eventually arrived, and **DDR**, the fraction of critical messages that arrived *before their deadline*. A late alert can count toward PDR but not DDR. More retries can improve arrival while also consuming bandwidth and time.

The [measured short-run summary](../experiments/results/multiseed/summary.csv) includes a difficult tight-deadline case where all three methods deliver few critical alerts on time. The [longer runs](../experiments/results/robustness/summary.csv) show a stronger warning: when two other senders crowd a short queue, AURA delivers fewer urgent alerts before deadline than one-shot sending. The [policy test](RESEARCH_EVALUATION.md) finds that skipping estimated-late retries saves some retry traffic under high load, but has not shown a clear improvement in on-time alert delivery. These are measured limits to the current design.

## What happens inside Cisco Packet Tracer

Open the editable [campus topology](../packet_tracer/topology/AURA-UDP-campus.pkt) in Packet Tracer 9.0. Its left sensor-side LAN connects through **Router0**, a transit link, and **Router1** to the server-side LAN. The monitoring server is **Server0 at `10.10.30.10`**.

The PCs labeled TEMP, SMOKE, and ALERT represent possible traffic-generator roles in the campus story. They are **separate from** the native Temperature Monitor and Smoke Detector. The native devices connect wirelessly to **HomeGateway0**; Tablet PC0 can open the gateway's device page at `http://192.168.25.1` and see both registered devices and their fields.

For a visible routed check, open PC0's browser and visit `http://10.10.30.10`. The custom page served by Server0 loaded across Router0 and Router1. [Its HTML source](../packet_tracer/documentation/server-index.html) is stored in the repo and in the saved Packet Tracer server. PC3 can load the same page, but PC3 is on Server0's LAN, so that shorter check alone does not show routing. The [Packet Tracer build guide](../packet_tracer/documentation/BUILD_GUIDE.md) lists addresses, cabling, and repeatable inspection steps.

The [readable evidence diagram](../packet_tracer/documentation/media/evidence-overview.svg) explains the observed paths. The [current PC0 screenshot](../packet_tracer/documentation/media/routed-http-after-chamber-2026-10-29.jpg) shows the routed page after the physical change. The saved topology has an Old Car named `SMOKE-TRIGGER-CAR` beside the native detector in a 1 m³ chamber. Physically activating the car produced visible exhaust and a recorded detector transition to `level 100, state 1`; merely changing the car's Attributes did not. The [validation record](VALIDATION.md) distinguishes this from the earlier manual Smoke test and notes the pending paired gateway capture.

## How to explore it yourself

1. **See the campus:** open the `.pkt` file, browse from PC0 to Server0, then use Tablet PC0 to inspect the gateway's registered devices.
2. **See the measurements:** open the [full comparison chart](../experiments/plots/multiseed.svg) or the [summary table](../experiments/results/multiseed/summary.csv). These were produced from NS2 runs, not Packet Tracer traffic.
3. **Test the decision and follow one message:** from the repository root, run `python3 -m http.server 8000 --bind 127.0.0.1` and open `http://localhost:8000/python/dashboard/`. Choose a condition, compare the modes and four AURA variants, then step through a saved message's events. Keep the server terminal open while using the page.
4. **Reproduce the experiment:** with NS2 2.35 available as `ns` in Ubuntu or WSL, follow the commands in the [README](../README.md). The [validation record](VALIDATION.md) lists the checks already performed.

## What this project does not claim

Packet Tracer verifies the campus demonstration; it does not execute AURA or validate its performance. NS2 uses synthetic workloads rather than live campus sensors. The results are descriptive across seven tested conditions, without a broad superiority claim. This implementation has only a small bounded window, no router queue priority or custom C++ UDP header, and no proven Internet-grade congestion fairness. The gateway's lab login and wireless setup are not a production security design.
