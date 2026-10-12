import csv
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("ns"), "NS2 is not installed")
class NS2IntegrationTest(unittest.TestCase):
    def run_mode(self, mode, loss, delay, background, deadline, interval=120):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["ns", str(ROOT / "ns2" / "run.tcl"), mode, str(loss),
                            str(delay), str(background), str(deadline), "11", d,
                            str(interval)], check=True, capture_output=True, text=True)
            with (Path(d) / "events.csv").open(newline="") as f:
                return list(csv.DictReader(f))

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
        self.assertTrue(any(r["event"] == "expire" for r in rows))
        self.assertTrue(any(r["event"] == "late" for r in rows))

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


if __name__ == "__main__":
    unittest.main()
