"""
PDF Service
Handles PDF loading, text extraction, and caching.
Uses PyPDF for parsing and Streamlit's cache to avoid re-processing the same file.
"""

from __future__ import annotations

import io
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


def load_pdf(uploaded_file) -> tuple[str, str | None]:
    """
    Extract plain text from a Streamlit UploadedFile (PDF).

    Returns:
        (text, None)          — on success
        ("",  error_message)  — on failure
    """
    try:
        # Read bytes once so the buffer position doesn't matter
        pdf_bytes = uploaded_file.read()
        return _parse_pdf_bytes(pdf_bytes, uploaded_file.name)
    except Exception as exc:
        logger.error("PDF load error: %s", exc)
        return "", f"Unexpected error reading file: {exc}"
    finally:
        # Reset the file pointer so callers can re-read if needed
        try:
            uploaded_file.seek(0)
        except Exception:
            pass


def _parse_pdf_bytes(pdf_bytes: bytes, filename: str = "") -> tuple[str, str | None]:
    """
    Core PDF parsing logic. Tries PyPDF first, then falls back to pypdf (alias).
    Wrapped separately so it can be unit-tested without a Streamlit context.
    """
    try:
        from pypdf import PdfReader  # preferred (pypdf ≥ 3)
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # legacy fallback
        except ImportError:
            return "", "PyPDF library not installed. Run: pip install pypdf"

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))

        if reader.is_encrypted:
            return "", "This PDF is password-protected. Please upload an unencrypted file."

        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_text = "\n".join(pages_text).strip()

        if not full_text:
            return "", (
                "No readable text found in this PDF. "
                "It may be image-based (scanned). Please use a text-based PDF."
            )

        logger.info("Parsed %d pages from '%s' (%d chars)", len(pages_text), filename, len(full_text))
        return full_text, None

    except Exception as exc:
        logger.error("PdfReader error: %s", exc)
        return "", f"Failed to parse PDF: {exc}"


def get_pdf_page_count(uploaded_file) -> int:
    """Return the number of pages in a PDF (best effort, returns 0 on error)."""
    try:
        from pypdf import PdfReader
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return len(reader.pages)
    except Exception:
        return 0
