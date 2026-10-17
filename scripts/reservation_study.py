"""Evaluate alert-slot admission against unchanged AURA and one-shot sending."""
import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from robustness import SCENARIOS, METRICS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "analysis"))
from metrics import calculate
from multiseed import paired_bootstrap_interval, write_csv

VARIANTS = (("baseline", "baseline", "full"),
            ("aura", "aura", "full"),
            ("aura_reserved", "aura", "reserved_alert_slot"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "experiments/results/reservation")
    parser.add_argument("--first-seed", type=int, default=121)
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
                with tempfile.TemporaryDirectory(prefix="aura-reserve-") as output:
                    subprocess.run(["ns", str(ROOT / "ns2/run.tcl"), mode,
                                    *map(str, config[:4]), str(seed), output,
                                    str(config[4]), policy,
                                    *map(str, config[5:])], check=True,
                                   stdout=subprocess.DEVNULL)
                    result = calculate(Path(output) / "events.csv")
                    for name in ("background_flow1_goodput_bps",
                                 "background_flow2_goodput_bps",
                                 "background_flow_fairness_jain"):
                        result.setdefault(name, None)
                    runs.append({"scenario": scenario, "seed": seed,
                                 "variant": variant, **result})
    write_csv(args.output / "runs.csv", runs)
    summary = []
    for scenario in SCENARIOS:
        for variant, _, _ in VARIANTS:
            subset = [row for row in runs if row["scenario"] == scenario
                      and row["variant"] == variant]
            item = {"scenario": scenario, "variant": variant,
                    "seeds": args.seeds}
            for metric in METRICS:
                values = [row[metric] for row in subset if row[metric] is not None]
                item[f"{metric}_mean"] = statistics.mean(values) if values else ""
                item[f"{metric}_sd"] = statistics.stdev(values) if len(values) > 1 else ""
            summary.append(item)
    write_csv(args.output / "summary.csv", summary)
    paired = []
    for scenario in SCENARIOS:
        for comparison in ("baseline", "aura"):
            for metric in METRICS:
                differences = []
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    values = {row["variant"]: row[metric] for row in runs
                              if row["scenario"] == scenario and row["seed"] == seed}
                    if values["aura_reserved"] is not None and values[comparison] is not None:
                        differences.append(values["aura_reserved"] - values[comparison])
                lower, upper = paired_bootstrap_interval(
                    differences,
                    f"reservation:{scenario}:{comparison}:{metric}:{args.first_seed}:{args.seeds}"
                ) if differences else ("", "")
                paired.append({"scenario": scenario, "comparison": comparison,
                               "metric": metric, "seeds": len(differences),
                               "reserved_minus_comparison_mean":
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
        "interpretation": "Matched seed indices; transport-dependent loss draws can diverge. Descriptive intervals only."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(runs)} runs to {args.output}")


if __name__ == "__main__":
    main()
