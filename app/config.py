"""
Configuration module for the Autonomous Insurance Claims Processing Agent.
Loads environment variables from .env file.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Gemini API Configuration
# ─────────────────────────────────────────────

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    logger.warning(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

# ─────────────────────────────────────────────
# Application Configuration
# ─────────────────────────────────────────────

APP_TITLE: str = "Autonomous Insurance Claims Processing Agent"
APP_VERSION: str = "1.0.0"
APP_DESCRIPTION: str = (
    "AI-powered FNOL document processor that extracts structured information "
    "and applies deterministic routing rules."
)

# Upload directory
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt"}

# ─────────────────────────────────────────────
# Business Rule Thresholds
# ─────────────────────────────────────────────

# Damage threshold for fast-track routing (in INR)
FAST_TRACK_DAMAGE_THRESHOLD: float = 25_000.0

# Fraud detection keywords (case-insensitive)
FRAUD_KEYWORDS: list[str] = ["fraud", "staged", "inconsistent"]

# Mandatory fields required for valid claim processing
MANDATORY_FIELDS: list[str] = [
    "policyNumber",
    "policyholderName",
    "incidentDate",
    "incidentTime",
    "incidentLocation",
    "incidentDescription",
    "claimant",
    "contactDetails",
    "assetType",
    "assetId",
    "estimatedDamage",
    "claimType",
    "attachments",
    "initialEstimate",
]

# Null-equivalent values to treat as missing
NULL_EQUIVALENTS: set[str] = {
    "",
    "null",
    "none",
    "n/a",
    "na",
    "unknown",
    "-",
    "not mentioned",
    "not available",
    "not provided",
}
