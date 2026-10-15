# Reproducible deadline-policy evaluation

## Question and hypothesis

Can a sender improve useful alert delivery and reduce retry cost by considering an alert's remaining lifetime before retransmitting? The proposed decision is `estimated_forward_delivery_time <= absolute_deadline − current_time`. It is implemented in [the NS2 sender](../ns2/run.tcl) and specified in [the protocol document](PROTOCOL.md). This is an experimental policy over established Selective Repeat and RTT estimation, not a claim of a new transport standard.

## Design

The checked-in [three-mode sweep](../experiments/results/multiseed/config.json) runs baseline, fixed Selective Repeat (SR), and AURA for 30 substream indices in each of three scenarios: 270 runs. The [AURA ablation](../experiments/results/ablation/config.json) runs `full`, `no_feasibility`, `fixed_window`, and `legacy` for the same 30 indices and scenarios: 360 more runs. A separate [held-out transport sweep](../experiments/results/holdout/multiseed/config.json) and [held-out ablation](../experiments/results/holdout/ablation/config.json) repeat those 630 runs on indices 31–60, which were not used to choose the reported policy bounds. Every run generates 30 messages (eight critical), with the same schedule and topology for a given scenario. Data and ACK error models have separately seeded RNG streams. A common substream index pairs replications, but different mode choices consume different random draws, so packet-by-packet losses are not identical.

The primary outcome is **DDR = timely first deliveries / all generated critical messages**. Lost, expired, and sender-abandoned alerts remain in the denominator. We also report overall and routine PDR, delivered-message delay, retries per generated message, and received background CBR goodput. Jain's index of critical and routine PDR is a class balance indicator, not a competing-flow fairness measurement. Summary means, per-run values, and paired differences with deterministic 5,000-resample percentile bootstrap 95% intervals are in the linked CSVs. These intervals describe the chosen workload and seeds; the scenarios and policy bounds were selected during development, so they are not preregistered confirmatory tests.

## Three-mode results

| Scenario | Baseline DDR | SR DDR | AURA DDR | AURA routine PDR | AURA background goodput |
|---|---:|---:|---:|---:|---:|
| Moderate loss | 81.7% | 83.3% | 93.3% | 100.0% | 56.6 Kb/s |
| Tight deadline | 12.9% | 10.0% | 10.4% | 92.1% | 101.6 Kb/s |
| High message rate | 86.3% | 73.3% | 89.2% | 100.0% | 84.2 Kb/s |

In the moderate case, AURA minus SR DDR averaged +10.0 percentage points (paired interval +5.4 to +14.6). In the high-rate case, it averaged +15.8 points (+9.2 to +22.9). In the tight-deadline case, AURA minus baseline averaged **−2.5 points** (−4.6 to −0.8); all modes delivered few alerts on time. AURA's tight-case routine PDR was 92.1%, below SR's 98.5%, and its class balance was 0.855. The tight scenario therefore does not support a claim that alert priority avoids harm to routine traffic. [Summary](../experiments/results/multiseed/summary.csv), [individual runs](../experiments/results/multiseed/runs.csv), and [paired intervals](../experiments/results/multiseed/paired.csv) provide the full values.

## Does the new deadline decision help?

| Scenario | Full DDR | Without feasibility DDR | Full retry overhead | Without feasibility overhead | Sender abandonments per run |
|---|---:|---:|---:|---:|---:|
| Moderate loss | 93.3% | 93.8% | 0.367 | 0.372 | 0.23 |
| Tight deadline | 10.4% | 10.4% | 0.659 | 0.659 | 0 |
| High message rate | 89.2% | 90.4% | 0.313 | 0.334 | 0.53 |

In the high-rate case, the feasibility policy reduced retry overhead by 0.021 sends per generated message (paired interval −0.042 to −0.002). Its DDR point estimate fell by 1.25 percentage points, with an interval from −4.17 to +1.25. The moderate DDR point estimate fell 0.42 points, also with an interval crossing zero. The tight deadline offered no feasible retry opportunity under this timer and workload. **These results do not demonstrate an improvement in DDR from the new feasibility decision.** They show a measurable retry-cost tradeoff and identify an important failure mode: a one-way time estimate can reject a retry that would have succeeded. The window ablation also shows little distinct effect at these settings; see [full ablation summary](../experiments/results/ablation/summary.csv) and [paired differences](../experiments/results/ablation/paired.csv).

The background CBR goodput was recorded directly at its NS2 receiving agent. In the high-rate ablation, full AURA and no-feasibility AURA were 84.23 and 84.25 Kb/s, respectively; the paired interval for their difference crosses zero. That check gives no evidence of a substantial background-flow gain from feasibility in this scenario. It does not establish congestion fairness or Internet safety.

## Fresh-seed validation (indices 31–60)

The held-out sweep repeats the same scenarios and policies with 30 new substream indices. In the high-rate condition, full AURA and the no-feasibility variant both reached **90.4% DDR**. Full AURA used 0.339 extra sends per generated message versus 0.357 without the check: a mean difference of −0.018, with a paired interval from −0.038 to +0.002. The direction of the retry-cost result repeats, but this interval includes zero. In moderate loss, full AURA reached 94.2% DDR versus 94.6% without the check; in the tight case both reached 10.4%. This fresh set again provides **no DDR gain attributable to the feasibility decision**. The [held-out summary](../experiments/results/holdout/ablation/summary.csv), [per-run data](../experiments/results/holdout/ablation/runs.csv), and [paired intervals](../experiments/results/holdout/ablation/paired.csv) are checked in, as are the [three-mode results](../experiments/results/holdout/multiseed/summary.csv). These are separate validation replications, not additional conditions.

## Reproduce and inspect

Run from the repository root in WSL with NS2 2.35 and Python 3.10+:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/multiseed.py --output /tmp/aura-multiseed
python3 scripts/ablation.py --output /tmp/aura-ablation
python3 scripts/multiseed.py --first-seed 31 --output /tmp/aura-heldout-multiseed
python3 scripts/ablation.py --first-seed 31 --output /tmp/aura-heldout-ablation
cmp experiments/results/multiseed/runs.csv /tmp/aura-multiseed/runs.csv
cmp experiments/results/ablation/runs.csv /tmp/aura-ablation/runs.csv
cmp experiments/results/holdout/multiseed/runs.csv /tmp/aura-heldout-multiseed/runs.csv
cmp experiments/results/holdout/ablation/runs.csv /tmp/aura-heldout-ablation/runs.csv
```

For a single trace, run `ns ns2/run.tcl aura 0.15 40 120 300 1 /tmp/aura-trace 60 full` and inspect `events.csv` for `abandon`, `control.csv` for window and timeout changes, and `background.csv` for CBR delivery. Compare it with `no_feasibility` using a separate output directory. `ns2.tr` and `ns2.nam` retain packet-level evidence.

## Limits and next experiment

The evaluation has only three short synthetic scenarios, eight critical messages per run, one CBR competitor, and a small window range. The fresh seeds test replication, not a new workload. The forward-time estimate ignores queueing variance; the deadline-aware policy needs testing with larger and varied traffic, longer observation windows, multiple competitors, and calibrated estimators. A wider window may expose congestion effects more clearly. The current bounded window and short timer are lab heuristics; [RFC 8085](https://www.rfc-editor.org/rfc/rfc8085.html) and [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298.html) provide reference guidance, but this implementation does not claim full compliance.
