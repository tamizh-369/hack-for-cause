"""Verdict computation and drift detection module for Public Health Claim Watchdog.

Applies deterministic, explainable rules to evaluate health claims against official
releases and produces verifiable evidence tables and drift alerts.
"""

from typing import Any, Dict, Optional, Tuple
import pandas as pd

from src.load import normalize_district_name, validate_data_quality
from src.mapping import resolve_indicator, slice_claim_data


def evaluate_claim(
    df: pd.DataFrame,
    claim: Dict[str, Any],
    release_filename: str = "dataset_release.csv",
) -> Dict[str, Any]:
    """Evaluate a single claim against a loaded dataset release.

    Verdict Rules (Build Plan Section 4):
    - 'Needs review': Quality check failed, district not found, or ambiguous mapping.
    - 'Supported': Direction matches and magnitude is within tolerance.
    - 'Unsupported': Direction or magnitude no longer matches, and quality checks passed.

    Returns full evidence object for transparent auditability.
    """
    claim_id = claim.get("id", "UNKNOWN")
    indicator_raw = claim.get("indicator", "")
    indicator = resolve_indicator(indicator_raw)
    district_raw = claim.get("district", "")
    district = normalize_district_name(district_raw)
    period_from = str(claim.get("period_from", "")).strip()
    period_to = str(claim.get("period_to", "")).strip()
    direction = str(claim.get("direction", "")).strip().lower()
    claimed_magnitude = claim.get("magnitude", None)
    tolerance = claim.get("tolerance", 0.0)

    evidence: Dict[str, Any] = {
        "claim_id": claim_id,
        "file_name": release_filename,
        "district": district,
        "indicator": indicator or indicator_raw,
        "period_from": period_from,
        "period_to": period_to,
        "old_value": None,
        "new_value": None,
        "computed_change": None,
        "claimed_direction": direction,
        "claimed_magnitude": claimed_magnitude,
        "tolerance": tolerance,
        "direction_matched": False,
        "magnitude_matched": False,
    }

    # Step 1: Pre-verdict Data Quality Checks
    if not indicator:
        return {
            "claim_id": claim_id,
            "verdict": "Needs review",
            "reason": f"Ambiguous indicator mapping: '{indicator_raw}' is not recognized in dataset schema.",
            "evidence": evidence,
            "quality_passed": False,
            "quality_error": f"Unknown indicator '{indicator_raw}'",
        }

    quality_passed, quality_error = validate_data_quality(
        df=df,
        district=district,
        indicator=indicator,
        period_from=period_from,
        period_to=period_to,
    )

    if not quality_passed:
        # Mandatory rule: If a quality check fails, verdict is Needs review, NEVER Unsupported
        return {
            "claim_id": claim_id,
            "verdict": "Needs review",
            "reason": quality_error or "Data-quality verification failed.",
            "evidence": evidence,
            "quality_passed": False,
            "quality_error": quality_error,
        }

    # Step 2: Slice claim data
    old_val, new_val, _, slice_err = slice_claim_data(df, claim)
    if slice_err or old_val is None or new_val is None:
        return {
            "claim_id": claim_id,
            "verdict": "Needs review",
            "reason": slice_err or "Failed to extract period values from release data.",
            "evidence": evidence,
            "quality_passed": False,
            "quality_error": slice_err,
        }

    # Step 3: Compute change
    computed_change = round(new_val - old_val, 2)
    evidence["old_value"] = round(old_val, 2)
    evidence["new_value"] = round(new_val, 2)
    evidence["computed_change"] = computed_change

    # Step 4: Direction evaluation
    # "up" implies computed_change > 0, "down" implies computed_change < 0
    if direction == "up":
        direction_matched = computed_change > 0
    elif direction == "down":
        direction_matched = computed_change < 0
    elif direction == "stable" or direction == "same":
        direction_matched = abs(computed_change) <= (tolerance or 0.5)
    else:
        direction_matched = False

    evidence["direction_matched"] = direction_matched

    # Step 5: Magnitude evaluation (if magnitude is specified in claim)
    if claimed_magnitude is not None:
        target_mag = float(claimed_magnitude)
        tol = float(tolerance or 0.0)

        # For "up", change should be within target_mag +- tol or at least target_mag - tol
        # Build plan: "Direction matches and magnitude is within tolerance"
        abs_change = abs(computed_change)
        magnitude_matched = abs(abs_change - target_mag) <= tol or (
            direction == "up" and computed_change >= (target_mag - tol)
        )
        evidence["magnitude_matched"] = magnitude_matched
    else:
        # If no explicit magnitude claimed, matching direction is sufficient
        magnitude_matched = True
        evidence["magnitude_matched"] = True

    # Step 6: Final Verdict
    if direction_matched and magnitude_matched:
        verdict = "Supported"
        reason = (
            f"Official release data confirms the claim: {indicator} in {district} "
            f"changed from {evidence['old_value']}% in {period_from} to "
            f"{evidence['new_value']}% in {period_to} (change: {computed_change:+g}%), "
            f"matching the claimed '{direction}' trajectory within tolerance."
        )
    else:
        verdict = "Unsupported"
        reasons_list = []
        if not direction_matched:
            reasons_list.append(
                f"direction mismatch (claimed '{direction}', observed change was {computed_change:+g}%)"
            )
        if not magnitude_matched:
            reasons_list.append(
                f"magnitude mismatch (claimed ~{claimed_magnitude}% ± {tolerance}%, observed change was {computed_change:+g}%)"
            )
        reason = (
            f"Official release data does not support the claim: {indicator} in {district} "
            f"changed from {evidence['old_value']}% in {period_from} to {evidence['new_value']}% "
            f"in {period_to} ({', '.join(reasons_list)})."
        )

    return {
        "claim_id": claim_id,
        "verdict": verdict,
        "reason": reason,
        "evidence": evidence,
        "quality_passed": True,
        "quality_error": None,
    }


def detect_drift(
    eval_release_1: Dict[str, Any],
    eval_release_2: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare evaluation results across Release 1 and Release 2 to detect status drift.

    A drift alert is triggered when an official data revision shifts the verdict
    (e.g., from Supported in Release 1 to Unsupported in Release 2).
    """
    v1 = eval_release_1.get("verdict")
    v2 = eval_release_2.get("verdict")
    ev1 = eval_release_1.get("evidence", {})
    ev2 = eval_release_2.get("evidence", {})

    has_drift = (v1 != v2)
    is_degraded = (v1 == "Supported" and v2 in ["Unsupported", "Needs review"])

    summary = ""
    if has_drift:
        if is_degraded:
            summary = (
                f"⚠️ REVISION DRIFT DETECTED: Claim was '{v1}' under Release 1 "
                f"(observed change: {ev1.get('computed_change'):+g}%), but under audited Release 2 "
                f"the verdict degraded to '{v2}' (observed change: {ev2.get('computed_change'):+g}%)."
            )
        else:
            summary = (
                f"Notice: Claim status shifted from '{v1}' in Release 1 to '{v2}' in Release 2."
            )
    else:
        summary = f"Consistent: Claim status remained '{v1}' across both data releases."

    return {
        "claim_id": eval_release_1.get("claim_id"),
        "has_drift": has_drift,
        "is_degraded": is_degraded,
        "verdict_release_1": v1,
        "verdict_release_2": v2,
        "evidence_release_1": ev1,
        "evidence_release_2": ev2,
        "drift_summary": summary,
    }
