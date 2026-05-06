"""이미지 입력 로더."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import List


def _guess_mime_type(path: Path) -> str:
    """파일 경로에서 MIME 타입을 추정한다."""

    mime_type, _ = mimetypes.guess_type(path.name)
    return mime_type or "image/png"


def load_image_as_data_url(image_path: str | Path) -> str:
    """이미지 파일을 data URL 형태의 base64 문자열로 변환한다."""

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {path}")

    mime_type = _guess_mime_type(path)
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def load_images(image_paths: List[str | Path]) -> List[str]:
    """여러 이미지 파일을 data URL 목록으로 변환한다."""

    if not image_paths:
        raise ValueError("최소 1개의 이미지 경로가 필요합니다.")

    return [load_image_as_data_url(image_path) for image_path in image_paths]
