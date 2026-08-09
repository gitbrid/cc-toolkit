"""PDF text extraction with automatic OCR fallback for scanned documents."""

import io
import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 50  # Pages with less text than this trigger OCR


@dataclass
class PageContent:
    """Extracted content from a single PDF page."""

    text: str
    page_number: int
    source_file: str
    ocr_applied: bool = False


def extract_pdf(pdf_path: str, ocr_languages: str = "spa+eng") -> list[PageContent]:
    """Extract text from all pages of a PDF, using OCR as fallback for image pages.

    Args:
        pdf_path: Path to the PDF file
        ocr_languages: Tesseract language codes for OCR fallback

    Returns:
        List of PageContent objects, one per page with text
    """
    import fitz  # PyMuPDF

    pages = []
    doc = fitz.open(pdf_path)
    filename = Path(pdf_path).name

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()

        ocr_applied = False

        # If page has very little text, it might be a scanned image
        if len(text) < MIN_TEXT_LENGTH:
            ocr_text = _try_ocr_page(page, ocr_languages)
            if ocr_text and len(ocr_text) > len(text):
                text = ocr_text
                ocr_applied = True

        if text:
            pages.append(
                PageContent(
                    text=text,
                    page_number=page_num + 1,  # 1-indexed for human readability
                    source_file=filename,
                    ocr_applied=ocr_applied,
                )
            )

    doc.close()
    return pages


def _try_ocr_page(page, languages: str) -> str:
    """Convert a PDF page to image and apply OCR.

    Renders the page at 300 DPI and runs Tesseract OCR on it.
    Returns empty string if OCR is not available or fails.
    """
    try:
        from .ocr import ocr_image, is_tesseract_available
        from PIL import Image

        if not is_tesseract_available():
            logger.debug("Tesseract not available, skipping OCR")
            return ""

        # Render page to image at 300 DPI for good OCR quality
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))

        return ocr_image(image, languages)
    except ImportError:
        logger.debug("PIL/pytesseract not installed, skipping OCR")
        return ""
    except Exception as e:
        logger.warning(f"OCR failed for page: {e}")
        return ""
