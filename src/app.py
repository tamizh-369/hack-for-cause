"""Streamlit App — Public Health Claim Watchdog.
Glassmorphism Aurora UI — deep-space dark background with frosted glass cards.
"""

from datetime import datetime
import json
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.check import detect_drift, evaluate_claim
from src.explain import LANGUAGES, explain_drift, explain_verdict
from src.load import load_release
from src.parse import parse_claim_sentence
from src.tour import get_tour_component_html
import streamlit.components.v1 as components

# ── page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health Claim Watchdog",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── MASTER CSS ────────────────────────────────────────────────────────
# Palette research: Aurora Dark Glassmorphism
#   Background  : #060614  ─ near-black deep indigo
#   Orb 1       : #7c3aed  ─ violet
#   Orb 2       : #2563eb  ─ electric blue
#   Orb 3       : #059669  ─ emerald
#   Glass bg    : rgba(255,255,255,0.06) + blur(20px)
#   Glass border: rgba(255,255,255,0.14)
#   Text primary: #f1f5f9
#   Accent cyan : #22d3ee
#   Accent rose : #fb7185
#   Accent amber: #fbbf24
#   Accent lime : #a3e635
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font ────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Deep-space animated background ─────────────── */
.stApp {
    background: #060614;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Floating orbs */
.stApp::before {
    content: '';
    position: fixed;
    width: 700px; height: 700px;
    top: -200px; left: -200px;
    background: radial-gradient(circle, rgba(124,58,237,0.35) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orbFloat 8s ease-in-out infinite alternate;
}
.stApp::after {
    content: '';
    position: fixed;
    width: 600px; height: 600px;
    bottom: -150px; right: -150px;
    background: radial-gradient(circle, rgba(37,99,235,0.30) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orbFloat 10s ease-in-out infinite alternate-reverse;
}
@keyframes orbFloat {
    0%   { transform: translate(0,0)    scale(1);    }
    50%  { transform: translate(30px,20px) scale(1.05); }
    100% { transform: translate(-20px,40px) scale(0.97); }
}

/* Extra emerald orb injected via JS-free div */
.orb-extra {
    position: fixed;
    width: 450px; height: 450px;
    top: 40%; left: 40%;
    background: radial-gradient(circle, rgba(5,150,105,0.18) 0%, transparent 65%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: orbFloat 12s ease-in-out 2s infinite alternate;
}

/* ── Glassmorphism base card ─────────────────────── */
.glass {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45),
                inset 0 1px 0 rgba(255,255,255,0.10);
    position: relative; z-index: 1;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.glass-sm {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.40);
    position: relative; z-index: 1;
    padding: 18px 22px;
    margin-bottom: 14px;
}

/* ── Animations ──────────────────────────────────── */
@keyframes fadeDown {
    from { opacity:0; transform: translateY(-24px); }
    to   { opacity:1; transform: translateY(0);     }
}
@keyframes fadeUp {
    from { opacity:0; transform: translateY(24px); }
    to   { opacity:1; transform: translateY(0);    }
}
@keyframes fadeLeft {
    from { opacity:0; transform: translateX(-32px); }
    to   { opacity:1; transform: translateX(0);     }
}
@keyframes fadeRight {
    from { opacity:0; transform: translateX(32px); }
    to   { opacity:1; transform: translateX(0);    }
}
@keyframes zoomIn {
    0%   { opacity:0; transform: scale(0.6) rotate(-8deg); }
    70%  { transform: scale(1.06) rotate(2deg); }
    100% { opacity:1; transform: scale(1) rotate(0); }
}
@keyframes shimmer {
    0%,100% { box-shadow: 0 0 0 0 rgba(251,113,133,0); }
    50%      { box-shadow: 0 0 28px 6px rgba(251,113,133,0.25); }
}
@keyframes borderPulse {
    0%,100% { border-color: rgba(251,191,36,0.4); }
    50%      { border-color: rgba(251,191,36,0.9); }
}
@keyframes floatUp {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
}
@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ── Hero ────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg,
        rgba(124,58,237,0.40) 0%,
        rgba(37,99,235,0.35) 50%,
        rgba(5,150,105,0.25) 100%);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 24px;
    padding: 30px 36px;
    margin-bottom: 24px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5),
                inset 0 1px 0 rgba(255,255,255,0.15);
    animation: fadeDown 0.65s cubic-bezier(.22,1,.36,1) both;
    display: flex; align-items: center; gap: 20px;
    position: relative; z-index: 1;
}
.hero-icon {
    font-size: 3.4rem;
    animation: floatUp 3s ease-in-out infinite;
    filter: drop-shadow(0 0 16px rgba(124,58,237,0.7));
}
.hero-title {
    font-size: 2rem; font-weight: 900;
    background: linear-gradient(90deg, #f1f5f9, #22d3ee, #a3e635);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; line-height: 1.15;
}
.hero-sub { color: rgba(241,245,249,0.65); font-size: 0.9rem; margin-top: 5px; font-weight: 400; }

/* ── Notice bar ──────────────────────────────────── */
.notice {
    background: rgba(251,191,36,0.10);
    border-left: 3px solid #fbbf24;
    border-radius: 12px;
    padding: 10px 18px;
    color: #fde68a;
    font-size: 0.85rem;
    margin-bottom: 20px;
    animation: fadeUp 0.5s ease both;
    position: relative; z-index: 1;
}

/* ── Claim card ──────────────────────────────────── */
.claim-card {
    animation: fadeLeft 0.55s cubic-bezier(.22,1,.36,1) both;
}
.pill {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: #fff !important;
    border-radius: 100px;
    padding: 3px 14px;
    font-size: 0.73rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.claim-text {
    font-size: 1.05rem; font-weight: 700;
    color: #f1f5f9; line-height: 1.55;
    margin: 8px 0 14px;
}
.claim-meta { font-size: 0.8rem; color: rgba(241,245,249,0.50); }
.claim-meta strong { color: rgba(241,245,249,0.80); }

/* ── Verdict ─────────────────────────────────────── */
.verdict-box {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100%;
}
.verdict-emoji {
    font-size: 4rem;
    animation: zoomIn 0.6s cubic-bezier(.36,.07,.19,.97) both;
    filter: drop-shadow(0 0 20px currentColor);
}
.verdict-label {
    font-size: 0.95rem; font-weight: 800;
    letter-spacing: 1.2px; text-transform: uppercase;
    margin-top: 10px;
    animation: fadeUp 0.4s 0.3s ease both; opacity:0;
    animation-fill-mode: both;
}
.verdict-supported   { color: #4ade80; }
.verdict-unsupported { color: #fb7185; }
.verdict-review      { color: #fbbf24; }

/* ── Metric card ─────────────────────────────────── */
.metric-card {
    text-align: center;
    animation: fadeUp 0.5s ease both;
    height: 100%;
}
.metric-val {
    font-size: 1.9rem; font-weight: 900;
    color: #f1f5f9;
    filter: drop-shadow(0 0 10px rgba(34,211,238,0.4));
}
.metric-val.up   { color: #4ade80; }
.metric-val.down { color: #fb7185; }
.metric-lbl {
    font-size: 0.72rem; font-weight: 600;
    color: rgba(241,245,249,0.45);
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-top: 5px;
}

/* ── Drift alert ─────────────────────────────────── */
.drift-alert {
    background: linear-gradient(135deg,
        rgba(251,113,133,0.12) 0%,
        rgba(251,191,36,0.08) 100%);
    border: 1.5px solid rgba(251,191,36,0.50);
    border-radius: 20px;
    padding: 22px 26px;
    margin: 18px 0;
    animation: fadeRight 0.55s ease both, borderPulse 2s 1s ease-in-out 4, shimmer 2s 0.5s ease-in-out 3;
    position: relative; z-index: 1;
}
.drift-row { display: flex; align-items: center; gap: 12px; }
.drift-icon { font-size: 2.2rem; animation: floatUp 1.5s ease-in-out infinite; }
.drift-title { font-size: 1.15rem; font-weight: 800; color: #fbbf24; }
.drift-body  { font-size: 0.9rem; color: rgba(241,245,249,0.75); margin-top: 10px; line-height: 1.65; }

/* ── Evidence table ──────────────────────────────── */
.ev-card { animation: fadeLeft 0.5s 0.1s ease both; }
.section-title {
    font-size: 1rem; font-weight: 800;
    color: #f1f5f9;
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 14px;
    letter-spacing: -0.2px;
}
.section-title span.accent { color: #22d3ee; }

/* ── Explain card ────────────────────────────────── */
.ex-card {
    animation: fadeRight 0.5s 0.15s ease both;
    color: #f1f5f9 !important;
}
.lang-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,211,238,0.15);
    border: 1px solid rgba(34,211,238,0.35);
    border-radius: 100px;
    padding: 3px 14px;
    font-size: 0.75rem; font-weight: 700;
    color: #22d3ee;
    margin-bottom: 12px;
}
.draft-badge {
    display: inline-block;
    background: rgba(251,191,36,0.12);
    border: 1px solid rgba(251,191,36,0.30);
    border-radius: 6px;
    padding: 1px 8px;
    font-size: 0.68rem;
    color: #fbbf24;
    margin-left: 6px;
}

/* ── Reviewer card ───────────────────────────────── */
.rev-card { animation: fadeUp 0.5s 0.2s ease both; }

/* ── Streamlit overrides ─────────────────────────── */
.block-container { padding-top: 1rem !important; }

[data-testid="stSidebar"] {
    background: rgba(6,6,20,0.92) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * { color: rgba(241,245,249,0.85) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }

/* Sidebar radio buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.88rem !important; font-weight: 500 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(124,58,237,0.7), rgba(37,99,235,0.7)) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.22s cubic-bezier(.22,1,.36,1) !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.5) !important;
    border-color: rgba(124,58,237,0.6) !important;
}
.stButton > button:active { transform: scale(0.97) translateY(0) !important; }

/* Primary button */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 4px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: rgba(241,245,249,0.55) !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.6), rgba(37,99,235,0.5)) !important;
    color: #fff !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.4) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f1f5f9 !important;
}

/* Text inputs & areas */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(124,58,237,0.6) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}

/* Labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stRadio label { color: rgba(241,245,249,0.65) !important; }

/* Expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: rgba(241,245,249,0.8) !important; }

/* Info/warning/success/error */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(10px) !important;
}

/* Caption */
.stCaption { color: rgba(241,245,249,0.40) !important; }

/* Markdown */
.stMarkdown p, .stMarkdown li { color: rgba(241,245,249,0.80); }
.stMarkdown strong { color: #f1f5f9 !important; }
.stMarkdown a { color: #22d3ee !important; }
.stMarkdown code { background: rgba(34,211,238,0.1); color: #22d3ee; border-radius:5px; padding:1px 5px; }

/* Sidebar caption */
[data-testid="stSidebar"] .stCaption { color: rgba(241,245,249,0.38) !important; }

/* Download button */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, rgba(5,150,105,0.6), rgba(6,95,70,0.6)) !important;
    border-color: rgba(74,222,128,0.3) !important;
    box-shadow: 0 4px 16px rgba(5,150,105,0.3) !important;
}

/* Audit row */
.audit-row {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-left: 4px solid #7c3aed;
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 10px;
    animation: fadeLeft 0.4s ease both;
    color: rgba(241,245,249,0.85) !important;
}
.audit-row code { color: #22d3ee; background: rgba(34,211,238,0.10); border-radius:4px; padding:1px 6px; }

/* Comparison tab */
.cmp-supported   { color: #4ade80; font-weight:700; }
.cmp-unsupported { color: #fb7185; font-weight:700; }
.cmp-review      { color: #fbbf24; font-weight:700; }

/* Hero tab variants */
.hero-green {
    background: linear-gradient(135deg,
        rgba(5,150,105,0.40) 0%,
        rgba(16,185,129,0.25) 100%);
}
.hero-rose {
    background: linear-gradient(135deg,
        rgba(225,29,72,0.38) 0%,
        rgba(251,113,133,0.22) 100%);
}
.hero-slate {
    background: linear-gradient(135deg,
        rgba(15,23,42,0.80) 0%,
        rgba(30,58,138,0.40) 100%);
}
.hero-indigo {
    background: linear-gradient(135deg,
        rgba(67,56,202,0.45) 0%,
        rgba(99,102,241,0.28) 100%);
}

/* Separator line */
.glass-sep {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.10), transparent);
    margin: 22px 0;
}
</style>

<!-- Floating orb 3 -->
<div class="orb-extra"></div>
""", unsafe_allow_html=True)


# ── DATA ──────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    raw_dir = BASE_DIR / "data" / "raw"
    df_r1 = load_release(raw_dir / "release_1.csv")
    df_r2 = load_release(raw_dir / "release_2.csv")
    with open(BASE_DIR / "data" / "claims.json", "r", encoding="utf-8") as f:
        claims = json.load(f)
    return df_r1, df_r2, claims

if "audit_trail"    not in st.session_state: st.session_state.audit_trail    = []
if "custom_claims"  not in st.session_state: st.session_state.custom_claims  = []

df_release_1, df_release_2, standard_claims = load_all_data()
all_claims = standard_claims + st.session_state.custom_claims

LANG_LABELS = {
    "en": "🇬🇧 English",
    "hi": "🇮🇳 हिंदी",
    "ta": "🇮🇳 தமிழ்",
}


# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:18px 0 10px">
        <div style="font-size:2.6rem;filter:drop-shadow(0 0 18px rgba(124,58,237,0.8));
                    animation:floatUp 3s ease-in-out infinite">🛡️</div>
        <div style="font-size:1.1rem;font-weight:900;color:#f1f5f9;margin-top:6px">
            Claim Watchdog
        </div>
        <div style="font-size:0.72rem;color:rgba(241,245,249,0.40);margin-top:3px">
            Transparent · Free · Open Source
        </div>
    </div>
    <hr style="border:none;height:1px;background:rgba(255,255,255,0.08);margin:10px 0 18px">
    """, unsafe_allow_html=True)

    st.markdown("**📁 Data Release**")
    release_choice = st.radio(
        "",
        ["🟡  Release 1  (Provisional)", "🟢  Release 2  (Audited)"],
        index=0, label_visibility="collapsed",
    )
    active_release_file = "release_1.csv" if "Release 1" in release_choice else "release_2.csv"
    active_df = df_release_1 if "Release 1" in release_choice else df_release_2

    st.markdown("<br>**🌐 Language**", unsafe_allow_html=True)
    lang_choice = st.selectbox(
        "", options=list(LANG_LABELS.keys()),
        format_func=lambda x: LANG_LABELS[x],
        label_visibility="collapsed",
    )

    st.markdown("<br>**📌 Claim**", unsafe_allow_html=True)
    claim_opts = {c["id"]: f"{c['id']}  ·  {c['district']}" for c in all_claims}
    selected_id = st.selectbox(
        "", options=list(claim_opts.keys()),
        format_func=lambda cid: claim_opts[cid],
        label_visibility="collapsed",
    )
    selected_claim = next(c for c in all_claims if c["id"] == selected_id)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶️  Play Demo Video (Auto)", type="primary", use_container_width=True):
        st.session_state.start_tour = True
        st.rerun()

    with st.expander("⏱️ 3-Min Pitch Guide"):
        st.markdown("""
1. 🟡 **Release 1** → CLM-001 → ✅ Supported
2. 🟢 Switch to **Release 2** → watch it change!
3. 🚨 Point to the **Drift Alert**
4. 🌐 Switch language to Tamil / Hindi
5. ✅ Click **Approve** → logged to session trail
6. *"Few tools re-check claims when data is revised."*
        """)

# ── INJECT CINEMATIC VIDEO ENGINE ────────────────────────────────────
should_start_tour = (st.query_params.get("tour") == "true") or st.session_state.get("start_tour", False)
components.html(get_tour_component_html(start_immediately=should_start_tour), height=0)
if st.session_state.get("start_tour"):
    st.session_state.start_tour = False


# ── TABS ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍  Verify",
    "⚖️  Compare",
    "✍️  Parser",
    "📂  Data",
    "📋  Audit",
])


# =====================================================================
# TAB 1 — VERIFY
# =====================================================================
with tab1:

    # ── Hero & Play Demo Video Row ──
    col_hero, col_vid = st.columns([3.2, 1.2])
    with col_hero:
        st.markdown("""
        <div class="hero">
            <div class="hero-icon">🛡️</div>
            <div>
                <div class="hero-title">Public Health Claim Watchdog</div>
                <div class="hero-sub">Tamil Nadu · Transparent Evidence · Bilingual · 100% Free</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_vid:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶️  Play Demo Video", type="primary", use_container_width=True):
            st.session_state.start_tour = True
            st.rerun()
        st.caption("🎬 Self-playing walkthrough with virtual cursor & CC subtitles")

    # ── Transparency notice ──
    st.markdown("""
    <div class="notice">
        ℹ️ <strong style="color:#fde68a">Demo Transparency:</strong>
        Illustrative claims evaluated on simulated releases mirroring official Tamil Nadu HMIS schema.
        The pipeline runs identically on real published CSV files.
    </div>
    """, unsafe_allow_html=True)

    # ── Evaluate ──
    eval_active = evaluate_claim(active_df, selected_claim, release_filename=active_release_file)
    eval_r1 = evaluate_claim(df_release_1, selected_claim, release_filename="release_1.csv")
    eval_r2 = evaluate_claim(df_release_2, selected_claim, release_filename="release_2.csv")
    drift_info = detect_drift(eval_r1, eval_r2)

    ev = eval_active["evidence"]
    verdict = eval_active["verdict"]

    # ── Claim card ──
    claim_type = selected_claim.get("claim_type", "Illustrative claim on simulated data")
    st.markdown(f"""
    <div class="glass claim-card">
        <div class="pill">🏷️  {claim_type}</div>
        <div class="claim-text">"{selected_claim['text']}"</div>
        <div class="claim-meta">
            👤 <strong>{selected_claim.get('speaker','—')}</strong> &nbsp;·&nbsp;
            📅 <strong>{selected_claim.get('claim_date','—')}</strong> &nbsp;·&nbsp;
            📍 <strong>{selected_claim.get('district','—')}</strong> &nbsp;·&nbsp;
            📊 <strong>{selected_claim.get('indicator','—').replace('_',' ').title()}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Verdict + metrics ──
    col_v, col_b, col_o, col_d = st.columns([1.4, 1, 1, 1])

    with col_v:
        if verdict == "Supported":
            ic, lbl, cls = "✅", "SUPPORTED",    "verdict-supported"
        elif verdict == "Unsupported":
            ic, lbl, cls = "❌", "UNSUPPORTED",  "verdict-unsupported"
        else:
            ic, lbl, cls = "⚠️", "NEEDS REVIEW", "verdict-review"
        st.markdown(f"""
        <div class="glass" style="height:100%;text-align:center;padding:28px 10px">
            <div style="font-size:4rem;filter:drop-shadow(0 0 20px rgba(255,255,255,0.3));
                        animation:zoomIn 0.6s cubic-bezier(.36,.07,.19,.97) both">{ic}</div>
            <div class="verdict-label {cls}" style="margin-top:12px">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

    for col, (period, raw_val, icon, label) in zip(
        [col_b, col_o, col_d],
        [
            (selected_claim["period_from"], ev.get("old_value"),        "📅", "Baseline"),
            (selected_claim["period_to"],   ev.get("new_value"),        "📅", "Outcome"),
            ("Δ Change",                    ev.get("computed_change"),  "📈", "Net Delta"),
        ]
    ):
        with col:
            if raw_val is not None:
                disp = f"{raw_val:+g}%" if label == "Net Delta" else f"{raw_val}%"
                if label == "Net Delta":
                    colour = "up" if raw_val > 0 else ("down" if raw_val < 0 else "")
                else:
                    colour = ""
            else:
                disp, colour = "—", ""
            st.markdown(f"""
            <div class="glass" style="height:100%;text-align:center;padding:24px 10px">
                <div class="metric-val {colour}">{disp}</div>
                <div class="metric-lbl">{icon} {period} — {label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Drift alert ──
    if drift_info["has_drift"]:
        ev1, ev2 = drift_info["evidence_release_1"], drift_info["evidence_release_2"]
        c1 = f"{ev1.get('computed_change', 0):+g}%" if ev1.get("computed_change") is not None else "—"
        c2 = f"{ev2.get('computed_change', 0):+g}%" if ev2.get("computed_change") is not None else "—"
        is_deg = drift_info["is_degraded"]
        st.markdown(f"""
        <div class="drift-alert">
            <div class="drift-row">
                <div class="drift-icon">🚨</div>
                <div class="drift-title">{'Revision Drift Detected' if is_deg else 'Status Changed'}</div>
            </div>
            <div class="drift-body">
                {"This claim matched provisional data but <strong style='color:#fb7185'>shifted to Unsupported</strong> after audited figures were published." if is_deg else drift_info['drift_summary']}<br><br>
                <span style="color:rgba(251,191,36,0.9)">📊 Provisional:</span> <strong>{c1}</strong>
                &nbsp;→&nbsp;
                <span style="color:rgba(251,191,36,0.9)">📋 Audited:</span> <strong>{c2}</strong><br>
                <span style="font-size:0.82rem;color:rgba(241,245,249,0.45)">
                Published figures are sometimes revised upon routine data auditing,
                and claims quoted earlier may no longer match.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="glass-sep">', unsafe_allow_html=True)

    # ── Evidence + Explanation ──
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("""
        <div class="ev-card">
        <div class="section-title">📊 <span class="accent">Verifiable</span> Evidence Table</div>
        </div>
        """, unsafe_allow_html=True)
        rows = [
            {"🏷️ Parameter": "Release file",            "📋 Value": str(ev.get("file_name"))},
            {"🏷️ Parameter": "District",               "📋 Value": str(ev.get("district"))},
            {"🏷️ Parameter": "Indicator",              "📋 Value": str(ev.get("indicator","")).replace("_"," ").title()},
            {"🏷️ Parameter": f"Baseline ({selected_claim['period_from']})", "📋 Value": f"{ev.get('old_value')}%"},
            {"🏷️ Parameter": f"Outcome ({selected_claim['period_to']})",    "📋 Value": f"{ev.get('new_value')}%"},
            {"🏷️ Parameter": "Computed Δ",             "📋 Value": f"{ev.get('computed_change'):+g}%" if ev.get("computed_change") is not None else "N/A"},
            {"🏷️ Parameter": "Claimed direction",      "📋 Value": f"{ev.get('claimed_direction')}  · Matched: {ev.get('direction_matched')}"},
            {"🏷️ Parameter": "Magnitude ± tolerance",  "📋 Value": f"~{ev.get('claimed_magnitude')}% ± {ev.get('tolerance')}%  · Matched: {ev.get('magnitude_matched')}"},
            {"🏷️ Parameter": "Data quality",           "📋 Value": "✅ PASS" if eval_active.get("quality_passed") else "⚠️ FAIL"},
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with right:
        chip = LANG_LABELS[lang_choice]
        st.markdown(f"""
        <div class="ex-card">
            <div class="section-title">
                🗣️ <span class="accent">Explanation</span>
                <span class="lang-chip">{chip}</span>
                <span class="draft-badge">draft</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        explanation = explain_verdict(selected_claim, eval_active, lang=lang_choice)
        with st.container():
            st.markdown(f"""
            <div class="glass" style="font-size:0.88rem;color:rgba(241,245,249,0.85);line-height:1.7">
            {explanation}
            </div>
            """, unsafe_allow_html=True)

        if drift_info["has_drift"]:
            with st.expander("🌐 Drift notice in selected language"):
                st.markdown(explain_drift(drift_info, lang=lang_choice))

    st.markdown('<hr class="glass-sep">', unsafe_allow_html=True)

    # ── Reviewer ──
    st.markdown("""
    <div class="rev-card">
        <div class="section-title">🧑‍💼 <span class="accent">Reviewer</span> Sign-Off
            <span style="font-size:0.72rem;color:rgba(241,245,249,0.35);font-weight:400;margin-left:8px">
            session audit trail with CSV export
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cr1, cr2 = st.columns([2, 1])
    with cr1:
        r_name = st.text_input("👤 Reviewer / Desk", value="Fact-Check Desk Reviewer")
        r_note = st.text_area("📝 Notes",
            value=f"Verified against {active_release_file}. Verdict: {verdict}."
                  + (" Drift noted." if drift_info["has_drift"] else ""),
            height=72)
    with cr2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        def _log(decision):
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "claim_id": selected_claim["id"],
                "claim": selected_claim["text"][:55] + "…",
                "release": active_release_file,
                "verdict": verdict,
                "has_drift": drift_info["has_drift"],
                "decision": decision,
                "reviewer": r_name,
                "notes": r_note,
            }
            st.session_state.audit_trail.append(entry)
            pd.DataFrame(st.session_state.audit_trail).to_csv(
                BASE_DIR / "data" / "session_audit_log.csv", index=False)

        if st.button("✅  Approve & Log", type="primary", use_container_width=True):
            _log("APPROVED")
            st.success(f"✅ {selected_claim['id']} approved and logged!")
        if st.button("❌  Reject & Log", use_container_width=True):
            _log("REJECTED")
            st.warning(f"❌ {selected_claim['id']} rejected and logged.")


# =====================================================================
# TAB 2 — COMPARE
# =====================================================================
with tab2:
    st.markdown("""
    <div class="hero hero-green">
        <div class="hero-icon" style="filter:drop-shadow(0 0 16px rgba(5,150,105,0.8))">⚖️</div>
        <div>
            <div class="hero-title" style="background:linear-gradient(90deg,#f1f5f9,#4ade80,#22d3ee);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
                Before vs After
            </div>
            <div class="hero-sub">How routine data audits shift published claim verdicts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for c in all_claims:
        r1 = evaluate_claim(df_release_1, c, "release_1.csv")
        r2 = evaluate_claim(df_release_2, c, "release_2.csv")
        dr = detect_drift(r1, r2)
        e1, e2 = r1["evidence"], r2["evidence"]
        rows.append({
            "ID": c["id"],
            "📍 District": c["district"],
            "📊 Indicator": c["indicator"].replace("_", " ").title(),
            "🟡 R1 Verdict": r1["verdict"],
            "🟡 R1 Δ": f"{e1['computed_change']:+g}%" if e1["computed_change"] is not None else "N/A",
            "🟢 R2 Verdict": r2["verdict"],
            "🟢 R2 Δ": f"{e2['computed_change']:+g}%" if e2["computed_change"] is not None else "N/A",
            "🚨 Drift": "🚨  YES" if dr["has_drift"] else "✅  Stable",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="drift-alert" style="animation-delay:0.15s">
        <div class="drift-row">
            <div class="drift-icon">💡</div>
            <div class="drift-title" style="color:#22d3ee">Coimbatore Revision Story (CLM-001)</div>
        </div>
        <div class="drift-body">
            🟡 <strong>Provisional Release 1:</strong> 74.2% → 83.8% &nbsp;<strong style="color:#4ade80">(+9.6%)</strong> — verdict: <em>Supported</em><br>
            🟢 <strong>Audited Release 2:</strong> 75.5% → 78.9% &nbsp;<strong style="color:#fb7185">(+3.4%)</strong> — verdict shifted to <em>Unsupported</em><br>
            <span style="font-size:0.82rem;color:rgba(241,245,249,0.45)">
            Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
# TAB 3 — PARSER
# =====================================================================
with tab3:
    st.markdown("""
    <div class="hero hero-rose">
        <div class="hero-icon" style="filter:drop-shadow(0 0 16px rgba(251,113,133,0.8))">✍️</div>
        <div>
            <div class="hero-title" style="background:linear-gradient(90deg,#f1f5f9,#fb7185,#fbbf24);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
                Free-Text Sentence Parser
            </div>
            <div class="hero-sub">Type a health claim · We parse it automatically · No paid API needed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="notice" style="border-left-color:#22d3ee;background:rgba(34,211,238,0.07)">
        ℹ️ <strong style="color:#22d3ee">Deterministic regex engine</strong> — works completely offline.
        Try: <em>"Immunization in Madurai rose by 4% between 2021 and 2022"</em>
    </div>
    """, unsafe_allow_html=True)

    sentence = st.text_input(
        "💬 Enter a health claim in plain language:",
        value="Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022",
    )

    if st.button("🔍  Parse & Verify", type="primary"):
        parsed = parse_claim_sentence(sentence, claim_id=f"CUSTOM-{len(st.session_state.custom_claims)+1:03d}")
        if parsed:
            st.success("✅ Parsed successfully into structured claim!")
            with st.expander("🧪 View parsed JSON"):
                st.json(parsed)
            pc1, pc2 = st.columns(2)
            with pc1:
                rr1 = evaluate_claim(df_release_1, parsed, "release_1.csv")
                vi = "✅" if rr1["verdict"]=="Supported" else ("❌" if rr1["verdict"]=="Unsupported" else "⚠️")
                st.markdown(f"""
                <div class="glass-sm">
                    <div style="font-size:1.5rem">{vi}</div>
                    <div style="font-weight:700;color:#f1f5f9;margin-top:4px">Release 1: {rr1['verdict']}</div>
                    <div style="font-size:0.8rem;color:rgba(241,245,249,0.55);margin-top:6px">{rr1['reason'][:120]}…</div>
                </div>""", unsafe_allow_html=True)
            with pc2:
                rr2 = evaluate_claim(df_release_2, parsed, "release_2.csv")
                vi2 = "✅" if rr2["verdict"]=="Supported" else ("❌" if rr2["verdict"]=="Unsupported" else "⚠️")
                st.markdown(f"""
                <div class="glass-sm">
                    <div style="font-size:1.5rem">{vi2}</div>
                    <div style="font-weight:700;color:#f1f5f9;margin-top:4px">Release 2: {rr2['verdict']}</div>
                    <div style="font-size:0.8rem;color:rgba(241,245,249,0.55);margin-top:6px">{rr2['reason'][:120]}…</div>
                </div>""", unsafe_allow_html=True)
            if st.button("➕  Add to Dashboard"):
                st.session_state.custom_claims.append(parsed)
                st.rerun()
        else:
            st.error("❌ Could not parse. Try: 'Immunization in Chennai rose by 5% between 2021 and 2022'")


# =====================================================================
# TAB 4 — DATA EXPLORER
# =====================================================================
with tab4:
    st.markdown("""
    <div class="hero hero-slate">
        <div class="hero-icon" style="filter:drop-shadow(0 0 16px rgba(37,99,235,0.8))">📂</div>
        <div>
            <div class="hero-title" style="background:linear-gradient(90deg,#f1f5f9,#818cf8,#22d3ee);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
                Data Explorer
            </div>
            <div class="hero-sub">Tamil Nadu HMIS simulated releases — inspect numbers directly</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown('<div class="section-title">🟡 Release 1 — Provisional</div>', unsafe_allow_html=True)
        st.dataframe(df_release_1, use_container_width=True)
    with dc2:
        st.markdown('<div class="section-title">🟢 Release 2 — Audited Revision</div>', unsafe_allow_html=True)
        st.dataframe(df_release_2, use_container_width=True)

    st.markdown("""
    <div class="notice" style="margin-top:16px">
        📎 Both releases are simulated representations structured around official MoHFW HMIS schemas for Tamil Nadu.
        The verification pipeline reads any CSV matching this schema identically.
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
# TAB 5 — AUDIT TRAIL
# =====================================================================
with tab5:
    st.markdown("""
    <div class="hero hero-indigo">
        <div class="hero-icon" style="filter:drop-shadow(0 0 16px rgba(99,102,241,0.8))">📋</div>
        <div>
            <div class="hero-title" style="background:linear-gradient(90deg,#f1f5f9,#818cf8,#a3e635);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
                Session Audit Trail
            </div>
            <div class="hero-sub">All reviewer decisions this session — exportable as CSV</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.audit_trail:
        for entry in reversed(st.session_state.audit_trail):
            di = "✅" if entry["decision"] == "APPROVED" else "❌"
            drift_tag = " · 🚨 Drift" if entry.get("has_drift") else ""
            v_colour = {"Supported":"#4ade80","Unsupported":"#fb7185","Needs review":"#fbbf24"}.get(entry["verdict"],"#f1f5f9")
            st.markdown(f"""
            <div class="audit-row">
                <strong style="font-size:1.1rem">{di} {entry['decision']}</strong> &nbsp;·&nbsp;
                <code>{entry['claim_id']}</code> &nbsp;·&nbsp;
                <strong style="color:{v_colour}">{entry['verdict']}</strong>{drift_tag} &nbsp;·&nbsp;
                📁 {entry['release']} &nbsp;·&nbsp; 🕐 {entry['timestamp']}<br>
                <span style="font-size:0.82rem;color:rgba(241,245,249,0.50);margin-top:4px;display:block">
                    👤 {entry['reviewer']} — {entry['notes'][:90]}…
                </span>
            </div>
            """, unsafe_allow_html=True)

        csv_bytes = pd.DataFrame(st.session_state.audit_trail).to_csv(index=False).encode("utf-8")
        st.download_button("📥  Download Audit Trail (CSV)", data=csv_bytes,
                           file_name="claim_watchdog_audit_trail.csv", mime="text/csv")
    else:
        st.markdown("""
        <div style="text-align:center;padding:72px 20px;animation:fadeUp 0.5s ease both">
            <div style="font-size:4rem;filter:drop-shadow(0 0 24px rgba(124,58,237,0.5));
                        animation:floatUp 3s ease-in-out infinite">📋</div>
            <div style="font-size:1.15rem;font-weight:800;color:#f1f5f9;margin-top:16px">
                No decisions logged yet
            </div>
            <div style="font-size:0.88rem;color:rgba(241,245,249,0.45);margin-top:6px">
                Go to <strong style="color:#22d3ee">🔍 Verify</strong> and click Approve or Reject
            </div>
        </div>
        """, unsafe_allow_html=True)
