"""Render sample or multi-seed result CSV as an accessible, dependency-free SVG."""
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

COLORS = {"baseline": "#b45a32", "sr": "#68549b", "aura": "#087b78"}
NAMES = {"baseline": "Baseline", "sr": "Selective Repeat", "aura": "AURA"}
METRICS = (
    ("PDR", "pdr", True),
    ("On-time critical (DDR)", "ddr", True),
    ("Extra sends / message", "retransmission_overhead", False),
)


def plot(summary, destination):
    with Path(summary).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        is_sweep = "scenario" in (reader.fieldnames or ())
    if not rows:
        raise ValueError(f"{summary}: no result rows")
    groups = defaultdict(list)
    for row in rows:
        mode = row.get("mode")
        if mode not in NAMES:
            raise ValueError(f"{summary}: unknown mode {mode!r}")
        groups[row["scenario"] if is_sweep else "Measured sample"].append(row)
    if any(len(group) != 3 or {row["mode"] for row in group} != set(NAMES)
           for group in groups.values()):
        raise ValueError(f"{summary}: each scenario needs one row for each transport mode")

    suffix = "_mean" if is_sweep else ""
    values = {}
    for row in rows:
        for _, metric, is_percent in METRICS:
            value = float(row[metric + suffix])
            if not math.isfinite(value) or value < 0 or (is_percent and value > 1):
                raise ValueError(f"{summary}: invalid {metric} value")
            values[id(row), metric] = value
    overhead_max = max(.5, math.ceil(max(values[id(row), "retransmission_overhead"]
                                        for row in rows) * 2) / 2)

    height = 160 + 205 * len(groups) + 54
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="{height}" viewBox="0 0 1020 {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Measured NS2 transport comparison</title>',
        '<desc id="desc">Each scenario compares baseline UDP, Selective Repeat and AURA for delivery ratio, on-time critical delivery and retransmission overhead.</desc>',
        '<rect width="1020" height="100%" rx="20" fill="#f5f2eb"/>',
        '<text x="34" y="48" fill="#163b43" font-family="Arial,sans-serif" font-size="28" font-weight="700">Measured NS2 outcomes</text>',
        f'<text x="34" y="77" fill="#52666b" font-family="Arial,sans-serif" font-size="16">{"30-seed means for each condition" if is_sweep else "One documented sample run"} · bars use the scales shown below</text>',
    ]
    for x, (title, _, is_percent) in zip((150, 450, 750), METRICS):
        scale = "0–100%" if is_percent else f"0–{overhead_max:g}"
        out.append(f'<text x="{x}" y="115" fill="#20343a" font-family="Arial,sans-serif" font-size="16" font-weight="700">{escape(title)}</text>')
        out.append(f'<text x="{x}" y="137" fill="#607176" font-family="Arial,sans-serif" font-size="13">Scale: {scale}</text>')
    for group_index, (scenario, group) in enumerate(groups.items()):
        top = 164 + group_index * 205
        label = scenario.replace("_", " ").title()
        out.append(f'<rect x="28" y="{top-17}" width="964" height="185" rx="13" fill="#fffefa" stroke="#d7dedb"/>')
        out.append(f'<text x="46" y="{top+10}" fill="#163b43" font-family="Arial,sans-serif" font-size="18" font-weight="700">{escape(label)}</text>')
        for row_index, row in enumerate(sorted(group, key=lambda item: list(NAMES).index(item["mode"]))):
            y = top + 41 + 42 * row_index
            mode = row["mode"]
            out.append(f'<circle cx="51" cy="{y+8}" r="7" fill="{COLORS[mode]}"/>')
            out.append(f'<text x="66" y="{y+14}" fill="#20343a" font-family="Arial,sans-serif" font-size="15">{NAMES[mode]}</text>')
            for x, (_, metric, is_percent) in zip((150, 450, 750), METRICS):
                value = values[id(row), metric]
                maximum = 1 if is_percent else overhead_max
                width = 176 * value / maximum
                display = f"{value*100:.1f}%" if is_percent else f"{value:.2f}"
                out.append(f'<rect x="{x}" y="{y-2}" width="176" height="22" rx="5" fill="#e9eeeb"/>')
                out.append(f'<rect x="{x}" y="{y-2}" width="{width:.1f}" height="22" rx="5" fill="{COLORS[mode]}"/>')
                out.append(f'<text x="{x+184}" y="{y+14}" fill="#20343a" font-family="Arial,sans-serif" font-size="14" font-weight="700">{display}</text>')
    footer_y = height - 25
    out.append(f'<text x="34" y="{footer_y}" fill="#52666b" font-family="Arial,sans-serif" font-size="14">Data: executed NS2 runs · the chart does not establish general superiority</text>')
    out.append("</svg>")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render measured NS2 CSVs as an SVG chart")
    parser.add_argument("summary", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        plot(args.summary, args.destination)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
