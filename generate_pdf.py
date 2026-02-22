#!/usr/bin/env python3
"""
generate_pdf.py — Convert FINDINGS.md to publication-quality PDF

Two engines:
  1. Pandoc + LaTeX     (gold standard for QJE / Brookings / SSRN)
  2. xhtml2pdf          (pure Python, no native deps, pip install xhtml2pdf markdown)

Usage:
  python generate_pdf.py                    # Auto-detect best engine
  python generate_pdf.py --engine pandoc    # Force Pandoc/LaTeX
  python generate_pdf.py --engine xhtml2pdf # Force xhtml2pdf
  python generate_pdf.py --engine both      # Generate both versions

Installation:
  Quick (Option B):   pip install xhtml2pdf markdown
  Best  (Option A):   Install Pandoc (https://pandoc.org) + MiKTeX (https://miktex.org)
"""

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FINDINGS_MD = OUTPUT_DIR / "FINDINGS.md"
FIGURES_DIR = OUTPUT_DIR / "figures"
PDF_DIR = OUTPUT_DIR / "reports"
PDF_DIR.mkdir(parents=True, exist_ok=True)

PANDOC_PDF = PDF_DIR / "FINDINGS_journal.pdf"
XHTML2PDF_OUT = PDF_DIR / "FINDINGS_publication.pdf"

FIGURE_FILES = sorted(
    [f for f in FIGURES_DIR.glob("*.png")],
    key=lambda p: p.name,
)

FIGURE_DESCRIPTIONS = {
    "01_outlay_composition.png": "Federal outlay composition (stacked area, FY2015-2025)",
    "02_revenue_composition.png": "Revenue by source (stacked area)",
    "03_interest_vs_safety_net.png": "Net interest vs. safety-net spending",
    "04_cpi_essentials.png": "CPI essentials indexed (with tariff event markers)",
    "05_profits_vs_wages.png": "Corporate profits vs. wages (indexed)",
    "06_customs_revenue_spike.png": "Customs revenue spike (bar chart)",
    "07_deficit_trend.png": "Federal deficit trend (with policy periods)",
    "09_income_security_waterfall.png": "Income security waterfall (FY2019-2025)",
    "10_interest_pct_gdp.png": "Net interest as percent of GDP",
    "fig1_income_distribution.png": "Income distribution by quintile (CPS ASEC)",
    "fig2_distributional_impact.png": "Distributional impact of FY2025 policy",
    "fig3_quantile_treatment_effects.png": "Simulated distributional burden curve",
    "fig4_spm_poverty_simulation.png": "SPM poverty simulation",
    "fig5_state_exposure.png": "State exposure classification map",
    "fig6_welfare_weighted_impact.png": "Welfare-weighted impact (CRRA)",
    "fig7_tariff_price_changes.png": "CPI price changes in tariff-affected goods",
    "fig8_tariff_burden_by_quintile.png": "Tariff burden by income quintile",
    "fig9_b50_tariff_by_category.png": "B50 vs. T50 tariff cost by goods category",
    "fig11_burden_decomposition.png": "Burden decomposition by income percentile (stacked area)",
    "fig12_structural_break_bands.png": "Structural break prediction bands (forest plot)",
    "fig13_services_price_acceleration.png": "Tariff pass-through: traded goods vs. services control",
    "fig14_b50_calibration.png": "B50 calibration diagram (quintile person shares)",
    "fig15_specification_curve.png": "Robustness specification summary (6 dimensions)",
    "fig16_counterfactual_waterfall.png": "CBO counterfactual waterfall (baseline to actual)",
    "fig17_historical_b50.png": "Historical B50 income share and transfer dependency",
    "fig18_welfare_logscale.png": "Welfare-weighted loss (log-scale, CRRA σ=2)",
    "fig19_state_exposure_dots.png": "State fiscal exposure index (dot plot)",
    "fig20_spm_dose_response.png": "SPM poverty dose-response (food program scenarios)",
    "fig21_scotus_scenario_comparison.png": "SCOTUS scenario: B50 per-person burden comparison (Section 12)",
    "fig22_scotus_quintile_decomposition.png": "Central combined scenario: quintile burden decomposition (Section 12)",
    "fig23_price_stickiness_flows.png": "Price stickiness and the incidence of tariff revocation (Section 12)",
    "fig24_scotus_welfare_sensitivity.png": "SCOTUS scenario: sensitivity range and welfare impact (Section 12)",
    "real_budget_function_waterfall.png": "Budget function waterfall (real terms)",
    "real_cumulative_by_tier.png": "Cumulative spending by tier (real terms)",
    "real_defense_vs_social.png": "Defense vs. social spending (real terms)",
    "real_interest_timeline.png": "Interest payment timeline (real terms)",
    "real_propensity_comparison.png": "Propensity classification comparison",
    "real_propensity_stacked_area.png": "Propensity stacked area chart",
    "real_tariff_windfall_flow.png": "Tariff windfall flow diagram. Assumes 4.5% 10-yr rate (FRED DGS10), 20× P/E (conservative); equity ownership 93% top-10 (Fed 2023 SCF), bond ownership ~67% top-10 (Fed DFA)",
    "real_top_agencies.png": "Top agencies by spending change",
    "25yr_spending_composition.png": "Real spending composition (stacked area, FY2000–2025)",
    "25yr_revenue_composition.png": "Revenue composition shares (stacked area, FY2000–2025)",
    "25yr_interest_vs_safetynet.png": "Interest vs. safety-net spending (25-year trajectory)",
    "25yr_customs_trajectory.png": "Customs revenue trajectory (with tariff regime markers)",
    "25yr_inequality_evolution.png": "Income inequality evolution (Census quintile shares)",
    "25yr_poverty_and_benefits.png": "B50 transfer dependency and poverty (CPS ASEC benchmarks)",
    "25yr_structural_breaks.png": "Structural break tests (4-panel: actual vs. trend)",
    "25yr_fy2025_context_dashboard.png": "FY2025 context dashboard (6-panel summary)",
}


def check_pandoc():
    pandoc_ok = shutil.which("pandoc") is not None
    latex_ok = any(shutil.which(e) for e in ("xelatex", "pdflatex", "lualatex"))
    return pandoc_ok and latex_ok


def check_xhtml2pdf():
    try:
        import xhtml2pdf  # noqa: F401
        return True
    except ImportError:
        return False


# ==============================================================================
#  PANDOC / LaTeX PIPELINE
# ==============================================================================

def prepare_pandoc_markdown():
    """Prepare Markdown with YAML front-matter for Pandoc -> LaTeX -> PDF."""
    text = FINDINGS_MD.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract title from the first H1 line in FINDINGS.md
    doc_title = "Working Paper"
    for line in lines:
        if line.startswith("# "):
            doc_title = line.lstrip("# ").strip()
            break

    yaml_block = f"""---
title: |
  {doc_title}
author:
  - Andy Salazar
date: February 2026
abstract: |
"""

    # Extract abstract
    in_abstract = False
    abstract_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith("## Abstract"):
            in_abstract = True
            continue
        if in_abstract:
            if line.startswith("**Keywords"):
                break
            abstract_lines.append("  " + line)

    yaml_block += "\n".join(abstract_lines).rstrip() + "\n"

    keywords = ""
    for line in lines:
        if line.startswith("**Keywords:**"):
            keywords = line.replace("**Keywords:**", "").strip()

    yaml_block += f"""
keywords: "{keywords}"
thanks: "Working Paper. Replication package: https://github.com/andsalazar/FederalBudgetAnalysis. Pre-registration: docs/hypothesis_preregistration.md"
geometry: margin=1in
fontsize: 11pt
linestretch: 1.5
numbersections: false
header-includes:
  - \\usepackage{{booktabs}}
  - \\usepackage{{longtable}}
  - \\usepackage{{graphicx}}
  - \\usepackage{{float}}
  - \\usepackage{{caption}}
  - \\captionsetup{{font=small,labelfont=bf}}
  - \\usepackage{{hyperref}}
  - \\hypersetup{{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}}
  - \\usepackage{{amsmath}}
  - \\usepackage{{array}}
  - \\renewcommand{{\\arraystretch}}{{1.2}}
  - \\setlength{{\\tabcolsep}}{{4pt}}
---
"""

    # Build body from "## 1. Introduction" onward
    body_lines = []
    found = False
    for line in lines:
        if "## 1. Introduction" in line:
            found = True
        if found:
            body_lines.append(line)
    body = "\n".join(body_lines)

    # Page breaks between major sections
    body = re.sub(r"\n(## \d+\.)", r"\n\\newpage\n\1", body)

    # Replace Appendix B table with inline figure references
    body = re.sub(r"## Appendix B: Figures.*?(?=\n##|\Z)", "", body, flags=re.DOTALL)

    figures_md = "\n\\newpage\n\n## Appendix B: Figures\n\n"
    for idx, f in enumerate(FIGURE_FILES, 1):
        desc = FIGURE_DESCRIPTIONS.get(f.name, f.stem.replace("_", " ").title())
        figures_md += f"![{desc}](figures/{f.name}){{width=90%}}\n\n"
    body += figures_md

    return yaml_block + "\n" + body


def generate_pandoc_pdf():
    print("=" * 60)
    print("Generating PDF via Pandoc + LaTeX...")
    print("=" * 60)

    prepared_md = PDF_DIR / "FINDINGS_prepared.md"
    prepared_md.write_text(prepare_pandoc_markdown(), encoding="utf-8")

    engine = next(
        (e for e in ("xelatex", "lualatex", "pdflatex") if shutil.which(e)),
        "pdflatex",
    )

    cmd = [
        "pandoc", str(prepared_md), "-o", str(PANDOC_PDF),
        f"--pdf-engine={engine}", "--standalone",
        "--toc", "--toc-depth=3",
        f"--resource-path={OUTPUT_DIR}",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd, capture_output=True, cwd=str(OUTPUT_DIR),
        encoding="utf-8", errors="replace",
    )

    if result.returncode == 0:
        sz = PANDOC_PDF.stat().st_size / (1024 * 1024)
        print(f"\n  PDF generated: {PANDOC_PDF} ({sz:.1f} MB)")
        return True
    else:
        print(f"\n  Pandoc failed: {result.stderr[:500]}")
        return False


# ==============================================================================
#  xhtml2pdf PIPELINE (pure Python, no native deps)
# ==============================================================================

ACADEMIC_CSS = """
@page {
    size: letter;
    margin: 1in 1in 1in 1in;

    @frame header_frame {
        -pdf-frame-content: headerContent;
        top: 0.3in;
        margin-left: 1in;
        margin-right: 1in;
        height: 0.4in;
    }
    @frame footer_frame {
        -pdf-frame-content: footerContent;
        bottom: 0.2in;
        margin-left: 1in;
        margin-right: 1in;
        height: 0.4in;
    }
}

body {
    font-family: Times-Roman;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #111111;
}

h1 {
    font-family: Helvetica;
    font-size: 16pt;
    text-align: center;
    margin-top: 40px;
    margin-bottom: 10px;
    line-height: 1.3;
}

h2 {
    font-family: Helvetica;
    font-size: 13pt;
    margin-top: 25px;
    margin-bottom: 8px;
    border-bottom: 1px solid #cccccc;
    padding-bottom: 4px;
    -pdf-keep-with-next: true;
}

h3 {
    font-family: Helvetica;
    font-size: 11pt;
    margin-top: 18px;
    margin-bottom: 6px;
    -pdf-keep-with-next: true;
}

h4 {
    font-family: Helvetica;
    font-size: 10.5pt;
    margin-top: 14px;
    -pdf-keep-with-next: true;
}

table {
    width: 99%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9pt;
}

thead tr {
    border-top: 2px solid #111111;
    border-bottom: 1px solid #111111;
    background-color: #f0f0f0;
}

tbody tr:last-child {
    border-bottom: 2px solid #111111;
}

th {
    padding: 4px 4px;
    text-align: left;
    font-weight: bold;
    font-family: Helvetica;
    font-size: 8.5pt;
}

td {
    padding: 3px 4px;
    text-align: left;
    font-size: 8.5pt;
}

strong, b {
    font-weight: bold;
}

em, i {
    font-style: italic;
}

code {
    font-family: Courier;
    font-size: 8.5pt;
    background-color: #f4f4f4;
    padding: 1px 2px;
}

img {
    width: 85%;
    display: block;
    margin: 10px auto;
}

.figure-caption {
    text-align: center;
    font-size: 9pt;
    font-style: italic;
    margin-top: 4px;
    margin-bottom: 20px;
}

a {
    color: #1a0dab;
    text-decoration: none;
}

hr {
    border: none;
    border-top: 1px solid #999999;
    margin: 20px 0;
}

ol, ul {
    margin-left: 20px;
    font-size: 10.5pt;
}

li {
    margin-bottom: 4px;
}

.page-break {
    page-break-before: always;
}

.ref-entry {
    text-indent: -24px;
    padding-left: 24px;
    margin-bottom: 4px;
    font-size: 9.5pt;
}
"""


def img_to_data_uri(path: Path) -> str:
    """Convert image file to base64 data URI for embedding in HTML."""
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def markdown_to_html(md_text: str) -> str:
    """Convert FINDINGS.md to styled HTML with embedded figures."""
    import markdown
    from markdown.extensions.tables import TableExtension

    # Strip the Appendix B figure table -- we replace with embedded images
    md_text = re.sub(
        r"## Appendix B: Figures.*?(?=\n##|\Z)",
        "## Appendix B: Figures\n\n<!-- FIGURES -->\n",
        md_text,
        flags=re.DOTALL,
    )

    # Insert page breaks before major numbered sections
    md_text = re.sub(
        r"\n---\n\n(## \d+\.)",
        r'\n<div class="page-break"></div>\n\n\1',
        md_text,
    )

    # Convert Markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=[
            TableExtension(),
            "markdown.extensions.fenced_code",
            "markdown.extensions.smarty",
        ],
    )

    # Build figures HTML with embedded base64 images
    figures_html = ""
    for idx, f in enumerate(FIGURE_FILES, 1):
        desc = FIGURE_DESCRIPTIONS.get(f.name, f.stem.replace("_", " ").title())
        data_uri = img_to_data_uri(f)
        figures_html += (
            f'<div style="margin: 15px 0; text-align: center;">'
            f'<img src="{data_uri}" width="480">'
            f'<div class="figure-caption">Figure {idx}. {desc}</div>'
            f'</div>\n'
        )

    # markdown passes HTML comments through without <p> wrapping
    html_body = html_body.replace("<!-- FIGURES -->", figures_html)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
    {ACADEMIC_CSS}
    </style>
</head>
<body>
    <div id="headerContent">
        <p style="font-size: 8pt; color: #666666; text-align: center; font-family: Helvetica;">
            Working Paper &mdash; February 2026
        </p>
    </div>
    <div id="footerContent">
        <p style="font-size: 9pt; text-align: center; font-family: Helvetica;">
            <pdf:pagenumber>
        </p>
    </div>

    {html_body}
</body>
</html>"""

    return full_html


def generate_xhtml2pdf():
    """Generate PDF via xhtml2pdf (pure Python)."""
    print("=" * 60)
    print("Generating PDF via xhtml2pdf...")
    print("=" * 60)

    from xhtml2pdf import pisa

    md_text = FINDINGS_MD.read_text(encoding="utf-8")
    print("  Converting Markdown to HTML...")
    html = markdown_to_html(md_text)

    # Save HTML preview
    html_file = PDF_DIR / "FINDINGS_preview.html"
    html_file.write_text(html, encoding="utf-8")
    print(f"  HTML preview: {html_file}")

    print("  Rendering PDF (this may take a minute with 29 embedded figures)...")
    with open(XHTML2PDF_OUT, "wb") as pdf_file:
        status = pisa.CreatePDF(html, dest=pdf_file)

    if status.err:
        print(f"\n  xhtml2pdf reported {status.err} error(s)")
        return False

    size_mb = XHTML2PDF_OUT.stat().st_size / (1024 * 1024)
    print(f"\n  PDF generated: {XHTML2PDF_OUT} ({size_mb:.1f} MB)")
    return True


# ==============================================================================
#  MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate publication PDF from FINDINGS.md"
    )
    parser.add_argument(
        "--engine",
        choices=["pandoc", "xhtml2pdf", "both", "auto"],
        default="auto",
        help="PDF engine (default: auto-detect best available)",
    )
    args = parser.parse_args()

    if not FINDINGS_MD.exists():
        print(f"Error: {FINDINGS_MD} not found")
        sys.exit(1)

    print(f"Source:  {FINDINGS_MD}")
    print(f"Figures: {len(FIGURE_FILES)} PNG files in {FIGURES_DIR}")
    print(f"Output:  {PDF_DIR}/\n")

    has_pandoc = check_pandoc()
    has_xhtml2pdf = check_xhtml2pdf()
    print(f"Pandoc + LaTeX:  {'available' if has_pandoc else 'not installed'}")
    print(f"xhtml2pdf:       {'available' if has_xhtml2pdf else 'not installed'}\n")

    engine = args.engine
    if engine == "auto":
        engine = "pandoc" if has_pandoc else ("xhtml2pdf" if has_xhtml2pdf else None)
        if not engine:
            print("No PDF engine found. Install one:")
            print("  pip install xhtml2pdf markdown          (quick)")
            print("  Install Pandoc + MiKTeX                 (best quality)")
            sys.exit(1)

    success = False
    if engine in ("pandoc", "both") and has_pandoc:
        success = generate_pandoc_pdf() or success
    elif engine == "pandoc" and not has_pandoc:
        print("Pandoc + LaTeX not found.")
        print("  Install from https://pandoc.org + https://miktex.org")

    if engine in ("xhtml2pdf", "both") and has_xhtml2pdf:
        success = generate_xhtml2pdf() or success
    elif engine == "xhtml2pdf" and not has_xhtml2pdf:
        print("xhtml2pdf not found. Run: pip install xhtml2pdf markdown")

    if not success:
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PDF READY FOR SUBMISSION")
    print("=" * 60)
    print()
    print("Submission targets:")
    print("  SSRN         Upload PDF at https://www.ssrn.com/")
    print("  Brookings    Contact BPEA editor; PDF + replication package")
    print("  QJE          https://academic.oup.com/qje (LaTeX preferred)")
    print("  NBER WP      Requires affiliation; internal portal")
    print()
    print("For top-5 journals, install Pandoc + MiKTeX for LaTeX-quality output.")
    print("For working paper repos (SSRN, NBER), xhtml2pdf output is sufficient.")


if __name__ == "__main__":
    main()
