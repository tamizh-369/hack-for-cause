"""Data loader and quality verification module for Public Health Claim Watchdog.

Handles reading dataset releases, normalizing district names, and executing
rigorous data-quality checks prior to any verdict evaluation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

# Standard district name normalization alias mapping (Tamil Nadu focus)
DISTRICT_ALIASES: Dict[str, str] = {
    "coimbatore": "Coimbatore",
    "kovai": "Coimbatore",
    "madurai": "Madurai",
    "salem": "Salem",
    "chennai": "Chennai",
    "madras": "Chennai",
    "trichy": "Tiruchirappalli",
    "tiruchirappalli": "Tiruchirappalli",
    "tiruchy": "Tiruchirappalli",
    "kancheepuram": "Kanchipuram",
    "kanchipuram": "Kanchipuram",
    "tirunelveli": "Tirunelveli",
    "nellai": "Tirunelveli",
    "vellore": "Vellore",
    "thanjavur": "Thanjavur",
}

REQUIRED_BASE_COLUMNS = ["district", "period"]

# Plausible range constraints for indicator values
INDICATOR_RANGES: Dict[str, Tuple[float, float]] = {
    "full_immunization_coverage": (0.0, 100.0),
    "institutional_delivery_rate": (0.0, 100.0),
    "anc_first_trimester_rate": (0.0, 100.0),
}


def normalize_district_name(district: str) -> str:
    """Normalize district name casing, whitespace, and known historical aliases."""
    if not district or not isinstance(district, str):
        return ""
    cleaned = district.strip().lower()
    return DISTRICT_ALIASES.get(cleaned, district.strip().title())


def load_release(filepath: str | Path) -> pd.DataFrame:
    """Load a raw release CSV file and perform baseline schema cleaning."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Release file not found at: {path}")

    df = pd.read_csv(path)
    if "district" in df.columns:
        df["district"] = df["district"].astype(str).apply(normalize_district_name)
    if "period" in df.columns:
        df["period"] = df["period"].astype(str).str.strip()

    return df


def validate_data_quality(
    df: pd.DataFrame,
    district: str,
    indicator: str,
    period_from: str,
    period_to: str,
) -> Tuple[bool, Optional[str]]:
    """Run data quality checks before any verdict computation.

    Checks:
    1. Required base and indicator columns are present.
    2. District name matches (normalized).
    3. Both requested periods (from and to) exist for the district.
    4. No missing/NaN/null values in the indicator column.
    5. Values lie within a plausible domain range (e.g. 0% - 100%).

    Rule: If any check fails, the claim verdict MUST be 'Needs review',
          never 'Unsupported'.
    """
    normalized_district = normalize_district_name(district)

    # 1. Required columns present
    if "district" not in df.columns or "period" not in df.columns:
        return False, "Data quality check failed: Base columns ('district', 'period') missing."

    if indicator not in df.columns:
        return False, f"Data quality check failed: Indicator column '{indicator}' not found in release schema."

    # 2. District exists in release
    districts_present = df["district"].unique()
    if normalized_district not in districts_present:
        return (
            False,
            f"Data quality check failed: District '{district}' (normalized '{normalized_district}') not found in dataset.",
        )

    # 3. Check requested periods exist
    district_df = df[df["district"] == normalized_district]
    periods_present = set(district_df["period"].astype(str).unique())

    if str(period_from) not in periods_present:
        return (
            False,
            f"Data quality check failed: Baseline period '{period_from}' missing for district '{normalized_district}'.",
        )

    if str(period_to) not in periods_present:
        return (
            False,
            f"Data quality check failed: End period '{period_to}' missing for district '{normalized_district}'.",
        )

    # 4. Check missing values for both periods
    row_from = district_df[district_df["period"] == str(period_from)]
    row_to = district_df[district_df["period"] == str(period_to)]

    val_from = row_from[indicator].values[0] if not row_from.empty else None
    val_to = row_to[indicator].values[0] if not row_to.empty else None

    if pd.isna(val_from):
        return (
            False,
            f"Data quality check failed: Missing or null value for '{indicator}' in district '{normalized_district}' for period {period_from}.",
        )

    if pd.isna(val_to):
        return (
            False,
            f"Data quality check failed: Missing or null value for '{indicator}' in district '{normalized_district}' for period {period_to}.",
        )

    # 5. Plausible range verification
    min_val, max_val = INDICATOR_RANGES.get(indicator, (0.0, float("inf")))
    try:
        f_from = float(val_from)
        f_to = float(val_to)
    except (ValueError, TypeError):
        return False, f"Data quality check failed: Non-numeric values found in indicator column '{indicator}'."

    if not (min_val <= f_from <= max_val):
        return (
            False,
            f"Data quality check failed: Value {f_from} in {period_from} outside plausible range [{min_val}, {max_val}].",
        )

    if not (min_val <= f_to <= max_val):
        return (
            False,
            f"Data quality check failed: Value {f_to} in {period_to} outside plausible range [{min_val}, {max_val}].",
        )

    return True, None
