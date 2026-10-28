"""Render a fixed-scale review figure from the four-schedule NS2 results."""
import csv
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "experiments/results/sensitivity/summary.csv"
OUTPUT = ROOT / "experiments/plots/sensitivity.svg"
WORKLOADS = (("crowded", "Crowded link · 300 ms alert deadline"),
             ("tight", "Tight deadline · 120 ms alert deadline"))
SCHEDULES = (("regular", "Regular · alert first"),
             ("regular_late_alert", "Regular · alert last"),
             ("burst_first_alert", "Burst · alert first"),
             ("burst_late_alert", "Burst · alert last"))
VARIANTS = (("baseline", "One-shot", "#b45a32"),
            ("aura", "Original AURA", "#087b78"),
            ("aura_reserved", "Reserved AURA", "#68549b"))


def render(summary_path=SUMMARY, output=OUTPUT):
    with Path(summary_path).open(newline="", encoding="utf-8") as stream:
        rows = {(row["scenario"], row["variant"]): row
                for row in csv.DictReader(stream)}
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="1270" viewBox="0 0 1120 1270" role="img" aria-labelledby="title desc">',
        '<title id="title">Alert arrival schedule sensitivity at a 128 Kb/s bottleneck</title>',
        '<desc id="desc">Fixed zero-to-100-percent deadline delivery bars compare one-shot, original AURA, and reserved AURA in two crowded workloads. Four schedules separate regular or burst timing from alert-first or alert-last order. Each result averages 30 NS2 seed indices.</desc>',
        '<rect width="1120" height="1270" fill="#f5f2eb"/>',
        '<text x="40" y="48" font-family="Arial,sans-serif" font-size="30" font-weight="700" fill="#163b43">When does alert order matter?</text>',
        '<text x="40" y="78" font-family="Arial,sans-serif" font-size="16" fill="#52666b">Deadline delivery ratio · 128 Kb/s bottleneck · 30 paired seeds per condition · fixed 0–100% scale</text>',
    ]
    for section_index, (workload, title) in enumerate(WORKLOADS):
        top = 105 + section_index * 557
        lines.extend([
            f'<rect x="28" y="{top}" width="1064" height="545" rx="18" fill="#fffefa" stroke="#d7dedb"/>',
            f'<text x="50" y="{top+34}" font-family="Arial,sans-serif" font-size="22" font-weight="700" fill="#163b43">{escape(title)}</text>',
            f'<text x="50" y="{top+58}" font-family="Arial,sans-serif" font-size="14" fill="#52666b">Two competing CBR flows · six-packet DropTail queue · 120 generated messages (30 alerts) per run</text>',
        ])
        for schedule_index, (schedule, label) in enumerate(SCHEDULES):
            group_y = top + 78 + schedule_index * 114
            lines.extend([
                f'<text x="50" y="{group_y+15}" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#20343a">{escape(label)}</text>',
                f'<line x1="50" y1="{group_y+109}" x2="1065" y2="{group_y+109}" stroke="#e7eeea"/>',
            ])
            for variant_index, (variant, variant_label, color) in enumerate(VARIANTS):
                key = (f"{workload}_{schedule}_128", variant)
                if key not in rows:
                    raise ValueError(f"Missing sensitivity result: {key}")
                row = rows[key]
                if row["seeds"] != "30":
                    raise ValueError(f"Expected 30 seeds for {key}")
                value = float(row["ddr_mean"])
                if not 0 <= value <= 1:
                    raise ValueError(f"DDR outside [0, 1] for {key}")
                bar_y = group_y + 23 + variant_index * 27
                lines.extend([
                    f'<text x="55" y="{bar_y+16}" font-family="Arial,sans-serif" font-size="14" fill="#354b4f">{escape(variant_label)}</text>',
                    f'<rect x="230" y="{bar_y}" width="670" height="19" rx="5" fill="#e9eeeb"/>',
                    f'<rect x="230" y="{bar_y}" width="{670*value:.1f}" height="19" rx="5" fill="{color}"/>',
                    f'<text x="918" y="{bar_y+16}" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#20343a">{value*100:.1f}%</text>',
                ])
    lines.extend([
        '<text x="40" y="1243" font-family="Arial,sans-serif" font-size="14" fill="#52666b">Bars show timely alerts divided by all generated alerts. Reservation can lower routine delivery; read the paired CSVs for that tradeoff.</text>',
        '</svg>',
    ])
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    render()
