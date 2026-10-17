"""Compare alert reservation under regular/bursty arrivals and two link rates."""
import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from multiseed import paired_bootstrap_interval, write_csv
from robustness import METRICS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "analysis"))
from metrics import calculate

# loss, delay_ms, background_kbps, deadline_ms, interval_ms,
# message_count, background_sources, queue_limit
WORKLOADS = {
    "crowded": (.15, 40, 180, 300, 60, 120, 2, 6),
    "tight": (.30, 80, 180, 120, 120, 120, 2, 6),
}
SCHEDULES = ("regular", "burst_late_alert")
LINK_RATES = (128, 256)
VARIANTS = (("baseline", "baseline", "full"),
            ("aura", "aura", "full"),
            ("aura_reserved", "aura", "reserved_alert_slot"))
COMPARISONS = (("aura", "baseline"),
               ("aura_reserved", "aura"),
               ("aura_reserved", "baseline"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "experiments/results/sensitivity")
    parser.add_argument("--first-seed", type=int, default=181)
    parser.add_argument("--seeds", type=int, default=30)
    args = parser.parse_args()
    if args.seeds < 2 or args.first_seed < 0:
        parser.error("use at least two seeds and a non-negative first seed")
    if shutil.which("ns") is None:
        parser.error("NS2 executable 'ns' was not found on PATH")
    args.output.mkdir(parents=True, exist_ok=True)

    runs = []
    scenario_keys = []
    for workload, config in WORKLOADS.items():
        for schedule in SCHEDULES:
            for rate in LINK_RATES:
                scenario = f"{workload}_{schedule}_{rate}"
                scenario_keys.append(scenario)
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    for variant, mode, policy in VARIANTS:
                        with tempfile.TemporaryDirectory(prefix="aura-sensitivity-") as output:
                            subprocess.run(["ns", str(ROOT / "ns2/run.tcl"), mode,
                                            *map(str, config[:4]), str(seed), output,
                                            str(config[4]), policy,
                                            *map(str, config[5:]), schedule, str(rate)],
                                           check=True, stdout=subprocess.DEVNULL)
                            result = calculate(Path(output) / "events.csv")
                            runs.append({"scenario": scenario, "workload": workload,
                                         "schedule": schedule, "bottleneck_kbps": rate,
                                         "seed": seed, "variant": variant, **result})
    write_csv(args.output / "runs.csv", runs)

    summary = []
    for scenario in scenario_keys:
        for variant, _, _ in VARIANTS:
            subset = [row for row in runs if row["scenario"] == scenario
                      and row["variant"] == variant]
            item = {"scenario": scenario, "variant": variant, "seeds": args.seeds}
            for metric in METRICS:
                values = [row[metric] for row in subset if row[metric] is not None]
                item[f"{metric}_mean"] = statistics.mean(values) if values else ""
                item[f"{metric}_sd"] = statistics.stdev(values) if len(values) > 1 else ""
            summary.append(item)
    write_csv(args.output / "summary.csv", summary)

    paired = []
    by_key = {(row["scenario"], row["seed"], row["variant"]): row for row in runs}
    for scenario in scenario_keys:
        for candidate, comparison in COMPARISONS:
            for metric in METRICS:
                differences = []
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    left = by_key[scenario, seed, candidate][metric]
                    right = by_key[scenario, seed, comparison][metric]
                    if left is not None and right is not None:
                        differences.append(left - right)
                lower, upper = paired_bootstrap_interval(
                    differences,
                    f"sensitivity:{scenario}:{candidate}:{comparison}:{metric}:"
                    f"{args.first_seed}:{args.seeds}",
                ) if differences else ("", "")
                paired.append({"scenario": scenario, "candidate": candidate,
                               "comparison": comparison, "metric": metric,
                               "seeds": len(differences),
                               "mean_difference": statistics.mean(differences)
                               if differences else "", "ci95_low": lower,
                               "ci95_high": upper})
    write_csv(args.output / "paired.csv", paired)
    (args.output / "config.json").write_text(json.dumps({
        "first_seed": args.first_seed, "seeds": args.seeds,
        "workloads": {name: dict(zip(("loss", "delay_ms", "background_kbps",
                                      "deadline_ms", "interval_ms", "message_count",
                                      "background_sources", "queue_limit"), config))
                      for name, config in WORKLOADS.items()},
        "schedules": {
            "regular": "One message each interval; alert is first in every four.",
            "burst_late_alert": "Three routine messages 5 ms apart, then an alert 5 ms later; bursts start four intervals apart.",
        },
        "bottleneck_kbps": LINK_RATES,
        "variants": [variant for variant, _, _ in VARIANTS],
        "paired_bootstrap_resamples": 5000,
        "interpretation": "Same schedule and seed index within each scenario; loss draws can diverge by transport. Descriptive intervals only.",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(runs)} runs across {len(scenario_keys)} scenarios to {args.output}")


if __name__ == "__main__":
    main()
