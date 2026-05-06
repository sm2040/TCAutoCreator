"""OpenRouter 기반 LLM 클라이언트 팩토리."""

from __future__ import annotations

import os

from langchain_openai import ChatOpenAI

from src.config import load_settings


def _apply_langsmith_environment() -> None:
    """LangSmith 관련 환경 변수를 현재 프로세스에 반영한다."""

    settings = load_settings()

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key

    os.environ["LANGSMITH_TRACING"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project


def get_text_llm(
    temperature: float = 0.1,
    max_retries: int = 2,
    max_tokens: int = 4096,
) -> ChatOpenAI:
    """텍스트 처리용 LLM 인스턴스를 반환한다."""

    settings = load_settings()
    _apply_langsmith_environment()

    return ChatOpenAI(
        model=settings.model_text,
        temperature=temperature,
        max_retries=max_retries,
        max_tokens=max_tokens,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def get_multimodal_llm(
    temperature: float = 0.1,
    max_retries: int = 2,
    max_tokens: int = 4096,
) -> ChatOpenAI:
    """멀티모달 처리용 LLM 인스턴스를 반환한다."""

    settings = load_settings()
    _apply_langsmith_environment()

    return ChatOpenAI(
        model=settings.model_multimodal,
        temperature=temperature,
        max_retries=max_retries,
        max_tokens=max_tokens,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )
