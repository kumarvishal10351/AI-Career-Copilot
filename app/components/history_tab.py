"""
History Tab Component
Displays a session-based log of all previous analyses.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from utils.session_manager import get_session, clear_history


def _score_color(score: int) -> str:
    if score >= 75:
        return "#68d391"
    if score >= 50:
        return "#f6ad55"
    return "#fc8181"


def render_history_tab() -> None:
    history: list[dict] = get_session("analysis_history", [])

    st.markdown(
        """
        <div style="color:#e2e8f0; font-weight:600; font-size:1.1rem; margin-bottom:0.3rem;">
            🕘 Session History
        </div>
        <div style="color:#718096; font-size:0.85rem; margin-bottom:1.5rem;">
            All analyses performed in this session are shown below. History clears when you close the tab.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not history:
        st.markdown(
            """
            <div class="info-card" style="text-align:center; padding:3rem 2rem; border-style:dashed;">
                <div style="font-size:3rem; margin-bottom:1rem;">🕘</div>
                <div style="color:#e2e8f0; font-size:1rem; font-weight:500;">No history yet</div>
                <div style="color:#718096; margin-top:0.4rem; font-size:0.85rem;">
                    Perform an analysis and it will appear here.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Summary stats ─────────────────────────────────────────────────────────
    analyses = [h for h in history if h.get("type") == "analysis"]
    if analyses:
        avg_ats   = round(sum(a["ats_score"] for a in analyses) / len(analyses))
        avg_match = round(sum(a["job_match"] for a in analyses) / len(analyses))
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="value">{len(analyses)}</div>
                    <div class="label">Analyses Run</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="value">{avg_ats}</div>
                    <div class="label">Avg ATS Score</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="value">{avg_match}%</div>
                    <div class="label">Avg Job Match</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

    # ── History entries ───────────────────────────────────────────────────────
    for entry in reversed(history):
        entry_type  = entry.get("type", "analysis")
        timestamp   = entry.get("timestamp", "")
        role        = entry.get("role", "Unknown Role")
        filename    = entry.get("filename", "resume.pdf")

        if entry_type == "analysis":
            ats_score = entry.get("ats_score", 0)
            job_match = entry.get("job_match", 0)
            ats_color = _score_color(ats_score)

            st.markdown(
                f"""
                <div class="history-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">📊 Resume Analysis</div>
                            <div style="color:#718096; font-size:0.8rem; margin-top:0.25rem;">
                                📁 {filename} &nbsp;·&nbsp; 🌐 {role}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:{ats_color}; font-weight:700; font-size:1.1rem;">{ats_score}</span>
                            <span style="color:#718096; font-size:0.75rem;">/100 ATS</span>
                            <div style="color:#a0aec0; font-size:0.8rem;">Match: {job_match}%</div>
                        </div>
                    </div>
                    <div style="color:#4a5568; font-size:0.75rem; margin-top:0.6rem;">🕐 {timestamp}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif entry_type == "improvement":
            st.markdown(
                f"""
                <div class="history-card">
                    <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">✍️ Resume Improvement</div>
                    <div style="color:#718096; font-size:0.8rem; margin-top:0.25rem;">
                        📁 {filename} &nbsp;·&nbsp; 🌐 {role}
                    </div>
                    <div style="color:#4a5568; font-size:0.75rem; margin-top:0.6rem;">🕐 {timestamp}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif entry_type == "interview":
            count = entry.get("question_count", 0)
            st.markdown(
                f"""
                <div class="history-card">
                    <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">🎯 Interview Questions</div>
                    <div style="color:#718096; font-size:0.8rem; margin-top:0.25rem;">
                        🌐 {role} &nbsp;·&nbsp; {count} questions generated
                    </div>
                    <div style="color:#4a5568; font-size:0.75rem; margin-top:0.6rem;">🕐 {timestamp}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    if st.button("🗑️ Clear History", key="clear_history_btn"):
        clear_history()
        st.rerun()
