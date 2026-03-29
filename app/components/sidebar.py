"""
Sidebar Component
Handles file upload, job description input, role selection, and analysis trigger.
"""

import streamlit as st

from services.pdf_service import load_pdf
from utils.session_manager import set_session, get_session
from utils.validators import validate_pdf_file, validate_job_description


ROLE_OPTIONS = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "DevOps / MLOps Engineer",
    "Product Manager",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "AI / LLM Engineer",
    "Cloud Architect",
    "Cybersecurity Analyst",
    "Business Analyst",
    "UX / UI Designer",
    "Other",
]


def render_sidebar() -> None:
    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding: 0.5rem 0 1.5rem 0;">
                <span style="font-size:2.2rem;">🧠</span>
                <div style="color:#667eea; font-weight:700; font-size:1.1rem; margin-top:0.3rem;">
                    AI Career Copilot
                </div>
                <div style="color:#718096; font-size:0.78rem; margin-top:0.2rem;">
                    Powered by Mistral AI
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # --- Target Role
        st.markdown("## 🌐 Target Role")
        
        # 1. Use a DIFFERENT key for the widget (e.g., "role_selector")
        role_input = st.selectbox(
            "Select your target job role",
            options=ROLE_OPTIONS,
            index=0,
            key="role_selector", 
            label_visibility="collapsed",
        )

        # 2. Manually update the 'selected_role' state that your app uses
        # This is now safe because 'selected_role' is no longer a widget key
        st.session_state["selected_role"] = role_input

# DELETE OR COMMENT OUT THE LINE BELOW:
# set_session("selected_role", selected_role)
        

        st.divider()

        # ── Resume Upload ─────────────────────────────────────────────────────
        st.markdown("## 📄 Resume (PDF)")
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf"],
            key="uploaded_resume",
            label_visibility="collapsed",
            help="Only PDF files are supported.",
        )

        if uploaded_file:
            file_ok, file_error = validate_pdf_file(uploaded_file)
            if not file_ok:
                st.error(f"❌ {file_error}")
                set_session("resume_text", None)
                set_session("resume_filename", None)
            else:
                # Only re-parse if the file changed
                current_name = get_session("resume_filename")
                if current_name != uploaded_file.name:
                    with st.spinner("Parsing resume…"):
                        text, parse_err = load_pdf(uploaded_file)
                    if parse_err:
                        st.error(f"❌ Could not parse PDF: {parse_err}")
                        set_session("resume_text", None)
                    else:
                        set_session("resume_text", text)
                        set_session("resume_filename", uploaded_file.name)
                        st.success(f"✅ **{uploaded_file.name}** loaded")
                else:
                    st.success(f"✅ **{uploaded_file.name}** ready")
        else:
            set_session("resume_text", None)
            set_session("resume_filename", None)

        st.divider()

        # ── Job Description ───────────────────────────────────────────────────
        st.markdown("## 🎯 Job Description")

    job_desc = st.text_area(
    "Paste the job description",
    height=200,
    placeholder="Paste the full job description here…",
    key="job_description",
    label_visibility="collapsed",
)

    jd_ok, jd_error = validate_job_description(job_desc)

    if job_desc and not jd_ok:
        st.warning(f"⚠️ {jd_error}")

        # ── Analyse Button ────────────────────────────────────────────────────
        ready = bool(get_session("resume_text") and get_session("job_description"))

        if st.button("🚀 Analyse Now", disabled=not ready, key="analyse_btn"):
            set_session("trigger_analysis", True)
            set_session("trigger_improvement", False)
            set_session("trigger_interview", False)

        if not ready:
            st.caption("Upload a resume & add a job description to begin.")

        st.divider()

        # ── Quick Actions ─────────────────────────────────────────────────────
        st.markdown("## ⚡ Quick Actions")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✍️ Improve", disabled=not ready, key="improve_btn"):
                set_session("trigger_improvement", True)
                set_session("trigger_analysis", False)
                set_session("trigger_interview", False)
        with c2:
            if st.button("🎯 Interview", disabled=not ready, key="interview_btn"):
                set_session("trigger_interview", True)
                set_session("trigger_analysis", False)
                set_session("trigger_improvement", False)

        st.divider()

        # ── Clear Session ─────────────────────────────────────────────────────
        if st.button("🧹 Clear All", key="clear_btn"):
            keys_to_clear = [
                "resume_text", "resume_filename", "job_description",
                "analysis_result", "improvement_result", "interview_result",
                "trigger_analysis", "trigger_improvement", "trigger_interview",
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        # ── Footer ────────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; color:#4a5568; font-size:0.72rem; margin-top:2rem;">
                Built with ❤️ using Mistral AI & Streamlit
            </div>
            """,
            unsafe_allow_html=True,
        )
