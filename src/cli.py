"""Command-Line Interface (CLI) runner for Public Health Claim Watchdog.

Allows running complete verification pipeline, generating verdicts, evidence tables,
drift alerts, and bilingual explanations directly from the terminal with no UI required.
"""

import json
from pathlib import Path
import sys

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from src.check import detect_drift, evaluate_claim
from src.explain import explain_drift, explain_verdict
from src.load import load_release


def run_pipeline(lang: str = "en"):
    print("=" * 78)
    print(" 🏥 PUBLIC HEALTH CLAIM WATCHDOG - CORE CLI VERIFIER")
    print(" State Scope: Tamil Nadu (MoHFW HMIS Schema)")
    print(" Demo Notice: Evaluates illustrative claims on simulated data mirroring HMIS.")
    print("=" * 78)

    raw_dir = BASE_DIR / "data" / "raw"
    claims_path = BASE_DIR / "data" / "claims.json"

    rel1_file = raw_dir / "release_1.csv"
    rel2_file = raw_dir / "release_2.csv"

    print(f"[*] Loading Release 1: {rel1_file.name}")
    df_r1 = load_release(rel1_file)
    print(f"[*] Loading Release 2: {rel2_file.name}")
    df_r2 = load_release(rel2_file)

    print(f"[*] Loading Claims: {claims_path.name}")
    with open(claims_path, "r", encoding="utf-8") as f:
        claims = json.load(f)

    print(f"[*] Found {len(claims)} claims to verify.\n")

    for i, claim in enumerate(claims, 1):
        print("-" * 78)
        print(f"📌 [Claim {i}] {claim['id']}: \"{claim['text']}\"")
        print(f"   Target: {claim['district']} | {claim['indicator']} ({claim['period_from']} -> {claim['period_to']})")
        print("-" * 78)

        def fmt_pct(val):
            return f"{val:+g}%" if isinstance(val, (int, float)) else "N/A"

        def fmt_val(val):
            return f"{val}%" if isinstance(val, (int, float)) else "N/A"

        # Evaluate on Release 1
        res_r1 = evaluate_claim(df_r1, claim, release_filename=rel1_file.name)
        ev1 = res_r1["evidence"]
        print(f"  📊 Release 1 ({rel1_file.name}):")
        print(f"     Verdict: [{res_r1['verdict']}]")
        print(f"     Values : Baseline={fmt_val(ev1.get('old_value'))}, Final={fmt_val(ev1.get('new_value'))}, Delta={fmt_pct(ev1.get('computed_change'))}")

        # Evaluate on Release 2
        res_r2 = evaluate_claim(df_r2, claim, release_filename=rel2_file.name)
        ev2 = res_r2["evidence"]
        print(f"  📊 Release 2 ({rel2_file.name}):")
        print(f"     Verdict: [{res_r2['verdict']}]")
        print(f"     Values : Baseline={fmt_val(ev2.get('old_value'))}, Final={fmt_val(ev2.get('new_value'))}, Delta={fmt_pct(ev2.get('computed_change'))}")

        # Drift Check
        drift = detect_drift(res_r1, res_r2)
        if drift["has_drift"]:
            print(f"  🚨 DRIFT ALERT: {drift['drift_summary']}")
            if drift["is_degraded"]:
                print(f"     [!] CRITICAL: Status degraded from {res_r1['verdict']} to {res_r2['verdict']} upon official data audit!")
        else:
            print(f"  ✅ Status consistent across releases ({res_r1['verdict']})")

        print("\n  📝 Bilingual Explanation Preview:")
        explanation = explain_verdict(claim, res_r2 if drift["has_drift"] else res_r1, lang=lang)
        # Format preview indentation
        for line in explanation.split("\n"):
            print(f"     {line}")
        print()

    print("=" * 78)
    print(" ✅ Pipeline execution completed successfully.")
    print("=" * 78)


if __name__ == "__main__":
    lang_arg = sys.argv[1] if len(sys.argv) > 1 else "en"
    run_pipeline(lang=lang_arg)
