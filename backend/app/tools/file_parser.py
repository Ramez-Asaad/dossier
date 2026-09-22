"""Extracts plain text from uploaded syllabus/resume/course files (PDF, TXT, MD)."""

import io
from pypdf import PdfReader


def parse_file_contents(filename: str, content_bytes: bytes) -> str:
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content_bytes))
            text_pages = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_pages.append(extracted)
            return "\n".join(text_pages).strip()
        except Exception as exc:
            raise ValueError(f"Could not parse PDF file '{filename}': {exc}") from exc

    # Plain text / Markdown / similar
    try:
        return content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content_bytes.decode("latin1")
        except Exception as exc:
            raise ValueError(f"Could not decode text file '{filename}': {exc}") from exc
