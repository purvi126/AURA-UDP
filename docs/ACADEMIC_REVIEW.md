# Academic review notes

## Abstract and problem

Critical campus alerts need timely delivery when links lose packets or share capacity with routine telemetry. UDP alone gives no end-to-end reliability; indiscriminate retry can consume scarce bandwidth after an alert is no longer useful. This project evaluates an application-level datagram protocol with Selective Repeat, deadline tracking, traffic classification, and RTT-adaptive retry using NS2. Packet Tracer separately illustrates the campus network and verifies connectivity.

## Objectives and existing approaches

The objective is to measure PDR, deadline delivery ratio, delay, goodput and retransmission cost under controlled loss, delay and background load. UDP is low-overhead but unreliable. Fixed Selective Repeat repairs loss but uses a static timer and ignores deadlines. AURA combines individual retries, RTT-based RTO and critical-first admission. This is an engineering integration and controlled comparison, not a proof of superior performance.

## Methodology and results

Use identical NS2 topology, initial seeds and message generation schedule for the three modes. The simulation creates 30 messages, every fourth critical, at 120 ms spacing. An independent CBR flow shares a 128 Kb/s bottleneck. Packet errors are injected on both data and ACK directions. NS2 creates packet traces and application events. Python deduplicates message IDs and computes metrics. [Sample CSV](../experiments/results/sample/summary.csv) and [stress CSV](../experiments/results/stress/summary.csv) are actual executed runs; do not generalize from them.

The 30-seed sweep adds moderate-loss, tight-deadline, and higher-message-rate conditions, with 270 runs in total. Mean DDR in moderate loss was 0.917 for AURA, 0.867 for fixed SR, and 0.863 for baseline. At the high message rate, it was 0.892, 0.658, and 0.883. In the tight-deadline condition, AURA and SR both reached 0.121, below baseline's 0.163. Fixed SR retained higher PDR throughout. These are descriptive outcomes of this short synthetic workload, not a universal superiority claim. The tight-deadline outcome shows that sender deadline awareness alone cannot overcome a slow congested path.

## Review presentation outline

1. Campus alert motivation and metrics definition.
2. NS2 topology, independent loss on data and ACK paths, Packet Tracer scope.
3. State machine and three mode differences.
4. Reproducible commands and representative event trace.
5. Sample, stress, and 30-seed results with limitations.
6. Live NS2 run and Packet Tracer ping/HTTP demonstration.
7. Future work: larger and more varied workloads, router queue priority, adaptive window, and formal uncertainty analysis.
