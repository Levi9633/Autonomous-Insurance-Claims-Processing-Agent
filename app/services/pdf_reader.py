"""
PDF/TXT document reader service.
Handles file reading for PDF (via PyMuPDF) and TXT documents.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_document(file_path: str) -> str:
    """
    Read and extract raw text from a PDF or TXT file.

    Args:
        file_path: Absolute path to the uploaded document.

    Returns:
        Extracted text content as a string.

    Raises:
        ValueError: If the file type is unsupported, the document is empty,
                    or no readable text could be extracted.
        RuntimeError: If PDF parsing fails due to corruption.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return _read_pdf(file_path)
    elif extension == ".txt":
        return _read_txt(file_path)
    else:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            "Only PDF (.pdf) and TXT (.txt) files are accepted."
        )


def _read_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).

    Args:
        file_path: Path to the PDF file.

    Returns:
        Concatenated text content from all pages.

    Raises:
        RuntimeError: If the PDF is corrupted or cannot be opened.
        ValueError: If no text could be extracted from the PDF.
    """
    try:
        # pyrefly: ignore [missing-import]
        import fitz  # PyMuPDF

        logger.info(f"Opening PDF: {file_path}")
        doc = fitz.open(file_path)

        if doc.page_count == 0:
            raise ValueError("The uploaded PDF has no pages.")

        text_parts: list[str] = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(page_text)

        doc.close()

        full_text = "\n".join(text_parts).strip()

        if not full_text:
            raise ValueError(
                "No readable text found in the uploaded PDF. "
                "The document may be image-based or encrypted."
            )

        logger.info(f"Successfully extracted {len(full_text)} characters from PDF.")
        return full_text

    except fitz.FileDataError as e:
        logger.error(f"Corrupted PDF file: {e}")
        raise RuntimeError(
            "The uploaded PDF appears to be corrupted or is not a valid PDF file."
        ) from e
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading PDF: {e}")
        raise RuntimeError(f"Failed to read PDF: {str(e)}") from e


def _read_txt(file_path: str) -> str:
    """
    Read a plain text file.

    Args:
        file_path: Path to the TXT file.

    Returns:
        File content as a string.

    Raises:
        ValueError: If the file is empty.
    """
    try:
        logger.info(f"Reading TXT file: {file_path}")

        # Try UTF-8 first, fall back to latin-1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

        content = content.strip()

        if not content:
            raise ValueError("The uploaded text file is empty.")

        logger.info(f"Successfully read {len(content)} characters from TXT file.")
        return content

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading TXT file: {e}")
        raise RuntimeError(f"Failed to read TXT file: {str(e)}") from e
