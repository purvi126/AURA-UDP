"""Dependency-free SVG comparison based only on measured summary.csv."""
import csv
import sys
from pathlib import Path
from xml.sax.saxutils import escape


def plot(summary, destination):
    with Path(summary).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    metrics = [("PDR", "pdr"), ("DDR", "ddr"), ("Retransmission overhead", "retransmission_overhead")]
    colors = {"baseline": "#537cba", "sr": "#41a477", "aura": "#d98d42"}
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520">',
           '<rect width="900" height="520" fill="white"/>',
           '<text x="36" y="38" font-family="sans-serif" font-size="24">Measured NS2 comparison</text>']
    for j, (title, key) in enumerate(metrics):
        x = 40 + 285*j
        out.append(f'<text x="{x}" y="85" font-family="sans-serif" font-size="17">{escape(title)}</text>')
        for i, row in enumerate(rows):
            value = float(row[key])
            y = 110 + 115*i
            width = min(215, max(0, 190*value))
            color = colors.get(row["mode"], "#888")
            out.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="14">{escape(row["mode"])}</text>')
            out.append(f'<rect x="{x}" y="{y+9}" width="{width:.1f}" height="29" fill="{color}"/>')
            out.append(f'<text x="{x}" y="{y+58}" font-family="sans-serif" font-size="13">{value:.3f}</text>')
    out.append('</svg>')
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    Path(destination).write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    plot(sys.argv[1], sys.argv[2])
