import csv
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
