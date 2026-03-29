"""
Analysis Tab Component
Renders the full Resume Analysis UI: ATS score, job match, skill gap,
section-wise breakdown, strengths/weaknesses, and smart suggestions.
"""

from __future__ import annotations

import streamlit as st

from services.llm_service import LLMService
from utils.session_manager import get_session, set_session, add_to_history


# ── Helpers ────────────────────────────────────────────────────────────────────

def _score_color(score: int) -> str:
    if score >= 75:
        return "#68d391"  # green
    if score >= 50:
        return "#f6ad55"  # orange
    return "#fc8181"       # red


def _render_metric_cards(data: dict) -> None:
    ats = data.get("ats_score", 0)
    match = data.get("job_match_percentage", 0)
    strengths_count = len(data.get("strengths", []))
    missing_count = len(data.get("missing_skills", []))

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, str(ats),            "ATS Score",        "/100"),
        (c2, f"{match}%",         "Job Match",        ""),
        (c3, str(strengths_count), "Strengths Found",  ""),
        (c4, str(missing_count),   "Skills to Add",    ""),
    ]
    for col, value, label, suffix in cards:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="value">{value}<span style="font-size:1rem;color:#a0aec0;">{suffix}</span></div>
                    <div class="label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_ats_gauge(score: int) -> None:
    color = _score_color(score)
    label = "Excellent" if score >= 75 else ("Good" if score >= 50 else "Needs Work")
    st.markdown(
        f"""
        <div style="margin: 1.5rem 0 0.5rem 0;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                <span style="color:#a0aec0; font-size:0.85rem; font-weight:500;">ATS COMPATIBILITY</span>
                <span style="color:{color}; font-size:0.85rem; font-weight:700;">{label} · {score}/100</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100)


def _render_section_scores(section_scores: dict) -> None:
    st.markdown(
        "<div style='color:#e2e8f0; font-weight:600; margin:1.5rem 0 1rem 0;'>📋 Section-wise Breakdown</div>",
        unsafe_allow_html=True,
    )
    icons = {
        "experience": "💼",
        "skills": "🛠️",
        "education": "🎓",
        "formatting": "📐",
        "keywords": "🔑",
    }
    rows_html = ""
    for key, score in section_scores.items():
        label = key.replace("_", " ").title()
        icon = icons.get(key.lower(), "•")
        color = _score_color(score)
        rows_html += f"""
        <div class="score-row">
            <span class="score-label">{icon} {label}</span>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{score}%; background: linear-gradient(90deg, {color}88, {color});"></div>
            </div>
            <span class="score-num" style="color:{color};">{score}</span>
        </div>
        """
    st.markdown(rows_html, unsafe_allow_html=True)


def _render_skill_gap(existing: list[str], missing: list[str]) -> None:
    st.markdown(
        "<div style='color:#e2e8f0; font-weight:600; margin:1.5rem 0 0.8rem 0;'>🔍 Skill Gap Analyzer</div>",
        unsafe_allow_html=True,
    )
    col_have, col_miss = st.columns(2)
    with col_have:
        st.markdown(
            "<div style='color:#68d391; font-size:0.85rem; font-weight:600; margin-bottom:0.5rem;'>✅ Skills You Have</div>",
            unsafe_allow_html=True,
        )
        tags = "".join(
            f'<span class="skill-tag present">{s}</span>' for s in existing
        )
        st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)

    with col_miss:
        st.markdown(
            "<div style='color:#fc8181; font-size:0.85rem; font-weight:600; margin-bottom:0.5rem;'>❌ Missing Skills</div>",
            unsafe_allow_html=True,
        )
        tags = "".join(
            f'<span class="skill-tag missing">{s}</span>' for s in missing
        )
        st.markdown(f"<div>{tags if missing else '<span style=\"color:#718096\">None detected!</span>'}</div>", unsafe_allow_html=True)


def _render_list_cards(title: str, items: list[str], icon: str = "•") -> None:
    if not items:
        return
    cards_html = "".join(
        f'<div class="info-card"><div class="card-title">{icon} {item}</div></div>'
        for item in items
    )
    st.markdown(
        f"<div style='color:#e2e8f0; font-weight:600; margin:1.5rem 0 0.8rem 0;'>{title}</div>{cards_html}",
        unsafe_allow_html=True,
    )


def _render_suggestions(suggestions: list[dict]) -> None:
    if not suggestions:
        return
    st.markdown(
        "<div style='color:#e2e8f0; font-weight:600; margin:1.5rem 0 0.8rem 0;'>🚀 Smart Suggestions</div>",
        unsafe_allow_html=True,
    )
    for item in suggestions:
        priority = item.get("priority", "low").lower()
        text = item.get("text", "")
        badge_html = f'<span class="badge {priority}">{priority}</span>'
        st.markdown(
            f'<div class="info-card">{badge_html}{text}</div>',
            unsafe_allow_html=True,
        )


# ── Main Tab Renderer ──────────────────────────────────────────────────────────

def render_analysis_tab() -> None:
    resume_text = get_session("resume_text")
    job_desc    = get_session("job_description")
    role        = get_session("selected_role", "Software Engineer")
    trigger     = get_session("trigger_analysis", False)

    # ── Prompt to fill inputs if not ready ────────────────────────────────────
    if not resume_text or not job_desc:
        st.markdown(
            """
            <div class="info-card" style="text-align:center; padding:3rem 2rem; border-style:dashed;">
                <div style="font-size:3rem; margin-bottom:1rem;">📊</div>
                <div style="color:#e2e8f0; font-size:1.1rem; font-weight:600;">Ready to analyse your resume?</div>
                <div style="color:#718096; margin-top:0.5rem; font-size:0.9rem;">
                    Upload your resume PDF and paste the job description in the sidebar, then click <strong>Analyse Now</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Run analysis ──────────────────────────────────────────────────────────
    cached_result = get_session("analysis_result")

    if trigger or cached_result is None:
        set_session("trigger_analysis", False)
        with st.spinner("🤖 Analysing your resume with AI… this may take 15-30 seconds."):
            service = LLMService()
            result, error = service.analyze_resume(resume_text, job_desc, role)

        if error:
            st.error(f"❌ Analysis failed: {error}")
            st.info("Check your MISTRAL_API_KEY and internet connection, then try again.")
            return

        set_session("analysis_result", result)
        add_to_history({
            "type": "analysis",
            "role": role,
            "filename": get_session("resume_filename", "resume.pdf"),
            "ats_score": result.get("ats_score", 0),
            "job_match": result.get("job_match_percentage", 0),
        })
        cached_result = result

    data = cached_result

    # ── Render results ────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='color:#718096; font-size:0.85rem; margin-bottom:1rem;'>Analysis for: <strong style='color:#667eea'>{role}</strong></div>",
        unsafe_allow_html=True,
    )

    _render_metric_cards(data)

    st.divider()

    _render_ats_gauge(data.get("ats_score", 0))

    st.divider()

    _render_section_scores(data.get("section_scores", {}))

    st.divider()

    _render_skill_gap(
        data.get("existing_skills", []),
        data.get("missing_skills", []),
    )

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        _render_list_cards("✅ Strengths", data.get("strengths", []), "💪")
    with col_r:
        _render_list_cards("⚠️ Weaknesses", data.get("weaknesses", []), "⚠️")

    st.divider()

    _render_suggestions(data.get("suggestions", []))

    # ── Re-analyse button ─────────────────────────────────────────────────────
    st.divider()
    if st.button("🔄 Re-analyse", key="reanalyse_btn"):
        set_session("analysis_result", None)
        set_session("trigger_analysis", True)
        st.rerun()
