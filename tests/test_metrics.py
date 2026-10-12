import csv
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "analysis"))
from metrics import calculate


class MetricsTest(unittest.TestCase):
    def test_duplicate_and_retransmission_count_once(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "events.csv"
            with path.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["time", "event", "id", "class", "attempt", "deadline"])
                for row in [(0, "generate", 1, "critical", 0, .2),
                            (.01, "send", 1, "critical", 1, .2),
                            (.11, "send", 1, "critical", 2, .2),
                            (.15, "deliver", 1, "critical", 2, .2),
                            (.16, "duplicate", 1, "critical", 1, .2)]:
                    w.writerow(row)
            result = calculate(path)
            self.assertEqual(result["delivered"], 1)
            self.assertEqual(result["ddr"], 1)
            self.assertEqual(result["retransmission_overhead"], 1)


if __name__ == "__main__":
    unittest.main()
