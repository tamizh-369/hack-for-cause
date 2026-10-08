"""Streamlit Web Application for Public Health Claim Watchdog.

Provides interactive verification, before/after dataset release toggle,
automatic revision drift alerts, verifiable evidence tables, bilingual explanations,
and a human-in-the-loop reviewer approval workflow.
"""

from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# Setup paths and environment
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.check import detect_drift, evaluate_claim
from src.explain import LANGUAGES, explain_drift, explain_verdict
from src.load import load_release, normalize_district_name
from src.mapping import INDICATOR_REGISTRY, get_indicator_metadata, resolve_indicator
from src.parse import parse_claim_sentence

# --- Page Configuration ---
st.set_page_config(
    page_title="Public Health Claim Watchdog",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 12px;
    }
    .badge-supported {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #A5D6A7;
    }
    .badge-unsupported {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #FFCDD2;
    }
    .badge-review {
        background-color: #FFF8E1;
        color: #F57F17;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #FFE082;
    }
    .drift-alert-box {
        background-color: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 10px;
        padding: 16px;
        margin: 15px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_all_data():
    """Load claims and releases with caching."""
    raw_dir = BASE_DIR / "data" / "raw"
    claims_file = BASE_DIR / "data" / "claims.json"

    df_r1 = load_release(raw_dir / "release_1.csv")
    df_r2 = load_release(raw_dir / "release_2.csv")

    with open(claims_file, "r", encoding="utf-8") as f:
        claims = json.load(f)

    return df_r1, df_r2, claims


# Initialize session state for reviewer workflow and audit trail
if "audit_trail" not in st.session_state:
    st.session_state.audit_trail = []

if "custom_claims" not in st.session_state:
    st.session_state.custom_claims = []

df_release_1, df_release_2, standard_claims = load_all_data()

# Combine standard and custom claims
all_claims = standard_claims + st.session_state.custom_claims

# --- Sidebar Controls ---
st.sidebar.image(
    "https://img.icons8.com/fluency/96/shield.png",
    width=64,
)
st.sidebar.title("Claim Watchdog")
st.sidebar.caption("Deterministic, Free & Open Source Health Claim Verification")

st.sidebar.markdown("---")
st.sidebar.subheader("1. Active Dataset Release")
release_choice = st.sidebar.radio(
    "Select Official Release to Audit:",
    options=["Release 1 (Provisional - Dec 2022)", "Release 2 (Audited Revision - Aug 2023)"],
    index=0,
    help="Toggle between initial provisional data and subsequent government audited data to inspect revisions.",
)

active_release_file = "release_1.csv" if "Release 1" in release_choice else "release_2.csv"
active_df = df_release_1 if "Release 1" in release_choice else df_release_2

st.sidebar.markdown("---")
st.sidebar.subheader("2. Explanation Language")
lang_choice = st.sidebar.selectbox(
    "Select Localized Language:",
    options=["en", "hi", "ta"],
    format_func=lambda x: LANGUAGES[x]["name"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("3. Select Pre-built Claim")
claim_options = {c["id"]: f"[{c['id']}] {c['district']} - {c['indicator']}" for c in all_claims}
selected_claim_id = st.sidebar.selectbox(
    "Choose Claim:",
    options=list(claim_options.keys()),
    format_func=lambda cid: claim_options[cid],
)

selected_claim = next(c for c in all_claims if c["id"] == selected_claim_id)

st.sidebar.markdown("---")
with st.sidebar.expander("⏱️ 3-Minute Pitch Script Guide"):
    st.markdown(
        """
        **Step-by-step Demo Guide:**
        1. **Problem (30s)**: Introduce Claim `CLM-001` (illustrative claim on simulated data).
           - *State problem:* *"Few tools re-check published claims when the underlying data is revised."*
           - *State explicitly:* *"This demo uses simulated releases that mirror real HMIS structure; the pipeline works on real files."*
        2. **Setup (20s)**: Show the claim linked to its release file and transparent filter.
        3. **Before (30s)**: Notice under **Release 1**, it is **Supported** (+9.6%).
        4. **Update (20s)**: Switch radio to **Release 2**!
        5. **After (40s)**: Status shifts to **Unsupported** (+3.4%). Point out **Drift Alert** and draft translations in Hindi and Tamil.
        6. **Review (20s)**: Click **Approve & Publish Alert** to record in the session audit trail with CSV export.
        7. **Close (20s)**: Completely free, offline fallback ready, open source.
        """
    )


# --- Main Dashboard Tabs ---
tab_verify, tab_compare, tab_parse, tab_data, tab_audit = st.tabs([
    "🔍 Claim Verification",
    "⚖️ Cross-Release Drift Comparison",
    "✍️ Custom Sentence Parser",
    "📂 Raw Data Explorer",
    "📋 Session Audit Trail",
])

# ==========================================
# TAB 1: CLAIM VERIFICATION
# ==========================================
with tab_verify:
    st.title("🛡️ Public Health Claim Watchdog")
    st.markdown(
        "Verifying claims against official public health releases using deterministic logic, "
        "reproducible evidence tables, and native bilingual explanations."
    )

    st.warning(
        "ℹ️ **Demo Transparency Note:** This prototype evaluates illustrative claims on simulated releases "
        "that mirror official MoHFW HMIS schema; the verification pipeline runs identically on real published CSV files."
    )

    # Active Claim Card
    claim_type_label = selected_claim.get("claim_type", "Illustrative claim on simulated data")
    st.info(
        f"**Claim ({selected_claim['id']}):** \"{selected_claim['text']}\"\n\n"
        f"🏷️ *Status:* **{claim_type_label}** | "
        f"👤 *Source:* {selected_claim.get('speaker', 'Illustrative Press Release')} | "
        f"📅 *Date:* {selected_claim.get('claim_date', 'N/A')}\n\n"
        f"🎯 *Context:* {selected_claim.get('context', 'Simulated demonstration context.')}"
    )

    # Run Evaluations
    eval_active = evaluate_claim(active_df, selected_claim, release_filename=active_release_file)
    eval_r1 = evaluate_claim(df_release_1, selected_claim, release_filename="release_1.csv")
    eval_r2 = evaluate_claim(df_release_2, selected_claim, release_filename="release_2.csv")
    drift_info = detect_drift(eval_r1, eval_r2)

    # Drift Alert Banner if active release is Release 2 and drift occurred
    if active_release_file == "release_2.csv" and drift_info["has_drift"]:
        st.markdown(
            f"""
            <div class="drift-alert-box">
                <h3 style="color: #D84315; margin: 0 0 10px 0;">🚨 Official Data Revision Drift Detected!</h3>
                <p style="font-size: 1.05rem; margin: 0;">
                    <b>{drift_info['drift_summary']}</b>
                </p>
                <p style="font-size: 0.88rem; color: #666; margin: 6px 0 0 0;">
                    (Demonstration using simulated revision releases mirroring HMIS auditing practices)
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Summary Metrics Row
    col_v, col_old, col_new, col_chg = st.columns([1.5, 1, 1, 1])

    ev = eval_active["evidence"]
    verdict = eval_active["verdict"]

    with col_v:
        st.markdown("##### Verdict Status")
        if verdict == "Supported":
            st.markdown('<span class="badge-supported">✅ SUPPORTED</span>', unsafe_allow_html=True)
        elif verdict == "Unsupported":
            st.markdown('<span class="badge-unsupported">❌ UNSUPPORTED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-review">⚠️ NEEDS REVIEW</span>', unsafe_allow_html=True)

    with col_old:
        old_val_str = f"{ev['old_value']}%" if ev["old_value"] is not None else "N/A"
        st.metric(f"Baseline ({selected_claim['period_from']})", old_val_str)

    with col_new:
        new_val_str = f"{ev['new_value']}%" if ev["new_value"] is not None else "N/A"
        st.metric(f"Comparison ({selected_claim['period_to']})", new_val_str)

    with col_chg:
        chg_str = f"{ev['computed_change']:+g}%" if ev["computed_change"] is not None else "N/A"
        st.metric("Net Change", chg_str)

    st.markdown("---")

    # Evidence Table & Deterministic Rules
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📊 Verifiable Evidence Table")
        st.caption("Extracted slice and parameter thresholds used to evaluate this claim:")

        evidence_df = pd.DataFrame([
            {"Parameter": "Active Release File", "Value": str(ev.get("file_name"))},
            {"Parameter": "Target District", "Value": str(ev.get("district"))},
            {"Parameter": "Indicator", "Value": str(ev.get("indicator"))},
            {"Parameter": "Period Baseline", "Value": f"{ev.get('period_from')} ({ev.get('old_value')}%)"},
            {"Parameter": "Period Comparison", "Value": f"{ev.get('period_to')} ({ev.get('new_value')}%)"},
            {"Parameter": "Computed Delta", "Value": f"{ev.get('computed_change'):+g}%" if ev.get('computed_change') is not None else "N/A"},
            {"Parameter": "Claimed Direction", "Value": f"{ev.get('claimed_direction')} (Matched: {ev.get('direction_matched')})"},
            {"Parameter": "Claimed Magnitude & Tol", "Value": f"~{ev.get('claimed_magnitude')}% ± {ev.get('tolerance')}% (Matched: {ev.get('magnitude_matched')})"},
            {"Parameter": "Data Quality Validated", "Value": "PASS" if eval_active.get("quality_passed") else f"FAIL ({eval_active.get('quality_error')})"},
        ])
        st.dataframe(evidence_df, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("🗣️ Localized Explanation (Draft Translations)")
        st.caption(f"Language: **{LANGUAGES[lang_choice]['name']}** *(Draft translation; human review in progress)*")

        explanation_text = explain_verdict(selected_claim, eval_active, lang=lang_choice)
        st.markdown(explanation_text)

        if active_release_file == "release_2.csv" and drift_info["has_drift"]:
            with st.expander("🚨 Regional Language Drift Alert Notice"):
                st.markdown(explain_drift(drift_info, lang=lang_choice))

    st.markdown("---")

    # Reviewer Decision Step (Phase 3 Requirement)
    st.subheader("🧑‍💼 Reviewer Decision & Action Console")
    st.caption("Human-in-the-loop audit step: Official review to approve or reject publishing this finding (Session audit trail with CSV export).")

    col_rev1, col_rev2 = st.columns([2, 1])
    with col_rev1:
        reviewer_name = st.text_input("Reviewer Name / Desk:", value="Fact-Check Desk Reviewer")
        reviewer_notes = st.text_area(
            "Reviewer Verification Notes:",
            value=f"Verified against {active_release_file}. Status: {verdict}."
            + (" Confirmed revision drift from provisional data." if drift_info["has_drift"] else ""),
            height=70,
        )

    with col_rev2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Approve & Publish Alert", type="primary", use_container_width=True):
            audit_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "claim_id": selected_claim["id"],
                "claim_text": selected_claim["text"],
                "release_audited": active_release_file,
                "verdict": verdict,
                "has_drift": drift_info["has_drift"],
                "decision": "APPROVED",
                "reviewer": reviewer_name,
                "notes": reviewer_notes,
            }
            st.session_state.audit_trail.append(audit_entry)

            # Local CSV audit append
            audit_log_path = BASE_DIR / "data" / "session_audit_log.csv"
            audit_df = pd.DataFrame(st.session_state.audit_trail)
            audit_df.to_csv(audit_log_path, index=False)

            st.success(f"Claim {selected_claim['id']} APPROVED and recorded in session audit trail!")

        if st.button("❌ Reject Alert", use_container_width=True):
            audit_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "claim_id": selected_claim["id"],
                "claim_text": selected_claim["text"],
                "release_audited": active_release_file,
                "verdict": verdict,
                "has_drift": drift_info["has_drift"],
                "decision": "REJECTED",
                "reviewer": reviewer_name,
                "notes": reviewer_notes,
            }
            st.session_state.audit_trail.append(audit_entry)

            # Local CSV audit append
            audit_log_path = BASE_DIR / "data" / "session_audit_log.csv"
            audit_df = pd.DataFrame(st.session_state.audit_trail)
            audit_df.to_csv(audit_log_path, index=False)

            st.warning(f"Claim {selected_claim['id']} marked as REJECTED.")


# ==========================================
# TAB 2: CROSS-RELEASE DRIFT COMPARISON
# ==========================================
with tab_compare:
    st.subheader("⚖️ Before & After Release Comparison Matrix")
    st.markdown(
        "Side-by-side inspection of all claims evaluated across both dataset releases. "
        "Enables reviewers to catch historical data revisions instantly."
    )

    comparison_rows = []
    for c in all_claims:
        res1 = evaluate_claim(df_release_1, c, release_filename="release_1.csv")
        res2 = evaluate_claim(df_release_2, c, release_filename="release_2.csv")
        drift = detect_drift(res1, res2)

        ev_1 = res1["evidence"]
        ev_2 = res2["evidence"]

        chg1 = f"{ev_1['computed_change']:+g}%" if ev_1["computed_change"] is not None else "N/A"
        chg2 = f"{ev_2['computed_change']:+g}%" if ev_2["computed_change"] is not None else "N/A"

        drift_badge = "🚨 DRIFT DETECTED" if drift["has_drift"] else "✅ STABLE"

        comparison_rows.append({
            "Claim ID": c["id"],
            "District": c["district"],
            "Indicator": c["indicator"],
            "Claimed Target": f"{c['direction']} ~{c.get('magnitude', 'N/A')}%",
            "Release 1 Verdict": res1["verdict"],
            "Release 1 Delta": chg1,
            "Release 2 Verdict": res2["verdict"],
            "Release 2 Delta": chg2,
            "Drift Status": drift_badge,
        })

    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)

    st.markdown("### Spotlight: The Revision Story (CLM-001 - Coimbatore Immunization)")
    st.markdown(
        """
        - **Provisional Data (`release_1.csv`)**: Full child immunization coverage in Coimbatore increased from 74.2% to 83.8% (+9.6%), supporting the illustrative claim of an 8.5% gain.
        - **Audited Reconciled Data (`release_2.csv`)**: Routine auditing adjusted the 2022 number to 78.9% (+3.4% net gain), causing the evaluated verdict to shift to **Unsupported**.
        - **Why this matters**: Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match.
        """
    )


# ==========================================
# TAB 3: CUSTOM SENTENCE PARSER
# ==========================================
with tab_parse:
    st.subheader("✍️ Free-Text Claim Parser (Deterministic Regex)")
    st.markdown(
        "Test unstructured natural language statements. Converts sentences into structured parameters "
        "without requiring paid LLM APIs or network connection."
    )

    default_sentence = "Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022"
    user_sentence = st.text_input("Enter a public health assertion sentence:", value=default_sentence)

    if st.button("Parse & Test Claim"):
        parsed = parse_claim_sentence(user_sentence, claim_id=f"CUSTOM-{len(st.session_state.custom_claims) + 1:03d}")
        if parsed:
            st.success("Successfully parsed statement into structured format!")
            st.json(parsed)

            col1, col2 = st.columns(2)
            with col1:
                res_r1 = evaluate_claim(df_release_1, parsed, "release_1.csv")
                st.markdown(f"**Release 1 Verdict:** `{res_r1['verdict']}`")
                st.caption(res_r1["reason"])

            with col2:
                res_r2 = evaluate_claim(df_release_2, parsed, "release_2.csv")
                st.markdown(f"**Release 2 Verdict:** `{res_r2['verdict']}`")
                st.caption(res_r2["reason"])

            if st.button("➕ Add This Claim to Active Dashboard"):
                st.session_state.custom_claims.append(parsed)
                st.rerun()
        else:
            st.error("Could not parse sentence into standard health indicator patterns.")


# ==========================================
# TAB 4: RAW DATA EXPLORER
# ==========================================
with tab_data:
    st.subheader("📂 Official Dataset Releases Explorer")
    st.markdown("Inspect official underlying data tables to verify numbers independently:")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("#### `release_1.csv` (Provisional - Dec 2022)")
        st.dataframe(df_release_1, use_container_width=True)

    with col_d2:
        st.markdown("#### `release_2.csv` (Audited Reconciled - Aug 2023)")
        st.dataframe(df_release_2, use_container_width=True)


# ==========================================
# TAB 5: REVIEWER AUDIT TRAIL
# ==========================================
with tab_audit:
    st.subheader("📋 In-Session Published Alerts & Audit Log")
    st.markdown("All human approvals/rejections recorded during this verification session:")

    if st.session_state.audit_trail:
        audit_df = pd.DataFrame(st.session_state.audit_trail)
        st.dataframe(audit_df, use_container_width=True, hide_index=True)

        # Export audit trail as CSV or JSON
        csv_data = audit_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Audit Trail (CSV)",
            data=csv_data,
            file_name="claim_watchdog_audit_trail.csv",
            mime="text/csv",
        )
    else:
        st.info("No claims have been reviewed yet in this session. Go to 'Claim Verification' tab and click Approve or Reject.")
