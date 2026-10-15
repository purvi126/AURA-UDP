"""Run reproducible seed sweeps and report distributions, without significance claims."""
import argparse
import csv
import json
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "analysis"))
from metrics import calculate

SCENARIOS = {
    "moderate": (0.15, 40, 80, 300, 120),
    "tight_deadline": (0.30, 80, 180, 120, 120),
    "high_rate": (0.15, 40, 120, 300, 60),
}
MODES = ("baseline", "sr", "aura")
METRICS = ("pdr", "ddr", "critical_pdr", "routine_pdr", "avg_delay_ms",
           "routine_avg_delay_ms", "retransmission_overhead",
           "class_delivery_fairness", "sender_abandonments", "background_goodput_bps")


def paired_bootstrap_interval(differences, key, resamples=5000):
    """Deterministic 95% percentile interval for a paired mean difference."""
    rng = random.Random(key)
    count = len(differences)
    means = sorted(sum(differences[rng.randrange(count)] for _ in range(count)) / count
                   for _ in range(resamples))
    return means[int(.025 * (resamples - 1))], means[int(.975 * (resamples - 1))]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/results/multiseed")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--first-seed", type=int, default=1)
    args = parser.parse_args()
    if args.seeds < 2:
        parser.error("--seeds must be at least 2")
    if args.first_seed < 0:
        parser.error("--first-seed must be non-negative")
    if shutil.which("ns") is None:
        parser.error("NS2 executable 'ns' was not found on PATH")
    args.output.mkdir(parents=True, exist_ok=True)
    runs = []
    for scenario, config in SCENARIOS.items():
        for seed in range(args.first_seed, args.first_seed + args.seeds):
            for mode in MODES:
                with tempfile.TemporaryDirectory(prefix="aura-ns2-") as tmp:
                    subprocess.run(
                        ["ns", str(ROOT / "ns2/run.tcl"), mode,
                         *map(str, config[:4]), str(seed), tmp, str(config[4])],
                        check=True, stdout=subprocess.DEVNULL,
                    )
                    runs.append({"scenario": scenario, "seed": seed, "mode": mode,
                                 **calculate(Path(tmp) / "events.csv")})
    write_csv(args.output / "runs.csv", runs)
    summary = []
    for scenario in SCENARIOS:
        for mode in MODES:
            subset = [r for r in runs if r["scenario"] == scenario and r["mode"] == mode]
            row = {"scenario": scenario, "mode": mode, "seeds": args.seeds}
            for metric in METRICS:
                values = [r[metric] for r in subset if r[metric] is not None]
                row[f"{metric}_mean"] = statistics.mean(values) if values else ""
                row[f"{metric}_sd"] = statistics.stdev(values) if len(values) > 1 else ""
            summary.append(row)
    write_csv(args.output / "summary.csv", summary)
    paired = []
    for scenario in SCENARIOS:
        for metric in ("pdr", "ddr", "routine_pdr", "retransmission_overhead",
                       "class_delivery_fairness", "background_goodput_bps"):
            for comparison in ("baseline", "sr"):
                differences = []
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    values = {r["mode"]: r[metric] for r in runs
                              if r["scenario"] == scenario and r["seed"] == seed}
                    if values["aura"] is not None and values[comparison] is not None:
                        differences.append(values["aura"] - values[comparison])
                lower, upper = paired_bootstrap_interval(
                    differences, f"{scenario}:{metric}:{comparison}:{args.first_seed}:{args.seeds}") if differences else ("", "")
                paired.append({"scenario": scenario, "metric": metric,
                               "comparison": comparison, "seeds": len(differences),
                               "aura_minus_comparison_mean": statistics.mean(differences) if differences else "",
                               "ci95_low": lower, "ci95_high": upper,
                               "aura_better": sum(x > 0 for x in differences),
                               "tied": sum(x == 0 for x in differences),
                               "aura_worse": sum(x < 0 for x in differences)})
    write_csv(args.output / "paired.csv", paired)
    (args.output / "config.json").write_text(json.dumps({
        "first_seed": args.first_seed, "seeds": args.seeds,
        "scenarios": {k: dict(zip(("loss", "delay_ms", "background_kbps",
                                   "deadline_ms", "interval_ms"), v))
                      for k, v in SCENARIOS.items()},
        "interpretation": "Paired percentile bootstrap intervals describe these seeds; no broad superiority claim.",
        "paired_bootstrap_resamples": 5000,
        "class_delivery_fairness": "Jain index of critical and routine PDR; not competing-flow fairness."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(runs)} runs across {len(SCENARIOS)} scenarios to {args.output}")


if __name__ == "__main__":
    main()
