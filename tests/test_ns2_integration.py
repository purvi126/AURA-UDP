import csv
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "analysis"))
from metrics import calculate

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("ns"), "NS2 is not installed")
class NS2IntegrationTest(unittest.TestCase):
    def run_mode(self, mode, loss, delay, background, deadline, interval=120,
                 seed=11, policy="full"):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), mode, str(loss),
                            str(delay), str(background), str(deadline), str(seed), d,
                            str(interval), policy], check=True, capture_output=True, text=True)
            with (Path(d) / "events.csv").open(newline="") as f:
                return list(csv.DictReader(f))

    def test_feasibility_abandons_unuseful_retry(self):
        args = ("aura", .15, 40, 120, 300)
        full = self.run_mode(*args, interval=60, seed=1)
        without = self.run_mode(*args, interval=60, seed=1,
                                policy="no_feasibility")
        abandoned = {r["id"] for r in full if r["event"] == "abandon"}
        self.assertTrue(abandoned)
        self.assertFalse(any(r["event"] == "abandon" for r in without))
        cutoff = {r["id"]: float(r["time"]) for r in full
                  if r["event"] == "abandon"}
        for row in full:
            if row["event"] == "send" and row["id"] in cutoff:
                self.assertLess(float(row["time"]), cutoff[row["id"]])

    def test_window_growth_is_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), "aura", "0", "40",
                            "80", "300", "1", d, "60"], check=True,
                           capture_output=True, text=True)
            with (Path(d) / "control.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
        self.assertTrue(any(r["event"] == "increase" for r in rows))
        self.assertTrue(all(4 <= int(r["window"]) <= 6 for r in rows))

    def test_timeout_reduces_grown_window(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), "aura", ".15", "40",
                            "120", "300", "1", d, "60"], check=True,
                           capture_output=True, text=True)
            with (Path(d) / "control.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
        grown = next(i for i, row in enumerate(rows) if row["event"] == "increase")
        self.assertEqual(int(rows[grown]["window"]), 5)
        later_timeout = next(row for row in rows[grown + 1:]
                             if row["event"] == "timeout")
        self.assertEqual(int(later_timeout["window"]), 4)

    def test_no_loss_and_ack(self):
        rows = self.run_mode("sr", 0, 10, 0, 500)
        self.assertEqual(sum(r["event"] == "deliver" for r in rows), 30)
        self.assertEqual(sum(r["event"] == "ack" for r in rows), 30)

    def test_loss_causes_retries(self):
        rows = self.run_mode("sr", .3, 40, 80, 300)
        self.assertTrue(any(r["event"] == "timeout" for r in rows))
        self.assertTrue(any(r["event"] == "send" and int(r["attempt"]) > 1 for r in rows))
        delivered = [r["id"] for r in rows if r["event"] == "deliver"]
        self.assertEqual(len(delivered), len(set(delivered)))

    def test_aura_deadline_expiration(self):
        rows = self.run_mode("aura", .3, 80, 180, 120)
        expired = [r for r in rows if r["event"] == "expire"]
        self.assertTrue(expired)
        self.assertTrue(all(abs(float(r["time"]) - float(r["deadline"])) < 1e-8
                            for r in expired if r["class"] == "critical"))
        self.assertTrue(any(r["event"] == "late" for r in rows))
        self.assertTrue(all(float(r["time"]) < float(r["deadline"])
                            for r in rows if r["event"] == "send" and r["class"] == "critical"))

    def test_critical_alert_admitted_ahead_of_queued_routine(self):
        rows = self.run_mode("aura", 0, 40, 180, 300, interval=20)
        first_send = {int(r["id"]): float(r["time"]) for r in rows
                      if r["event"] == "send" and r["attempt"] == "1"}
        # Message 6 is routine and was generated before critical message 9.
        self.assertLess(first_send[9], first_send[6])

    def test_ack_loss(self):
        rows = self.run_mode("sr", .7, 20, 0, 500)
        self.assertTrue(any(r["event"] == "timeout" for r in rows))
        self.assertTrue(any(r["event"] == "duplicate" for r in rows))

    def test_out_of_order_is_delivered_once(self):
        rows = self.run_mode("sr", .3, 80, 180, 120)
        order = [int(r["id"]) for r in rows if r["event"] == "deliver"]
        self.assertNotEqual(order, sorted(order))
        self.assertEqual(len(order), len(set(order)))

    def test_aura_timeout_adapts(self):
        rows = self.run_mode("aura", .3, 40, 80, 300)
        sends = {int(r["id"]): float(r["time"]) for r in rows if r["event"] == "send" and r["attempt"] == "1"}
        intervals = [float(r["time"]) - sends[int(r["id"])] for r in rows
                     if r["event"] == "timeout" and r["attempt"] == "1" and int(r["id"]) in sends]
        self.assertTrue(intervals)
        self.assertTrue(any(abs(value - .3) > .02 for value in intervals))

    def test_common_observation_finish_time(self):
        baseline = self.run_mode("baseline", .15, 40, 80, 300)
        aura = self.run_mode("aura", .15, 40, 80, 300)
        for rows in (baseline, aura):
            self.assertEqual(rows[-1]["event"], "finish")
        self.assertEqual(baseline[-1]["time"], aura[-1]["time"])

    def test_extended_workload_counts_and_competing_flows(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), "aura", ".15", "40",
                            "180", "300", "61", d, "60", "full", "120", "2", "6"],
                           check=True, capture_output=True, text=True)
            with (Path(d) / "events.csv").open(newline="") as f:
                rows = list(csv.DictReader(f))
            result = calculate(Path(d) / "events.csv")
        self.assertEqual(sum(r["event"] == "generate" for r in rows), 120)
        self.assertEqual(result["generated"], 120)
        self.assertGreater(result["background_flow1_goodput_bps"], 0)
        self.assertGreater(result["background_flow2_goodput_bps"], 0)
        self.assertGreaterEqual(result["background_flow_fairness_jain"], .5)
        self.assertLessEqual(result["background_flow_fairness_jain"], 1)

    def test_reserved_alert_slot_reduces_crowded_alert_wait(self):
        delays = {}
        for policy in ("full", "reserved_alert_slot"):
            with tempfile.TemporaryDirectory() as d:
                subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), "aura",
                                ".15", "40", "180", "300", "61", d,
                                "60", policy, "120", "2", "6"],
                               check=True, capture_output=True, text=True)
                with (Path(d) / "events.csv").open(newline="") as f:
                    rows = list(csv.DictReader(f))
            generated = {row["id"]: float(row["time"]) for row in rows
                         if row["event"] == "generate" and row["class"] == "critical"}
            first_sends = {row["id"]: float(row["time"]) for row in rows
                           if row["event"] == "send" and row["attempt"] == "1"
                           and row["class"] == "critical"}
            delays[policy] = [first_sends[mid] - time for mid, time in generated.items()
                              if mid in first_sends]
        self.assertLess(sum(delays["reserved_alert_slot"]), sum(delays["full"]))
        self.assertGreater(len(delays["reserved_alert_slot"]), 20)

    def test_arrival_schedule_controls_are_independent_of_link_rate(self):
        results = {}
        for schedule in ("regular", "regular_late_alert",
                         "burst_first_alert", "burst_late_alert"):
            for rate in (128, 256):
                with tempfile.TemporaryDirectory() as d:
                    subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), "baseline",
                                    "0", "40", "0", "300", "181", d,
                                    "60", "full", "8", "1", "6",
                                    schedule, str(rate)],
                                   check=True, capture_output=True, text=True)
                    with (Path(d) / "events.csv").open(newline="") as f:
                        rows = list(csv.DictReader(f))
                    generated = [row for row in rows if row["event"] == "generate"]
                    results[schedule, rate] = (generated,
                                               calculate(Path(d) / "events.csv"))
        for schedule in ("regular", "regular_late_alert",
                         "burst_first_alert", "burst_late_alert"):
            self.assertEqual([row["time"] for row in results[schedule, 128][0]],
                             [row["time"] for row in results[schedule, 256][0]])
            expected = ["critical", "routine", "routine", "routine"] \
                if schedule in ("regular", "burst_first_alert") else \
                ["routine", "routine", "routine", "critical"]
            self.assertEqual([row["class"] for row in results[schedule, 128][0][:4]],
                             expected)
        for first, late in (("regular", "regular_late_alert"),
                            ("burst_first_alert", "burst_late_alert")):
            self.assertEqual([row["time"] for row in results[first, 128][0]],
                             [row["time"] for row in results[late, 128][0]])
        self.assertEqual([round(float(row["time"]), 3) for row in
                          results["burst_late_alert", 128][0][:4]],
                         [.1, .105, .11, .115])
        self.assertLess(results["burst_late_alert", 256][1]["avg_delay_ms"],
                        results["burst_late_alert", 128][1]["avg_delay_ms"])


if __name__ == "__main__":
    unittest.main()
