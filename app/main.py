"""
AI Career Copilot — Main Entry Point
Production-grade Streamlit application
"""

import sys
import os

# Ensure app/ is on the path so sibling imports work
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv

from components.sidebar import render_sidebar
from components.analysis_tab import render_analysis_tab
from components.improvement_tab import render_improvement_tab
from components.interview_tab import render_interview_tab
from components.history_tab import render_history_tab
from utils.session_manager import initialize_session_state
from utils.validators import validate_api_key

# ── Environment ────────────────────────────────────────────────────────────────
load_dotenv()
from utils.session_manager import initialize_session_state

def main():
    initialize_session_state()  # ✅ MUST be first

    render_sidebar()
    ...

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/ai-career-copilot",
        "Report a bug": "https://github.com/your-repo/ai-career-copilot/issues",
        "About": "# AI Career Copilot\nTransform your resume. Land your dream job.",
    },
)


# ── Custom CSS ─────────────────────────────────────────────────────────────────
def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Global ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
        }

        /* ── Header ── */
        .app-header {
            text-align: center;
            padding: 2.5rem 0 1.5rem 0;
        }
        .app-header h1 {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.4rem;
        }
        .app-header p {
            color: #a0aec0;
            font-size: 1.1rem;
            font-weight: 300;
            letter-spacing: 0.05em;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 1px solid rgba(102, 126, 234, 0.2);
        }
        [data-testid="stSidebar"] .stMarkdown h2 {
            color: #667eea;
            font-size: 1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 0.4rem;
            border: 1px solid rgba(102, 126, 234, 0.15);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #a0aec0;
            font-weight: 500;
            padding: 0.5rem 1.2rem;
            transition: all 0.2s;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
        }

        /* ── Cards ── */
        .metric-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: border-color 0.3s;
        }
        .metric-card:hover { border-color: rgba(102, 126, 234, 0.5); }
        .metric-card .value {
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .metric-card .label {
            color: #a0aec0;
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        /* ── Section Score Card ── */
        .score-row {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.9rem;
        }
        .score-label {
            color: #cbd5e0;
            font-size: 0.9rem;
            min-width: 110px;
            font-weight: 500;
        }
        .score-bar-bg {
            flex: 1;
            background: rgba(255,255,255,0.07);
            border-radius: 100px;
            height: 8px;
            overflow: hidden;
        }
        .score-bar-fill {
            height: 100%;
            border-radius: 100px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.6s ease;
        }
        .score-num {
            color: #e2e8f0;
            font-size: 0.85rem;
            font-weight: 600;
            min-width: 38px;
            text-align: right;
        }

        /* ── Skill Tags ── */
        .skill-tag {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            border-radius: 100px;
            font-size: 0.82rem;
            font-weight: 500;
            margin: 0.25rem;
        }
        .skill-tag.present {
            background: rgba(72, 187, 120, 0.15);
            border: 1px solid rgba(72, 187, 120, 0.4);
            color: #68d391;
        }
        .skill-tag.missing {
            background: rgba(245, 101, 101, 0.12);
            border: 1px solid rgba(245, 101, 101, 0.35);
            color: #fc8181;
        }

        /* ── Priority Badge ── */
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-right: 0.5rem;
        }
        .badge.high   { background: rgba(245,101,101,0.15); color: #fc8181; border: 1px solid rgba(245,101,101,0.3); }
        .badge.medium { background: rgba(237,137,54,0.15);  color: #f6ad55; border: 1px solid rgba(237,137,54,0.3); }
        .badge.low    { background: rgba(72,187,120,0.15);  color: #68d391; border: 1px solid rgba(72,187,120,0.3); }

        /* ── Info Card ── */
        .info-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(102,126,234,0.15);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 0.8rem;
            color: #cbd5e0;
            font-size: 0.93rem;
            line-height: 1.6;
        }
        .info-card .card-title {
            color: #e2e8f0;
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        /* ── Question Card ── */
        .q-card {
            background: rgba(102,126,234,0.06);
            border-left: 3px solid #667eea;
            border-radius: 0 10px 10px 0;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
            color: #e2e8f0;
            font-size: 0.95rem;
        }
        .q-hint {
            color: #a0aec0;
            font-size: 0.82rem;
            margin-top: 0.4rem;
            font-style: italic;
        }

        /* ── History Card ── */
        .history-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1rem 1.3rem;
            margin-bottom: 0.7rem;
            cursor: pointer;
            transition: border-color 0.2s;
        }
        .history-card:hover { border-color: rgba(102,126,234,0.4); }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.4rem;
            transition: opacity 0.2s, transform 0.1s;
            width: 100%;
        }
        .stButton > button:hover {
            opacity: 0.88;
            transform: translateY(-1px);
        }
        .stButton > button:active { transform: translateY(0); }

        /* ── Text areas & inputs ── */
        .stTextArea textarea, .stSelectbox select {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(102,126,234,0.2) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
        }

        /* ── Spinner ── */
        .stSpinner > div { border-top-color: #667eea !important; }

        /* ── Divider ── */
        hr { border-color: rgba(102,126,234,0.15) !important; }

        /* ── Alert boxes ── */
        .stAlert { border-radius: 10px !important; }

        /* ── Progress bar ── */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea, #764ba2) !important;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            background: rgba(255,255,255,0.03) !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
        }

        /* ── File uploader ── */
        [data-testid="stFileUploader"] {
            border: 2px dashed rgba(102,126,234,0.3) !important;
            border-radius: 12px !important;
            background: rgba(102,126,234,0.04) !important;
            padding: 1rem !important;
        }

        /* ── Success/warning boxes ── */
        .element-container .stSuccess {
            background: rgba(72,187,120,0.1);
            border: 1px solid rgba(72,187,120,0.3);
        }
        .element-container .stWarning {
            background: rgba(237,137,54,0.1);
            border: 1px solid rgba(237,137,54,0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── App ────────────────────────────────────────────────────────────────────────
def main() -> None:
    initialize_session_state()
    inject_custom_css()

    # ── API key guard ──────────────────────────────────────────────────────────
    api_key = os.getenv("MISTRAL_API_KEY", "")
    if not validate_api_key(api_key):
        st.markdown(
            """
            <div class="app-header">
                <h1>🧠 AI Career Copilot</h1>
                <p>Transform your resume. Land your dream job.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.error(
            "⚠️ **MISTRAL_API_KEY** is missing or invalid. "
            "Please add it to your `.env` file and restart the app."
        )
        st.code("MISTRAL_API_KEY=your_mistral_api_key_here", language="bash")
        st.info("Get your free API key → https://console.mistral.ai/")
        st.stop()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="app-header">
            <h1>🧠 AI Career Copilot</h1>
            <p>Transform your resume. Land your dream job.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    render_sidebar()

    # ── Main tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊  Resume Analysis", "✍️  Improve Resume", "🎯  Interview Prep", "🕘  History"]
    )

    with tab1:
        render_analysis_tab()
    with tab2:
        render_improvement_tab()
    with tab3:
        render_interview_tab()
    with tab4:
        render_history_tab()


if __name__ == "__main__":
    main()
