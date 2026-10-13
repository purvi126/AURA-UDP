"""Metrics from NS2 application events; each message ID is counted once."""
import csv
import json
import sys
from pathlib import Path


def calculate(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    generated = {int(r["id"]): r for r in rows if r["event"] == "generate"}
    delivered = {}
    sends = 0
    sent_ids = set()
    for row in rows:
        mid = int(row["id"])
        if row["event"] == "send":
            sends += 1
            sent_ids.add(mid)
        elif row["event"] == "deliver" and mid not in delivered:
            delivered[mid] = row
    n = len(generated)
    critical = [mid for mid, row in generated.items() if row["class"] == "critical"]
    timely = sum(mid in delivered and float(delivered[mid]["time"]) <= float(generated[mid]["deadline"]) for mid in critical)
    delays = [float(row["time"]) - float(generated[mid]["time"]) for mid, row in delivered.items()]
    end = max((float(r["time"]) for r in rows), default=0)
    start = min((float(r["time"]) for r in rows), default=0)
    span = max(end - start, 1e-9)
    # Agent/Message payload is small; goodput uses a documented 64-byte logical message.
    return {
        "generated": n,
        "delivered": len(delivered),
        "pdr": len(delivered) / n if n else 0,
        "ddr": timely / len(critical) if critical else 0,
        "critical_alert_success_rate": timely / len(critical) if critical else 0,
        "avg_delay_ms": 1000 * sum(delays) / len(delays) if delays else None,
        "throughput_messages_per_s": len(delivered) / span,
        "goodput_bps_logical_64B": 8 * 64 * len(delivered) / span,
        # Generated messages may expire in the queue without a first send.
        "retransmission_overhead": (sends - len(sent_ids)) / n if n else 0,
        "sends": sends,
    }


if __name__ == "__main__":
    print(json.dumps(calculate(sys.argv[1]), indent=2))
