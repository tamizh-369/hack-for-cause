"""Sentence to structured claim rule-based parser.

Deterministic regex parser mapping natural language health statements
into structured claim dictionaries without relying on external paid APIs.
"""

import re
from typing import Any, Dict, Optional

from src.load import normalize_district_name
from src.mapping import resolve_indicator

DIRECTION_KEYWORDS = {
    "rose": "up",
    "risen": "up",
    "increased": "up",
    "climbed": "up",
    "grew": "up",
    "surged": "up",
    "improved": "up",
    "fell": "down",
    "dropped": "down",
    "decreased": "down",
    "declined": "down",
    "reduced": "down",
}


def parse_claim_sentence(sentence: str, claim_id: str = "CUSTOM-001") -> Optional[Dict[str, Any]]:
    """Parse a free-text health statement into a structured claim object."""
    if not sentence or not isinstance(sentence, str):
        return None

    text = sentence.strip()

    # 1. Detect Direction
    direction = "up"
    for word, dir_val in DIRECTION_KEYWORDS.items():
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            direction = dir_val
            break

    # 2. Detect Magnitude (percentage)
    magnitude: Optional[float] = None
    mag_match = re.search(r"(\d+(\.\d+)?)\s*%", text)
    if mag_match:
        try:
            magnitude = float(mag_match.group(1))
        except ValueError:
            magnitude = None

    # 3. Detect Period range (e.g. "between 2021 and 2022" or "from 2021 to 2022")
    period_from = "2021"
    period_to = "2022"
    period_match = re.search(
        r"(?:between|from)\s+(\d{4})\s+(?:and|to)\s+(\d{4})", text, re.IGNORECASE
    )
    if period_match:
        period_from = period_match.group(1)
        period_to = period_match.group(2)

    # 4. Detect District (known districts)
    known_districts = ["Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Amravati", "Solapur"]
    detected_district = "Pune"
    for dist in known_districts:
        if re.search(rf"\b{dist}\b", text, re.IGNORECASE):
            detected_district = dist
            break

    # 5. Detect Indicator
    indicator = "full_immunization_coverage"
    if re.search(r"immuniz|vaccin", text, re.IGNORECASE):
        indicator = "full_immunization_coverage"
    elif re.search(r"deliver|birth|hospital", text, re.IGNORECASE):
        indicator = "institutional_delivery_rate"
    elif re.search(r"anc|antenatal|trimester", text, re.IGNORECASE):
        indicator = "anc_first_trimester_rate"

    return {
        "id": claim_id,
        "text": text,
        "indicator": resolve_indicator(indicator) or indicator,
        "district": normalize_district_name(detected_district),
        "period_from": period_from,
        "period_to": period_to,
        "direction": direction,
        "magnitude": magnitude,
        "tolerance": 1.0,
        "speaker": "Custom User Input",
        "claim_date": "2026-10-08",
        "context": "Parsed via deterministic regex parser.",
    }
