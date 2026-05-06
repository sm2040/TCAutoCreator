"""입력 유형별 테스트 케이스 생성 Worker."""

from __future__ import annotations

from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from src.models.llm_clients import get_multimodal_llm, get_text_llm
from src.models.schemas import TestCase, TestCaseBatch
from src.prompts.worker import WORKER_MULTIMODAL_INSTRUCTIONS, WORKER_SYSTEM, worker_prompt


def _build_parser() -> PydanticOutputParser[TestCaseBatch]:
    """테스트 케이스 배치 파서를 생성한다."""

    return PydanticOutputParser(pydantic_object=TestCaseBatch)


def generate_test_cases_from_text(input_content: str) -> List[TestCase]:
    """텍스트 입력으로부터 테스트 케이스 목록을 생성한다.

    Args:
        input_content: 기획서 또는 요구사항 원문 텍스트

    Returns:
        생성된 테스트 케이스 목록
    """

    parser = _build_parser()
    chain = worker_prompt | get_text_llm() | parser

    result = chain.invoke(
        {
            "input_content": input_content,
            "format_instructions": parser.get_format_instructions(),
        }
    )
    return result.test_cases


def generate_test_cases_from_images(
    image_data_urls: List[str],
    description: str | None = None,
) -> List[TestCase]:
    """이미지 입력으로부터 테스트 케이스 목록을 생성한다.

    Args:
        image_data_urls: data URL 형태의 이미지 목록
        description: 이미지에 대한 추가 설명

    Returns:
        생성된 테스트 케이스 목록
    """

    parser = _build_parser()
    content: list[dict[str, object]] = [
        {
            "type": "text",
            "text": WORKER_MULTIMODAL_INSTRUCTIONS.format(
                format_instructions=parser.get_format_instructions()
            ),
        }
    ]

    if description:
        content.append(
            {
                "type": "text",
                "text": f"[추가 설명]\n{description}",
            }
        )

    for image_data_url in image_data_urls:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_data_url},
            }
        )

    llm = get_multimodal_llm()
    response = llm.invoke(
        [
            SystemMessage(content=WORKER_SYSTEM),
            HumanMessage(content=content),
        ]
    )
    result = parser.invoke(response)
    return result.test_cases


def generate_test_cases(input_content: str) -> List[TestCase]:
    """기존 텍스트 기반 생성 함수 호환용 별칭."""

    return generate_test_cases_from_text(input_content)


def worker_node(state: "TCGeneratorState") -> "TCGeneratorState":
    """확정된 입력 자료와 전략을 바탕으로 테스트 케이스를 생성한다.

    입력 state key:
    - input_type
    - text
    - images
    - description
    - analysis
    - strategy

    출력 state key:
    - test_cases
    """

    strategy = state.get("strategy")
    analysis = state.get("analysis")

    if strategy is None or analysis is None:
        raise ValueError("Worker 실행 전에 analysis와 strategy가 필요합니다.")

    strategy_summary = strategy.model_dump_json(indent=2, ensure_ascii=False)
    analysis_summary = analysis.model_dump_json(indent=2, ensure_ascii=False)

    if state["input_type"] == "image":
        description_parts = [
            "[분석 결과]",
            analysis_summary,
            "",
            "[테스트 전략]",
            strategy_summary,
        ]
        if state.get("user_feedback"):
            description_parts.extend(["", "[사용자 피드백]", state["user_feedback"]])
        if state.get("description"):
            description_parts.extend(["", "[추가 설명]", state["description"]])

        test_cases = generate_test_cases_from_images(
            state.get("images") or [],
            description="\n".join(description_parts),
        )
    else:
        input_text = state.get("text") or ""
        combined_text = "\n\n".join(
            [
                "[원본 자료]",
                input_text,
                "",
                "[분석 결과]",
                analysis_summary,
                "",
                "[테스트 전략]",
                strategy_summary,
                "",
                "[사용자 피드백]",
                state.get("user_feedback") or "없음",
            ]
        )
        test_cases = generate_test_cases_from_text(combined_text)

    updated_state = dict(state)
    updated_state["test_cases"] = test_cases
    return updated_state
