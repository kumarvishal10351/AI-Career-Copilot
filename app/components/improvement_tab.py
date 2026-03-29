"""
Resume Improvement Tab Component
Rewrites the resume to better match the job description and provides
PDF and TXT download options.
"""

from __future__ import annotations

import streamlit as st

from services.llm_service import LLMService
from services.export_service import export_as_pdf, export_as_txt
from utils.session_manager import get_session, set_session


def render_improvement_tab() -> None:
    resume_text = get_session("resume_text")
    job_desc    = get_session("job_description")
    role        = get_session("selected_role", "Software Engineer")
    trigger     = get_session("trigger_improvement", False)

    # ── Guard ─────────────────────────────────────────────────────────────────
    if not resume_text or not job_desc:
        st.markdown(
            """
            <div class="info-card" style="text-align:center; padding:3rem 2rem; border-style:dashed;">
                <div style="font-size:3rem; margin-bottom:1rem;">✍️</div>
                <div style="color:#e2e8f0; font-size:1.1rem; font-weight:600;">Resume Improvement</div>
                <div style="color:#718096; margin-top:0.5rem; font-size:0.9rem;">
                    Upload your resume and paste a job description in the sidebar first.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Trigger from sidebar or local button ───────────────────────────────────
    cached = get_session("improvement_result")

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        local_btn = st.button("✍️ Generate Improved Resume", key="local_improve_btn")

    if trigger or local_btn or cached is None:
        set_session("trigger_improvement", False)
        with st.spinner("🤖 Rewriting your resume… this may take 20-40 seconds."):
            service = LLMService()
            improved, error = service.improve_resume(resume_text, job_desc, role)

        if error:
            st.error(f"❌ Improvement failed: {error}")
            return

        set_session("improvement_result", improved)
        cached = improved

    improved_text: str = cached

    # ── Display ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="color:#e2e8f0; font-weight:600; font-size:1.1rem; margin:1rem 0 0.5rem 0;">
            ✍️ Improved Resume
        </div>
        <div style="color:#718096; font-size:0.85rem; margin-bottom:1rem;">
            ATS-optimised · Professionally written · Keyword-enhanced
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Editable text area so user can tweak
    edited = st.text_area(
        "Edit your improved resume below before downloading:",
        value=improved_text,
        height=420,
        key="editable_improved_resume",
        label_visibility="collapsed",
    )

    st.divider()

    # ── Download Buttons ──────────────────────────────────────────────────────
    st.markdown(
        "<div style='color:#e2e8f0; font-weight:600; margin-bottom:0.8rem;'>📥 Export Resume</div>",
        unsafe_allow_html=True,
    )

    dl1, dl2, dl3 = st.columns(3)

    # TXT
    with dl1:
        txt_bytes = export_as_txt(edited)
        st.download_button(
            label="📄 Download as TXT",
            data=txt_bytes,
            file_name="improved_resume.txt",
            mime="text/plain",
            key="dl_txt",
        )

    # PDF
    with dl2:
        pdf_bytes, pdf_err = export_as_pdf(edited)
        if pdf_err:
            st.warning(f"PDF export unavailable: {pdf_err}")
        else:
            st.download_button(
                label="📑 Download as PDF",
                data=pdf_bytes,
                file_name="improved_resume.pdf",
                mime="application/pdf",
                key="dl_pdf",
            )

    # Copy to clipboard hint
    with dl3:
        st.markdown(
            """
            <div class="info-card" style="text-align:center; padding:0.65rem 1rem;">
                <span style="color:#a0aec0; font-size:0.82rem;">
                    📋 Or select all text in the box above and copy manually.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── What changed section ──────────────────────────────────────────────────
    with st.expander("📌 What was improved?"):
        st.markdown(
            """
            <div class="info-card">
                <div class="card-title">✅ Improvements Applied</div>
                <ul style="color:#a0aec0; line-height:2; padding-left:1.2rem;">
                    <li>Action verbs added to bullet points (e.g., "Led", "Built", "Designed")</li>
                    <li>Keywords from the job description embedded naturally</li>
                    <li>Quantified achievements where possible</li>
                    <li>Cleaned up formatting for ATS parsers</li>
                    <li>Removed redundant language and filler phrases</li>
                    <li>Skills section realigned to match job requirements</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Regenerate ────────────────────────────────────────────────────────────
    if st.button("🔄 Regenerate", key="regen_improve_btn"):
        set_session("improvement_result", None)
        set_session("trigger_improvement", True)
        st.rerun()
