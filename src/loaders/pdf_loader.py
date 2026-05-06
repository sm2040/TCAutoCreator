"""PDF 입력 로더."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def load_pdf_text(pdf_path: str | Path) -> str:
    """PDF에서 텍스트를 추출한다."""

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {path}")

    reader = PdfReader(str(path))
    extracted_pages: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            extracted_pages.append(page_text.strip())

    if not extracted_pages:
        raise ValueError(
            "PDF에서 추출 가능한 텍스트를 찾지 못했습니다. 이미지 기반 PDF일 수 있습니다."
        )

    return "\n\n".join(extracted_pages)
