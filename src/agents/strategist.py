"""Strategist 노드 구현."""

from __future__ import annotations

from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser

from src.graph.state import TCGeneratorState
from src.models.llm_clients import get_text_llm
from src.models.schemas import TestStrategy
from src.prompts.strategist import strategist_prompt


def strategist_node(state: TCGeneratorState) -> TCGeneratorState:
    """분석 결과를 바탕으로 테스트 전략을 수립한다.

    입력 state key:
    - analysis

    출력 state key:
    - strategy
    """

    analysis = state.get("analysis")
    if analysis is None:
        raise ValueError("Strategist 실행 전에 analysis가 필요합니다.")

    base_parser = PydanticOutputParser(pydantic_object=TestStrategy)
    parser = OutputFixingParser.from_llm(parser=base_parser, llm=get_text_llm())
    chain = strategist_prompt | get_text_llm() | parser

    strategy = chain.invoke(
        {
            "analysis_summary": analysis.model_dump_json(
                indent=2,
                ensure_ascii=False,
            ),
            "user_feedback": state.get("user_feedback") or "없음",
            "format_instructions": parser.get_format_instructions(),
        }
    )

    updated_state = dict(state)
    updated_state["strategy"] = strategy
    return updated_state
