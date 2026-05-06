"""환경 변수와 프로젝트 설정을 관리한다."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_MULTIMODAL_MODEL = "google/gemini-2.5-flash"
DEFAULT_TEXT_MODEL = "openai/gpt-oss-20b:free"
DEFAULT_LANGSMITH_PROJECT = "tc-auto-creator"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass(frozen=True)
class Settings:
    """프로젝트 전역 설정."""

    openrouter_api_key: str
    langsmith_api_key: str | None
    langsmith_tracing: bool
    langsmith_project: str
    model_multimodal: str
    model_text: str
    openrouter_base_url: str = OPENROUTER_BASE_URL


def _get_bool_env(name: str, default: bool = False) -> bool:
    """환경 변수 문자열을 bool로 변환한다."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    """`.env`를 포함한 환경 변수에서 설정을 읽어온다."""

    load_dotenv()

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
        )

    return Settings(
        openrouter_api_key=openrouter_api_key,
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        langsmith_tracing=_get_bool_env("LANGSMITH_TRACING", default=True),
        langsmith_project=os.getenv(
            "LANGSMITH_PROJECT", DEFAULT_LANGSMITH_PROJECT
        ),
        model_multimodal=os.getenv(
            "MODEL_MULTIMODAL", DEFAULT_MULTIMODAL_MODEL
        ),
        model_text=os.getenv("MODEL_TEXT", DEFAULT_TEXT_MODEL),
    )
