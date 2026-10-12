# Academic review notes

## Abstract and problem

Critical campus alerts need timely delivery when links lose packets or share capacity with routine telemetry. UDP alone gives no end-to-end reliability; indiscriminate retry can consume scarce bandwidth after an alert is no longer useful. This project evaluates an application-level datagram protocol with Selective Repeat, deadline tracking, traffic classification, and RTT-adaptive retry using NS2. Packet Tracer separately illustrates the campus network and verifies connectivity.

## Objectives and existing approaches

The objective is to measure PDR, deadline delivery ratio, delay, goodput and retransmission cost under controlled loss, delay and background load. UDP is low-overhead but unreliable. Fixed Selective Repeat repairs loss but uses a static timer and ignores deadlines. AURA combines individual retries, RTT-based RTO and critical-first admission. This is an engineering integration and controlled comparison, not a proof of superior performance.

## Methodology and results

Use identical NS2 topology, initial seeds and message generation schedule for the three modes. The simulation creates 30 messages, every fourth critical, at 120 ms spacing. An independent CBR flow shares a 128 Kb/s bottleneck. Packet errors are injected on both data and ACK directions. NS2 creates packet traces and application events. Python deduplicates message IDs and computes metrics. [Sample CSV](../experiments/results/sample/summary.csv) and [stress CSV](../experiments/results/stress/summary.csv) are actual executed runs; do not generalize from them.

The sample shows all modes delivered critical alerts by deadline; reliability improved total PDR but added retries. Under the tighter stress case, DDR was low for every mode and AURA did not beat baseline. This is evidence that deadline awareness alone cannot overcome a slow congested path and that priority admission may need a workload with meaningful queued critical messages or link-level scheduling to affect DDR.

## Review presentation outline

1. Campus alert motivation and metrics definition.
2. NS2 topology, independent loss on data and ACK paths, Packet Tracer scope.
3. State machine and three mode differences.
4. Reproducible commands and representative event trace.
5. Sample and stress results with limitations.
6. Live NS2 run and Packet Tracer ping/HTTP demonstration.
7. Future work: multi-seed trials, traffic intensity sweep, queue priority and adaptive window.
