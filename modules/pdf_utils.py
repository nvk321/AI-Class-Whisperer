import os
from pypdf import PdfReader

# Optional: pytesseract + pdf2image for OCR
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_LIBS_AVAILABLE = True
except ImportError:
    OCR_LIBS_AVAILABLE = False
    print("⚠️ pytesseract or pdf2image not installed — OCR fallback disabled.")

# Optional: configure Tesseract path on Windows if installed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF. Uses PyPDF first, then OCR fallback if available.
    Returns combined text as string.
    """
    text = ""

    # --- 1. Try PyPDF extraction first ---
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        if text.strip():
            return clean_text(text)
    except Exception as e:
        print(f"PyPDF failed: {e}")

    # --- 2. OCR fallback if available ---
    if OCR_LIBS_AVAILABLE:
        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img)
            return clean_text(text)
        except Exception as e:
            print(f"⚠️ OCR failed: {e}")
            print("OCR skipped. Normal PDFs will still work.")
            return ""
    else:
        print("⚠️ OCR skipped — Tesseract/pdf2image not available.")
        return ""

def clean_text(text):
    """
    Simple cleanup: remove extra spaces, newlines, and tabs
    """
    lines = text.splitlines()
    cleaned = " ".join(line.strip() for line in lines if line.strip())
    return cleaned
