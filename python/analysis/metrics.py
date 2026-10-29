"""Metrics from NS2 application events; each message ID is counted once."""
import argparse
import csv
import json
import math
from pathlib import Path


def calculate(path):
    """Turn one complete NS2 event log into unique-message metrics."""
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
    abandoned_ids = set()
    finish_time = None
    times = []
    allowed = {"generate", "send", "receive", "deliver", "ack", "timeout",
               "duplicate", "expire", "abandon", "late", "fail", "finish"}
    # Reject malformed or partial logs before computing delivery rates.
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
            # A retry can arrive later, but delivery counts once per ID.
            delivered[mid] = row
        elif event == "abandon":
            abandoned_ids.add(mid)
    if not generated:
        raise ValueError(f"{path}: no generated messages")
    if finish_time is None:
        raise ValueError(f"{path}: missing finish event; simulation may be incomplete")
    n = len(generated)
    critical = [mid for mid, row in generated.items() if row["class"] == "critical"]
    routine = [mid for mid, row in generated.items() if row["class"] == "routine"]
    # DDR includes every generated alert in its denominator, even if it
    # expired in the sender queue before its first transmission.
    timely = sum(mid in delivered and float(delivered[mid]["time"]) <= float(generated[mid]["deadline"]) for mid in critical)
    delays = [float(row["time"]) - float(generated[mid]["time"]) for mid, row in delivered.items()]
    if any(delay < 0 for delay in delays):
        raise ValueError(f"{path}: delivery precedes generation")
    start = min(float(row["time"]) for row in generated.values())
    end = finish_time
    if end <= start:
        raise ValueError(f"{path}: observation interval must end after generation")
    span = end - start
    background_path = Path(path).with_name("background.csv")
    background_packets = None
    background_goodput = None
    flow_metrics = {}
    if background_path.exists():
        with background_path.open(newline="", encoding="utf-8") as f:
            background_rows = list(csv.DictReader(f))
        if len(background_rows) != 1:
            raise ValueError(f"{background_path}: expected one background summary row")
        background_packets = int(background_rows[0]["received_packets"])
        background_bytes = int(background_rows[0]["received_bytes"])
        if background_packets < 0 or background_bytes < 0:
            raise ValueError(f"{background_path}: negative background counter")
        # Background CBR starts at t=0.05; use the shared simulation finish.
        background_goodput = 8 * background_bytes / (end - .05)
        flow_columns = {"flow1_packets", "flow1_bytes", "flow2_packets", "flow2_bytes"}
        present = flow_columns.intersection(background_rows[0])
        if present:
            if present != flow_columns:
                raise ValueError(f"{background_path}: incomplete per-flow counters")
            counters = {name: int(background_rows[0][name]) for name in flow_columns}
            if any(value < 0 for value in counters.values()):
                raise ValueError(f"{background_path}: negative per-flow counter")
            if (counters["flow1_packets"] + counters["flow2_packets"] != background_packets
                    or counters["flow1_bytes"] + counters["flow2_bytes"] != background_bytes):
                raise ValueError(f"{background_path}: per-flow counters do not match totals")
            rate1 = 8 * counters["flow1_bytes"] / (end - .05)
            rate2 = 8 * counters["flow2_bytes"] / (end - .05)
            denom = 2 * (rate1**2 + rate2**2)
            flow_metrics = {
                "background_flow1_goodput_bps": rate1,
                "background_flow2_goodput_bps": rate2,
                "background_flow_fairness_jain": ((rate1 + rate2)**2 / denom
                                                  if denom else None),
            }
    # PDR asks whether a message arrived; DDR asks whether it arrived on time.
    critical_pdr = sum(mid in delivered for mid in critical) / len(critical) if critical else 0
    routine_pdr = sum(mid in delivered for mid in routine) / len(routine) if routine else 0
    routine_delays = [float(delivered[mid]["time"]) - float(generated[mid]["time"])
                      for mid in routine if mid in delivered]
    fairness_denom = 2 * (critical_pdr**2 + routine_pdr**2)
    class_fairness = ((critical_pdr + routine_pdr)**2 / fairness_denom
                      if critical and routine and fairness_denom else None)
    # Agent/Message payload is small; goodput uses a documented 64-byte logical message.
    return {
        "generated": n,
        "delivered": len(delivered),
        "pdr": len(delivered) / n if n else 0,
        "ddr": timely / len(critical) if critical else 0,
        "critical_alert_success_rate": timely / len(critical) if critical else 0,
        "critical_pdr": critical_pdr,
        "routine_pdr": routine_pdr,
        "routine_avg_delay_ms": (1000 * sum(routine_delays) / len(routine_delays)
                                 if routine_delays else None),
        "class_delivery_fairness": class_fairness,
        "sender_abandonments": sum(mid in critical for mid in abandoned_ids),
        "background_received_packets": background_packets,
        "background_goodput_bps": background_goodput,
        "avg_delay_ms": 1000 * sum(delays) / len(delays) if delays else None,
        "throughput_messages_per_s": len(delivered) / span,
        "goodput_bps_logical_64B": 8 * 64 * len(delivered) / span,
        # Generated messages may expire in the queue without a first send.
        "retransmission_overhead": (sends - len(sent_ids)) / n if n else 0,
        "sends": sends,
        **flow_metrics,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate metrics from an NS2 event log")
    parser.add_argument("events", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(calculate(args.events), indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
