"""OCR support via Tesseract for scanned PDFs."""

import logging

logger = logging.getLogger(__name__)

_tesseract_available: bool | None = None


def is_tesseract_available() -> bool:
    """Check if Tesseract OCR is installed and accessible."""
    global _tesseract_available
    if _tesseract_available is None:
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            _tesseract_available = True
        except Exception:
            _tesseract_available = False
    return _tesseract_available


def ocr_image(image, languages: str = "spa+eng") -> str:
    """Apply OCR to a PIL Image and return extracted text.

    Args:
        image: PIL Image object
        languages: Tesseract language codes (e.g. "spa+eng" for Spanish + English)

    Returns:
        Extracted text string, or empty string on failure
    """
    try:
        import pytesseract

        text = pytesseract.image_to_string(image, lang=languages)
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""
