"""
API routes for the Autonomous Insurance Claims Processing Agent.
Defines the POST /process-claim endpoint.
"""

import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import ALLOWED_EXTENSIONS, UPLOAD_DIR
from app.models import ClaimResponse, ErrorResponse
from app.services.extractor import extract_fields
from app.services.pdf_reader import read_document
from app.services.reasoning import generate_reasoning
from app.services.router import determine_route
from app.services.validator import validate_and_normalize

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/process-claim",
    response_model=ClaimResponse,
    summary="Process an FNOL claim document",
    description=(
        "Upload a PDF or TXT FNOL document. The system will extract structured fields, "
        "validate mandatory information, apply deterministic routing rules, and return "
        "a complete JSON response with the recommended processing queue."
    ),
    responses={
        200: {"description": "Claim processed successfully", "model": ClaimResponse},
        400: {"description": "Invalid file type or unreadable document", "model": ErrorResponse},
        422: {"description": "Validation error"},
        500: {"description": "Internal server or AI extraction error", "model": ErrorResponse},
    },
)
async def process_claim(
    file: UploadFile = File(..., description="FNOL document in PDF or TXT format"),
) -> JSONResponse:
    """
    Main FNOL processing endpoint.

    Pipeline:
        Upload → Document Reader → Gemini Extraction → Pydantic Validation
        → Business Rule Engine → Route Recommendation → JSON Response
    """
    temp_file_path: str | None = None

    try:
        # ── Step 1: Validate file type ────────────────────────────────
        filename = file.filename or "uploaded_file"
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            logger.warning(f"Rejected unsupported file type: '{extension}'")
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported file type '{extension}'.",
                    "detail": "Only PDF (.pdf) and TXT (.txt) files are accepted.",
                },
            )

        # ── Step 2: Save uploaded file temporarily ────────────────────
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = f"{unique_id}_{filename}"
        temp_file_path = os.path.join(UPLOAD_DIR, safe_filename)

        content = await file.read()

        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "The uploaded file is empty."},
            )

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        logger.info(f"File saved temporarily: {temp_file_path}")

        # ── Step 3: Read document text ────────────────────────────────
        try:
            document_text = read_document(temp_file_path)
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={"error": str(e)},
            )
        except RuntimeError as e:
            return JSONResponse(
                status_code=400,
                content={"error": str(e)},
            )

        # ── Step 4: Extract fields using Gemini ───────────────────────
        try:
            raw_fields = extract_fields(document_text)
        except RuntimeError as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "AI extraction failed.",
                    "detail": str(e),
                },
            )
        except ValueError as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "AI returned an invalid response.",
                    "detail": str(e),
                },
            )

        # ── Step 5: Validate & normalize fields ───────────────────────
        normalized_fields, missing_fields = validate_and_normalize(raw_fields)

        # ── Step 6: Determine routing (pure Python) ───────────────────
        recommended_route = determine_route(normalized_fields, missing_fields)

        # ── Step 7: Generate reasoning ────────────────────────────────
        reasoning = generate_reasoning(
            route=recommended_route,
            missing_fields=missing_fields,
            estimated_damage=normalized_fields.estimatedDamage,
            claim_type=normalized_fields.claimType,
        )

        # ── Step 8: Build and return response ─────────────────────────
        response = ClaimResponse(
            extractedFields=normalized_fields,
            missingFields=missing_fields,
            recommendedRoute=recommended_route,
            reasoning=reasoning,
        )

        logger.info(
            f"Claim processed successfully. Route: {recommended_route}. "
            f"Missing fields: {len(missing_fields)}"
        )

        return JSONResponse(
            status_code=200,
            content=response.model_dump(),
        )

    except Exception as e:
        logger.exception(f"Unexpected error processing claim: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected server error occurred.",
                "detail": str(e),
            },
        )

    finally:
        # ── Cleanup: Remove temporary uploaded file ───────────────────
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Temporary file removed: {temp_file_path}")
            except OSError as e:
                logger.warning(f"Could not remove temporary file: {e}")
