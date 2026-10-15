"""Build the editable AURA-UDP Review 2 progress report from checked-in evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
BLUE = "173B59"
PALE = "EAF1F6"
GRAY = "D9D9D9"


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def border(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for side in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{side}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "5")
        element.set(qn("w:color"), GRAY)
        borders.append(element)


def table(doc, headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.autofit = False
    for i, header in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.width = Inches(widths[i])
        cell.text = header
        shade(cell, BLUE)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
        border(cell)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].width = Inches(widths[i])
            cells[i].text = str(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri % 2:
                shade(cells[i], "F4F7F9")
            border(cells[i])
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.12
                for run in p.runs:
                    run.font.size = Pt(9)
            margins = cell._tc.get_or_add_tcPr()
            mar = OxmlElement("w:tcMar")
            for side in ("top", "start", "bottom", "end"):
                e = OxmlElement(f"w:{side}")
                e.set(qn("w:w"), "90")
                e.set(qn("w:type"), "dxa")
                mar.append(e)
            margins.append(mar)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def add_text(doc, text, *, bold_lead=None):
    p = doc.add_paragraph()
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(text)
    return p


def add_caption(doc, text):
    p = doc.add_paragraph(style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(text)
    return p


def page_break(doc):
    doc.add_page_break()


def build(output: Path, chart_png: Path) -> None:
    doc = Document()
    doc.core_properties.title = "AURA-UDP Computer Networks Lab Review 2"
    doc.core_properties.subject = "Seven-page implementation progress report"
    doc.core_properties.author = "Purvi Valmeti; M Harshita Sri"
    doc.core_properties.keywords = "AURA-UDP, NS2, Cisco Packet Tracer, Review 2"
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.top_margin = Inches(0.72)
    sec.bottom_margin = Inches(0.68)
    sec.left_margin = Inches(0.76)
    sec.right_margin = Inches(0.76)
    sec.header_distance = Inches(0.3)
    sec.footer_distance = Inches(0.35)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(25, 32, 38)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.17
    for name, size, before, after in [
        ("Title", 20, 0, 13),
        ("Heading 1", 13, 13, 6),
        ("Heading 2", 11, 10, 4),
    ]:
        s = styles[name]
        s.font.name = "Aptos"
        s.font.size = Pt(size)
        s.font.bold = name != "Title"
        s.font.color.rgb = RGBColor(0, 0, 0)
        s.paragraph_format.space_before = Pt(before)
        s.paragraph_format.space_after = Pt(after)
        s.paragraph_format.keep_with_next = True
    styles["Title"].font.bold = True
    # Word's built-in Title style can carry an accent border in some themes.
    title_ppr = styles["Title"].element.get_or_add_pPr()
    for existing in list(title_ppr):
        if existing.tag == qn("w:pBdr"):
            title_ppr.remove(existing)
    styles["Caption"].font.name = "Aptos"
    styles["Caption"].font.size = Pt(8.5)
    styles["Caption"].font.color.rgb = RGBColor(70, 79, 87)
    styles["Caption"].paragraph_format.space_after = Pt(8)
    styles["List Bullet"].paragraph_format.space_after = Pt(4)

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run("15 October 2026  •  Page ")
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    footer._p.append(fld)

    course = doc.add_paragraph()
    course.paragraph_format.space_after = Pt(5)
    course.add_run("COMPUTER NETWORKS LAB  |  REVIEW 2").bold = True
    doc.add_paragraph("AURA-UDP implementation progress report", style="Title")
    p = doc.add_paragraph()
    p.add_run("Implementation assessment  •  Approximately 70–75% complete").bold = True
    p.add_run("\nDeadline-aware reliable transport for critical campus IoT messages")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Purvi Valmeti").bold = True
    p.add_run("  •  24BCE2191")
    p.add_run("\n")
    p.add_run("M Harshita Sri").bold = True
    p.add_run("  •  24BCE2471")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    p.add_run("GitHub repository: ")
    p.add_run("https://github.com/purvi126/AURA-UDP")
    add_text(doc, "This report explains what has been built, how it was checked, what the measured results show, and what remains for the final review. The 70–75% figure is an assessment of project readiness, not a measured software or network metric.")
    doc.add_heading("The project in one minute", level=1)
    add_text(doc, "A smart campus sends routine readings and urgent alerts to a monitoring room. A lost or late routine reading may be tolerable; a smoke alert is useful only if it arrives before its deadline. AURA-UDP asks whether a sender can improve timely alert delivery while controlling the cost of retransmissions.")
    add_text(doc, "Two tools show different parts of that question. NS2 runs the actual transport experiment and produces timing, loss, and retry measurements. Cisco Packet Tracer is an editable campus network model that shows routers, HTTP connectivity, an IoT gateway, and registered sensor devices. The tools do not exchange live packets.")
    doc.add_heading("What is implemented at this milestone", level=1)
    table(doc, ["Workstream", "Implemented and evidenced", "Status"], [
        ("Transport in NS2", "Baseline, Selective Repeat, and AURA sender/receiver behavior; ACKs, deadlines, retry and congestion-window decisions.", "Built"),
        ("Evaluation", "Three scenarios, paired seed sweeps, policy ablations, fresh-seed checks, metrics, charts, and a local dashboard.", "Built"),
        ("Campus in Packet Tracer", "Two routers, monitoring server, native temperature and smoke devices, gateway registration, routed HTTP check.", "Built"),
        ("Final research claim and demo", "Wider workloads, stronger fairness/congestion tests, improved retry estimate, and final presentation evidence.", "Remaining"),
    ], [1.45, 4.65, 0.83])
    doc.add_heading("How the pieces fit", level=1)
    add_text(doc, "Campus alert idea  →  NS2 sender and lossy link  →  event logs and metrics  →  comparison charts and dashboard")
    add_text(doc, "Campus layout idea  →  Packet Tracer routers, server, gateway, and sensors  →  connectivity and registration screenshots")

    page_break(doc)
    doc.add_heading("What happens inside NS2", level=1)
    add_text(doc, "The script ns2/run.tcl builds a sender, router, monitoring receiver, and competing CBR sender. Its 128 Kb/s bottleneck has a short queue and configurable packet loss. Each run creates 30 messages; every fourth is critical and has an absolute deadline. Data and ACK paths have separate loss streams.")
    table(doc, ["Mode", "Sender behavior", "Purpose"], [
        ("Baseline UDP", "Sends a message once; no ACK or retry.", "Reference for low overhead."),
        ("Fixed Selective Repeat", "Uses a four-message window, ACKs and individual retries with a fixed timer.", "Reference reliable method."),
        ("AURA", "Orders urgent alerts by deadline, gives routine traffic regular turns, adapts timer and small window, and checks whether a retry can still arrive in time.", "Tests the deadline-aware policy."),
    ], [1.48, 4.35, 1.1])
    doc.add_heading("The decision being tested", level=2)
    add_text(doc, "For a critical message, the sender compares estimated forward delivery time with time remaining until its absolute deadline. If the estimated trip is longer, AURA abandons that retransmission. The first send is still attempted while the alert is live. This can save traffic, but a rough estimate may reject a retry that would have succeeded.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Retry when estimated delivery time ≤ deadline − current time")
    run.bold = True
    add_text(doc, "AURA takes RTT samples only from packets that have not been retransmitted, then uses smoothed RTT and variation to set a bounded retry timer. Its sender window starts at four messages, can grow to six after ACK progress, and falls back on a timeout. After three urgent admissions, a waiting routine message gets the next available slot. These are explicit lab rules, not a claim of a complete Internet congestion controller.")
    doc.add_heading("What is measured", level=2)
    add_bullet(doc, "Deadline delivery ratio (DDR): critical messages first delivered on time divided by all generated critical messages, including lost and abandoned ones.")
    add_bullet(doc, "Packet delivery ratio (PDR): unique messages delivered eventually divided by all generated messages. A late alert can count in PDR but not DDR.")
    add_bullet(doc, "Also recorded: delay for delivered messages, extra sends per generated message, routine delivery, and received background traffic.")
    add_text(doc, "NS2 writes events.csv, control.csv, background.csv, a packet trace, and a NAM trace. Python analysis deduplicates message IDs and produces summary CSVs, plots, and the local dashboard. The dashboard reads saved results; it does not run NS2.")
    doc.add_heading("Experiment design", level=2)
    add_text(doc, "The development set uses 30 seed indices across three conditions and three transport modes (270 runs), plus four AURA variants (360 runs). A fresh 30-seed set repeats both sweeps. Total recorded evaluation: 1,260 NS2 runs. Within a scenario, modes use the same topology, generation schedule, and seed index; changed retry behavior means packet-by-packet loss draws are not identical.")

    page_break(doc)
    doc.add_heading("NS2 evidence and measured findings", level=1)
    add_text(doc, "The figure below is generated from the checked-in NS2 run summaries. It compares delivery and retry behavior across moderate loss, tight deadlines, and a higher message rate. It is experimental output, not Packet Tracer traffic.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(chart_png), width=Inches(6.35))
    add_caption(doc, "Figure 1  NS2 30-seed comparison from experiments/plots/multiseed.svg")
    table(doc, ["Scenario", "Baseline DDR", "Fixed SR DDR", "AURA DDR"], [
        ("Moderate loss", "81.7%", "83.3%", "93.3%"),
        ("Tight deadline", "12.9%", "10.0%", "10.4%"),
        ("High message rate", "86.3%", "73.3%", "89.2%"),
    ], [2.03, 1.6, 1.6, 1.7])
    add_text(doc, "AURA delivered more critical messages on time than fixed SR in the moderate and high-rate conditions. The tight-deadline condition remained difficult for every mode, and baseline exceeded AURA there. The feasibility check reduced high-rate retry cost in the development set, but did not show a DDR gain; on fresh seeds, full AURA and the version without this check both reached 90.4% DDR. These are descriptive results for three short synthetic workloads.")

    page_break(doc)
    doc.add_heading("Cisco Packet Tracer implementation", level=1)
    add_text(doc, "The editable packet_tracer/topology/AURA-UDP-campus.pkt models the campus side of the project. PC0 on the sensor LAN reaches Server0 at 10.10.30.10 through Router0 and Router1. Separately, a native Temperature Monitor and Smoke Detector register with HomeGateway0; Tablet PC0 displays them at 192.168.25.1.")
    t = doc.add_table(rows=1, cols=2)
    t.autofit = False
    captures = [
        (ROOT / "packet_tracer/documentation/media/routed-http-pc0.jpg", "PC0 browser: routed HTTP page served by Server0."),
        (ROOT / "packet_tracer/documentation/media/gateway-devices.jpg", "Tablet gateway view: smoke and temperature devices registered."),
    ]
    for cell, (path, caption) in zip(t.rows[0].cells, captures):
        cell.width = Inches(3.42)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Inches(3.17))
        cp = cell.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cp.add_run(caption)
        r.font.size = Pt(8.5)
        r.italic = True
    add_caption(doc, "Figures 2 and 3  Original 513-pixel Packet Tracer captures; captions identify the verified checks")
    doc.add_heading("Addressing and the two verified paths", level=2)
    table(doc, ["Segment", "Addresses", "Role"], [
        ("Sensor LAN", "10.10.10.0/24", "PC0–PC2 and HomeGateway0 reach Router0."),
        ("Router transit", "10.10.20.0/30", "Router0 and Router1 exchange routed traffic."),
        ("Server LAN", "10.10.30.0/24", "Server0 is 10.10.30.10."),
        ("Gateway IoT LAN", "192.168.25.0/24", "Tablet and native sensors use the gateway's local network."),
    ], [1.55, 1.55, 3.83])
    add_text(doc, "PC0's HTTP check crosses both routers to Server0. The separate tablet check stays on the gateway LAN and shows TEMP-SENSOR and SMOKE-SENSOR. PC3 can also load the page, but shares Server0's LAN, so that check alone does not prove routing.")
    add_text(doc, "Packet Tracer does not run AURA or feed NS2. A triggered smoke transition remains unverified; the gateway settings are for a lab demonstration.")

    page_break(doc)
    doc.add_heading("Results pipeline and reviewer interface", level=1)
    add_text(doc, "A simulation run is useful only if its output can be inspected and counted consistently. The repository keeps the run configuration, the raw event sequence, per-run measurements, and summary tables. This allows a reviewer to trace a plotted value back to generated messages rather than accepting a dashboard number without evidence.")
    table(doc, ["Stage", "Main file or output", "What happens"], [
        ("1  Simulate", "ns2/run.tcl", "Builds the network and schedules data, ACKs, loss, deadlines, and competing CBR traffic."),
        ("2  Record", "events.csv, control.csv, background.csv", "Logs message events, sender policy decisions, and received competing traffic."),
        ("3  Calculate", "python/analysis/metrics.py", "Counts unique deliveries, on-time critical arrivals, delay, retry cost, and goodput."),
        ("4  Repeat", "scripts/multiseed.py, scripts/ablation.py", "Runs the mode comparison and four policy variants for paired seed indices."),
        ("5  Present", "summary.csv, SVG plots, dashboard", "Shows the measured comparisons and lets a reviewer inspect saved message events."),
    ], [1.0, 2.55, 3.38])
    doc.add_heading("Why the measurements are auditable", level=2)
    add_text(doc, "Each message has an ID, so duplicate packet arrivals do not become multiple successful deliveries. A critical message that arrives after its deadline is still a delivery for PDR but is a DDR miss. Lost, expired, and sender-abandoned alerts remain in DDR's denominator. The competing flow is measured at its receiving agent rather than inferred from offered load. These choices prevent a large retry count from being mistaken for useful alert delivery.")
    add_text(doc, "The experiment configuration is checked in beside the CSVs. Separate RNG streams model data and ACK errors. A matched seed index gives a consistent comparison framework, but different sending policies consume different random draws; it does not guarantee identical per-packet losses. The result tables report means and paired bootstrap intervals for the chosen scenarios, not a universal performance guarantee.")
    doc.add_heading("What the dashboard does", level=2)
    add_text(doc, "The local Python dashboard is a guided viewer for the saved NS2 experiment. A reviewer can choose a condition, compare baseline, fixed Selective Repeat, and AURA, inspect the feasibility-rule ablation, and follow one message through generation, sending, retry, delivery, or deadline miss. Its files live in python/dashboard/. It reads committed results; opening the page neither starts a simulator nor connects to Packet Tracer.")
    doc.add_heading("Code and build checks", level=2)
    add_text(doc, "The validation record reports 19 passing Python and NS2 checks. They cover deadline expiration, abandonment, bounded-window response, the DDR denominator, competing-flow goodput, and chart generation. GitHub Actions installs NS2, runs the tests, checks dashboard syntax and data paths, and executes small comparison and ablation smoke sweeps on pushes. Full 30-seed sweeps were also repeated and their key CSV outputs matched byte for byte.")

    page_break(doc)
    doc.add_heading("Review 2 completion assessment", level=1)
    add_text(doc, "The present project is a working research prototype with an editable campus demonstration. The 70–75% estimate reflects completion of the main implementation and evidence pipeline, while allowing substantial work for stronger validation and the final demonstration. It is an assessment of deliverables, not a score assigned by the course or a percentage derived from lines of code.")
    table(doc, ["Work area", "Evidence already available", "Work still needed"], [
        ("NS2 transport", "Three sender modes, ACK handling, deadlines, RTT-based timing, and a bounded window execute in ns2/run.tcl.", "Refine the forward-time estimate; test behavior over wider queueing and congestion regimes."),
        ("Experimental analysis", "1,260 recorded runs, per-run data, summaries, plots, policy ablations, and fresh-seed replication.", "Use longer and more varied workloads; study multiple competitors and fairness more directly."),
        ("Packet Tracer campus", "Saved .pkt topology, routed PC0 HTTP, ping checks, native sensor registration, and gateway screenshots.", "Verify a triggered smoke transition and capture a clearer end-to-end demonstration sequence."),
        ("Dashboard and documentation", "Local results viewer, README, protocol description, build guide, validation record, and this report.", "Polish final presentation and ensure a reviewer can reproduce the demonstration without setup surprises."),
        ("Final claim", "Measured gains in two scenarios and a documented failure case; feasibility ablation is reported honestly.", "Decide whether an improved decision rule gives a repeatable DDR benefit without harming routine traffic."),
    ], [1.28, 2.82, 2.83])
    doc.add_heading("What the current results support", level=2)
    add_bullet(doc, "AURA's complete sender policy improved on-time critical delivery against fixed SR in the moderate-loss and high-rate development scenarios.")
    add_bullet(doc, "The tight-deadline setting exposed a real limitation: few critical alerts reached the receiver on time, and baseline did better than AURA.")
    add_bullet(doc, "The newer feasibility decision saved some retry traffic in the development high-rate case, but no DDR improvement was demonstrated; fresh-seed high-rate DDR was equal with and without it.")
    doc.add_heading("What should not be claimed yet", level=2)
    add_text(doc, "The data do not establish that AURA is generally superior across networks or that its small adaptive window is Internet-grade congestion control. Packet Tracer shows connectivity and IoT registration, not AURA transport behavior. The native sensors in Packet Tracer are not live inputs to the NS2 workload. Keeping those boundaries explicit makes the final review stronger because every claim has a matching check.")

    page_break(doc)
    doc.add_heading("Verification and final review plan", level=1)
    add_text(doc, "The repository records 19 passing Python and NS2 checks, repeatable sweep outputs, and a GitHub Actions workflow that runs tests and small NS2 smoke sweeps. The saved Packet Tracer checks cover routed HTTP, pings, and native IoT registration. Versioned Git commits and releases provide rollback points.")
    doc.add_heading("Remaining work for the final review", level=2)
    add_bullet(doc, "Test longer and more varied workloads, more competing traffic, and a wider range of deadlines and loss conditions.")
    add_bullet(doc, "Improve the forward-time estimate with queueing uncertainty and evaluate whether the deadline decision improves DDR without starving routine traffic.")
    add_bullet(doc, "Strengthen congestion and fairness evaluation; the current bounded window is a lab heuristic, not an Internet-grade controller.")
    add_bullet(doc, "Capture a verified smoke-event transition in Packet Tracer and prepare a concise live demonstration and final report.")
    doc.add_heading("How to reproduce the evidence", level=2)
    add_text(doc, "Open packet_tracer/topology/AURA-UDP-campus.pkt in Packet Tracer 9.0. On PC0, browse to http://10.10.30.10. On Tablet PC0, browse to http://192.168.25.1 and inspect the gateway device list.")
    add_text(doc, "In Ubuntu or WSL with NS2 2.35 installed, run python3 scripts/multiseed.py and python3 scripts/ablation.py from the repository root. Open experiments/plots/multiseed.svg and docs/RESEARCH_EVALUATION.md for the measured comparison. To inspect the local dashboard, start python3 -m http.server 8000 --bind 127.0.0.1 from the repository root, then open http://localhost:8000/python/dashboard/.")
    doc.add_heading("Source files in the repository", level=2)
    table(doc, ["File or folder", "What it contains"], [
        ("ns2/run.tcl", "Topology, transport behavior, deadlines, ACKs, and logs."),
        ("scripts/ and python/analysis/", "Experiment runners, metrics, and plots."),
        ("experiments/results/", "Per-run and summary data for development and fresh seeds."),
        ("packet_tracer/", "Editable campus topology, web page, build guide, and captures."),
        ("docs/PROTOCOL.md and docs/VALIDATION.md", "Decision rules and verification record."),
    ], [2.65, 4.28])
    add_text(doc, "Review 2 conclusion: the core simulation, comparison pipeline, campus model, and presentation evidence are implemented. The final phase should focus on broader validation and a clearer demonstration of when the deadline-aware decision helps or fails.")

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--chart-png",
        type=Path,
        default=ROOT / "docs/reviews/assets/multiseed.png",
    )
    args = parser.parse_args()
    build(args.output, args.chart_png)
