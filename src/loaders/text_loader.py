"""텍스트 입력 로더."""

from __future__ import annotations


def load_text_input(raw_text: str) -> str:
    """CLI 텍스트 입력을 정리하고 검증한다."""

    cleaned_text = raw_text.strip()
    if not cleaned_text:
        raise ValueError("입력 텍스트가 비어 있습니다. --text 값을 확인해주세요.")

    return cleaned_text
