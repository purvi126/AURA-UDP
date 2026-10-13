"""Run reproducible seed sweeps and report distributions, without significance claims."""
import argparse
import csv
import json
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
METRICS = ("pdr", "ddr", "avg_delay_ms", "retransmission_overhead")


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
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
        for metric in ("pdr", "ddr"):
            for comparison in ("baseline", "sr"):
                differences = []
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    values = {r["mode"]: r[metric] for r in runs
                              if r["scenario"] == scenario and r["seed"] == seed}
                    differences.append(values["aura"] - values[comparison])
                paired.append({"scenario": scenario, "metric": metric,
                               "comparison": comparison, "seeds": args.seeds,
                               "aura_minus_comparison_mean": statistics.mean(differences),
                               "aura_better": sum(x > 0 for x in differences),
                               "tied": sum(x == 0 for x in differences),
                               "aura_worse": sum(x < 0 for x in differences)})
    write_csv(args.output / "paired.csv", paired)
    (args.output / "config.json").write_text(json.dumps({
        "first_seed": args.first_seed, "seeds": args.seeds,
        "scenarios": {k: dict(zip(("loss", "delay_ms", "background_kbps",
                                   "deadline_ms", "interval_ms"), v))
                      for k, v in SCENARIOS.items()},
        "interpretation": "Descriptive seed sweep; no statistical significance claim."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(runs)} runs across {len(SCENARIOS)} scenarios to {args.output}")


if __name__ == "__main__":
    main()
