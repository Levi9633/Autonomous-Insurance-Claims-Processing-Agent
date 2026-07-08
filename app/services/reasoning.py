"""
Reasoning generation service.
Generates human-readable explanations for each routing decision.
All explanations are deterministic — generated from templates, not AI.
"""

import logging
from typing import Optional

from app.services.router import (
    ROUTE_FAST_TRACK,
    ROUTE_INVESTIGATION_FLAG,
    ROUTE_MANUAL_REVIEW,
    ROUTE_SPECIALIST_QUEUE,
    ROUTE_STANDARD,
)

logger = logging.getLogger(__name__)


def generate_reasoning(
    route: str,
    missing_fields: list[str],
    estimated_damage: Optional[float] = None,
    claim_type: Optional[str] = None,
) -> str:
    """
    Generate a clear, professional explanation for the routing decision.

    Args:
        route: The recommended processing route.
        missing_fields: List of missing mandatory field names.
        estimated_damage: Normalized damage amount (for fast-track explanation).
        claim_type: Extracted claim type (for specialist queue explanation).

    Returns:
        Human-readable reasoning string.
    """
    if route == ROUTE_MANUAL_REVIEW:
        return _manual_review_reason(missing_fields)

    if route == ROUTE_INVESTIGATION_FLAG:
        return (
            "The incident description contains suspicious keywords (e.g., 'fraud', 'staged', "
            "'inconsistent') that indicate potential fraud or reporting inconsistencies. "
            "This claim must be reviewed by the investigation team before any further processing."
        )

    if route == ROUTE_SPECIALIST_QUEUE:
        claim_label = f"'{claim_type}'" if claim_type else "Injury"
        return (
            f"The claim type is {claim_label}, which falls under medical or personal injury coverage. "
            "Injury-related claims require specialist handling by a dedicated claims team with "
            "appropriate medical and legal expertise."
        )

    if route == ROUTE_FAST_TRACK:
        rupee = "\u20b9"
        damage_str = (
            f"{rupee}{estimated_damage:,.0f}" if estimated_damage is not None else f"below {rupee}25,000"
        )
        return (
            f"The estimated damage ({damage_str}) is below the {rupee}25,000 fast-track threshold. "
            "All mandatory fields are present, no fraud indicators were detected, and the claim "
            "does not require specialist handling. This claim qualifies for accelerated processing."
        )

    if route == ROUTE_STANDARD:
        return (
            "This claim has passed all validation checks. All mandatory fields are complete, "
            "no fraud keywords were detected, the claim type does not require specialist review, "
            "and the damage amount exceeds the fast-track threshold. "
            "The claim will follow the standard claims processing workflow."
        )

    # Fallback for unexpected route values
    logger.warning(f"Unexpected route value: '{route}'. Using generic reasoning.")
    return f"The claim has been routed to '{route}' based on the applied business rules."


def _manual_review_reason(missing_fields: list[str]) -> str:
    """
    Generate detailed reasoning for manual review routing.

    Args:
        missing_fields: List of missing mandatory field names.

    Returns:
        Formatted reasoning string listing the missing fields.
    """
    if not missing_fields:
        return (
            "This claim has been flagged for manual review. "
            "Please verify all mandatory fields before continuing."
        )

    count = len(missing_fields)
    field_label = "field" if count == 1 else "fields"

    if count == 1:
        fields_str = f"'{missing_fields[0]}'"
    elif count == 2:
        fields_str = f"'{missing_fields[0]}' and '{missing_fields[1]}'"
    else:
        formatted = [f"'{f}'" for f in missing_fields[:-1]]
        fields_str = ", ".join(formatted) + f", and '{missing_fields[-1]}'"

    return (
        f"This claim is incomplete. The following mandatory {field_label} "
        f"{'is' if count == 1 else 'are'} missing or empty: {fields_str}. "
        "The claim cannot proceed to automated processing until all required "
        "information has been provided. A manual review agent will contact the "
        "policyholder to collect the missing details."
    )
