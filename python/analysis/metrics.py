"""Metrics from NS2 application events; each message ID is counted once."""
import argparse
import csv
import json
import math
from pathlib import Path


def calculate(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path}: event log is empty")
    required = {"time", "event", "id", "class", "attempt", "deadline"}
    if not required.issubset(rows[0]):
        raise ValueError(f"{path}: missing event columns: {', '.join(sorted(required - rows[0].keys()))}")
    generated = {}
    delivered = {}
    sends = 0
    sent_ids = set()
    finish_time = None
    times = []
    allowed = {"generate", "send", "receive", "deliver", "ack", "timeout",
               "duplicate", "expire", "late", "fail", "finish"}
    for row in rows:
        event = row["event"]
        if event not in allowed:
            raise ValueError(f"{path}: unknown event {event!r}")
        time = float(row["time"])
        if not math.isfinite(time) or time < 0:
            raise ValueError(f"{path}: invalid event time {row['time']!r}")
        if times and time < times[-1]:
            raise ValueError(f"{path}: event times are out of order")
        if finish_time is not None:
            raise ValueError(f"{path}: events appear after finish")
        times.append(time)
        if event == "finish":
            finish_time = time
            continue
        mid = int(row["id"])
        if mid <= 0:
            raise ValueError(f"{path}: message IDs must be positive")
        if event == "generate":
            if mid in generated:
                raise ValueError(f"{path}: duplicate generation for message {mid}")
            if row["class"] not in {"critical", "routine"}:
                raise ValueError(f"{path}: invalid message class {row['class']!r}")
            deadline = float(row["deadline"])
            if not math.isfinite(deadline) or deadline < time:
                raise ValueError(f"{path}: invalid deadline for message {mid}")
            generated[mid] = row
        elif mid not in generated:
            raise ValueError(f"{path}: {event} for message {mid} before generation")
        elif row["class"] != generated[mid]["class"]:
            raise ValueError(f"{path}: class changed for message {mid}")
        if event == "send":
            sends += 1
            sent_ids.add(mid)
        elif event == "deliver" and mid not in delivered:
            delivered[mid] = row
    if not generated:
        raise ValueError(f"{path}: no generated messages")
    n = len(generated)
    critical = [mid for mid, row in generated.items() if row["class"] == "critical"]
    timely = sum(mid in delivered and float(delivered[mid]["time"]) <= float(generated[mid]["deadline"]) for mid in critical)
    delays = [float(row["time"]) - float(generated[mid]["time"]) for mid, row in delivered.items()]
    if any(delay < 0 for delay in delays):
        raise ValueError(f"{path}: delivery precedes generation")
    start = min(float(row["time"]) for row in generated.values())
    end = finish_time if finish_time is not None else max(times)
    if end <= start:
        raise ValueError(f"{path}: observation interval must end after generation")
    span = end - start
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
    parser = argparse.ArgumentParser(description="Calculate metrics from an NS2 event log")
    parser.add_argument("events", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(calculate(args.events), indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
