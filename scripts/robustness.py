"""Evaluate longer and more congested workloads with matched seed indices."""
import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "analysis"))
from metrics import calculate
from multiseed import paired_bootstrap_interval, write_csv

# loss, delay_ms, background_kbps, deadline_ms, interval_ms,
# message_count, background_sources, queue_limit
SCENARIOS = {
    "long_moderate": (.15, 40, 80, 300, 120, 120, 1, 12),
    "long_high_rate": (.15, 40, 120, 300, 60, 120, 1, 12),
    "two_flow_congestion": (.15, 40, 180, 300, 60, 120, 2, 6),
    "two_flow_tight": (.30, 80, 180, 120, 120, 120, 2, 6),
}
VARIANTS = (("baseline", "baseline", "full"),
            ("sr", "sr", "full"),
            ("aura", "aura", "full"),
            ("aura_no_feasibility", "aura", "no_feasibility"))
METRICS = ("ddr", "pdr", "critical_pdr", "routine_pdr",
           "retransmission_overhead", "class_delivery_fairness",
           "background_goodput_bps", "background_flow_fairness_jain")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "experiments/results/robustness")
    parser.add_argument("--first-seed", type=int, default=61)
    parser.add_argument("--seeds", type=int, default=30)
    args = parser.parse_args()
    if args.seeds < 2 or args.first_seed < 0:
        parser.error("use at least two seeds and a non-negative first seed")
    if shutil.which("ns") is None:
        parser.error("NS2 executable 'ns' was not found on PATH")
    args.output.mkdir(parents=True, exist_ok=True)
    runs = []
    for scenario, config in SCENARIOS.items():
        for seed in range(args.first_seed, args.first_seed + args.seeds):
            for variant, mode, policy in VARIANTS:
                with tempfile.TemporaryDirectory(prefix="aura-robust-") as tmp:
                    subprocess.run(["ns", str(ROOT / "ns2/run.tcl"), mode,
                                    *map(str, config[:4]), str(seed), tmp,
                                    *map(str, (config[4], policy, *config[5:]))],
                                   check=True, stdout=subprocess.DEVNULL)
                    metrics = calculate(Path(tmp) / "events.csv")
                    for name in ("background_flow1_goodput_bps",
                                 "background_flow2_goodput_bps",
                                 "background_flow_fairness_jain"):
                        metrics.setdefault(name, None)
                    runs.append({"scenario": scenario, "seed": seed,
                                 "variant": variant, **metrics})
    write_csv(args.output / "runs.csv", runs)
    summary = []
    for scenario in SCENARIOS:
        for variant, _, _ in VARIANTS:
            subset = [r for r in runs if r["scenario"] == scenario
                      and r["variant"] == variant]
            row = {"scenario": scenario, "variant": variant, "seeds": args.seeds}
            for metric in METRICS:
                values = [r[metric] for r in subset if r[metric] is not None]
                row[f"{metric}_mean"] = statistics.mean(values) if values else ""
                row[f"{metric}_sd"] = statistics.stdev(values) if len(values) > 1 else ""
            summary.append(row)
    write_csv(args.output / "summary.csv", summary)
    paired = []
    for scenario in SCENARIOS:
        for comparison in ("baseline", "sr", "aura_no_feasibility"):
            for metric in METRICS:
                differences = []
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    values = {r["variant"]: r[metric] for r in runs
                              if r["scenario"] == scenario and r["seed"] == seed}
                    if values["aura"] is not None and values[comparison] is not None:
                        differences.append(values["aura"] - values[comparison])
                lower, upper = paired_bootstrap_interval(
                    differences,
                    f"robustness:{scenario}:{comparison}:{metric}:{args.first_seed}:{args.seeds}"
                ) if differences else ("", "")
                paired.append({"scenario": scenario, "comparison": comparison,
                               "metric": metric, "seeds": len(differences),
                               "aura_minus_comparison_mean":
                               statistics.mean(differences) if differences else "",
                               "ci95_low": lower, "ci95_high": upper})
    write_csv(args.output / "paired.csv", paired)
    (args.output / "config.json").write_text(json.dumps({
        "first_seed": args.first_seed, "seeds": args.seeds,
        "variants": [variant for variant, _, _ in VARIANTS],
        "scenarios": {name: dict(zip(("loss", "delay_ms", "background_kbps",
                                      "deadline_ms", "interval_ms", "message_count",
                                      "background_sources", "queue_limit"), values))
                      for name, values in SCENARIOS.items()},
        "paired_bootstrap_resamples": 5000,
        "interpretation": "Descriptive paired seed intervals; variants may consume different loss draws.",
        "background_flow_fairness_jain": "Jain index of two received CBR flow rates; blank for one-flow scenarios.",
        "class_delivery_fairness": "Jain index of critical and routine PDR, not network fairness."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(runs)} runs across {len(SCENARIOS)} scenarios to {args.output}")


if __name__ == "__main__":
    main()
