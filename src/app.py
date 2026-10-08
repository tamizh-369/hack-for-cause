"""Streamlit Web Application — Public Health Claim Watchdog.

Elegant, animated, icon-first UI designed for all literacy levels.
Provides interactive verification, before/after release toggle,
revision drift alerts, evidence tables, draft translations, and a
session audit trail.
"""

from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# ---------- Paths & environment ----------
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.check import detect_drift, evaluate_claim
from src.explain import LANGUAGES, explain_drift, explain_verdict
from src.load import load_release
from src.parse import parse_claim_sentence

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="Health Claim Watchdog",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# FULL CUSTOM CSS — animations, palette, cards, icons
# =====================================================================
st.markdown("""
<style>
/* ─── Google Font ─── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}

/* ─── Background gradient ─── */
.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #fdf6ff 50%, #f0fff4 100%);
}

/* ─── Remove default streamlit menu padding ─── */
.block-container { padding-top: 1.2rem !important; }

/* ─── Sidebar styling ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* ─── Hero banner ─── */
@keyframes fadeSlideDown {
    0%  { opacity: 0; transform: translateY(-30px); }
    100%{ opacity: 1; transform: translateY(0);     }
}
.hero-banner {
    background: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(71,118,230,0.3);
    animation: fadeSlideDown 0.7s ease both;
    display: flex;
    align-items: center;
    gap: 18px;
}
.hero-icon { font-size: 3.2rem; animation: pulse 2s infinite; }
.hero-title { color: #fff; font-size: 2rem; font-weight: 900; margin: 0; letter-spacing: -0.5px; }
.hero-sub   { color: rgba(255,255,255,0.82); font-size: 0.95rem; margin: 4px 0 0; }

/* ─── Pulse animation ─── */
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.12); }
}

/* ─── Notice banner ─── */
@keyframes fadeIn {
    from { opacity:0; transform: translateY(10px); }
    to   { opacity:1; transform: translateY(0);     }
}
.notice-banner {
    background: linear-gradient(90deg,#fffde7,#fff8e1);
    border-left: 5px solid #ffc107;
    border-radius: 12px;
    padding: 12px 20px;
    margin-bottom: 18px;
    font-size: 0.9rem;
    color: #5d4037;
    animation: fadeIn 0.5s ease both;
}

/* ─── Claim card ─── */
@keyframes slideInLeft {
    from { opacity:0; transform: translateX(-40px); }
    to   { opacity:1; transform: translateX(0);     }
}
.claim-card {
    background: #fff;
    border-radius: 18px;
    padding: 22px 26px;
    border-left: 6px solid #8E54E9;
    box-shadow: 0 4px 20px rgba(142,84,233,0.12);
    animation: slideInLeft 0.55s ease both;
    margin-bottom: 22px;
}
.claim-type-pill {
    display: inline-block;
    background: linear-gradient(90deg, #8E54E9, #4776E6);
    color: #fff !important;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    margin-bottom: 10px;
}
.claim-text {
    font-size: 1.08rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 6px 0 12px;
    line-height: 1.5;
}
.claim-meta { font-size: 0.82rem; color: #777; }

/* ─── Verdict badge ─── */
@keyframes popIn {
    0%   { opacity:0; transform: scale(0.5) rotate(-6deg); }
    70%  { transform: scale(1.08) rotate(2deg); }
    100% { opacity:1; transform: scale(1) rotate(0); }
}
.verdict-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.verdict-icon { font-size: 3.8rem; animation: popIn 0.6s cubic-bezier(.36,.07,.19,.97) both; }
.verdict-label {
    font-size: 1.1rem; font-weight: 900; letter-spacing: 0.6px;
    margin-top: 8px; text-align: center; text-transform: uppercase;
    animation: fadeIn 0.4s 0.3s ease both; opacity: 0;
    animation-fill-mode: both;
}
.verdict-supported  { color: #2E7D32; }
.verdict-unsupported{ color: #C62828; }
.verdict-review     { color: #E65100; }

/* ─── Big metric card ─── */
@keyframes countUp {
    from { opacity:0; transform:translateY(14px); }
    to   { opacity:1; transform:translateY(0);    }
}
.big-metric {
    background: #fff;
    border-radius: 16px;
    padding: 18px 10px 14px;
    text-align: center;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    animation: countUp 0.5s ease both;
    height: 100%;
}
.big-metric-value { font-size: 2rem; font-weight: 900; color: #1a1a2e; }
.big-metric-label { font-size: 0.8rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 4px; }
.metric-up   { color: #2E7D32 !important; }
.metric-down { color: #C62828 !important; }

/* ─── Drift alert ─── */
@keyframes shakeBorder {
    0%, 100% { border-color: #ff9800; }
    50%       { border-color: #ff5722; }
}
@keyframes slideInRight {
    from { opacity:0; transform: translateX(60px); }
    to   { opacity:1; transform: translateX(0);    }
}
.drift-alert {
    background: linear-gradient(135deg,#fff3e0,#ffe0b2);
    border: 3px solid #ff9800;
    border-radius: 18px;
    padding: 22px 26px;
    margin: 18px 0;
    animation: slideInRight 0.55s ease both, shakeBorder 1.5s 0.8s ease-in-out 3;
    box-shadow: 0 4px 20px rgba(255,152,0,0.2);
}
.drift-emoji { font-size: 2.4rem; animation: pulse 1s infinite; display: inline-block; }
.drift-title { font-size: 1.25rem; font-weight: 900; color: #bf360c; display: inline-block; margin-left: 10px; vertical-align: middle; }
.drift-body  { font-size: 0.95rem; color: #5d4037; margin-top: 10px; line-height: 1.6; }

/* ─── Evidence table ─── */
.evidence-card {
    background: #fff;
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    animation: fadeIn 0.5s 0.1s ease both;
}

/* ─── Explain card ─── */
.explain-card {
    background: linear-gradient(135deg,#f8f0ff,#f0f4ff);
    border-radius: 16px;
    padding: 22px;
    border: 1.5px solid #d0aaff;
    animation: fadeIn 0.5s 0.2s ease both;
}

/* ─── Language pill buttons area ─── */
.lang-badge {
    display: inline-block;
    background: linear-gradient(90deg,#4776E6,#8E54E9);
    color: #fff !important;
    border-radius: 14px;
    padding: 4px 16px;
    font-size: 0.82rem;
    font-weight: 700;
    margin: 4px 2px;
    animation: fadeIn 0.4s ease both;
}

/* ─── Reviewer console ─── */
.reviewer-card {
    background: #fff;
    border-radius: 16px;
    padding: 22px;
    border-top: 4px solid #4776E6;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    animation: fadeIn 0.5s 0.15s ease both;
}

/* ─── Comparison row colours ─── */
.cmp-supported   { background: #E8F5E9; border-radius: 6px; padding: 2px 8px; color: #2E7D32; font-weight: 700; }
.cmp-unsupported { background: #FFEBEE; border-radius: 6px; padding: 2px 8px; color: #C62828; font-weight: 700; }
.cmp-review      { background: #FFF8E1; border-radius: 6px; padding: 2px 8px; color: #E65100; font-weight: 700; }

/* ─── Streamlit button hover glow ─── */
.stButton > button {
    transition: all 0.25s ease !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 6px 20px rgba(71,118,230,0.35) !important;
}
.stButton > button:active {
    transform: scale(0.97) !important;
}

/* ─── Radio / selectbox ─── */
[data-testid="stRadio"] label, [data-testid="stSelectbox"] label {
    font-size: 0.92rem !important;
    font-weight: 700 !important;
}

/* ─── Tab row ─── */
.stTabs [data-baseweb="tab"] {
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 8px 18px !important;
    transition: background 0.2s, color 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg,#4776E6,#8E54E9) !important;
    color: #fff !important;
}

/* ─── Audit trail ─── */
.audit-row {
    background: #fff;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border-left: 5px solid #4776E6;
    animation: slideInLeft 0.4s ease both;
}

/* ─── Section headers ─── */
.section-header {
    font-size: 1.2rem;
    font-weight: 900;
    color: #1a1a2e;
    margin: 18px 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ─── Status ring ─── */
@keyframes spinRing {
    to { stroke-dashoffset: 0; }
}
</style>
""", unsafe_allow_html=True)


# =====================================================================
# DATA LOADING
# =====================================================================
@st.cache_data
def load_all_data():
    raw_dir = BASE_DIR / "data" / "raw"
    claims_file = BASE_DIR / "data" / "claims.json"
    df_r1 = load_release(raw_dir / "release_1.csv")
    df_r2 = load_release(raw_dir / "release_2.csv")
    with open(claims_file, "r", encoding="utf-8") as f:
        claims = json.load(f)
    return df_r1, df_r2, claims


if "audit_trail" not in st.session_state:
    st.session_state.audit_trail = []
if "custom_claims" not in st.session_state:
    st.session_state.custom_claims = []

df_release_1, df_release_2, standard_claims = load_all_data()
all_claims = standard_claims + st.session_state.custom_claims


# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("## 🛡️ Claim Watchdog")
    st.caption("Deterministic · Free · Open Source")
    st.markdown("---")

    st.markdown("### 📁 Data Release")
    release_choice = st.radio(
        "",
        options=[
            "🟡  Release 1  (Provisional)",
            "🟢  Release 2  (Audited)"
        ],
        index=0,
    )

    active_release_file = "release_1.csv" if "Release 1" in release_choice else "release_2.csv"
    active_df = df_release_1 if "Release 1" in release_choice else df_release_2

    st.markdown("---")
    st.markdown("### 🌐 Language")
    lang_choice = st.selectbox(
        "",
        options=["en", "hi", "ta"],
        format_func=lambda x: {"en": "🇬🇧 English", "hi": "🇮🇳 हिंदी (Hindi)", "ta": "🇮🇳 தமிழ் (Tamil)"}[x],
    )

    st.markdown("---")
    st.markdown("### 📌 Choose Claim")
    claim_options = {
        c["id"]: f"{c['id']} · {c['district']}"
        for c in all_claims
    }
    selected_claim_id = st.selectbox(
        "",
        options=list(claim_options.keys()),
        format_func=lambda cid: claim_options[cid],
    )

    st.markdown("---")
    with st.expander("⏱️ 3-Min Pitch Guide"):
        st.markdown("""
**Step-by-step:**
1. 🟡 Select **Release 1** → CLM-001 shows ✅ **Supported**
2. 🟢 Switch to **Release 2** → Watch status change!
3. 🚨 Point out the **Drift Alert**
4. 🌐 Change language to Tamil or Hindi
5. ✅ Click **Approve** → session audit trail logs it
6. 💬 *"Few tools re-check claims when data is revised."*
""")

selected_claim = next(c for c in all_claims if c["id"] == selected_claim_id)


# =====================================================================
# TABS
# =====================================================================
tab_verify, tab_compare, tab_parse, tab_data, tab_audit = st.tabs([
    "🔍  Verify Claim",
    "⚖️  Compare Releases",
    "✍️  Text Parser",
    "📂  Data Explorer",
    "📋  Audit Trail",
])


# =====================================================================
# TAB 1: CLAIM VERIFICATION
# =====================================================================
with tab_verify:

    # Hero banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-icon">🛡️</div>
        <div>
            <div class="hero-title">Public Health Claim Watchdog</div>
            <div class="hero-sub">Transparent · Verifiable · Bilingual · Free</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Transparency notice
    st.markdown("""
    <div class="notice-banner">
        ℹ️ <strong>Demo Transparency:</strong> This prototype evaluates illustrative claims on
        simulated releases that mirror official Tamil Nadu HMIS schema.
        The pipeline runs identically on real published CSV files.
    </div>
    """, unsafe_allow_html=True)

    # --- Evaluate ---
    eval_active = evaluate_claim(active_df, selected_claim, release_filename=active_release_file)
    eval_r1 = evaluate_claim(df_release_1, selected_claim, release_filename="release_1.csv")
    eval_r2 = evaluate_claim(df_release_2, selected_claim, release_filename="release_2.csv")
    drift_info = detect_drift(eval_r1, eval_r2)

    ev = eval_active["evidence"]
    verdict = eval_active["verdict"]

    # --- Claim card ---
    claim_type = selected_claim.get("claim_type", "Illustrative claim on simulated data")
    st.markdown(f"""
    <div class="claim-card">
        <div class="claim-type-pill">🏷️ {claim_type}</div>
        <div class="claim-text">"{selected_claim['text']}"</div>
        <div class="claim-meta">
            👤 {selected_claim.get('speaker','—')} &nbsp;|&nbsp;
            📅 {selected_claim.get('claim_date','—')} &nbsp;|&nbsp;
            📌 {selected_claim.get('district','—')} &nbsp;|&nbsp;
            📊 {selected_claim.get('indicator','—').replace('_',' ').title()}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Verdict + Metrics row ---
    col_v, col_old, col_new, col_chg = st.columns([1.5, 1, 1, 1])

    with col_v:
        if verdict == "Supported":
            icon, label, cls = "✅", "SUPPORTED", "verdict-supported"
        elif verdict == "Unsupported":
            icon, label, cls = "❌", "UNSUPPORTED", "verdict-unsupported"
        else:
            icon, label, cls = "⚠️", "NEEDS REVIEW", "verdict-review"
        st.markdown(f"""
        <div class="verdict-wrap">
            <div class="verdict-icon">{icon}</div>
            <div class="verdict-label {cls}">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_old:
        val = f"{ev['old_value']}%" if ev["old_value"] is not None else "—"
        st.markdown(f"""
        <div class="big-metric">
            <div class="big-metric-value">{val}</div>
            <div class="big-metric-label">📅 {selected_claim['period_from']} Baseline</div>
        </div>
        """, unsafe_allow_html=True)

    with col_new:
        val = f"{ev['new_value']}%" if ev["new_value"] is not None else "—"
        st.markdown(f"""
        <div class="big-metric">
            <div class="big-metric-value">{val}</div>
            <div class="big-metric-label">📅 {selected_claim['period_to']} Outcome</div>
        </div>
        """, unsafe_allow_html=True)

    with col_chg:
        if ev["computed_change"] is not None:
            chg = ev["computed_change"]
            chg_str = f"{chg:+g}%"
            colour_cls = "metric-up" if chg > 0 else "metric-down"
        else:
            chg_str, colour_cls = "—", ""
        st.markdown(f"""
        <div class="big-metric">
            <div class="big-metric-value {colour_cls}">{chg_str}</div>
            <div class="big-metric-label">📈 Net Change</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Drift alert ---
    if drift_info["has_drift"]:
        is_deg = drift_info["is_degraded"]
        ev1 = drift_info["evidence_release_1"]
        ev2 = drift_info["evidence_release_2"]
        chg1 = f"{ev1.get('computed_change', 0):+g}%" if ev1.get("computed_change") is not None else "—"
        chg2 = f"{ev2.get('computed_change', 0):+g}%" if ev2.get("computed_change") is not None else "—"
        st.markdown(f"""
        <div class="drift-alert">
            <span class="drift-emoji">🚨</span>
            <span class="drift-title">{'Revision Drift Detected!' if is_deg else 'Status Change Detected'}</span>
            <div class="drift-body">
                {"⬇️ This claim was <strong>Supported</strong> in the provisional release but shifted to <strong>Unsupported</strong> after audited data was published." if is_deg else drift_info['drift_summary']}
                <br><br>
                📊 Provisional change: <strong>{chg1}</strong> &nbsp;→&nbsp;
                Audited change: <strong>{chg2}</strong><br>
                <em style="font-size:0.85rem;color:#8d6e63;">Published figures are sometimes revised upon routine data auditing,
                and claims quoted earlier may no longer match.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Evidence table + Explanation side by side ---
    col_left, col_right = st.columns([1.15, 1])

    with col_left:
        st.markdown('<div class="section-header">📊 Verifiable Evidence Table</div>', unsafe_allow_html=True)
        with st.container():
            evidence_rows = [
                {"🏷️ Parameter": "Release file",            "📋 Value": str(ev.get("file_name"))},
                {"🏷️ Parameter": "District",               "📋 Value": str(ev.get("district"))},
                {"🏷️ Parameter": "Indicator",              "📋 Value": str(ev.get("indicator","")).replace("_"," ").title()},
                {"🏷️ Parameter": f"Baseline ({selected_claim['period_from']})",
                                                            "📋 Value": f"{ev.get('old_value')}%"},
                {"🏷️ Parameter": f"Outcome ({selected_claim['period_to']})",
                                                            "📋 Value": f"{ev.get('new_value')}%"},
                {"🏷️ Parameter": "Computed change",        "📋 Value": f"{ev.get('computed_change'):+g}%" if ev.get("computed_change") is not None else "N/A"},
                {"🏷️ Parameter": "Claimed direction",      "📋 Value": f"{ev.get('claimed_direction')} · Matched: {ev.get('direction_matched')}"},
                {"🏷️ Parameter": "Claimed magnitude ± tol","📋 Value": f"~{ev.get('claimed_magnitude')}% ± {ev.get('tolerance')}% · Matched: {ev.get('magnitude_matched')}"},
                {"🏷️ Parameter": "Data quality",           "📋 Value": "✅ PASS" if eval_active.get("quality_passed") else f"⚠️ FAIL"},
            ]
            st.dataframe(pd.DataFrame(evidence_rows), use_container_width=True, hide_index=True)

    with col_right:
        lang_names = {"en": "🇬🇧 English", "hi": "🇮🇳 हिंदी", "ta": "🇮🇳 தமிழ்"}
        st.markdown(
            f'<div class="section-header">🗣️ Explanation <span class="lang-badge">{lang_names[lang_choice]}</span>'
            f' <span style="font-size:0.72rem;color:#aaa;font-weight:400">(draft translation)</span></div>',
            unsafe_allow_html=True
        )
        explanation_text = explain_verdict(selected_claim, eval_active, lang=lang_choice)
        st.markdown(f'<div class="explain-card">{explanation_text}</div>', unsafe_allow_html=True)

        if drift_info["has_drift"]:
            with st.expander("🌐 Drift Alert — Regional Language"):
                st.markdown(explain_drift(drift_info, lang=lang_choice))

    st.markdown("---")

    # --- Reviewer console ---
    st.markdown('<div class="section-header">🧑‍💼 Reviewer Sign-Off</div>', unsafe_allow_html=True)
    st.caption("Human-in-the-loop: approve or reject before publishing · Session audit trail with CSV export.")

    with st.container():
        col_r1, col_r2 = st.columns([2, 1])

        with col_r1:
            reviewer_name = st.text_input("👤 Reviewer name / desk", value="Fact-Check Desk Reviewer")
            reviewer_notes = st.text_area(
                "📝 Notes",
                value=f"Verified against {active_release_file}. Status: {verdict}."
                + (" Confirmed revision drift." if drift_info["has_drift"] else ""),
                height=72,
            )

        with col_r2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("✅ Approve & Log", type="primary", use_container_width=True):
                entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "claim_id": selected_claim["id"],
                    "claim_text": selected_claim["text"][:60] + "…",
                    "release": active_release_file,
                    "verdict": verdict,
                    "has_drift": drift_info["has_drift"],
                    "decision": "APPROVED",
                    "reviewer": reviewer_name,
                    "notes": reviewer_notes,
                }
                st.session_state.audit_trail.append(entry)
                pd.DataFrame(st.session_state.audit_trail).to_csv(
                    BASE_DIR / "data" / "session_audit_log.csv", index=False
                )
                st.success(f"✅ Claim {selected_claim['id']} approved and logged!")

            if st.button("❌ Reject & Log", use_container_width=True):
                entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "claim_id": selected_claim["id"],
                    "claim_text": selected_claim["text"][:60] + "…",
                    "release": active_release_file,
                    "verdict": verdict,
                    "has_drift": drift_info["has_drift"],
                    "decision": "REJECTED",
                    "reviewer": reviewer_name,
                    "notes": reviewer_notes,
                }
                st.session_state.audit_trail.append(entry)
                pd.DataFrame(st.session_state.audit_trail).to_csv(
                    BASE_DIR / "data" / "session_audit_log.csv", index=False
                )
                st.warning(f"❌ Claim {selected_claim['id']} rejected and logged.")


# =====================================================================
# TAB 2: CROSS-RELEASE COMPARISON
# =====================================================================
with tab_compare:
    st.markdown('<div class="hero-banner" style="background:linear-gradient(135deg,#11998e,#38ef7d)"><div class="hero-icon">⚖️</div><div><div class="hero-title">Before vs After</div><div class="hero-sub">How revisions shift verdicts across releases</div></div></div>', unsafe_allow_html=True)

    rows = []
    for c in all_claims:
        r1 = evaluate_claim(df_release_1, c, "release_1.csv")
        r2 = evaluate_claim(df_release_2, c, "release_2.csv")
        dr = detect_drift(r1, r2)
        e1, e2 = r1["evidence"], r2["evidence"]
        rows.append({
            "ID": c["id"],
            "📍 District": c["district"],
            "📊 Indicator": c["indicator"].replace("_"," ").title(),
            "🟡 Rel-1 Verdict": r1["verdict"],
            "🟡 Rel-1 Δ": f"{e1['computed_change']:+g}%" if e1["computed_change"] is not None else "N/A",
            "🟢 Rel-2 Verdict": r2["verdict"],
            "🟢 Rel-2 Δ": f"{e2['computed_change']:+g}%" if e2["computed_change"] is not None else "N/A",
            "🚨 Drift": "🚨 YES" if dr["has_drift"] else "✅ Stable",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="drift-alert" style="animation-delay:0.1s">
        <span class="drift-emoji">💡</span>
        <span class="drift-title" style="color:#1a237e">The Coimbatore Revision Story</span>
        <div class="drift-body">
            🟡 <strong>Provisional data (Release 1):</strong> Immunization coverage rose from 74.2% → 83.8% <strong>(+9.6%)</strong> — claim <em>Supported</em>.<br>
            🟢 <strong>Audited data (Release 2):</strong> Reconciled to 75.5% → 78.9% <strong>(+3.4%)</strong> — verdict shifts to <em>Unsupported</em>.<br>
            <em style="color:#8d6e63">Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
# TAB 3: FREE TEXT PARSER
# =====================================================================
with tab_parse:
    st.markdown('<div class="hero-banner" style="background:linear-gradient(135deg,#f093fb,#f5576c)"><div class="hero-icon">✍️</div><div><div class="hero-title">Sentence Parser</div><div class="hero-sub">Type a health claim in plain English — we parse it automatically</div></div></div>', unsafe_allow_html=True)

    st.info("ℹ️ No paid API needed. Deterministic regex engine, works offline.")

    user_sentence = st.text_input(
        "💬 Type a health claim:",
        value="Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022",
        placeholder="e.g. Institutional deliveries in Madurai rose by 4% between 2021 and 2022"
    )

    if st.button("🔍 Parse & Verify", type="primary"):
        parsed = parse_claim_sentence(user_sentence, claim_id=f"CUSTOM-{len(st.session_state.custom_claims)+1:03d}")
        if parsed:
            st.success("✅ Parsed into structured claim!")
            with st.expander("🧪 View parsed structure"):
                st.json(parsed)
            c1, c2 = st.columns(2)
            with c1:
                rr1 = evaluate_claim(df_release_1, parsed, "release_1.csv")
                v1_icon = "✅" if rr1["verdict"] == "Supported" else ("❌" if rr1["verdict"] == "Unsupported" else "⚠️")
                st.markdown(f"### {v1_icon} Release 1: `{rr1['verdict']}`")
                st.caption(rr1["reason"])
            with c2:
                rr2 = evaluate_claim(df_release_2, parsed, "release_2.csv")
                v2_icon = "✅" if rr2["verdict"] == "Supported" else ("❌" if rr2["verdict"] == "Unsupported" else "⚠️")
                st.markdown(f"### {v2_icon} Release 2: `{rr2['verdict']}`")
                st.caption(rr2["reason"])

            if st.button("➕ Add to Dashboard"):
                st.session_state.custom_claims.append(parsed)
                st.rerun()
        else:
            st.error("❌ Could not parse this sentence. Try a simpler structure like 'Immunization in Chennai rose by 5% between 2021 and 2022'.")


# =====================================================================
# TAB 4: RAW DATA EXPLORER
# =====================================================================
with tab_data:
    st.markdown('<div class="hero-banner" style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364)"><div class="hero-icon">📂</div><div><div class="hero-title">Data Explorer</div><div class="hero-sub">Inspect the underlying Tamil Nadu HMIS releases</div></div></div>', unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### 🟡 Release 1 — Provisional (Dec 2022)")
        st.dataframe(df_release_1, use_container_width=True)
    with d2:
        st.markdown("#### 🟢 Release 2 — Audited Revision (Aug 2023)")
        st.dataframe(df_release_2, use_container_width=True)

    st.caption("Both releases are simulated representations structured around official MoHFW HMIS schemas for Tamil Nadu.")


# =====================================================================
# TAB 5: SESSION AUDIT TRAIL
# =====================================================================
with tab_audit:
    st.markdown('<div class="hero-banner" style="background:linear-gradient(135deg,#1a1a2e,#4776E6)"><div class="hero-icon">📋</div><div><div class="hero-title">Session Audit Trail</div><div class="hero-sub">All reviewer decisions logged this session — exportable as CSV</div></div></div>', unsafe_allow_html=True)

    if st.session_state.audit_trail:
        for i, entry in enumerate(reversed(st.session_state.audit_trail)):
            dec_icon = "✅" if entry["decision"] == "APPROVED" else "❌"
            drift_tag = " 🚨" if entry.get("has_drift") else ""
            st.markdown(f"""
            <div class="audit-row">
                <strong>{dec_icon} {entry['decision']}</strong> &nbsp;—&nbsp;
                <code>{entry['claim_id']}</code> &nbsp;|&nbsp;
                <strong>{entry['verdict']}</strong>{drift_tag} &nbsp;|&nbsp;
                📁 {entry['release']} &nbsp;|&nbsp;
                🕐 {entry['timestamp']}<br>
                <span style="font-size:0.85rem;color:#555">👤 {entry['reviewer']} — {entry['notes'][:80]}…</span>
            </div>
            """, unsafe_allow_html=True)

        df_audit = pd.DataFrame(st.session_state.audit_trail)
        st.download_button(
            "📥 Download Audit Trail (CSV)",
            data=df_audit.to_csv(index=False).encode("utf-8"),
            file_name="claim_watchdog_audit_trail.csv",
            mime="text/csv",
        )
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#aaa;">
            <div style="font-size:3.5rem">📋</div>
            <div style="font-size:1.1rem;font-weight:700;margin-top:12px">No decisions logged yet</div>
            <div style="font-size:0.9rem;margin-top:6px">Go to <strong>🔍 Verify Claim</strong> and click Approve or Reject</div>
        </div>
        """, unsafe_allow_html=True)
