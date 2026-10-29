# AURA-UDP: project and use guide

## What this project does

AURA-UDP studies how a sender should deliver routine IoT readings and urgent alerts when a network is congested or loses packets. An alert matters only if it arrives before its deadline. The project compares three application-layer sending policies in **NS2 2.35**: one-shot datagrams, fixed Selective Repeat (SR), and AURA. AURA prioritizes early-deadline alerts, adapts its retry timer and small sending window, and skips retries estimated to arrive too late. An experimental variant reserves one sending slot for an alert.

The **Cisco Packet Tracer 9.0** file is a separate, editable smart-campus demonstration. It shows a routed sensor-side LAN, a monitoring server, a Home Gateway, and native temperature and smoke devices. The Packet Tracer devices do not feed NS2, and its HTTP page does not execute AURA. Use NS2 data for transport claims and Packet Tracer for topology, connectivity, and sensor behavior.

## Where to start

| Goal | Open |
|---|---|
| Understand the methods and limits | [Project explanation](PROJECT_EXPLAINED.md), [protocol specification](PROTOCOL.md), [research evaluation](RESEARCH_EVALUATION.md) |
| Explore measured results | [Local dashboard](../python/dashboard/index.html) and [saved result tables](../experiments/results/sensitivity/summary.csv) |
| Inspect the campus | [Editable Packet Tracer topology](../packet_tracer/topology/AURA-UDP-campus.pkt) and [build guide](../packet_tracer/documentation/BUILD_GUIDE.md) |
| Present the work | [Five-minute review guide](FINAL_REVIEW_GUIDE.md) and [validation record](VALIDATION.md) |

## Run the NS2 work

Install NS2 2.35 so `ns` is on the path, plus Python 3.10 or newer. On this Windows machine, run the following from Ubuntu WSL in `/mnt/d/projects/AURA-UDP`:

```bash
python3 -m unittest discover -s tests -v
ns ns2/run.tcl aura 0.15 40 80 300 7 /tmp/aura-demo
python3 python/analysis/metrics.py /tmp/aura-demo/events.csv
```

The NS2 script writes event, control, background, trace, and NAM files under `/tmp/aura-demo`. `events.csv` records message generation, sends, receives, acknowledgments, deadlines, retries, and abandonment. The metrics script counts delivered messages once and reports packet delivery ratio (PDR), on-time critical-alert delivery ratio (DDR), delay, and retry cost. Run `python3 scripts/multiseed.py --help`, `python3 scripts/ablation.py --help`, or `python3 scripts/sensitivity.py --help` for the larger sweeps. The checked-in CSV files already contain the measured results; the dashboard reads them rather than launching NS2.

Start the dashboard server in a separate terminal from the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://localhost:8000/python/dashboard/`. Keep the terminal running while browsing. The dashboard compares policies, network conditions, late versus early alert arrival, and individual recorded message events.

## Use the Packet Tracer topology

1. Open `packet_tracer/topology/AURA-UDP-campus.pkt` in Packet Tracer 9.0. Save a personal copy before experimenting if you need to preserve the checked-in state.
2. Open **PC0 → Desktop → Web Browser**, enter `http://10.10.30.10`, and verify the AURA campus page. PC0 reaches Server0 across Router0 and Router1.
3. Open **Tablet PC0 → Desktop → Web Browser**, enter `http://192.168.25.1`, sign into the lab Home Gateway, and expand `TEMP-SENSOR` and `SMOKE-SENSOR` on **Devices**. The lab's default gateway account is documented in the [build guide](../packet_tracer/documentation/BUILD_GUIDE.md). If a physical move drops registration, use `SMOKE-SENSOR → Config → Settings` to reconnect its IoT Server to Home Gateway, then refresh Devices.
4. For the smoke demonstration, open **Physical → Corporate Office → SMOKE-TEST-CHAMBER** in the main topology. The Old Car and Smoke Detector were saved together there, with the car OFF. Record the detector's Attributes `level` and `state`, right-click the car and select **Interact** to start it, advance the Environment clock, and refresh the detector. Visible exhaust and a rise to `state 1` were observed on 2026-10-29. Use **Interact** again to stop the car. Editing the car's Attributes `state` alone did not trigger smoke in the recorded test.
5. The separate manual threshold test used the Environment dialog's Smoke Manual Adjustment in Main Wiring Closet. Keep that evidence distinct from the car test. See [exact readings and screenshots](VALIDATION.md).

## How to interpret the results

The saved NS2 sweeps cover 3,540 runs across short, long, crowded, reservation, and arrival/link-rate studies. AURA does not consistently beat the one-shot baseline. In some tight, crowded cases, the baseline delivers more alerts before the deadline. Reservation helps some late-alert bursts but costs routine delivery. The [evaluation](RESEARCH_EVALUATION.md) explains each result and limitation.

Packet Tracer verified the routed HTTP page, sensor registration, a manual smoke response, and a separate local car-caused detector alarm. A new pointer-free gateway sequence shows the car test changing from Alarm red at Level 0 to Alarm green at Level 100, then recovering near zero after car OFF. The native detector's editable threshold has **not** been verified as 30; its Specifications page and observed closet behavior disagree near Level 34. See the [evidence guide](../packet_tracer/documentation/EVIDENCE_GUIDE.md) and [desktop status](PENDING_DESKTOP_CHECKS.md) before presenting a live reproduction.
