"""Draw a readable, fixed-scale SVG of long-workload deadline delivery."""
import csv
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "experiments/results/robustness/summary.csv"
OUTPUT = ROOT / "experiments/plots/robustness.svg"
SCENARIOS = (("long_moderate", "Long moderate", "120 messages · one CBR flow · queue 12"),
             ("long_high_rate", "Long high rate", "120 messages · one CBR flow · queue 12"),
             ("two_flow_congestion", "Two-flow congestion", "120 messages · two CBR flows · queue 6"),
             ("two_flow_tight", "Two-flow tight deadline", "120 messages · two CBR flows · queue 6"))
VARIANTS = (("baseline", "One-shot", "#b45a32"),
            ("sr", "Selective Repeat", "#68549b"),
            ("aura", "AURA", "#087b78"),
            ("aura_no_feasibility", "AURA without feasibility", "#61747a"))


def render(summary_path=SUMMARY, output=OUTPUT):
    with Path(summary_path).open(newline="", encoding="utf-8") as f:
        summary = {(row["scenario"], row["variant"]): row for row in csv.DictReader(f)}
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="876" viewBox="0 0 1060 876" role="img" aria-labelledby="title desc">',
        '<title id="title">Long-workload deadline delivery comparison</title>',
        '<desc id="desc">Fixed-scale bars compare timely critical-alert delivery for one-shot, Selective Repeat, AURA, and AURA without feasibility across four 120-message conditions and 30 seeds each. AURA falls below one-shot under two-flow congestion.</desc>',
        '<rect width="1060" height="876" fill="#f5f2eb"/>',
        '<text x="30" y="43" font-family="Arial,sans-serif" font-size="27" font-weight="700" fill="#163b43">Longer runs reveal where AURA helps—and where it does not</text>',
        '<text x="30" y="73" font-family="Arial,sans-serif" font-size="16" fill="#52666b">Critical alerts delivered before deadline (DDR) · 30 fresh seeds per condition · fixed 0–100% scale</text>',
    ]
    for index, (scenario, title, detail) in enumerate(SCENARIOS):
        y = 94 + index * 184
        lines.extend([
            f'<rect x="28" y="{y}" width="1004" height="173" rx="13" fill="#fffefa" stroke="#d7dedb"/>',
            f'<text x="47" y="{y+27}" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#163b43">{escape(title)}</text>',
            f'<text x="291" y="{y+27}" font-family="Arial,sans-serif" font-size="14" fill="#52666b">{escape(detail)}</text>',
        ])
        for row_index, (variant, label, color) in enumerate(VARIANTS):
            row = summary[scenario, variant]
            value = float(row["ddr_mean"])
            bar_y = y + 39 + row_index * 30
            lines.extend([
                f'<text x="47" y="{bar_y+17}" font-family="Arial,sans-serif" font-size="14" fill="#20343a">{escape(label)}</text>',
                f'<rect x="260" y="{bar_y}" width="620" height="20" rx="5" fill="#e9eeeb"/>',
                f'<rect x="260" y="{bar_y}" width="{620*value:.1f}" height="20" rx="5" fill="{color}"/>',
                f'<text x="896" y="{bar_y+16}" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#20343a">{value*100:.1f}%</text>',
            ])
    lines.extend([
        '<text x="30" y="852" font-family="Arial,sans-serif" font-size="14" fill="#52666b">Two-flow cases show congestion limits. The feasibility rule saves some retries but has no established DDR gain.</text>',
        '</svg>',
    ])
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    render()
