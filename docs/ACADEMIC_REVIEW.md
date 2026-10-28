# Academic review notes

## Project fit

The Computer Networks Lab topic list permits NS-2/NS-3 simulation projects and separately shows Cisco Packet Tracer network and IoT examples. AURA-UDP fits the **IoT communication and network performance** theme: it evaluates deadline-sensitive campus alerts under loss, delay, and competing load. The Packet Tracer topology illustrates the campus endpoints and checks routing, HTTP, and IoT registration. The two tools are independent; Packet Tracer does not execute the AURA sender and its sensors do not inject traffic into NS2. The project does **not** compare MQTT with CoAP, emulate a MANET, or evaluate native TCP congestion-control variants. Those are alternative topics in the list, not results of this project.

## Question and contribution

Critical alerts can be lost, delayed, or delivered after they cease to be useful. The question is whether an application-level reliable datagram sender can deliver more alerts **before** their deadlines without excessive retries or unacceptable harm to routine traffic. Baseline one-shot delivery, fixed Selective Repeat, and AURA run over the same NS2 topology and configured workload. AURA combines established components with an explicit decision about whether a retry is still feasible, deadline-ordered alert admission, a routine admission guard, and an experimental reserved-alert sender slot. The contribution is the defined policy and its controlled evaluation, **not** a new UDP wire format or a proven Internet-safe transport.

The primary metric is **deadline delivery ratio (DDR)**: critical messages first delivered on or before their deadline divided by **all generated critical messages**. Lost, late, expired, and abandoned alerts remain in the denominator. Report routine PDR, extra sends per generated message, delay of delivered messages, and received background CBR goodput beside DDR. The two-CBR-flow Jain score compares those background receivers only; it is not fairness against TCP.

## Implementation evidence

| Claim | Where to show it |
|---|---|
| NS2 executes the sender, receiver, data/ACK loss, competing traffic, and deadline events | [`ns2/run.tcl`](../ns2/run.tcl), a fresh `events.csv`, `control.csv`, and `ns2.tr` |
| Metrics are computed from unique message events | [`python/analysis/metrics.py`](../python/analysis/metrics.py) and [metric tests](../tests/test_metrics.py) |
| Repeated comparisons use new paired seed indices and saved configurations | [research evaluation](RESEARCH_EVALUATION.md) and [`experiments/results/`](../experiments/results/) |
| Packet Tracer has a routed campus path and registered native sensors | [editable topology](../packet_tracer/topology/AURA-UDP-campus.pkt), [build guide](../packet_tracer/documentation/BUILD_GUIDE.md), and [validation record](VALIDATION.md) |
| Automated checks pass | [GitHub Actions workflow](../.github/workflows/python.yml) and [validation record](VALIDATION.md) |

The checked-in studies total **3,540 NS2 runs**: 1,260 short development and fresh-seed validation runs, 480 longer robustness runs, 360 alert-reservation runs, and 1,440 arrival-order/link-rate runs. Every comparison is synthetic and workload-specific. A shared seed index and schedule make paired replication possible; transport-dependent retransmissions can consume different loss draws, so compared packets are not guaranteed identical loss outcomes. The later scenarios were designed after seeing earlier weaknesses, making their intervals descriptive rather than preregistered confirmatory evidence.

## Results to explain without overclaiming

In the original 30-seed moderate-loss condition, AURA's DDR was **93.3%**, fixed SR's **83.3%**, and one-shot's **81.7%**. In the tight-deadline condition, AURA reached only **10.4%**, below one-shot's **12.9%**. Removing AURA's retry-feasibility rule did not establish a DDR gain from that rule; it sometimes saved extra sends. In longer two-flow congestion, original AURA fell below one-shot DDR. Reserving a sender slot for the next alert reduced that deficit but lowered routine delivery. The four-schedule study separates burst spacing from alert position: in the 128 Kb/s crowded burst, moving the alert from first to last cut one-shot DDR by **43.6 percentage points** and reserved AURA DDR by **15.2 points** across paired seeds. These findings describe a specific queue and load; they do not show universal superiority. Full means and intervals are in [RESEARCH_EVALUATION.md](RESEARCH_EVALUATION.md).

## Packet Tracer status

The saved topology verifies PC0-to-Server0 routed HTTP and shows the native temperature and smoke devices registered to the Home Gateway. The smoke stimulus car is present. **A smoke alarm transition has not been verified**: the last observed car state was `1`, while the detector still showed `level 0, state 0`. Use the [desktop checklist](PENDING_DESKTOP_CHECKS.md) to test the detector threshold and car stimulus separately. Do not describe the Packet Tracer sensor as the source of NS2 traffic.

## Likely questions

**Why NS2 and Packet Tracer?** NS2 measures transport behavior over a repeatable lossy topology. Packet Tracer demonstrates the campus devices, routes, HTTP endpoint, and gateway registration. Their jobs differ, and neither silently proves the other.

**Is AURA actually a new UDP protocol?** It is an application-level reliable datagram policy implemented with NS2 `Agent/Message` instances. It does not introduce a native UDP header, custom C++ agent, or production deployment.

**Why report DDR rather than PDR alone?** A fire alert arriving after its deadline is delivered but no longer useful. DDR includes every generated alert in the denominator and checks whether first delivery was timely.

**What failed?** AURA's feasibility rule did not show a deadline-delivery gain. Original AURA can lose to one-shot in crowded conditions. Reservation improves some alert outcomes while reducing routine delivery. The Packet Tracer alarm transition is still unverified.

**What would come next?** Recheck the live smoke transition, test coexistence against a congestion-controlled flow, and evaluate a queue-aware deadline estimate. These are future work, not current results.
