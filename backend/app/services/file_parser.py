"""
Lightweight document text extraction for the complaint intake upload flow.

Per the assignment, production-grade OCR/parsing is explicitly NOT
required -- this uses straightforward text-layer extraction only
(pypdf, python-docx, mail-parser). Scanned/image-only PDFs will yield
little or no text; that's expected and acceptable for this scope.
"""
import io

import mailparser
from docx import Document
from pypdf import PdfReader

from app.utils.exceptions import FileProcessingError

SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt", "eml"}


def _extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _extract_docx_text(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def _extract_txt_text(file_bytes: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    raise FileProcessingError("Unable to decode text file with utf-8 or latin-1.")


def _extract_eml_text(file_bytes: bytes) -> str:
    mail = mailparser.parse_from_bytes(file_bytes)
    from_display = ", ".join(f"{name} <{addr}>" if name else addr for name, addr in (mail.from_ or []))
    parts = [f"Subject: {mail.subject}", f"From: {from_display}"]
    body = mail.body or (mail.text_plain[0] if mail.text_plain else "")
    parts.append(body)
    return "\n".join(str(p) for p in parts if p).strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Dispatches to the right parser based on file extension."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in SUPPORTED_EXTENSIONS:
        raise FileProcessingError(
            f"Unsupported file type '.{extension}'. Supported formats: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )

    try:
        if extension == "pdf":
            text = _extract_pdf_text(file_bytes)
        elif extension == "docx":
            text = _extract_docx_text(file_bytes)
        elif extension == "txt":
            text = _extract_txt_text(file_bytes)
        else:  # eml
            text = _extract_eml_text(file_bytes)
    except FileProcessingError:
        raise
    except Exception as exc:
        raise FileProcessingError(f"Failed to parse .{extension} file: {exc}") from exc

    if not text:
        raise FileProcessingError(
            "No extractable text found in this file. If it's a scanned/image-based "
            "document, OCR is out of scope for this system -- try pasting the text instead."
        )

    return text
