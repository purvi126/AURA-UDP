"""Isolate AURA's feasibility and congestion-window decisions with paired seeds."""
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
from multiseed import SCENARIOS, paired_bootstrap_interval, write_csv

POLICIES = ("full", "no_feasibility", "fixed_window", "legacy")
METRICS = ("ddr", "pdr", "routine_pdr", "retransmission_overhead",
           "class_delivery_fairness", "sender_abandonments", "background_goodput_bps")


def main():
    parser = argparse.ArgumentParser(description="Compare AURA policy components")
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/results/ablation")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--first-seed", type=int, default=1)
    args = parser.parse_args()
    if args.seeds < 2 or args.first_seed < 0:
        parser.error("use at least two seeds and a non-negative first seed")
    if shutil.which("ns") is None:
        parser.error("NS2 executable 'ns' was not found on PATH")
    args.output.mkdir(parents=True, exist_ok=True)
    runs = []
    for scenario, config in SCENARIOS.items():
        for seed in range(args.first_seed, args.first_seed + args.seeds):
            for policy in POLICIES:
                with tempfile.TemporaryDirectory(prefix="aura-ablation-") as tmp:
                    subprocess.run(["ns", str(ROOT / "ns2/run.tcl"), "aura",
                                    *map(str, config[:4]), str(seed), tmp,
                                    str(config[4]), policy], check=True,
                                   stdout=subprocess.DEVNULL)
                    runs.append({"scenario": scenario, "seed": seed, "policy": policy,
                                 **calculate(Path(tmp) / "events.csv")})
    write_csv(args.output / "runs.csv", runs)
    summary = []
    for scenario in SCENARIOS:
        for policy in POLICIES:
            subset = [r for r in runs if r["scenario"] == scenario and r["policy"] == policy]
            row = {"scenario": scenario, "policy": policy, "seeds": args.seeds}
            for metric in METRICS:
                values = [r[metric] for r in subset if r[metric] is not None]
                row[f"{metric}_mean"] = statistics.mean(values) if values else ""
            summary.append(row)
    write_csv(args.output / "summary.csv", summary)
    paired = []
    for scenario in SCENARIOS:
        for metric in METRICS:
            for comparison in POLICIES[1:]:
                differences = []
                for seed in range(args.first_seed, args.first_seed + args.seeds):
                    values = {r["policy"]: r[metric] for r in runs
                              if r["scenario"] == scenario and r["seed"] == seed}
                    if values["full"] is not None and values[comparison] is not None:
                        differences.append(values["full"] - values[comparison])
                lower, upper = paired_bootstrap_interval(
                    differences, f"ablation:{scenario}:{metric}:{comparison}:{args.first_seed}:{args.seeds}") if differences else ("", "")
                paired.append({"scenario": scenario, "metric": metric,
                               "comparison": comparison, "seeds": len(differences),
                               "full_minus_comparison_mean": statistics.mean(differences) if differences else "",
                               "ci95_low": lower, "ci95_high": upper})
    write_csv(args.output / "paired.csv", paired)
    (args.output / "config.json").write_text(json.dumps({
        "first_seed": args.first_seed, "seeds": args.seeds,
        "policies": POLICIES,
        "scenarios": {k: dict(zip(("loss", "delay_ms", "background_kbps",
                                   "deadline_ms", "interval_ms"), v))
                      for k, v in SCENARIOS.items()},
        "paired_bootstrap_resamples": 5000,
        "interpretation": "Ablation isolates feasibility and window components; intervals describe these paired seeds, not general superiority.",
        "class_delivery_fairness": "Jain index of critical and routine PDR; not competing-flow fairness.",
        "background_goodput_bps": "Received CBR bytes divided by the shared interval from t=0.05 to simulation finish."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(runs)} AURA ablation runs to {args.output}")


if __name__ == "__main__":
    main()
