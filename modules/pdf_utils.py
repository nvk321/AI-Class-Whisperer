import os
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract

# Optional: configure Tesseract path on Windows if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF. Uses PyPDF first, then OCR as fallback.
    Returns combined text as string.
    """
    text = ""

    # --- 1. Try PyPDF extraction first ---
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        if text.strip():  # If PyPDF extracted anything, return it
            return clean_text(text)
    except Exception as e:
        print(f"PyPDF failed: {e}")

    # --- 2. OCR fallback (scanned PDFs) ---
    try:
        images = convert_from_path(file_path)
        for img in images:
            text += pytesseract.image_to_string(img)
        return clean_text(text)
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""

def clean_text(text):
    """
    Simple cleanup: remove extra spaces, newlines, and tabs
    """
    lines = text.splitlines()
    cleaned = " ".join(line.strip() for line in lines if line.strip())
    return cleaned
