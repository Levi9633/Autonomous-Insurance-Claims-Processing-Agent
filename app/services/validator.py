"""
Validation service for extracted FNOL claim fields.
Checks mandatory fields and applies data normalization before routing.
"""

import logging
import re
from typing import Any, Optional, Union

from app.config import MANDATORY_FIELDS, NULL_EQUIVALENTS
from app.models import ExtractedFields

logger = logging.getLogger(__name__)

# Human-readable display names for mandatory fields
FIELD_DISPLAY_NAMES: dict[str, str] = {
    "policyNumber": "Policy Number",
    "policyholderName": "Policyholder Name",
    "incidentDate": "Incident Date",
    "incidentTime": "Incident Time",
    "incidentLocation": "Incident Location",
    "incidentDescription": "Incident Description",
    "claimant": "Claimant",
    "contactDetails": "Contact Details",
    "assetType": "Asset Type",
    "assetId": "Asset ID",
    "estimatedDamage": "Estimated Damage",
    "claimType": "Claim Type",
    "attachments": "Attachments",
    "initialEstimate": "Initial Estimate",
}


def validate_and_normalize(fields: ExtractedFields) -> tuple[ExtractedFields, list[str]]:
    """
    Normalize field values and identify missing mandatory fields.

    Normalization steps applied:
    - Trim whitespace from all string values
    - Treat null-equivalent strings as missing (None)
    - Strip currency symbols and convert monetary values to float

    Args:
        fields: Raw ExtractedFields model from Gemini extraction.

    Returns:
        Tuple of:
        - Normalized ExtractedFields model
        - List of human-readable missing mandatory field names
    """
    # Convert to dict for mutation
    data = fields.model_dump()

    # Step 1: Normalize all string values
    for key, value in data.items():
        data[key] = _normalize_value(key, value)

    # Step 2: Normalize monetary fields specifically
    data["estimatedDamage"] = _normalize_monetary(data.get("estimatedDamage"))
    data["initialEstimate"] = _normalize_monetary(data.get("initialEstimate"))

    # Step 3: Rebuild normalized model
    normalized_fields = ExtractedFields(**data)

    # Step 4: Identify missing mandatory fields
    missing_fields = _find_missing_fields(data)

    if missing_fields:
        logger.info(f"Missing mandatory fields detected: {missing_fields}")
    else:
        logger.info("All mandatory fields are present.")

    return normalized_fields, missing_fields


def _normalize_value(key: str, value: Any) -> Any:
    """
    Normalize a single field value.

    - Strings: strip whitespace, replace null-equivalents with None
    - Lists: process each element
    - Numeric fields: leave as-is (handled separately)
    - None: return None
    """
    # Skip monetary fields – handled separately
    if key in ("estimatedDamage", "initialEstimate"):
        return value

    if value is None:
        return None

    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lower() in NULL_EQUIVALENTS:
            return None
        return stripped if stripped else None

    if isinstance(value, list):
        return [_normalize_value(key, item) for item in value]

    return value


def _normalize_monetary(value: Optional[Union[str, float, int]]) -> Optional[float]:
    """
    Normalize a monetary value to a float.

    Handles:
    - Numeric types (int/float): return as float
    - Strings like "₹18,000" or "18,000 INR" → 18000.0
    - Null-equivalent strings → None
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        stripped = value.strip()

        if stripped.lower() in NULL_EQUIVALENTS:
            return None

        # Remove currency symbols, commas, spaces, and letters (INR, Rs.)
        cleaned = re.sub(r"[₹,\s]", "", stripped)
        cleaned = re.sub(r"(?i)(inr|rs\.?)", "", cleaned).strip()

        if not cleaned:
            return None

        try:
            return float(cleaned)
        except ValueError:
            logger.warning(
                f"Could not convert monetary value '{value}' to float. "
                "Treating as missing."
            )
            return None

    return None


def _find_missing_fields(data: dict) -> list[str]:
    """
    Check all mandatory fields for missing or null values.

    Args:
        data: Normalized field data as a dictionary.

    Returns:
        List of human-readable field names that are missing.
    """
    missing: list[str] = []

    for field_key in MANDATORY_FIELDS:
        value = data.get(field_key)

        if value is None:
            display_name = FIELD_DISPLAY_NAMES.get(field_key, field_key)
            missing.append(display_name)

    return missing
