"""Show the NS2 -> event CSV -> Python metrics handoff in one command."""

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "analysis"))
from metrics import calculate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/aura-pipeline-demo"))
    parser.add_argument("--mode", choices=("baseline", "sr", "aura"), default="aura")
    args = parser.parse_args()
    if shutil.which("ns") is None:
        parser.error("NS2 executable 'ns' is not on PATH")

    output = args.output.resolve()
    command = ["ns", str(ROOT / "ns2" / "run.tcl"), args.mode,
               "0.15", "40", "80", "300", "7", str(output)]
    print("STEP 1 — NS2 runs the transport simulation:", flush=True)
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)

    events = output / "events.csv"
    print(f"\nSTEP 2 — NS2 event output: {events}")
    with events.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    first_critical = next(row["id"] for row in rows if row["event"] == "generate"
                          and row["class"] == "critical")
    print("First critical message lifecycle (time, event, id, attempt, deadline):")
    for row in rows:
        if row["id"] == first_critical:
            print("  " + ", ".join(row[key] for key in
                                   ("time", "event", "id", "attempt", "deadline")))

    print("\nSTEP 3 — Python reads that NS2 CSV and calculates outcomes:")
    result = calculate(events)
    for key in ("generated", "delivered", "pdr", "ddr", "sends",
                "retransmission_overhead", "sender_abandonments"):
        print(f"  {key}: {result[key]}")
    metrics_file = output / "metrics.json"
    metrics_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Full Python result: {metrics_file}")
    print("NS2 simulates the network and transport; Python launches NS2 and analyzes its output.")


if __name__ == "__main__":
    main()
