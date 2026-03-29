"""
Validators
Input validation helpers used across the app.
All validators return (is_valid: bool, error_message: str).
"""

from __future__ import annotations

MIN_JOB_DESC_WORDS = 20
MAX_FILE_SIZE_MB   = 10


def validate_api_key(api_key: str | None) -> bool:
    """Return True if the API key looks plausible (non-empty, non-placeholder)."""
    if not api_key:
        return False
    key = api_key.strip()
    if len(key) < 10:
        return False
    if key.lower() in ("your_mistral_api_key_here", "your_key_here", "xxx", "test"):
        return False
    return True


def validate_pdf_file(uploaded_file) -> tuple[bool, str]:
    """
    Validate an uploaded Streamlit file object.
    Returns (True, "") on success, (False, error_message) on failure.
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    # Check MIME / extension
    name = uploaded_file.name.lower()
    if not name.endswith(".pdf"):
        return False, "Only PDF files are supported."

    # Check file size
    try:
        size_bytes = uploaded_file.size
        if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, f"File too large (max {MAX_FILE_SIZE_MB} MB)."
        if size_bytes == 0:
            return False, "Uploaded file appears to be empty."
    except AttributeError:
        pass  # some test stubs don't have .size

    return True, ""


def validate_job_description(text: str) -> tuple[bool, str]:
    """
    Ensure the job description has enough content to be useful.
    Returns (True, "") on success, (False, error_message) on failure.
    """
    if not text or not text.strip():
        return False, "Job description is empty."

    word_count = len(text.split())
    if word_count < MIN_JOB_DESC_WORDS:
        return (
            False,
            f"Job description seems too short ({word_count} words). "
            f"Please paste the full description (at least {MIN_JOB_DESC_WORDS} words).",
        )

    return True, ""
