# AURA transport policy and experiment method

## Scope and state

NS2 `Agent/Message` instances carry numbered application datagrams over real simulated links and packet error models. The topology has a 128 Kb/s router-to-receiver bottleneck, a 12-packet DropTail queue, and a competing CBR source. Data and returning ACK packets have separate error models and RNG streams. All transport logic is in [`ns2/run.tcl`](../ns2/run.tcl); Packet Tracer is a separate connectivity model.

A message follows `queued → pending → acked | failed | expired | abandoned`. The receiver delivers an ID once and ACKs every copy. A critical message delivered after its absolute deadline counts toward PDR but never DDR. Sender `expired` or `abandoned` does **not** prove the receiver failed to deliver it: its data packet might have arrived while its ACK was lost.

The baseline sends once with no ACK. Fixed Selective Repeat (SR) uses a four-message window, individual retries (up to five sends), and a fixed 300 ms timer. AURA adds an estimated retry feasibility decision, deadline ordering, routine admission guard, RTT-derived timer, and a bounded variable window.

## Deadline decision

For critical message *i*, generation at time *gᵢ* sets the absolute deadline `Dᵢ = gᵢ + deadline_ms / 1000`. At each attempted **retransmission**, AURA computes:

```text
remaining_i = D_i - now
expected_forward = max(configured_one_way_link_delay, SRTT / 2)
retry only when now < D_i and expected_forward <= remaining_i
```

With no valid RTT sample, `expected_forward` is the configured one-way bottleneck delay. This is a lab heuristic, assuming roughly symmetric paths; it omits queue variance and processing time. First sends are always attempted while the alert is live, because the estimate must not suppress a potentially deliverable original. When a retry fails the feasibility check, `abandon` is logged and its sender slot is freed. An exact deadline event independently expires any still queued or pending critical message. The receiver records late arrivals even if the sender already stopped.

Critical messages are admitted in earliest-absolute-deadline order. After three consecutive critical admissions, the oldest waiting routine message gets the next available slot. This guard operates at the sender only; the router still uses DropTail and offers no class-specific scheduling.

## RTT, timer, and window

Only ACKs for packets never retransmitted contribute RTT samples (Karn's rule). The initial sample sets `SRTT = R`, `RTTVAR = R / 2`; later samples use `RTTVAR ← 0.75·RTTVAR + 0.25·|SRTT − R|` and `SRTT ← 0.875·SRTT + 0.125·R`. AURA then sets `RTO = clamp(SRTT + 4·RTTVAR, 0.08, 1.0)` seconds. The initial RTO is 0.3 seconds, and timeout multiplies it by 1.5 up to 1 second. These estimator equations follow [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298.html), but the **80 ms floor and 1.5× timeout backoff are lab choices, not RFC 6298 compliant TCP timer behavior**.

AURA starts with four messages in flight. After one current-window's worth of ACKs, it increases the window by one, to a maximum of six. A timeout halves the current window with a floor of four and resets the ACK counter. `control.csv` records window increases, timeouts, and abandoned retries. This small bounded response is an experimental heuristic, not a claim of Internet-safe congestion control. [RFC 8085](https://www.rfc-editor.org/rfc/rfc8085.html) motivates congestion safeguards for UDP applications; this project does not establish coexistence fairness against the CBR flow.

## Metrics and reproducibility

PDR = unique delivered messages / all generated messages. DDR = critical messages first delivered on or before their own deadline / **all generated critical messages**, including lost, expired, and abandoned ones. Critical-alert success rate is currently identical to DDR. Routine PDR and critical PDR are tracked separately. Class delivery balance is Jain's index of those two PDRs; it is **not competing-flow fairness**. A background `Agent/LossMonitor` records received CBR bytes, and background goodput divides those bits by the common interval from CBR start (`t=0.05 s`) to simulation finish. This is a coexistence indicator, not a full fairness test. Delay averages only delivered messages. Retransmission overhead = `(all send events − IDs sent at least once) / generated messages`. Logical goodput assumes 64 bytes per unique delivery; the actual NS2 packet header can differ.

The seed is an NS2 RNG substream index. Data and ACK loss use separately seeded streams; the same topology, generation schedule, background rate, and substream index are applied to every compared mode. Different transport choices consume different numbers of random draws, so a shared seed does **not** impose an identical per-packet loss mask. Paired seed differences and deterministic percentile bootstrap intervals describe these 30 replications; they do not prove general superiority. See [research evaluation](RESEARCH_EVALUATION.md) for the checked-in sweeps and policy ablations.

Run `python3 scripts/multiseed.py` to regenerate the three-mode comparison and `python3 scripts/ablation.py` for four AURA variants: `full`, `no_feasibility`, `fixed_window`, and `legacy`. `legacy` uses the former fixed-window, critical-front, no-feasibility sender. Both other ablations retain earliest-deadline ordering and the routine guard while removing only their named component. Each NS2 run produces `events.csv`, `control.csv`, `background.csv`, `ns2.tr`, and `ns2.nam`.
