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

## Longer and more congested workloads (indices 61–90)

The [robustness script](../scripts/robustness.py) adds four 120-message conditions with 30 fresh seed indices each: 480 runs. Every condition compares baseline, SR, full AURA, and AURA without the feasibility decision. Two conditions split their total CBR background rate over **two** independent senders and reduce the router queue from 12 to six packets. The per-flow counters provide each background stream's received goodput and a Jain index between those two CBR streams. That score is **not** AURA-versus-background fairness and cannot establish Internet-safe congestion behavior. All variants within a condition share the same generation schedule and seed index, with the same loss-draw limitation described above.

| Condition | Baseline DDR | SR DDR | Full AURA DDR | No-feasibility DDR | Full AURA routine PDR |
|---|---:|---:|---:|---:|---:|
| Long moderate | 85.2% | 84.6% | 97.4% | 97.7% | 100.0% |
| Long high rate | 85.6% | 27.0% | 86.4% | 85.3% | 100.0% |
| Two-flow congestion | **67.4%** | 6.8% | 56.2% | 54.3% | 74.7% |
| Two-flow tight deadline | **22.8%** | 4.2% | 4.3% | 4.3% | 75.5% |

In the two-flow congestion case, full AURA minus baseline DDR averaged −11.2 percentage points with a paired percentile interval of −15.4 to −7.0. In the two-flow tight case, the difference was −18.4 points (−20.8 to −16.1). These are clear **failures of the broad performance hypothesis** for these workloads. AURA still beats fixed SR in the congested case, but that is not enough: one-shot delivery meets more alert deadlines. Queueing and retry load are plausible explanations, not isolated causal findings. The separate [paired comparisons](../experiments/results/robustness/paired.csv) and [individual runs](../experiments/results/robustness/runs.csv) allow checking every value.

The feasibility rule reduced extra sends per generated message by 0.022 in the long high-rate case (paired interval −0.035 to −0.009) and by 0.019 in two-flow congestion (−0.030 to −0.007). Its DDR differences from no-feasibility AURA were +1.1 and +1.9 points, respectively, with both paired intervals crossing zero. In long moderate, full AURA's DDR was 0.2 points lower. In the two-flow tight case, the variants were identical on DDR and retry overhead: the timer offered no useful decision point before the short deadline. **The new rule has a repeatable retry-saving effect in two conditions, but no established deadline-delivery gain.**

The two-flow CBR Jain score averaged 0.932 for AURA in the congestion case and 0.995 in the tight case. A score close to one only means the two CBR receivers got similar rates; it says nothing about whether either flow got a fair share relative to AURA or how a TCP competitor would respond. The [fixed-scale SVG](../experiments/plots/robustness.svg) keeps the negative findings visible.

## Alert-slot admission study (indices 121–150)

The crowded failure motivated a narrower hypothesis: a newly generated alert can wait behind routine packets already occupying all sender-window slots. The experimental `reserved_alert_slot` policy admits at most `window − 1` routine messages when no alert is queued. A critical message may use the remaining slot immediately. This does not preempt an in-flight packet or add router-level priority. It retains the original deadline-feasibility check, timeout estimator, and 4–6 slot window. The original `full` implementation and the 61–90 results remain unchanged.

The [reservation script](../scripts/reservation_study.py) ran one-shot, original AURA, and reserved AURA on the same four 120-message conditions, with 30 additional seed indices per condition: 360 runs. Within a condition, each mode uses the same traffic schedule and seed index, while mode-dependent loss-draw consumption remains a limitation. This study was motivated by observed failures, so its descriptive paired intervals are **not a preregistered proof of general superiority**.

| Condition | One-shot DDR | Original AURA DDR | Reserved DDR | Original routine PDR | Reserved routine PDR |
|---|---:|---:|---:|---:|---:|
| Long moderate | 84.0% | 96.4% | 96.7% | 100.0% | 100.0% |
| Long high rate | 84.2% | 85.9% | 89.4% | 100.0% | 100.0% |
| Two-flow congestion | 69.6% | 55.8% | 69.8% | 77.9% | 63.3% |
| Two-flow tight deadline | **25.6%** | 4.3% | 22.2% | 73.0% | 59.0% |

In two-flow congestion, reserved minus original AURA DDR is +14.0 percentage points (paired 95% interval +9.1 to +18.7), while reserved minus baseline is +0.2 points (−3.7 to +4.1). Under the tight deadline, reservation gains +17.9 points over original AURA (+15.3 to +20.7) yet remains **3.3 points below one-shot** (−6.4 to −0.3). Thus the new admission rule substantially reduces the earlier regression but does not solve the tight case. It shifts service away from routine messages: routine PDR decreases by 14.6 and 13.9 points in the two crowded cases, respectively. The [per-run data](../experiments/results/reservation/runs.csv), [summary](../experiments/results/reservation/summary.csv), [paired intervals](../experiments/results/reservation/paired.csv), and [configuration](../experiments/results/reservation/config.json) allow independent checks. Competing CBR throughput and the two-CBR-flow balance score are included, but they still do not establish fairness to an Internet transport.

## Arrival-order and link-rate sensitivity (indices 181–210)

The [sensitivity script](../scripts/sensitivity.py) tests a different explanation for the crowded results: an alert's position within a short burst may matter as much as the average message rate. It repeats the two crowded workloads above with either one message every interval (**regular**, critical first in each group of four) or three routine messages 5 ms apart followed by a critical message 5 ms later (**late-alert burst**). Groups start four intervals apart, preserving the same average offered message rate and 30 critical messages per 120-message run. The bottleneck is either 128 or 256 Kb/s; the loss rate, propagation delay, two competing CBR sources, and six-packet queue are held fixed within each workload. One-shot, original AURA, and reserved AURA each run on 30 fresh substream indices per condition: **720 runs**. The comparison pairs seed indices and traffic schedules, subject to the mode-dependent loss-draw limitation described above. These conditions were chosen after observing earlier results, so their bootstrap intervals are descriptive.

| Workload | Arrival schedule | Link | One-shot DDR | Original AURA DDR | Reserved DDR | Reserved routine PDR |
|---|---|---:|---:|---:|---:|---:|
| Crowded | Regular | 128 Kb/s | 69.9% | 58.1% | 70.8% | 63.6% |
| Crowded | Regular | 256 Kb/s | 85.1% | 96.7% | 95.8% | 100.0% |
| Crowded | Late alert burst | 128 Kb/s | 25.4% | 52.8% | 56.8% | 59.3% |
| Crowded | Late alert burst | 256 Kb/s | 85.0% | 93.4% | 93.8% | 100.0% |
| Tight deadline | Regular | 128 Kb/s | 23.4% | 4.0% | 21.4% | 60.4% |
| Tight deadline | Regular | 256 Kb/s | 69.6% | 26.1% | 70.4% | 81.9% |
| Tight deadline | Late alert burst | 128 Kb/s | 6.4% | 0.9% | 18.2% | 59.6% |
| Tight deadline | Late alert burst | 256 Kb/s | 66.8% | 20.6% | 67.1% | 80.6% |

At 128 Kb/s with regular arrivals, reservation raises DDR over original AURA by 12.7 points in the crowded workload (paired 95% interval +7.1 to +17.9), but differs from one-shot by only +0.9 points (−3.6 to +5.2). In the tight workload, reserved DDR is 2.0 points below one-shot (−5.3 to +1.3). With the late-alert burst at 128 Kb/s, one-shot DDR drops sharply; reserved AURA exceeds it by 31.3 points in crowded traffic (+27.9 to +34.9) and 11.8 points in the tight workload (+8.9 to +14.7). This is evidence for these configured burst conditions, not proof that reservation always wins.

At 256 Kb/s, reserved AURA exceeds one-shot in both crowded conditions, but in both tight conditions the paired intervals for its difference from one-shot span zero. Original AURA remains far below both in the tight conditions, despite the higher link rate. Reservation also costs routine delivery when capacity is constrained: at 128 Kb/s, the crowded regular case falls from 78.0% routine PDR under original AURA to 63.6% with reservation; the crowded burst case falls from 77.6% to 59.3%. At 256 Kb/s, both AURA policies deliver 100% of routine messages in the crowded cases, but tight-case routine delivery remains lower with reservation than with original AURA. Background goodput and the between-CBR-flow balance score are in the [summary](../experiments/results/sensitivity/summary.csv); those measurements still cannot establish transport fairness against TCP or Internet safety. See [per-run values](../experiments/results/sensitivity/runs.csv), [paired intervals](../experiments/results/sensitivity/paired.csv), and the [exact configuration](../experiments/results/sensitivity/config.json).

## Reproduce and inspect

Run from the repository root in WSL with NS2 2.35 and Python 3.10+:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/multiseed.py --output /tmp/aura-multiseed
python3 scripts/ablation.py --output /tmp/aura-ablation
python3 scripts/multiseed.py --first-seed 31 --output /tmp/aura-heldout-multiseed
python3 scripts/ablation.py --first-seed 31 --output /tmp/aura-heldout-ablation
python3 scripts/robustness.py --output /tmp/aura-robustness
python3 scripts/reservation_study.py --output /tmp/aura-reservation
python3 scripts/sensitivity.py --output /tmp/aura-sensitivity
cmp experiments/results/multiseed/runs.csv /tmp/aura-multiseed/runs.csv
cmp experiments/results/ablation/runs.csv /tmp/aura-ablation/runs.csv
cmp experiments/results/holdout/multiseed/runs.csv /tmp/aura-heldout-multiseed/runs.csv
cmp experiments/results/holdout/ablation/runs.csv /tmp/aura-heldout-ablation/runs.csv
cmp experiments/results/robustness/runs.csv /tmp/aura-robustness/runs.csv
cmp experiments/results/robustness/paired.csv /tmp/aura-robustness/paired.csv
cmp experiments/results/reservation/runs.csv /tmp/aura-reservation/runs.csv
cmp experiments/results/reservation/paired.csv /tmp/aura-reservation/paired.csv
cmp experiments/results/sensitivity/runs.csv /tmp/aura-sensitivity/runs.csv
cmp experiments/results/sensitivity/summary.csv /tmp/aura-sensitivity/summary.csv
cmp experiments/results/sensitivity/paired.csv /tmp/aura-sensitivity/paired.csv
```

For a single trace, run `ns ns2/run.tcl aura 0.15 40 120 300 1 /tmp/aura-trace 60 full` and inspect `events.csv` for `abandon`, `control.csv` for window and timeout changes, and `background.csv` for CBR delivery. Compare it with `no_feasibility` using a separate output directory. `ns2.tr` and `ns2.nam` retain packet-level evidence.

## Limits and next experiment

The evaluation includes short and long synthetic scenarios, regular and one late-alert burst schedule, and two bottleneck rates. The window varies only from four to six messages, and the forward-time estimate ignores queueing variance. The reservation result demonstrates an alert-versus-routine tradeoff; several tight cases still fail to beat one-shot delivery. A next study should vary burst sizes and spacing, add a competing TCP-like flow, and test estimator confidence bounds and pacing rules, then evaluate whether DDR improves without harming routine or competing traffic. The current bounded window and short timer are lab heuristics; [RFC 8085](https://www.rfc-editor.org/rfc/rfc8085.html) and [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298.html) provide reference guidance, but this implementation does not claim full compliance.
