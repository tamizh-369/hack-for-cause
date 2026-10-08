"""Unit tests for src/load.py (Data Loading & Quality Checks for Tamil Nadu)."""

from pathlib import Path
import pandas as pd
import pytest

from src.load import (
    load_release,
    normalize_district_name,
    validate_data_quality,
)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def test_district_normalization():
    """Verify alias mapping and whitespace/casing normalization for Tamil Nadu."""
    assert normalize_district_name("kovai") == "Coimbatore"
    assert normalize_district_name("Coimbatore") == "Coimbatore"
    assert normalize_district_name("  MADURAI  ") == "Madurai"
    assert normalize_district_name("kancheepuram") == "Kanchipuram"
    assert normalize_district_name("trichy") == "Tiruchirappalli"
    assert normalize_district_name("nellai") == "Tirunelveli"


def test_load_releases_exist_and_valid():
    """Verify raw release files load cleanly with expected columns."""
    df1 = load_release(RAW_DATA_DIR / "release_1.csv")
    df2 = load_release(RAW_DATA_DIR / "release_2.csv")

    assert not df1.empty
    assert not df2.empty
    assert "district" in df1.columns
    assert "period" in df1.columns
    assert "full_immunization_coverage" in df1.columns
    assert "institutional_delivery_rate" in df1.columns
    assert "anc_first_trimester_rate" in df1.columns


def test_validate_data_quality_valid():
    """Test data quality validation passes for clean data (Coimbatore immunization)."""
    df1 = load_release(RAW_DATA_DIR / "release_1.csv")
    valid, err = validate_data_quality(
        df=df1,
        district="Coimbatore",
        indicator="full_immunization_coverage",
        period_from="2021",
        period_to="2022",
    )
    assert valid is True
    assert err is None


def test_validate_data_quality_missing_district():
    """Test quality check catches non-existent district."""
    df1 = load_release(RAW_DATA_DIR / "release_1.csv")
    valid, err = validate_data_quality(
        df=df1,
        district="NonExistentDistrict",
        indicator="full_immunization_coverage",
        period_from="2021",
        period_to="2022",
    )
    assert valid is False
    assert "not found" in err.lower()


def test_validate_data_quality_missing_value():
    """Test quality check detects missing/NaN value in Salem ANC data."""
    df1 = load_release(RAW_DATA_DIR / "release_1.csv")
    valid, err = validate_data_quality(
        df=df1,
        district="Salem",
        indicator="anc_first_trimester_rate",
        period_from="2021",
        period_to="2022",
    )
    assert valid is False
    assert "missing or null value" in err.lower()


def test_validate_data_quality_out_of_range():
    """Test quality check catches implausible percentage values (> 100 or < 0)."""
    bad_df = pd.DataFrame({
        "district": ["Coimbatore", "Coimbatore"],
        "period": ["2021", "2022"],
        "full_immunization_coverage": [125.0, 75.0],  # 125% is out of bounds
    })
    valid, err = validate_data_quality(
        df=bad_df,
        district="Coimbatore",
        indicator="full_immunization_coverage",
        period_from="2021",
        period_to="2022",
    )
    assert valid is False
    assert "outside plausible range" in err.lower()
