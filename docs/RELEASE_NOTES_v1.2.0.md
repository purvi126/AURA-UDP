# AURA-UDP v1.2.0 — deadline-policy evaluation

This release adds an explicit decision about whether a critical alert has enough lifetime left for a retransmission, then evaluates that decision instead of assuming it helps.

## Changes

- AURA now orders critical alerts by absolute deadline, gives waiting routine messages a turn after three critical admissions, and logs a sender `abandon` event when an estimated-late retry is skipped.
- A bounded four-to-six-message sender window reacts to ACKs and timeouts. The RTT estimator, backoff, and window decisions are specified in [the protocol document](PROTOCOL.md).
- Separate data and ACK RNG streams, a received-background-flow counter, routine PDR, class delivery balance, and paired bootstrap intervals make tradeoffs visible.
- A 270-run baseline/SR/AURA comparison and a 360-run AURA ablation are checked in as per-run and aggregate CSVs. The dashboard and vector chart show the four policy variants.
- The [plain-language guide](PROJECT_EXPLAINED.md), [research evaluation](RESEARCH_EVALUATION.md), README, and validation record explain both the implementation and its limits.

## Evidence and result

Nineteen local Python/NS2 tests passed, the Node dashboard check passed, and both 30-seed sweeps reproduced their `runs.csv`, `summary.csv`, and `paired.csv` files byte for byte. The dashboard served over local HTTP with a 200 response. GitHub CI also runs tests, the dashboard check, an SVG reproduction check, and three-seed smoke sweeps.

In the high-rate scenario, the feasibility rule lowered retry overhead by 0.021 extra sends per generated message versus disabling that rule; its paired 95% interval was −0.042 to −0.002. DDR did **not** improve: the point estimate was 1.25 percentage points lower, with an interval crossing zero. The tight-deadline scenario remains difficult for all modes. These results support a narrow retry-cost observation, not a broad performance or congestion-fairness claim.

## Recovery

The tag `v1.2.0` identifies the released source and results. The prior `v1.1.0` and `v1.0.0` tags remain available. See [the rollback guide](ROLLBACK.md) for safe file restore or revert commands; do not force-push shared `main`.
