"""Regression checks for plots generated from measured result files."""
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from python.analysis.plot import plot

ROOT = Path(__file__).resolve().parents[1]


class PlotTest(unittest.TestCase):
    def test_full_sweep_fits_all_scenarios(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sweep.svg"
            plot(ROOT / "experiments/results/multiseed/summary.csv", output)
            root = ET.parse(output).getroot()
            self.assertEqual(root.attrib["viewBox"], "0 0 1020 829")
            text = output.read_text(encoding="utf-8")
            for label in ("Moderate", "Tight Deadline", "High Rate"):
                self.assertIn(label, text)

    def test_sample_uses_single_scenario(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sample.svg"
            plot(ROOT / "experiments/results/sample/summary.csv", output)
            root = ET.parse(output).getroot()
            self.assertEqual(root.attrib["viewBox"], "0 0 1020 419")


if __name__ == "__main__":
    unittest.main()
