"""Run identical NS2 scenarios for each transport mode."""
import argparse
import csv
import json
import math
import shutil
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "analysis"))
from metrics import calculate


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=ROOT / "experiments" / "results" / "sample")
    p.add_argument("--loss", type=float, default=0.15)
    p.add_argument("--delay-ms", type=int, default=40)
    p.add_argument("--background-kbps", type=int, default=80)
    p.add_argument("--deadline-ms", type=int, default=300)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--interval-ms", type=int, default=120)
    a = p.parse_args()
    if not math.isfinite(a.loss) or not 0 <= a.loss <= 1:
        p.error("--loss must be between 0 and 1")
    if a.delay_ms <= 0 or a.deadline_ms <= 0 or a.interval_ms <= 0:
        p.error("--delay-ms, --deadline-ms, and --interval-ms must be positive")
    if a.background_kbps < 0 or a.seed < 0:
        p.error("--background-kbps and --seed must be non-negative")
    if shutil.which("ns") is None:
        p.error("NS2 executable 'ns' was not found on PATH")
    a.output.mkdir(parents=True, exist_ok=True)
    summary = []
    for mode in ("baseline", "sr", "aura"):
        dest = a.output / mode
        subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), mode, str(a.loss),
                        str(a.delay_ms), str(a.background_kbps), str(a.deadline_ms),
                        str(a.seed), str(dest), str(a.interval_ms)], check=True)
        summary.append({"mode": mode, **calculate(dest / "events.csv")})
    with (a.output / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)
    (a.output / "config.json").write_text(json.dumps(vars(a), default=str, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
