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
  python generate_pdf.py --docx             # Also generate Word (.docx)

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

# Canonical filename stem (Author_ShortTitle_Year)
PAPER_STEM = "Salazar_FiscalBreaks_2026"

# Default output names (overridden when --source is used)
PANDOC_PDF = PDF_DIR / f"{PAPER_STEM}_journal.pdf"
XHTML2PDF_OUT = PDF_DIR / f"{PAPER_STEM}_publication.pdf"

# Catalog figures in narrative order (Appendix G, Figures 1–14)
_CATALOG_ORDER = [
    "25yr_structural_breaks.png",            # 1  Structural break tests (4-panel)
    "25yr_customs_trajectory.png",           # 2  Customs revenue trajectory
    "25yr_interest_vs_safetynet.png",        # 3  Interest vs. safety-net (25-year)
    "25yr_revenue_composition.png",          # 4  Revenue composition shares
    "25yr_inequality_evolution.png",         # 5  Income inequality evolution
    "fig2_distributional_impact.png",        # 6  Distributional impact by quintile
    "fig11_burden_decomposition.png",        # 7  Burden decomposition
    "fig13_services_price_acceleration.png", # 8  Tariff pass-through
    "fig7_tariff_price_changes.png",         # 9  CPI price changes
    "fig8_tariff_burden_by_quintile.png",    # 10 Tariff burden by quintile
    "fig16_counterfactual_waterfall.png",    # 11 CBO counterfactual waterfall
    "fig15_specification_curve.png",         # 12 Specification curve
    "fig12_structural_break_bands.png",      # 13 Structural break prediction bands
    "fig14_b50_calibration.png",             # 14 B50 calibration diagram
]

# All PNG files: catalog order first, then remaining in alphabetical order
_all_pngs = sorted(
    [f for f in FIGURES_DIR.glob("*.png")],
    key=lambda p: p.name,
)
_catalog_set = set(_CATALOG_ORDER)
_ordered = []
for _name in _CATALOG_ORDER:
    _match = next((f for f in _all_pngs if f.name == _name), None)
    if _match:
        _ordered.append(_match)
_ordered.extend(f for f in _all_pngs if f.name not in _catalog_set)
FIGURE_FILES = _ordered

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
    "fig21_scotus_scenario_comparison.png": "SCOTUS scenario: B50 per-person burden comparison (Appendix E)",
    "fig22_scotus_quintile_decomposition.png": "Central combined scenario: quintile burden decomposition (Appendix E)",
    "fig23_price_stickiness_flows.png": "Price stickiness and the incidence of tariff revocation (Appendix E)",
    "fig24_scotus_welfare_sensitivity.png": "SCOTUS scenario: sensitivity range and welfare impact (Appendix E)",
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

def prepare_pandoc_markdown(source_md=None):
    """Prepare Markdown with YAML front-matter for Pandoc -> LaTeX -> PDF."""
    src = source_md or FINDINGS_MD
    text = src.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract title from the first H1 line in FINDINGS.md
    doc_title = "Working Paper"
    for line in lines:
        if line.startswith("# "):
            doc_title = line.lstrip("# ").strip()
            break

    # Detect date from the markdown (look for **Date:** line)
    doc_date = "March 2026"
    for line in lines:
        if line.strip().startswith("**Date:"):
            doc_date = line.replace("**Date:**", "").strip()
            break

    yaml_block = f"""---
title: |
  {doc_title}
author:
  - Andy Salazar
date: {doc_date}
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
    jel_codes = ""
    for line in lines:
        if line.startswith("**Keywords:**"):
            keywords = line.replace("**Keywords:**", "").strip()
        if line.startswith("**JEL Codes:**"):
            jel_codes = line.replace("**JEL Codes:**", "").strip()

    thanks_parts = ["Working Paper. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6285038."]
    if jel_codes:
        thanks_parts.append(f"JEL: {jel_codes}.")
    thanks_parts.append("Replication package: https://github.com/andsalazar/FederalBudgetAnalysis.")
    thanks_parts.append("Pre-registration: docs/hypothesis_preregistration.md")
    thanks_text = " ".join(thanks_parts)

    yaml_block += f"""
keywords: "{keywords}"
thanks: "{thanks_text}"
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
    body = re.sub(r"\n(## Appendix [A-G])", r"\n\\newpage\n\1", body)

    # Replace Appendix G (or Appendix B/F) figure table with inline figure references
    # (this also removes the \newpage that was inserted before the original heading)
    body = re.sub(r"\\newpage\n\n?## Appendix [BFG]: Figures.*?(?=\n##|\n\\newpage|\Z)", "", body, flags=re.DOTALL)

    figures_md = "\n\\newpage\n\n## Appendix G: Figures\n\n"
    for idx, f in enumerate(FIGURE_FILES, 1):
        desc = FIGURE_DESCRIPTIONS.get(f.name, f.stem.replace("_", " ").title())
        figures_md += f"![{desc}](figures/{f.name}){{width=90%}}\n\n"

    # Appendix G (Figures) is the last appendix — simply append
    body += figures_md

    # Replace Unicode symbols with LaTeX-safe equivalents for reliable XeLaTeX rendering.
    # NOTE: U+2212 (−) is replaced with ASCII hyphen-minus to avoid collision
    # with literal $ (dollar) signs in text like "−$36B".
    unicode_to_latex = {
        "\u2212": "-",          # − → ASCII hyphen-minus (safe near $ signs)
        "\u00d7": "$\\times$",  # × (multiplication sign)
        "\u2264": "$\\leq$",    # ≤ (less-than-or-equal)
        "\u2265": "$\\geq$",    # ≥ (greater-than-or-equal)
        "\u2248": "$\\approx$", # ≈ (approximately equal)
        "\u03c1": "$\\rho$",    # ρ
        "\u03c3": "$\\sigma$",  # σ
        "\u03b1": "$\\alpha$",  # α
        "\u03b2": "$\\beta$",   # β
        "\u0394": "$\\Delta$",  # Δ
        "\u00b1": "$\\pm$",     # ±
    }
    result = yaml_block + "\n" + body
    for char, latex in unicode_to_latex.items():
        result = result.replace(char, latex)
    return result


def generate_pandoc_pdf(source_md=None, output_pdf=None):
    print("=" * 60)
    print("Generating PDF via Pandoc + LaTeX...")
    print("=" * 60)

    target_pdf = output_pdf or PANDOC_PDF
    stem = target_pdf.stem
    prepared_md = PDF_DIR / f"{stem}_prepared.md"
    prepared_md.write_text(prepare_pandoc_markdown(source_md), encoding="utf-8")

    engine = next(
        (e for e in ("xelatex", "lualatex", "pdflatex") if shutil.which(e)),
        "pdflatex",
    )

    cmd = [
        "pandoc", str(prepared_md), "-o", str(target_pdf),
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
        sz = target_pdf.stat().st_size / (1024 * 1024)
        print(f"\n  PDF generated: {target_pdf} ({sz:.1f} MB)")
        return True
    else:
        print(f"\n  Pandoc failed: {result.stderr[:500]}")
        return False


def generate_pandoc_docx(source_md=None, output_docx=None):
    """Generate Word (.docx) via Pandoc — handles tables, math (OMML), and images."""
    print("=" * 60)
    print("Generating Word document via Pandoc...")
    print("=" * 60)

    target_docx = output_docx or (PDF_DIR / f"{PAPER_STEM}.docx")
    stem = target_docx.stem
    prepared_md = PDF_DIR / f"{stem}_prepared.md"
    prepared_md.write_text(prepare_pandoc_markdown(source_md), encoding="utf-8")

    cmd = [
        "pandoc", str(prepared_md), "-o", str(target_docx),
        "--standalone",
        "--toc", "--toc-depth=3",
        f"--resource-path={OUTPUT_DIR}",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd, capture_output=True, cwd=str(OUTPUT_DIR),
        encoding="utf-8", errors="replace",
    )

    if result.returncode == 0:
        sz = target_docx.stat().st_size / (1024 * 1024)
        print(f"\n  Word document generated: {target_docx} ({sz:.1f} MB)")
        return True
    else:
        print(f"\n  Pandoc (docx) failed: {result.stderr[:500]}")
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

    # Strip the Appendix B, F, or G figure table -- we replace with embedded images
    md_text = re.sub(
        r"## Appendix [BFG]: Figures.*?(?=\n##|\Z)",
        "## Appendix G: Figures\n\n<!-- FIGURES -->\n",
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

    # Detect date from the markdown
    doc_date = "March 2026"
    for line in md_text.split("\n"):
        if line.strip().startswith("**Date:"):
            doc_date = line.replace("**Date:**", "").strip()
            break

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
            Working Paper &mdash; {doc_date}
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


def generate_xhtml2pdf(source_md=None, output_pdf=None):
    """Generate PDF via xhtml2pdf (pure Python)."""
    print("=" * 60)
    print("Generating PDF via xhtml2pdf...")
    print("=" * 60)

    from xhtml2pdf import pisa

    src = source_md or FINDINGS_MD
    target_pdf = output_pdf or XHTML2PDF_OUT
    stem = target_pdf.stem
    md_text = src.read_text(encoding="utf-8")
    print(f"  Source: {src}")
    print("  Converting Markdown to HTML...")
    html = markdown_to_html(md_text)

    # Save HTML preview
    html_file = PDF_DIR / f"{stem}_preview.html"
    html_file.write_text(html, encoding="utf-8")
    print(f"  HTML preview: {html_file}")

    print("  Rendering PDF (this may take a minute with embedded figures)...")
    with open(target_pdf, "wb") as pdf_file:
        status = pisa.CreatePDF(html, dest=pdf_file)

    if status.err:
        print(f"\n  xhtml2pdf reported {status.err} error(s)")
        return False

    size_mb = target_pdf.stat().st_size / (1024 * 1024)
    print(f"\n  PDF generated: {target_pdf} ({size_mb:.1f} MB)")
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
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Source markdown file (default: output/FINDINGS.md)",
    )
    parser.add_argument(
        "--version-tag",
        type=str,
        default=None,
        help="Version tag for output filenames (e.g., 'v4' -> Salazar_FiscalBreaks_2026_v4_journal.pdf)",
    )
    parser.add_argument(
        "--docx",
        action="store_true",
        help="Also generate a Word (.docx) document via Pandoc (requires Pandoc)",
    )
    args = parser.parse_args()

    # Resolve source file
    if args.source:
        source_path = Path(args.source)
        if not source_path.is_absolute():
            source_path = BASE_DIR / source_path
    else:
        source_path = FINDINGS_MD

    # Resolve output filenames
    vtag = args.version_tag
    if vtag:
        pandoc_out = PDF_DIR / f"{PAPER_STEM}_{vtag}_journal.pdf"
        xhtml2pdf_out = PDF_DIR / f"{PAPER_STEM}_{vtag}_publication.pdf"
        docx_out = PDF_DIR / f"{PAPER_STEM}_{vtag}.docx"
    else:
        pandoc_out = PANDOC_PDF
        xhtml2pdf_out = XHTML2PDF_OUT
        docx_out = PDF_DIR / f"{PAPER_STEM}.docx"

    if not source_path.exists():
        print(f"Error: {source_path} not found")
        sys.exit(1)

    print(f"Source:  {source_path}")
    print(f"Figures: {len(FIGURE_FILES)} PNG files in {FIGURES_DIR}")
    print(f"Output:  {PDF_DIR}/")
    if vtag:
        print(f"Version: {vtag}")
    print()

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
        success = generate_pandoc_pdf(source_md=source_path, output_pdf=pandoc_out) or success
    elif engine == "pandoc" and not has_pandoc:
        print("Pandoc + LaTeX not found.")
        print("  Install from https://pandoc.org + https://miktex.org")

    if engine in ("xhtml2pdf", "both") and has_xhtml2pdf:
        success = generate_xhtml2pdf(source_md=source_path, output_pdf=xhtml2pdf_out) or success
    elif engine == "xhtml2pdf" and not has_xhtml2pdf:
        print("xhtml2pdf not found. Run: pip install xhtml2pdf markdown")

    # Word document generation (optional)
    if args.docx:
        if has_pandoc:
            docx_ok = generate_pandoc_docx(source_md=source_path, output_docx=docx_out)
            success = success or docx_ok
        else:
            print("Pandoc not found — cannot generate Word document.")
            print("  Install from https://pandoc.org")

    if not success:
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PDF READY FOR SUBMISSION")
    print("=" * 60)
    print()
    print("Upload to SSRN or submit to target journal.")
    print("For journal submission, Pandoc + MiKTeX gives LaTeX-quality output.")
    print("For working paper repos (SSRN, NBER), xhtml2pdf output is sufficient.")


if __name__ == "__main__":
    main()
