"""
Pydantic models for the Autonomous Insurance Claims Processing Agent.
Defines strongly-typed models for extracted fields and API responses.
"""

from typing import Optional, Union
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Extracted Fields Model
# ─────────────────────────────────────────────

class ExtractedFields(BaseModel):
    """
    Structured representation of all fields extracted from an FNOL document.
    All fields are Optional – Gemini returns null for unavailable values.
    """

    # Policy Information
    policyNumber: Optional[str] = Field(None, description="Insurance policy number")
    claimNumber: Optional[str] = Field(None, description="Claim reference number")
    policyholderName: Optional[str] = Field(None, description="Full name of the policyholder")
    effectiveDates: Optional[str] = Field(None, description="Policy effective date range")

    # Contact / Address
    address: Optional[str] = Field(None, description="Policyholder's street address")
    city: Optional[str] = Field(None, description="City of residence")
    pinCode: Optional[str] = Field(None, description="Postal / PIN code")
    mobile: Optional[str] = Field(None, description="Mobile phone number")
    email: Optional[str] = Field(None, description="Email address")

    # Incident Information
    incidentDate: Optional[str] = Field(None, description="Date of the incident")
    incidentTime: Optional[str] = Field(None, description="Time of the incident")
    incidentLocation: Optional[str] = Field(None, description="Location where the incident occurred")
    incidentDescription: Optional[str] = Field(None, description="Detailed description of the incident")

    # Involved Parties
    claimant: Optional[str] = Field(None, description="Name of the claimant")
    thirdParties: Optional[str] = Field(None, description="Third party details if applicable")
    contactDetails: Optional[str] = Field(None, description="Contact information for the claimant")

    # Asset Details
    assetType: Optional[str] = Field(None, description="Type of insured asset")
    assetId: Optional[str] = Field(None, description="Asset identifier (e.g., vehicle registration number)")
    estimatedDamage: Optional[Union[float, str]] = Field(None, description="Estimated damage amount in INR")
    initialEstimate: Optional[Union[float, str]] = Field(None, description="Initial repair/loss estimate in INR")

    # Claim Classification
    claimType: Optional[str] = Field(None, description="Type of claim (e.g., Vehicle, Injury, Property)")
    attachments: Optional[str] = Field(None, description="List of attached supporting documents")

    # Declaration
    declaration: Optional[str] = Field(None, description="Declaration statement by claimant")
    declarationDate: Optional[str] = Field(None, description="Date of declaration")
    signature: Optional[str] = Field(None, description="Signature acknowledgement")


# ─────────────────────────────────────────────
# API Response Models
# ─────────────────────────────────────────────

class ClaimResponse(BaseModel):
    """
    Complete API response returned after processing an FNOL claim document.
    """

    extractedFields: ExtractedFields = Field(
        ..., description="All fields extracted from the document"
    )
    missingFields: list[str] = Field(
        default_factory=list,
        description="List of mandatory fields that are missing or empty",
    )
    recommendedRoute: str = Field(
        ...,
        description=(
            "Routing decision: Manual Review | Investigation Flag | "
            "Specialist Queue | Fast-track | Standard Processing"
        ),
    )
    reasoning: str = Field(
        ..., description="Human-readable explanation of the routing decision"
    )


class ErrorResponse(BaseModel):
    """
    Structured error response for invalid or unprocessable documents.
    """

    error: str = Field(..., description="Error message describing what went wrong")
    detail: Optional[str] = Field(None, description="Additional error detail if available")


class ValidationResponse(BaseModel):
    """
    Response returned when Pydantic model validation fails.
    """

    error: str = Field(default="Validation error")
    detail: list[dict] = Field(
        default_factory=list,
        description="List of validation errors from Pydantic",
    )
