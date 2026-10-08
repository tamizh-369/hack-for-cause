"""Unit tests for src/check.py (Verdict Logic, Evidence & Drift Detection)."""

import json
from pathlib import Path
import pytest

from src.check import detect_drift, evaluate_claim
from src.load import load_release

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLAIMS_FILE = BASE_DIR / "data" / "claims.json"


@pytest.fixture
def claims():
    with open(CLAIMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def release_1():
    return load_release(RAW_DATA_DIR / "release_1.csv")


@pytest.fixture
def release_2():
    return load_release(RAW_DATA_DIR / "release_2.csv")


def test_verdict_supported(claims, release_1):
    """Test claim CLM-001 is Supported under Release 1 provisional data."""
    claim = claims[0]  # Pune immunization +8.5%
    result = evaluate_claim(release_1, claim, release_filename="release_1.csv")

    assert result["verdict"] == "Supported"
    assert result["quality_passed"] is True
    ev = result["evidence"]
    assert ev["old_value"] == 72.4
    assert ev["new_value"] == 81.9
    assert ev["computed_change"] == 9.5
    assert ev["direction_matched"] is True
    assert ev["magnitude_matched"] is True


def test_verdict_unsupported_on_release_2(claims, release_2):
    """Test claim CLM-001 becomes Unsupported under Release 2 audited data."""
    claim = claims[0]  # Pune immunization
    result = evaluate_claim(release_2, claim, release_filename="release_2.csv")

    assert result["verdict"] == "Unsupported"
    assert result["quality_passed"] is True
    ev = result["evidence"]
    assert ev["old_value"] == 74.1
    assert ev["new_value"] == 77.3
    assert ev["computed_change"] == 3.2  # Revision showed only 3.2%, not 8.5%
    assert ev["magnitude_matched"] is False


def test_drift_detection(claims, release_1, release_2):
    """Test that revision drift is accurately detected between Release 1 and Release 2."""
    claim = claims[0]
    res_1 = evaluate_claim(release_1, claim, release_filename="release_1.csv")
    res_2 = evaluate_claim(release_2, claim, release_filename="release_2.csv")

    drift = detect_drift(res_1, res_2)
    assert drift["has_drift"] is True
    assert drift["is_degraded"] is True
    assert drift["verdict_release_1"] == "Supported"
    assert drift["verdict_release_2"] == "Unsupported"
    assert "REVISION DRIFT DETECTED" in drift["drift_summary"]


def test_verdict_consistently_supported(claims, release_1, release_2):
    """Test claim CLM-002 (Nagpur institutional delivery) is Supported on both releases."""
    claim = claims[1]
    res_1 = evaluate_claim(release_1, claim, release_filename="release_1.csv")
    res_2 = evaluate_claim(release_2, claim, release_filename="release_2.csv")

    assert res_1["verdict"] == "Supported"
    assert res_2["verdict"] == "Supported"

    drift = detect_drift(res_1, res_2)
    assert drift["has_drift"] is False
    assert drift["is_degraded"] is False


def test_verdict_needs_review_missing_data(claims, release_1):
    """Test claim CLM-003 yields 'Needs review' due to missing baseline ANC data."""
    claim = claims[2]  # Nashik ANC
    result = evaluate_claim(release_1, claim, release_filename="release_1.csv")

    assert result["verdict"] == "Needs review"
    assert result["quality_passed"] is False
    assert "missing or null value" in result["reason"].lower()


def test_evidence_structure_completeness(claims, release_1):
    """Verify that every verdict contains complete and transparent evidence fields."""
    claim = claims[0]
    result = evaluate_claim(release_1, claim, release_filename="release_1.csv")
    ev = result["evidence"]

    expected_keys = [
        "claim_id",
        "file_name",
        "district",
        "indicator",
        "period_from",
        "period_to",
        "old_value",
        "new_value",
        "computed_change",
        "claimed_direction",
        "claimed_magnitude",
        "tolerance",
        "direction_matched",
        "magnitude_matched",
    ]
    for key in expected_keys:
        assert key in ev, f"Missing evidence field: {key}"
