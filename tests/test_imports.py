"""초기 세팅 검증용 테스트."""

from src.config import load_settings
from src.models.llm_clients import get_multimodal_llm, get_text_llm
from src.models.schemas import ScreenAnalysis, TestCase, TestStrategy


def test_schema_classes_exist() -> None:
    assert TestCase.model_fields
    assert ScreenAnalysis.model_fields
    assert TestStrategy.model_fields


def test_llm_factories_require_env() -> None:
    try:
        load_settings()
    except ValueError:
        return

    assert get_text_llm() is not None
    assert get_multimodal_llm() is not None
