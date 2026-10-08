"""Indicator mapping and data slicing module for Public Health Claim Watchdog.

Connects claims (defined by indicator, district, and time period) to the
underlying dataset schema and extracts the precise data slice.
"""

from typing import Any, Dict, Optional, Tuple
import pandas as pd
from src.load import normalize_district_name

# Registry of supported indicators, columns, units, and descriptions
INDICATOR_REGISTRY: Dict[str, Dict[str, str]] = {
    "full_immunization_coverage": {
        "column": "full_immunization_coverage",
        "label": "Full Child Immunization Coverage (12-23 months)",
        "unit": "%",
        "description": "Percentage of children 12-23 months fully immunized against vaccine-preventable diseases.",
    },
    "institutional_delivery_rate": {
        "column": "institutional_delivery_rate",
        "label": "Institutional Deliveries Rate",
        "unit": "%",
        "description": "Percentage of total deliveries conducted in recognized healthcare facilities.",
    },
    "anc_first_trimester_rate": {
        "column": "anc_first_trimester_rate",
        "label": "Antenatal Care 1st Trimester Registration",
        "unit": "%",
        "description": "Percentage of pregnant women who registered for antenatal care during the first trimester.",
    },
}

# Alias synonyms for indicators if free text or alternative naming is encountered
INDICATOR_ALIASES: Dict[str, str] = {
    "immunization": "full_immunization_coverage",
    "immunisation": "full_immunization_coverage",
    "child_immunization": "full_immunization_coverage",
    "full_immunization": "full_immunization_coverage",
    "delivery": "institutional_delivery_rate",
    "institutional_delivery": "institutional_delivery_rate",
    "hospital_births": "institutional_delivery_rate",
    "anc": "anc_first_trimester_rate",
    "anc_registration": "anc_first_trimester_rate",
    "early_anc": "anc_first_trimester_rate",
}


def resolve_indicator(indicator_key: str) -> Optional[str]:
    """Resolve an indicator key or alias to its standardized canonical column name."""
    if not indicator_key:
        return None
    cleaned = indicator_key.strip().lower()
    if cleaned in INDICATOR_REGISTRY:
        return cleaned
    return INDICATOR_ALIASES.get(cleaned, None)


def get_indicator_metadata(indicator_key: str) -> Optional[Dict[str, str]]:
    """Retrieve metadata (label, unit, description) for an indicator."""
    canonical = resolve_indicator(indicator_key)
    return INDICATOR_REGISTRY.get(canonical) if canonical else None


def slice_claim_data(
    df: pd.DataFrame,
    claim: Dict[str, Any],
) -> Tuple[Optional[float], Optional[float], Dict[str, Any], Optional[str]]:
    """Extract baseline and comparison period values for a specific claim.

    Returns:
        (old_val, new_val, filter_metadata, error_message)
    """
    district_raw = claim.get("district", "")
    district = normalize_district_name(district_raw)
    indicator_raw = claim.get("indicator", "")
    indicator = resolve_indicator(indicator_raw)
    period_from = str(claim.get("period_from", "")).strip()
    period_to = str(claim.get("period_to", "")).strip()

    filter_info = {
        "district_input": district_raw,
        "district_normalized": district,
        "indicator_input": indicator_raw,
        "indicator_canonical": indicator,
        "period_from": period_from,
        "period_to": period_to,
    }

    if not indicator:
        return (
            None,
            None,
            filter_info,
            f"Ambiguous mapping: Indicator '{indicator_raw}' is not recognized in the indicator registry.",
        )

    district_rows = df[df["district"] == district]
    if district_rows.empty:
        return (
            None,
            None,
            filter_info,
            f"District mapping failed: District '{district}' not present in dataset.",
        )

    row_from = district_rows[district_rows["period"] == period_from]
    row_to = district_rows[district_rows["period"] == period_to]

    if row_from.empty:
        return (
            None,
            None,
            filter_info,
            f"Period mapping failed: Baseline period '{period_from}' not found for '{district}'.",
        )

    if row_to.empty:
        return (
            None,
            None,
            filter_info,
            f"Period mapping failed: End period '{period_to}' not found for '{district}'.",
        )

    old_val_raw = row_from[indicator].values[0]
    new_val_raw = row_to[indicator].values[0]

    if pd.isna(old_val_raw) or pd.isna(new_val_raw):
        return (
            None,
            None,
            filter_info,
            f"Missing indicator data for '{indicator}' in {district} ({period_from} or {period_to}).",
        )

    try:
        old_val = float(old_val_raw)
        new_val = float(new_val_raw)
    except (ValueError, TypeError):
        return (
            None,
            None,
            filter_info,
            f"Non-numeric indicator values encountered for '{indicator}' in {district}.",
        )

    return old_val, new_val, filter_info, None
