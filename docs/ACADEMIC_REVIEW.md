# Academic review notes

## Abstract and problem

Critical campus alerts need timely delivery when links lose packets or share capacity with routine telemetry. UDP alone gives no end-to-end reliability; indiscriminate retry can consume scarce bandwidth after an alert is no longer useful. This project evaluates an application-level datagram protocol with Selective Repeat, deadline tracking, traffic classification, and RTT-adaptive retry using NS2. Packet Tracer separately illustrates the campus network and verifies connectivity.

## Objectives and existing approaches

The objective is to measure PDR, deadline delivery ratio, delay, goodput, routine delivery and retransmission cost under controlled loss, delay and background load. UDP is low-overhead but unreliable. Fixed Selective Repeat repairs loss but uses a static timer and ignores deadlines. AURA combines individual retries, an RTT-based RTO, a bounded window, deadline-ordered admission, and an explicit retry feasibility test. The test is the research hypothesis; the other mechanisms are established techniques.

## Methodology and results

Use identical NS2 topology, paired RNG substream indices, and message generation schedule for the three modes within each condition. The simulation creates 30 messages, every fourth critical, at 120 ms spacing in the moderate and tight-deadline conditions and 60 ms in the high-rate condition. An independent CBR flow shares a 128 Kb/s bottleneck. Packet errors are injected on both data and ACK directions. Different retry behavior consumes different draws, so paired indices do not force identical loss masks. NS2 creates packet traces, application events, and received-background counters. Python deduplicates message IDs and computes metrics. [Sample CSV](../experiments/results/sample/summary.csv) and [stress CSV](../experiments/results/stress/summary.csv) are actual executed runs; do not generalize from them.

The 30-seed sweep adds moderate-loss, tight-deadline, and higher-message-rate conditions, with 270 runs in total. Mean DDR in moderate loss was 0.933 for AURA, 0.833 for fixed SR, and 0.817 for baseline. At the high message rate, it was 0.892, 0.733, and 0.863. In the tight-deadline condition, AURA reached 0.104 and fixed SR reached 0.100, both below baseline's 0.129. Fixed SR retained higher overall PDR throughout. A separate 360-run ablation shows that the new feasibility check reduces retry overhead under high message rate, but its DDR point estimate is lower than the version without that check; the paired DDR interval crosses zero. Both sweeps were repeated on fresh seed indices 31–60. That validation set showed equal high-rate DDR for full AURA and the no-feasibility variant, with fewer mean retries for full AURA but an interval crossing zero. The narrow policy has therefore **not demonstrated a timely-delivery improvement**. See [RESEARCH_EVALUATION.md](RESEARCH_EVALUATION.md) for means, intervals, routine delivery, background CBR goodput, and limitations. Throughput and goodput use a common observation end time within each scenario.

## Review presentation outline

1. Campus alert motivation and metrics definition.
2. NS2 topology, independent loss on data and ACK paths, Packet Tracer scope.
3. State machine and three mode differences.
4. Reproducible commands and representative event trace.
5. Sample, stress, 30-seed comparison, and 30-seed policy ablations with limitations.
6. Live NS2 run and Packet Tracer ping/HTTP demonstration.
7. Future work: held-out seeds, larger and varied workloads, queue-aware feasibility, stronger congestion control, and competing-flow fairness analysis.
