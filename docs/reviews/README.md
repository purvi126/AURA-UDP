# Review 2 progress report

The [PDF](AURA-UDP-Review-2-70-percent-progress.pdf) and [editable Word document](AURA-UDP-Review-2-70-percent-progress.docx) summarize the implementation as of 15 October 2026. The 70% figure is an overall planning estimate for the academic project, not a measured completion metric or a transport result.

The NS2 figure comes from [the 30-seed comparison](../../experiments/plots/multiseed.svg). The Packet Tracer captures are the original [routed HTTP](../../packet_tracer/documentation/media/routed-http-pc0.jpg) and [gateway device](../../packet_tracer/documentation/media/gateway-devices.jpg) screenshots. Their small source resolution is why the report uses explanatory captions.

The Word file can be rebuilt with `python scripts/build_review2_report.py --output docs/reviews/AURA-UDP-Review-2-70-percent-progress.docx` from the repository root after installing `python-docx`. The checked-in `assets/multiseed.png` is a raster export of the linked SVG for Word compatibility. Export the Word file to PDF after edits, and inspect each page before replacing the checked-in PDF.
