"""
Deterministic routing engine for FNOL claims.
All routing decisions are implemented in Python — Gemini is NOT involved.

Routing Priority:
    1. Manual Review        – Any mandatory field is missing
    2. Investigation Flag   – Fraud keywords in incident description
    3. Specialist Queue     – Claim type is "injury"
    4. Fast-track           – Estimated damage < ₹25,000
    5. Standard Processing  – All other cases
"""

import logging
from typing import Optional

from app.config import FAST_TRACK_DAMAGE_THRESHOLD, FRAUD_KEYWORDS
from app.models import ExtractedFields

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Route Constants
# ─────────────────────────────────────────────
ROUTE_MANUAL_REVIEW = "Manual Review"
ROUTE_INVESTIGATION_FLAG = "Investigation Flag"
ROUTE_SPECIALIST_QUEUE = "Specialist Queue"
ROUTE_FAST_TRACK = "Fast-track"
ROUTE_STANDARD = "Standard Processing"


def determine_route(
    fields: ExtractedFields,
    missing_fields: list[str],
) -> str:
    """
    Apply deterministic business rules to determine the processing route.

    Rules are evaluated in strict priority order. The first matching rule wins.

    Args:
        fields: Normalized extracted FNOL fields.
        missing_fields: List of mandatory fields that are missing.

    Returns:
        One of the five route strings defined above.
    """

    # ── Priority 1: Missing mandatory fields ──────────────────────────
    if missing_fields:
        logger.info(f"Route: {ROUTE_MANUAL_REVIEW} (missing fields: {missing_fields})")
        return ROUTE_MANUAL_REVIEW

    # ── Priority 2: Fraud keywords in description ─────────────────────
    if _contains_fraud_keywords(fields.incidentDescription):
        logger.info(f"Route: {ROUTE_INVESTIGATION_FLAG} (fraud keywords detected)")
        return ROUTE_INVESTIGATION_FLAG

    # ── Priority 3: Injury claim type ────────────────────────────────
    if _is_injury_claim(fields.claimType):
        logger.info(f"Route: {ROUTE_SPECIALIST_QUEUE} (claim type = injury)")
        return ROUTE_SPECIALIST_QUEUE

    # ── Priority 4: Low damage fast-track ────────────────────────────
    if _qualifies_for_fast_track(fields.estimatedDamage):
        logger.info(
            f"Route: {ROUTE_FAST_TRACK} "
            f"(damage {fields.estimatedDamage} < {FAST_TRACK_DAMAGE_THRESHOLD})"
        )
        return ROUTE_FAST_TRACK

    # ── Priority 5: Default ──────────────────────────────────────────
    logger.info(f"Route: {ROUTE_STANDARD}")
    return ROUTE_STANDARD


def _contains_fraud_keywords(description: Optional[str]) -> bool:
    """
    Check if the incident description contains any fraud-related keywords.
    Matching is case-insensitive.
    """
    if not description:
        return False

    description_lower = description.lower()
    for keyword in FRAUD_KEYWORDS:
        if keyword.lower() in description_lower:
            logger.debug(f"Fraud keyword detected: '{keyword}'")
            return True

    return False


def _is_injury_claim(claim_type: Optional[str]) -> bool:
    """
    Check if the claim type indicates an injury.
    Matching is case-insensitive.
    """
    if not claim_type:
        return False

    return "injury" in claim_type.lower()


def _qualifies_for_fast_track(estimated_damage: Optional[float]) -> bool:
    """
    Check if the estimated damage is below the fast-track threshold.
    Returns False if the damage value is None or non-numeric.
    """
    if estimated_damage is None:
        return False

    try:
        return float(estimated_damage) < FAST_TRACK_DAMAGE_THRESHOLD
    except (TypeError, ValueError):
        return False
