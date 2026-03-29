"""
Interview Preparation Tab Component
Generates Technical, HR/Behavioural, and Scenario-based interview questions
with answer hints and a difficulty indicator.
"""

from __future__ import annotations

import streamlit as st

from services.llm_service import LLMService
from utils.session_manager import get_session, set_session


# ── Helpers ────────────────────────────────────────────────────────────────────

_DIFFICULTY_COLOR = {"easy": "#68d391", "medium": "#f6ad55", "hard": "#fc8181"}


def _render_question_card(idx: int, q: dict) -> None:
    question   = q.get("question", q.get("q", ""))
    hint       = q.get("hint", "")
    difficulty = q.get("difficulty", "medium").lower()
    color      = _DIFFICULTY_COLOR.get(difficulty, "#a0aec0")

    st.markdown(
        f"""
        <div class="q-card">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                <span style="color:#667eea; font-weight:600; font-size:0.85rem;">Q{idx}</span>
                <span style="color:{color}; font-size:0.75rem; font-weight:600; text-transform:uppercase;">
                    {difficulty}
                </span>
            </div>
            <div>{question}</div>
            {"<div class='q-hint'>💡 Hint: " + hint + "</div>" if hint else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_section(title: str, icon: str, questions: list[dict]) -> None:
    if not questions:
        return
    st.markdown(
        f"""
        <div style="color:#e2e8f0; font-weight:700; font-size:1.05rem;
                    margin:1.5rem 0 0.8rem 0; display:flex; align-items:center; gap:0.5rem;">
            <span>{icon}</span><span>{title}</span>
            <span style="color:#718096; font-size:0.82rem; font-weight:400;">({len(questions)} questions)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for i, q in enumerate(questions, start=1):
        _render_question_card(i, q)


# ── Main Tab Renderer ──────────────────────────────────────────────────────────

def render_interview_tab() -> None:
    resume_text = get_session("resume_text")
    job_desc    = get_session("job_description")
    role        = get_session("selected_role", "Software Engineer")
    trigger     = get_session("trigger_interview", False)

    # ── Guard ─────────────────────────────────────────────────────────────────
    if not resume_text or not job_desc:
        st.markdown(
            """
            <div class="info-card" style="text-align:center; padding:3rem 2rem; border-style:dashed;">
                <div style="font-size:3rem; margin-bottom:1rem;">🎯</div>
                <div style="color:#e2e8f0; font-size:1.1rem; font-weight:600;">Interview Preparation</div>
                <div style="color:#718096; margin-top:0.5rem; font-size:0.9rem;">
                    Upload your resume and paste a job description in the sidebar first.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col, diff_col, _ = st.columns([1.5, 1.5, 3])
    with ctrl_col:
        local_btn = st.button("🎯 Generate Questions", key="local_interview_btn")
    with diff_col:
        difficulty_filter = st.selectbox(
            "Difficulty",
            ["All", "Easy", "Medium", "Hard"],
            index=0,
            key="difficulty_filter",
            label_visibility="visible",
        )

    # ── Generate ──────────────────────────────────────────────────────────────
    cached = get_session("interview_result")

    if trigger or local_btn or cached is None:
        set_session("trigger_interview", False)
        with st.spinner("🤖 Generating interview questions… this may take 20-30 seconds."):
            service = LLMService()
            result, error = service.generate_interview_questions(resume_text, job_desc, role)

        if error:
            st.error(f"❌ Question generation failed: {error}")
            return

        set_session("interview_result", result)
        cached = result

    data: dict = cached

    # ── Filter by difficulty ───────────────────────────────────────────────────
    def _filter(qs: list[dict]) -> list[dict]:
        if difficulty_filter == "All":
            return qs
        return [q for q in qs if q.get("difficulty", "").lower() == difficulty_filter.lower()]

    technical  = _filter(data.get("technical", []))
    behavioral = _filter(data.get("behavioral", []))
    scenario   = _filter(data.get("scenario", []))

    total = len(technical) + len(behavioral) + len(scenario)

    # ── Summary banner ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="info-card" style="display:flex; gap:2rem; align-items:center; margin-bottom:1rem;">
            <div>
                <span style="color:#667eea; font-size:1.4rem; font-weight:700;">{total}</span>
                <span style="color:#a0aec0; font-size:0.85rem; margin-left:0.3rem;">Questions Generated</span>
            </div>
            <div style="color:#718096; font-size:0.82rem;">
                🔧 {len(technical)} Technical &nbsp;·&nbsp;
                🤝 {len(behavioral)} Behavioural &nbsp;·&nbsp;
                🧩 {len(scenario)} Scenario
            </div>
            <div style="color:#718096; font-size:0.82rem; margin-left:auto;">
                Role: <strong style="color:#667eea">{role}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sections ──────────────────────────────────────────────────────────────
    _render_section("Technical Questions",     "🔧", technical)
    _render_section("HR & Behavioural",        "🤝", behavioral)
    _render_section("Scenario-based",          "🧩", scenario)

    if total == 0:
        st.info("No questions match the selected difficulty filter.")

    st.divider()

    # ── Export questions as text ───────────────────────────────────────────────
    def _questions_to_text() -> str:
        lines = [f"Interview Questions — {role}\n{'='*50}\n"]
        for section, qs in [("Technical", technical), ("Behavioural", behavioral), ("Scenario", scenario)]:
            if qs:
                lines.append(f"\n{section} Questions\n{'-'*30}")
                for i, q in enumerate(qs, 1):
                    lines.append(f"\nQ{i}. {q.get('question', q.get('q', ''))}")
                    if q.get("hint"):
                        lines.append(f"   Hint: {q['hint']}")
        return "\n".join(lines)

    st.download_button(
        "📥 Download All Questions",
        data=_questions_to_text(),
        file_name="interview_questions.txt",
        mime="text/plain",
        key="dl_questions",
    )

    # ── Regenerate ────────────────────────────────────────────────────────────
    if st.button("🔄 Regenerate Questions", key="regen_interview_btn"):
        set_session("interview_result", None)
        set_session("trigger_interview", True)
        st.rerun()
