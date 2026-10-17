"""Estimate paired effects of alert order and arrival clustering from saved runs."""
import argparse
import csv
import json
import statistics
from pathlib import Path

from multiseed import paired_bootstrap_interval, write_csv
from robustness import METRICS

ROOT = Path(__file__).resolve().parents[1]
CONTRASTS = (
    ("regular_late_alert", "regular", "alert_order_regular"),
    ("burst_late_alert", "burst_first_alert", "alert_order_burst"),
    ("burst_first_alert", "regular", "clustering_alert_first"),
    ("burst_late_alert", "regular_late_alert", "clustering_alert_last"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "experiments/results/sensitivity")
    args = parser.parse_args()
    try:
        config = json.loads((args.input / "config.json").read_text(encoding="utf-8"))
        with (args.input / "runs.csv").open(newline="", encoding="utf-8") as f:
            runs = list(csv.DictReader(f))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"read sensitivity inputs: {exc}")

    schedules = tuple(config["schedules"])
    variants = tuple(config["variants"])
    seeds = range(config["first_seed"], config["first_seed"] + config["seeds"])
    rates = tuple(config["bottleneck_kbps"])
    workloads = tuple(config["workloads"])
    if set(schedules) != {"regular", "regular_late_alert",
                          "burst_first_alert", "burst_late_alert"}:
        parser.error("all four arrival schedules are required for paired contrasts")

    by_key = {}
    for row in runs:
        key = (row["workload"], row["schedule"], int(row["bottleneck_kbps"]),
               int(row["seed"]), row["variant"])
        if key in by_key:
            parser.error(f"duplicate run: {key}")
        by_key[key] = row
    expected = {(workload, schedule, rate, seed, variant)
                for workload in workloads for schedule in schedules
                for rate in rates for seed in seeds for variant in variants}
    if set(by_key) != expected:
        parser.error(f"incomplete or unexpected runs: expected {len(expected)}, got {len(by_key)}")

    pairs = []
    for workload in workloads:
        for rate in rates:
            for variant in variants:
                for candidate, comparison, effect in CONTRASTS:
                    for metric in METRICS:
                        differences = []
                        for seed in seeds:
                            left = by_key[workload, candidate, rate, seed, variant][metric]
                            right = by_key[workload, comparison, rate, seed, variant][metric]
                            if left != "" and right != "":
                                differences.append(float(left) - float(right))
                        lower, upper = paired_bootstrap_interval(
                            differences,
                            f"schedule:{workload}:{rate}:{variant}:{effect}:{metric}:"
                            f"{config['first_seed']}:{config['seeds']}",
                        ) if differences else ("", "")
                        pairs.append({"workload": workload, "bottleneck_kbps": rate,
                                      "variant": variant, "effect": effect,
                                      "candidate_schedule": candidate,
                                      "comparison_schedule": comparison,
                                      "metric": metric, "seeds": len(differences),
                                      "mean_difference": statistics.mean(differences)
                                      if differences else "", "ci95_low": lower,
                                      "ci95_high": upper})
    output = args.input / "schedule_pairs.csv"
    write_csv(output, pairs)
    print(f"Saved {len(pairs)} paired schedule contrasts to {output}")


if __name__ == "__main__":
    main()
