"""
AI Career Copilot — Main Entry Point
Production-ready, industry-level, no sidebar
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv

from components.analysis_tab import render_analysis_tab
from components.improvement_tab import render_improvement_tab
from components.interview_tab import render_interview_tab
from components.history_tab import render_history_tab
from utils.session_manager import initialize_session_state, set_session, get_session
from utils.validators import validate_api_key, validate_pdf_file, validate_job_description
from services.pdf_service import load_pdf

load_dotenv()

st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com/your-repo/ai-career-copilot",
        "Report a bug": "https://github.com/your-repo/ai-career-copilot/issues",
        "About": "# AI Career Copilot\nTransform your resume. Land your dream job.",
    },
)

ROLE_OPTIONS = [
    "Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "Data Analyst", "DevOps / MLOps Engineer", "Product Manager",
    "Backend Developer", "Frontend Developer", "Full Stack Developer",
    "AI / LLM Engineer", "Cloud Architect", "Cybersecurity Analyst",
    "Business Analyst", "UX / UI Designer", "Other",
]


def inject_custom_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }

    .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* ══════════════════════════════════════
       BACKGROUND
    ══════════════════════════════════════ */
    .stApp {
        background:
            radial-gradient(ellipse at 10% 20%, rgba(102,126,234,0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 80%, rgba(118,75,162,0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(240,147,251,0.06) 0%, transparent 70%),
            radial-gradient(ellipse at 80% 10%, rgba(0,212,255,0.08) 0%, transparent 40%),
            linear-gradient(135deg, #06060f 0%, #0d0d1a 30%, #131328 60%, #0f1628 100%);
        min-height: 100vh;
    }
    .stApp::before {
        content: '';
        position: fixed; inset: 0;
        background-image:
            linear-gradient(rgba(102,126,234,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(102,126,234,0.03) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none; z-index: 0;
        animation: gridDrift 25s linear infinite;
    }
    @keyframes gridDrift {
        0%   { transform: translate(0,0); }
        100% { transform: translate(60px,60px); }
    }

    /* ══════════════════════════════════════
       TOP NAVBAR
    ══════════════════════════════════════ */
    .top-navbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.85rem 2.5rem;
        background: rgba(8,8,20,0.95);
        backdrop-filter: blur(30px);
        border-bottom: 1px solid rgba(102,126,234,0.18);
        box-shadow: 0 2px 40px rgba(0,0,0,0.6), 0 1px 0 rgba(102,126,234,0.1);
        position: sticky; top: 0; z-index: 1000;
    }
    .navbar-brand { display: flex; align-items: center; gap: 0.9rem; }
    .brand-icon {
        font-size: 1.9rem;
        filter: drop-shadow(0 0 10px rgba(102,126,234,0.9))
                drop-shadow(0 0 22px rgba(240,147,251,0.5));
        animation: iconPulse 3s ease-in-out infinite;
    }
    @keyframes iconPulse {
        0%,100% { filter: drop-shadow(0 0 10px rgba(102,126,234,0.9)) drop-shadow(0 0 22px rgba(240,147,251,0.5)); }
        50%      { filter: drop-shadow(0 0 20px rgba(102,126,234,1))   drop-shadow(0 0 40px rgba(240,147,251,0.8)); }
    }
    .brand-name {
        font-family: 'Orbitron', sans-serif; font-size: 1rem; font-weight: 900;
        background: linear-gradient(135deg,#00d4ff,#667eea,#f093fb);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; animation: titleGlow 4s linear infinite; letter-spacing: 0.06em;
    }
    @keyframes titleGlow {
        0%   { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    .brand-sub {
        font-family: 'Rajdhani', sans-serif; font-size: 0.58rem;
        color: #3a4560; text-transform: uppercase; letter-spacing: 0.18em;
    }
    .navbar-status { display: flex; align-items: center; gap: 1.8rem; }
    .nav-status-item {
        display: flex; align-items: center; gap: 0.35rem;
        font-family: 'Rajdhani', sans-serif; font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase; color: #4a5568;
    }
    .nav-dot { width:6px; height:6px; border-radius:50%; animation:pulseDot 2.5s ease-in-out infinite; }
    .nav-dot.green  { background:#68d391; box-shadow:0 0 6px #68d391; }
    .nav-dot.blue   { background:#63b3ed; box-shadow:0 0 6px #63b3ed; }
    .nav-dot.purple { background:#b794f4; box-shadow:0 0 6px #b794f4; }
    @keyframes pulseDot {
        0%,100% { opacity:1; transform:scale(1); }
        50%      { opacity:0.4; transform:scale(0.65); }
    }

    /* ══════════════════════════════════════
       CONTROL PANEL
    ══════════════════════════════════════ */
    .control-panel-wrap {
        background: rgba(8,8,22,0.8);
        backdrop-filter: blur(24px);
        border-bottom: 1px solid rgba(102,126,234,0.12);
        padding: 1.4rem 2.5rem 1rem 2.5rem;
        box-shadow: 0 6px 30px rgba(0,0,0,0.4);
    }
    .cp-label {
        font-family: 'Rajdhani', sans-serif; color: #5a6eea;
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.18em; margin-bottom: 0.45rem;
        display: flex; align-items: center; gap: 0.3rem;
    }

    /* ── Save Description button — subtle, inside JD column ── */
    .save-desc-btn .stButton > button {
        background: rgba(102,126,234,0.08) !important;
        border: 1px solid rgba(102,126,234,0.25) !important;
        border-radius: 8px !important;
        color: #667eea !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        padding: 0.3rem 0.8rem !important;
        width: auto !important;
        min-width: unset !important;
        box-shadow: none !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease !important;
        float: right;
        margin-top: 0.3rem;
    }
    .save-desc-btn .stButton > button:hover {
        background: rgba(102,126,234,0.18) !important;
        border-color: rgba(102,126,234,0.5) !important;
        box-shadow: 0 0 12px rgba(102,126,234,0.25) !important;
        transform: none !important;
    }

    /* ── Saved JD display box ── */
    .saved-jd-box {
        background: rgba(102,126,234,0.06);
        border: 1px solid rgba(102,126,234,0.2);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-top: 0.4rem;
        color: #a0aec0;
        font-size: 0.82rem;
        line-height: 1.6;
        max-height: 80px;
        overflow: hidden;
        position: relative;
    }
    .saved-jd-box::after {
        content: '';
        position: absolute; bottom: 0; left: 0; right: 0;
        height: 30px;
        background: linear-gradient(transparent, rgba(8,8,22,0.9));
        border-radius: 0 0 12px 12px;
    }
    .saved-jd-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.65rem; font-weight: 700; color: #68d391;
        text-transform: uppercase; letter-spacing: 0.12em;
        margin-bottom: 0.3rem; display: flex; align-items: center; gap: 0.3rem;
    }

    /* ── Action buttons row ── */
    .glow-divider {
        height: 1px;
        background: linear-gradient(90deg,transparent,rgba(102,126,234,0.3),transparent);
        margin: 0.9rem 0; box-shadow: 0 0 6px rgba(102,126,234,0.15);
    }

    /* ── Ready badge ── */
    .ready-badge {
        display: inline-flex; align-items: center; gap: 0.5rem;
        padding: 0.5rem 1rem; border-radius: 10px;
        font-family: 'Rajdhani', sans-serif; font-size: 0.75rem;
        font-weight: 700; letter-spacing: 0.08em; white-space: nowrap;
    }
    .ready-badge.ready    { background:rgba(72,187,120,0.08);  border:1px solid rgba(72,187,120,0.3);  color:#68d391; }
    .ready-badge.notready { background:rgba(113,128,150,0.06); border:1px solid rgba(113,128,150,0.12); color:#4a5568; }
    .ready-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
    .green-dot { background:#68d391; box-shadow:0 0 7px #68d391; animation:pulseDot 2s ease-in-out infinite; }
    .grey-dot  { background:#4a5568; }

    /* ══════════════════════════════════════
       ACTION BUTTONS — Animated & Polished
    ══════════════════════════════════════ */

    /* Base — override all stButton */
    .stButton > button {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        width: 100% !important;
        animation: btnAppear 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both !important;
    }

    @keyframes btnAppear {
        0%   { opacity: 0; transform: translateY(10px) scale(0.95); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* Shimmer sweep on hover */
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important; left: -100% !important;
        width: 100% !important; height: 100% !important;
        background: linear-gradient(90deg,transparent,rgba(255,255,255,0.18),transparent) !important;
        transition: left 0.5s ease !important;
        z-index: 1 !important;
    }
    .stButton > button:hover::before { left: 100% !important; }

    /* Ripple ring on hover */
    .stButton > button::after {
        content: '' !important;
        position: absolute !important;
        inset: 0 !important;
        border-radius: 12px !important;
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
        box-shadow: 0 0 0 0 rgba(255,255,255,0.3) !important;
    }
    .stButton > button:hover::after {
        animation: rippleRing 0.6s ease-out !important;
    }
    @keyframes rippleRing {
        0%   { box-shadow: 0 0 0 0 rgba(255,255,255,0.3); opacity: 1; }
        100% { box-shadow: 0 0 0 12px rgba(255,255,255,0); opacity: 0; }
    }

    .stButton > button:disabled {
        opacity: 0.25 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
        filter: grayscale(0.6) !important;
    }

    /* Analyse — Blue/Purple with animated gradient border */
    .btn-analyse .stButton > button {
        background: linear-gradient(135deg, #4158d0 0%, #667eea 50%, #764ba2 100%) !important;
        background-size: 200% 200% !important;
        color: white !important;
        padding: 0.78rem 0.8rem !important;
        font-size: 0.84rem !important;
        box-shadow:
            0 4px 20px rgba(102,126,234,0.45),
            inset 0 1px 0 rgba(255,255,255,0.15),
            0 0 0 1px rgba(102,126,234,0.3) !important;
        animation: btnAppear 0.5s cubic-bezier(0.34,1.56,0.64,1) both, gradientShift 4s ease infinite !important;
    }
    .btn-analyse .stButton > button:hover:not(:disabled) {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow:
            0 10px 32px rgba(102,126,234,0.65),
            0 4px 12px rgba(102,126,234,0.3),
            inset 0 1px 0 rgba(255,255,255,0.2),
            0 0 20px rgba(102,126,234,0.4) !important;
    }
    .btn-analyse .stButton > button:active:not(:disabled) {
        transform: translateY(-1px) scale(0.99) !important;
    }

    /* Improve — Teal/Green with pulse glow */
    .btn-improve .stButton > button {
        background: linear-gradient(135deg, #0f9b8e 0%, #11998e 50%, #38ef7d 100%) !important;
        background-size: 200% 200% !important;
        color: white !important;
        padding: 0.78rem 0.8rem !important;
        font-size: 0.84rem !important;
        box-shadow:
            0 4px 20px rgba(17,153,142,0.4),
            inset 0 1px 0 rgba(255,255,255,0.15),
            0 0 0 1px rgba(56,239,125,0.2) !important;
        animation: btnAppear 0.5s 0.05s cubic-bezier(0.34,1.56,0.64,1) both, gradientShift 4s 1s ease infinite !important;
    }
    .btn-improve .stButton > button:hover:not(:disabled) {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow:
            0 10px 32px rgba(56,239,125,0.5),
            0 4px 12px rgba(17,153,142,0.3),
            inset 0 1px 0 rgba(255,255,255,0.2),
            0 0 20px rgba(56,239,125,0.35) !important;
    }
    .btn-improve .stButton > button:active:not(:disabled) {
        transform: translateY(-1px) scale(0.99) !important;
    }

    /* Interview — Pink/Red with glow pulse */
    .btn-interview .stButton > button {
        background: linear-gradient(135deg, #c94b4b 0%, #f5576c 50%, #f093fb 100%) !important;
        background-size: 200% 200% !important;
        color: white !important;
        padding: 0.78rem 0.8rem !important;
        font-size: 0.84rem !important;
        box-shadow:
            0 4px 20px rgba(245,87,108,0.4),
            inset 0 1px 0 rgba(255,255,255,0.15),
            0 0 0 1px rgba(240,147,251,0.2) !important;
        animation: btnAppear 0.5s 0.1s cubic-bezier(0.34,1.56,0.64,1) both, gradientShift 4s 2s ease infinite !important;
    }
    .btn-interview .stButton > button:hover:not(:disabled) {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow:
            0 10px 32px rgba(240,147,251,0.5),
            0 4px 12px rgba(245,87,108,0.35),
            inset 0 1px 0 rgba(255,255,255,0.2),
            0 0 20px rgba(245,87,108,0.4) !important;
    }
    .btn-interview .stButton > button:active:not(:disabled) {
        transform: translateY(-1px) scale(0.99) !important;
    }

    /* History — Amber/Orange */
    .btn-history .stButton > button {
        background: linear-gradient(135deg, #b8860b 0%, #f6ad55 50%, #f6d365 100%) !important;
        background-size: 200% 200% !important;
        color: #1a1a2e !important;
        padding: 0.78rem 0.8rem !important;
        font-size: 0.84rem !important;
        box-shadow:
            0 4px 20px rgba(246,173,85,0.35),
            inset 0 1px 0 rgba(255,255,255,0.25),
            0 0 0 1px rgba(246,211,101,0.2) !important;
        animation: btnAppear 0.5s 0.15s cubic-bezier(0.34,1.56,0.64,1) both, gradientShift 4s 3s ease infinite !important;
    }
    .btn-history .stButton > button:hover:not(:disabled) {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow:
            0 10px 32px rgba(246,173,85,0.6),
            0 4px 12px rgba(246,211,101,0.3),
            inset 0 1px 0 rgba(255,255,255,0.3),
            0 0 20px rgba(246,173,85,0.4) !important;
    }
    .btn-history .stButton > button:active:not(:disabled) {
        transform: translateY(-1px) scale(0.99) !important;
    }

    /* Clear — Ghost with red hover */
    .btn-clear .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #4a5568 !important;
        padding: 0.78rem 0.8rem !important;
        font-size: 0.82rem !important;
        box-shadow: none !important;
        animation: btnAppear 0.5s 0.2s cubic-bezier(0.34,1.56,0.64,1) both !important;
        backdrop-filter: blur(8px) !important;
    }
    .btn-clear .stButton > button:hover:not(:disabled) {
        background: rgba(245,101,101,0.12) !important;
        border-color: rgba(245,101,101,0.4) !important;
        color: #fc8181 !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow:
            0 6px 20px rgba(245,101,101,0.2),
            0 0 12px rgba(245,101,101,0.15) !important;
    }
    .btn-clear .stButton > button:active:not(:disabled) {
        transform: translateY(0) scale(0.99) !important;
    }

    /* Shared gradient animation */
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ══════════════════════════════════════
       TABS — Animated & Polished
    ══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
        background: rgba(255,255,255,0.02);
        border-radius: 14px;
        padding: 0.4rem;
        border: 1px solid rgba(102,126,234,0.15);
        box-shadow: 0 2px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03);
        backdrop-filter: blur(12px);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        color: #4a5568 !important;
        font-weight: 700 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.06em !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        bottom: 0; left: 50%; transform: translateX(-50%);
        width: 0; height: 2px;
        background: linear-gradient(90deg, #667eea, #f093fb);
        transition: width 0.3s ease;
        border-radius: 2px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #a78bfa !important;
        background: rgba(102,126,234,0.1) !important;
        transform: translateY(-1px) !important;
    }
    .stTabs [data-baseweb="tab"]:hover::before { width: 80%; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4158d0 0%, #667eea 50%, #764ba2 100%) !important;
        background-size: 200% 200% !important;
        animation: gradientShift 4s ease infinite !important;
        color: white !important;
        box-shadow:
            0 4px 16px rgba(102,126,234,0.45),
            inset 0 1px 0 rgba(255,255,255,0.2) !important;
        transform: translateY(-1px) !important;
    }
    .stTabs [aria-selected="true"]::before { width: 0 !important; }
    .stTabs [data-baseweb="tab-panel"] {
        animation: tabFadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        padding-top: 1.2rem !important;
    }
    @keyframes tabFadeIn {
        from { opacity: 0; transform: translateY(8px) scale(0.99); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* ══════════════════════════════════════
       CONTENT AREA
    ══════════════════════════════════════ */
    .content-wrap { padding: 1.5rem 2.5rem 2rem 2.5rem; }

    /* ── Welcome Screen ── */
    .welcome-screen { text-align: center; padding: 3.5rem 2rem; }
    .w-icon {
        font-size: 5rem; display: block; margin-bottom: 1.2rem;
        filter: drop-shadow(0 0 28px rgba(102,126,234,0.7))
                drop-shadow(0 0 56px rgba(240,147,251,0.4));
        animation: iconPulse 3s ease-in-out infinite;
    }
    .welcome-screen h2 {
        font-family: 'Orbitron', sans-serif; font-size: 2rem; font-weight: 900;
        background: linear-gradient(135deg,#00d4ff,#667eea,#f093fb);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; animation: titleGlow 4s linear infinite;
        margin-bottom: 0.8rem;
    }
    .welcome-screen p {
        color: #4a5568; font-size: 1rem; font-family: 'Rajdhani', sans-serif;
        letter-spacing: 0.04em; max-width: 580px; margin: 0 auto 2rem auto;
        line-height: 1.7;
    }
    .step-cards { display:flex; gap:1.2rem; justify-content:center; flex-wrap:wrap; margin-top:1.5rem; }
    .step-card {
        background: rgba(255,255,255,0.02); border: 1px solid rgba(102,126,234,0.15);
        border-radius: 16px; padding: 1.4rem 1.6rem; text-align: left;
        min-width: 170px; max-width: 210px;
        transition: all 0.3s ease; animation: cardSlideUp 0.6s ease-out both;
    }
    .step-card:hover { border-color:rgba(102,126,234,0.4); transform:translateY(-4px); box-shadow:0 10px 30px rgba(102,126,234,0.12); }
    .step-num { font-family:'Orbitron',sans-serif; font-size:0.62rem; font-weight:700; color:#667eea; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.5rem; }
    .step-icon { font-size:1.8rem; margin-bottom:0.4rem; display:block; }
    .step-title { font-family:'Rajdhani',sans-serif; color:#e2e8f0; font-size:0.88rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; }
    .step-desc { color:#4a5568; font-size:0.78rem; margin-top:0.3rem; line-height:1.5; }

    /* ── Tab placeholder ── */
    .tab-placeholder {
        text-align: center; padding: 2.5rem 2rem;
        animation: cardSlideUp 0.4s ease-out both;
    }
    .tab-placeholder .ph-icon { font-size:2.8rem; margin-bottom:0.8rem; display:block; opacity:0.5; }
    .tab-placeholder .ph-title {
        font-family:'Rajdhani',sans-serif; font-size:1rem; font-weight:700;
        color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.4rem;
    }
    .tab-placeholder .ph-hint { color:#2d3748; font-size:0.85rem; line-height:1.6; }

    /* ── Result section header ── */
    .result-section-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 1.2rem; padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(102,126,234,0.15);
    }
    .result-section-title {
        font-family: 'Orbitron', sans-serif; font-size: 0.9rem; font-weight: 700;
        background: linear-gradient(135deg,#667eea,#f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; letter-spacing: 0.06em;
    }
    .result-section-badge {
        font-family: 'Rajdhani', sans-serif; font-size: 0.68rem; font-weight: 700;
        color: #68d391; background: rgba(72,187,120,0.1);
        border: 1px solid rgba(72,187,120,0.25); border-radius: 6px;
        padding: 0.2rem 0.6rem; text-transform: uppercase; letter-spacing: 0.1em;
    }

    /* ══════════════════════════════════════
       ALL CARDS & COMPONENTS
    ══════════════════════════════════════ */
    @keyframes cardSlideUp { from{opacity:0;transform:translateY(14px);} to{opacity:1;transform:translateY(0);} }
    @keyframes shimmer { 0%{transform:translateX(-100%) translateY(-100%) rotate(45deg);} 100%{transform:translateX(100%) translateY(100%) rotate(45deg);} }

    .metric-card { background:rgba(255,255,255,0.03); border:1px solid rgba(102,126,234,0.18); border-radius:16px; padding:1.6rem 1.2rem; text-align:center; backdrop-filter:blur(16px); transition:all 0.3s ease; position:relative; overflow:hidden; animation:cardSlideUp 0.5s ease-out both; }
    .metric-card::before { content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background:linear-gradient(45deg,transparent 30%,rgba(255,255,255,0.025) 50%,transparent 70%); animation:shimmer 5s linear infinite; }
    .metric-card:hover { border-color:rgba(102,126,234,0.4); transform:translateY(-3px); box-shadow:0 10px 30px rgba(102,126,234,0.15); }
    .metric-card .value { font-family:'Orbitron',sans-serif; font-size:2.4rem; font-weight:700; background:linear-gradient(135deg,#00d4ff,#667eea,#f093fb); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; line-height:1.1; }
    .metric-card .label { font-family:'Rajdhani',sans-serif; color:#4a5568; font-size:0.75rem; font-weight:700; margin-top:0.4rem; text-transform:uppercase; letter-spacing:0.14em; }

    .score-row{display:flex;align-items:center;gap:1rem;margin-bottom:0.9rem;}
    .score-label{color:#a0aec0;font-family:'Rajdhani',sans-serif;font-size:0.88rem;font-weight:600;min-width:110px;}
    .score-bar-bg{flex:1;background:rgba(255,255,255,0.05);border-radius:100px;height:8px;overflow:hidden;}
    .score-bar-fill{height:100%;border-radius:100px;background:linear-gradient(90deg,#00d4ff,#667eea,#764ba2,#f093fb);background-size:200% 100%;box-shadow:0 0 8px rgba(102,126,234,0.4);animation:barFill 1s ease-out both,barShimmer 3s linear infinite;}
    @keyframes barFill{from{width:0% !important;}}
    @keyframes barShimmer{0%{background-position:200% center;}100%{background-position:0% center;}}
    .score-num{font-family:'Orbitron',sans-serif;color:#a0aec0;font-size:0.78rem;font-weight:700;min-width:38px;text-align:right;}

    .skill-tag{display:inline-block;padding:0.3rem 0.8rem;border-radius:100px;font-size:0.78rem;font-weight:600;font-family:'Rajdhani',sans-serif;letter-spacing:0.05em;margin:0.2rem;transition:all 0.2s ease;animation:tagPop 0.4s cubic-bezier(0.34,1.56,0.64,1) both;}
    @keyframes tagPop{from{opacity:0;transform:scale(0.7);}to{opacity:1;transform:scale(1);}}
    .skill-tag:hover{transform:scale(1.07) translateY(-1px);}
    .skill-tag.present{background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.35);color:#68d391;}
    .skill-tag.missing{background:rgba(245,101,101,0.08);border:1px solid rgba(245,101,101,0.3);color:#fc8181;}

    .badge{display:inline-block;padding:0.18rem 0.55rem;border-radius:5px;font-family:'Rajdhani',sans-serif;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-right:0.4rem;}
    .badge.high{background:rgba(245,101,101,0.12);color:#fc8181;border:1px solid rgba(245,101,101,0.28);}
    .badge.medium{background:rgba(237,137,54,0.12);color:#f6ad55;border:1px solid rgba(237,137,54,0.28);}
    .badge.low{background:rgba(72,187,120,0.12);color:#68d391;border:1px solid rgba(72,187,120,0.28);}

    .info-card{background:rgba(255,255,255,0.02);border:1px solid rgba(102,126,234,0.14);border-radius:12px;padding:1.1rem 1.4rem;margin-bottom:0.8rem;color:#a0aec0;font-size:0.9rem;line-height:1.65;transition:all 0.25s ease;animation:cardSlideUp 0.5s ease-out both;}
    .info-card:hover{border-color:rgba(102,126,234,0.35);background:rgba(102,126,234,0.04);transform:translateX(3px);}
    .info-card .card-title{font-family:'Rajdhani',sans-serif;color:#e2e8f0;font-weight:700;font-size:1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.4rem;}

    .q-card{background:rgba(102,126,234,0.04);border-left:2px solid rgba(102,126,234,0.4);border-radius:0 10px 10px 0;padding:1rem 1.2rem;margin-bottom:0.8rem;color:#a0aec0;font-size:0.9rem;line-height:1.6;animation:cardSlideUp 0.5s ease-out both;transition:all 0.25s ease;}
    .q-card:hover{background:rgba(102,126,234,0.08);transform:translateX(3px);}
    .q-hint{color:#4a5568;font-size:0.78rem;margin-top:0.4rem;font-style:italic;}

    .history-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.7rem;cursor:pointer;transition:all 0.25s ease;animation:cardSlideUp 0.5s ease-out both;}
    .history-card:hover{border-color:rgba(102,126,234,0.35);transform:translateY(-2px);box-shadow:0 6px 20px rgba(102,126,234,0.1);}

    /* ── Inputs ── */
    .stTextArea textarea{background:rgba(255,255,255,0.04) !important;border:1px solid rgba(102,126,234,0.2) !important;border-radius:10px !important;color:#e2e8f0 !important;font-family:'Inter',sans-serif !important;font-size:0.88rem !important;transition:all 0.25s ease !important;line-height:1.6 !important;}
    .stTextArea textarea:focus{border-color:rgba(102,126,234,0.5) !important;box-shadow:0 0 0 3px rgba(102,126,234,0.1) !important;background:rgba(255,255,255,0.06) !important;}
    .stSelectbox > div > div{background:rgba(255,255,255,0.04) !important;border:1px solid rgba(102,126,234,0.2) !important;border-radius:10px !important;color:#e2e8f0 !important;}
    [data-testid="stFileUploader"]{border:1px dashed rgba(102,126,234,0.28) !important;border-radius:12px !important;background:rgba(102,126,234,0.03) !important;transition:all 0.25s ease !important;}
    [data-testid="stFileUploader"]:hover{border-color:rgba(102,126,234,0.5) !important;background:rgba(102,126,234,0.06) !important;}

    /* ── Misc ── */
    .stProgress > div > div > div > div{background:linear-gradient(90deg,#00d4ff,#667eea,#764ba2,#f093fb) !important;background-size:200% 100% !important;animation:barShimmer 3s linear infinite !important;border-radius:100px !important;}
    .stSpinner > div{border-top-color:#667eea !important;}
    .stAlert{border-radius:10px !important;}
    .element-container .stSuccess{background:rgba(72,187,120,0.08) !important;border:1px solid rgba(72,187,120,0.25) !important;}
    .element-container .stWarning{background:rgba(237,137,54,0.08) !important;border:1px solid rgba(237,137,54,0.25) !important;}
    .element-container .stError{background:rgba(245,101,101,0.08) !important;border:1px solid rgba(245,101,101,0.25) !important;}
    .element-container .stInfo{background:rgba(99,179,237,0.08) !important;border:1px solid rgba(99,179,237,0.25) !important;}
    .streamlit-expanderHeader{background:rgba(255,255,255,0.02) !important;border-radius:8px !important;color:#a0aec0 !important;border:1px solid rgba(102,126,234,0.12) !important;font-family:'Rajdhani',sans-serif !important;font-weight:600 !important;}
    hr{border:none !important;height:1px !important;background:linear-gradient(90deg,transparent,rgba(102,126,234,0.3),transparent) !important;}
    ::-webkit-scrollbar{width:5px;}
    ::-webkit-scrollbar-track{background:rgba(255,255,255,0.01);}
    ::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#4158d0,#764ba2);border-radius:100px;}
    </style>
    """, unsafe_allow_html=True)


def render_control_panel() -> bool:
    """
    Renders the full inline control panel.
    Returns ready (bool).
    """
    st.markdown('<div class="control-panel-wrap">', unsafe_allow_html=True)

    # ── Row 1: Role | Upload | Job Description ─────────────────────────────
    col_role, col_upload, col_jd = st.columns([1.3, 1.8, 3.4], gap="large")

    with col_role:
        st.markdown('<div class="cp-label">🌐 Target Role</div>', unsafe_allow_html=True)
        role_input = st.selectbox(
            "role",
            options=ROLE_OPTIONS,
            index=ROLE_OPTIONS.index(
                st.session_state.get("selected_role", "Software Engineer")
            ) if st.session_state.get("selected_role") in ROLE_OPTIONS else 0,
            key="role_selector",
            label_visibility="collapsed",
        )
        st.session_state["selected_role"] = role_input

    with col_upload:
        st.markdown('<div class="cp-label">📄 Resume (PDF)</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=["pdf"],
            key="uploaded_resume",
            label_visibility="collapsed",
            help="PDF only. Max 10MB.",
        )
        if uploaded_file:
            file_ok, file_error = validate_pdf_file(uploaded_file)
            if not file_ok:
                st.error(f"❌ {file_error}")
                set_session("resume_text", None)
                set_session("resume_filename", None)
            else:
                current_name = get_session("resume_filename")
                if current_name != uploaded_file.name:
                    with st.spinner("⚙️ Parsing…"):
                        text, parse_err = load_pdf(uploaded_file)
                    if parse_err:
                        st.error(f"❌ {parse_err}")
                        set_session("resume_text", None)
                    else:
                        set_session("resume_text", text)
                        set_session("resume_filename", uploaded_file.name)
                        st.success(f"✅ **{uploaded_file.name}**")
                else:
                    st.success(f"✅ **{uploaded_file.name}** ready")
        else:
            set_session("resume_text", None)
            set_session("resume_filename", None)

    with col_jd:
        st.markdown('<div class="cp-label">🎯 Job Description</div>', unsafe_allow_html=True)

        saved_jd = get_session("saved_job_description")
        editing_jd = st.session_state.get("editing_jd", True)

        if saved_jd and not editing_jd:
            preview = saved_jd[:200] + ("…" if len(saved_jd) > 200 else "")
            st.markdown(f"""
                <div class="saved-jd-label">✓ &nbsp;Job Description Saved</div>
                <div class="saved-jd-box">{preview}</div>
            """, unsafe_allow_html=True)
            if st.button("✏️ Edit Description", key="edit_jd_btn"):
                st.session_state["editing_jd"] = True
                st.rerun()
        else:
            job_desc = st.text_area(
                "Job Description",
                value=saved_jd or "",
                height=110,
                placeholder="Paste the full job description here…",
                key="job_description_input",
                label_visibility="collapsed",
            )
            if job_desc:
                jd_ok, jd_error = validate_job_description(job_desc)
                if not jd_ok:
                    st.warning(f"⚠️ {jd_error}")

            jd_save_col, jd_btn_col = st.columns([3, 1])
            with jd_btn_col:
                st.markdown('<div class="save-desc-btn">', unsafe_allow_html=True)
                if st.button("💾 Save", key="save_jd_btn"):
                    if job_desc and job_desc.strip():
                        set_session("saved_job_description", job_desc.strip())
                        st.session_state["job_description"] = job_desc.strip()
                        st.session_state["editing_jd"] = False
                        st.rerun()
                    else:
                        st.error("Please enter a job description first.")
                st.markdown('</div>', unsafe_allow_html=True)

        if saved_jd and not editing_jd:
            st.session_state["job_description"] = saved_jd

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── Row 2: Status + Action Buttons ────────────────────────────────────────
    ready = bool(get_session("resume_text") and get_session("saved_job_description"))

    r_col, a_col, b_col, c_col, d_col, e_col = st.columns(
        [2.0, 1.4, 1.4, 1.4, 1.2, 1.0], gap="small"
    )

    with r_col:
        if ready:
            st.markdown("""
                <div class="ready-badge ready">
                    <div class="ready-dot green-dot"></div>
                    ✓ Ready — Choose an action
                </div>
            """, unsafe_allow_html=True)
        else:
            missing = []
            if not get_session("resume_text"):
                missing.append("Resume")
            if not get_session("saved_job_description"):
                missing.append("Job Description")
            st.markdown(f"""
                <div class="ready-badge notready">
                    <div class="ready-dot grey-dot"></div>
                    Needs: {" + ".join(missing) if missing else "—"}
                </div>
            """, unsafe_allow_html=True)

    with a_col:
        st.markdown('<div class="btn-analyse">', unsafe_allow_html=True)
        if st.button(
            "🔍 Analyse Resume",
            disabled=not ready,
            key="analyse_btn",
            help="Run ATS analysis on your resume vs job description",
        ):
            set_session("trigger_analysis", True)
            set_session("active_section", "analysis")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with b_col:
        st.markdown('<div class="btn-improve">', unsafe_allow_html=True)
        if st.button(
            "✍️ Improve Resume",
            disabled=not ready,
            key="improve_btn",
            help="Get AI-powered resume improvement suggestions",
        ):
            set_session("trigger_improvement", True)
            set_session("active_section", "improvement")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_col:
        st.markdown('<div class="btn-interview">', unsafe_allow_html=True)
        if st.button(
            "🎯 Interview Prep",
            disabled=not ready,
            key="interview_btn",
            help="Generate tailored interview questions",
        ):
            set_session("trigger_interview", True)
            set_session("active_section", "interview")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with d_col:
        st.markdown('<div class="btn-history">', unsafe_allow_html=True)
        if st.button(
            "🕘 History",
            key="history_btn",
            help="View past analyses",
        ):
            set_session("active_section", "history")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with e_col:
        st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
        if st.button("🧹 Clear", key="clear_btn", help="Reset everything"):
            for k in [
                "resume_text", "resume_filename",
                "job_description", "job_description_input",
                "saved_job_description", "editing_jd",
                "analysis_result", "improvement_result", "interview_result",
                "trigger_analysis", "trigger_improvement", "trigger_interview",
                "active_section",
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return ready


def _tab_placeholder(icon: str, title: str, hint: str) -> None:
    st.markdown(f"""
        <div class="tab-placeholder">
            <span class="ph-icon">{icon}</span>
            <div class="ph-title">{title}</div>
            <div class="ph-hint">{hint}</div>
        </div>
    """, unsafe_allow_html=True)


def render_results_area() -> None:
    """
    Results area with 4 tabs.
    KEY FIX: Results are CACHED in session_state.
    Clicking a new button does NOT clear previous results.
    Each tab shows its cached result independently.
    """
    active = get_session("active_section", "analysis")

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    # NOTE: section-nav pills REMOVED (was redundant with tabs below)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍  Resume Analysis",
        "✍️  Improve Resume",
        "🎯  Interview Prep",
        "🕘  History",
    ])

    has_analysis    = bool(get_session("analysis_result"))
    has_improvement = bool(get_session("improvement_result"))
    has_interview   = bool(get_session("interview_result"))

    # ── Tab 1: Analysis ────────────────────────────────────────────────────────
    with tab1:
        if get_session("trigger_analysis") and active == "analysis":
            st.markdown("""
                <div class="result-section-header">
                    <div class="result-section-title">RESUME ANALYSIS</div>
                    <div class="result-section-badge">● LIVE RESULT</div>
                </div>
            """, unsafe_allow_html=True)
            render_analysis_tab()
            set_session("trigger_analysis", False)
        elif has_analysis:
            st.markdown("""
                <div class="result-section-header">
                    <div class="result-section-title">RESUME ANALYSIS</div>
                    <div class="result-section-badge">● CACHED RESULT</div>
                </div>
            """, unsafe_allow_html=True)
            render_analysis_tab()
        else:
            _tab_placeholder(
                "🔍", "Resume Analysis",
                "Click <b>Analyse Resume</b> in the control panel above to run a full ATS compatibility check on your resume."
            )

    # ── Tab 2: Improvement ────────────────────────────────────────────────────
    with tab2:
        if get_session("trigger_improvement") and active == "improvement":
            st.markdown("""
                <div class="result-section-header">
                    <div class="result-section-title">RESUME IMPROVEMENT</div>
                    <div class="result-section-badge">● LIVE RESULT</div>
                </div>
            """, unsafe_allow_html=True)
            render_improvement_tab()
            set_session("trigger_improvement", False)
        elif has_improvement:
            st.markdown("""
                <div class="result-section-header">
                    <div class="result-section-title">RESUME IMPROVEMENT</div>
                    <div class="result-section-badge">● CACHED RESULT</div>
                </div>
            """, unsafe_allow_html=True)
            render_improvement_tab()
        else:
            _tab_placeholder(
                "✍️", "Improve Resume",
                "Click <b>Improve Resume</b> in the control panel above to get AI-powered rewrite suggestions."
            )

    # ── Tab 3: Interview ──────────────────────────────────────────────────────
    with tab3:
        if get_session("trigger_interview") and active == "interview":
            st.markdown("""
                <div class="result-section-header">
                    <div class="result-section-title">INTERVIEW PREP</div>
                    <div class="result-section-badge">● LIVE RESULT</div>
                </div>
            """, unsafe_allow_html=True)
            render_interview_tab()
            set_session("trigger_interview", False)
        elif has_interview:
            st.markdown("""
                <div class="result-section-header">
                    <div class="result-section-title">INTERVIEW PREP</div>
                    <div class="result-section-badge">● CACHED RESULT</div>
                </div>
            """, unsafe_allow_html=True)
            render_interview_tab()
        else:
            _tab_placeholder(
                "🎯", "Interview Prep",
                "Click <b>Interview Prep</b> in the control panel above to generate tailored interview questions."
            )

    # ── Tab 4: History ────────────────────────────────────────────────────────
    with tab4:
        render_history_tab()

    st.markdown('</div>', unsafe_allow_html=True)


def render_welcome_screen() -> None:
    st.markdown("""
        <div class="welcome-screen">
            <span class="w-icon">🧠</span>
            <h2>AI Career Copilot</h2>
            <p>
                Your AI-powered career toolkit. Upload your resume, paste a job description,
                then choose an action to get instant professional insights.
            </p>
            <div class="step-cards">
                <div class="step-card">
                    <span class="step-num">Step 01</span>
                    <span class="step-icon">📄</span>
                    <div class="step-title">Upload Resume</div>
                    <div class="step-desc">Upload your PDF resume in the panel above</div>
                </div>
                <div class="step-card">
                    <span class="step-num">Step 02</span>
                    <span class="step-icon">🎯</span>
                    <div class="step-title">Add Job Description</div>
                    <div class="step-desc">Paste the target job description & save it</div>
                </div>
                <div class="step-card">
                    <span class="step-num">Step 03</span>
                    <span class="step-icon">🚀</span>
                    <div class="step-title">Choose Action</div>
                    <div class="step-desc">Analyse, Improve, or get Interview Prep</div>
                </div>
                <div class="step-card">
                    <span class="step-num">Step 04</span>
                    <span class="step-icon">✨</span>
                    <div class="step-title">View Results</div>
                    <div class="step-desc">Results cached — switch tabs anytime</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def main() -> None:
    initialize_session_state()
    inject_custom_css()

    if "editing_jd" not in st.session_state:
        st.session_state["editing_jd"] = True

    api_key = os.getenv("MISTRAL_API_KEY", "")
    if not validate_api_key(api_key):
        st.markdown("""
            <div style="max-width:520px;margin:5rem auto;text-align:center;padding:2rem;">
                <div style="font-size:5rem;filter:drop-shadow(0 0 25px rgba(102,126,234,0.8));margin-bottom:1rem;">🧠</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:1.6rem;font-weight:900;
                    background:linear-gradient(135deg,#00d4ff,#667eea,#f093fb);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;margin-bottom:2rem;">AI Career Copilot</div>
            </div>
        """, unsafe_allow_html=True)
        st.error("⚠️ **MISTRAL_API_KEY** is missing. Add it to `.env` and restart.")
        st.code("MISTRAL_API_KEY=your_mistral_api_key_here", language="bash")
        st.info("🔑 Get your free API key → https://console.mistral.ai/")
        st.stop()

    st.markdown("""
        <div class="top-navbar">
            <div class="navbar-brand">
                <span class="brand-icon">🧠</span>
                <div>
                    <div class="brand-name">AI CAREER COPILOT</div>
                    <div class="brand-sub">Powered by Mistral AI</div>
                </div>
            </div>
            <div class="navbar-status">
                <div class="nav-status-item"><div class="nav-dot green"></div>System Online</div>
                <div class="nav-status-item"><div class="nav-dot blue"></div>AI Powered</div>
                <div class="nav-status-item"><div class="nav-dot purple"></div>Mistral Engine</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    render_control_panel()

    if not get_session("active_section"):
        render_welcome_screen()
    else:
        render_results_area()


if __name__ == "__main__":
    main()
