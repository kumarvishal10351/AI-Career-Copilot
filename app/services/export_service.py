"""
Export Service
Converts resume text to downloadable TXT and PDF formats.
Uses fpdf2 for PDF generation with clean, ATS-friendly formatting.
"""

from __future__ import annotations

import logging
import textwrap

logger = logging.getLogger(__name__)


# ── TXT Export ─────────────────────────────────────────────────────────────────

def export_as_txt(text: str) -> bytes:
    """Return the resume text as UTF-8 encoded bytes."""
    return text.encode("utf-8")


# ── PDF Export ─────────────────────────────────────────────────────────────────

def export_as_pdf(text: str) -> tuple[bytes, str | None]:
    """
    Render resume text as a clean, ATS-friendly PDF using fpdf2.

    Returns:
        (pdf_bytes, None)          — on success
        (b"",       error_message) — on failure
    """
    try:
        from fpdf import FPDF
    except ImportError:
        return b"", "fpdf2 not installed. Run: pip install fpdf2"

    try:
        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()

        # ── Fonts ──────────────────────────────────────────────────────────────
        # fpdf2 ships DejaVu which supports Unicode
        pdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
        pdf.add_font("DejaVu", "B", "DejaVuSansCondensed-Bold.ttf", uni=True)

        pdf.set_margins(left=18, top=18, right=18)

        # ── Render lines ───────────────────────────────────────────────────────
        lines = text.split("\n")
        max_chars_per_line = 95

        for raw_line in lines:
            raw_line = raw_line.rstrip()

            # Blank line → small vertical gap
            if not raw_line:
                pdf.ln(3)
                continue

            # All-caps or short lines (<= 60 chars) → treat as section heading
            is_heading = (
                raw_line.isupper()
                or (len(raw_line) <= 60 and raw_line.endswith(":"))
                or raw_line.startswith("##")
            )

            if is_heading:
                heading = raw_line.lstrip("#").strip()
                pdf.ln(4)
                pdf.set_font("DejaVu", "B", 11)
                pdf.set_text_color(40, 40, 80)
                pdf.cell(0, 7, heading, ln=True)
                # Underline via a thin rule
                x, y = pdf.get_x(), pdf.get_y()
                pdf.set_draw_color(100, 126, 234)
                pdf.set_line_width(0.4)
                pdf.line(18, y, 192, y)
                pdf.ln(2)
            else:
                pdf.set_font("DejaVu", "", 9.5)
                pdf.set_text_color(50, 50, 50)

                # Wrap long lines
                wrapped = textwrap.wrap(raw_line, width=max_chars_per_line)
                for wline in wrapped:
                    pdf.cell(0, 5.5, wline, ln=True)

        return bytes(pdf.output()), None

    except Exception as exc:
        logger.warning("fpdf2 PDF export with embedded fonts failed (%s). Trying fallback.", exc)
        return _pdf_fallback(text)


def _pdf_fallback(text: str) -> tuple[bytes, str | None]:
    """
    Fallback PDF renderer using only built-in fpdf2 Helvetica font.
    Doesn't support Unicode but works without font files.
    """
    try:
        from fpdf import FPDF

        # Sanitise to Latin-1 (Helvetica's range)
        safe_text = text.encode("latin-1", errors="replace").decode("latin-1")

        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()
        pdf.set_margins(left=18, top=18, right=18)

        lines = safe_text.split("\n")
        for raw_line in lines:
            raw_line = raw_line.rstrip()

            if not raw_line:
                pdf.ln(3)
                continue

            is_heading = raw_line.isupper() or raw_line.endswith(":")
            if is_heading:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(40, 40, 80)
                pdf.cell(0, 7, raw_line, ln=True)
                x, y = pdf.get_x(), pdf.get_y()
                pdf.line(18, y, 192, y)
                pdf.ln(2)
            else:
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(50, 50, 50)
                wrapped = textwrap.wrap(raw_line, width=95)
                for wline in wrapped:
                    pdf.cell(0, 5.5, wline, ln=True)

        return bytes(pdf.output()), None

    except Exception as exc:
        logger.error("PDF fallback also failed: %s", exc)
        return b"", f"PDF export failed: {exc}"
