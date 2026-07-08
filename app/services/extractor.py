"""
AI extraction service using Google Gemini 2.5 Flash.
Responsible ONLY for structured field extraction from document text.
All routing and business logic is handled separately in Python.
"""

import json
import logging
import re
from pathlib import Path

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models import ExtractedFields

logger = logging.getLogger(__name__)

# Load extraction prompt template once at module level
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extraction_prompt.txt"
_PROMPT_TEMPLATE: str = _PROMPT_PATH.read_text(encoding="utf-8")


def extract_fields(document_text: str) -> ExtractedFields:
    """
    Send document text to Gemini 2.5 Flash for structured field extraction.

    Args:
        document_text: Raw text content extracted from the FNOL document.

    Returns:
        ExtractedFields Pydantic model populated with extracted values.

    Raises:
        RuntimeError: If the Gemini API call fails.
        ValueError: If Gemini returns invalid or unparseable JSON.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Please add your API key to the .env file."
        )

    # Build the full prompt with document text injected
    prompt = _PROMPT_TEMPLATE.replace("{document_text}", document_text)

    logger.info("Sending document to Gemini for structured extraction...")

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        raw_response = response.text
        logger.info("Gemini extraction completed successfully.")
        logger.debug(f"Raw Gemini response: {raw_response[:500]}...")

        # Parse and validate the JSON response
        extracted_data = _parse_gemini_response(raw_response)

        # Validate against Pydantic model
        extracted_fields = ExtractedFields(**extracted_data)
        logger.info("Pydantic validation of extracted fields succeeded.")

        return extracted_fields

    except (ImportError, ModuleNotFoundError) as e:
        logger.error(f"google-genai SDK not installed: {e}")
        raise RuntimeError(
            "The google-genai SDK is not installed. "
            "Run: pip install google-genai"
        ) from e
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise RuntimeError(f"Gemini API call failed: {str(e)}") from e


def _parse_gemini_response(raw_response: str) -> dict:
    """
    Parse the raw text response from Gemini into a Python dictionary.

    Handles cases where Gemini includes markdown code blocks despite instructions.

    Args:
        raw_response: Raw text returned by Gemini.

    Returns:
        Parsed dictionary of extracted fields.

    Raises:
        ValueError: If the response cannot be parsed as valid JSON.
    """
    if not raw_response or not raw_response.strip():
        raise ValueError("Gemini returned an empty response.")

    text = raw_response.strip()

    # Strip markdown code blocks if present (```json ... ``` or ``` ... ```)
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()

    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError(
                f"Expected a JSON object but got {type(parsed).__name__}."
            )
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        logger.error(f"Problematic response text: {text[:1000]}")
        raise ValueError(
            f"Gemini returned invalid JSON that could not be parsed: {str(e)}"
        ) from e
