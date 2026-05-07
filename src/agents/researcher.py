"""Researcher 노드 구현."""

from __future__ import annotations

from langchain.output_parsers import OutputFixingParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.graph.state import TCGeneratorState
from src.models.llm_clients import get_multimodal_llm, get_text_llm
from src.models.schemas import ScreenAnalysis
from src.prompts.researcher import RESEARCHER_SYSTEM, researcher_prompt


def researcher_node(state: TCGeneratorState) -> TCGeneratorState:
    """입력 자료를 분석해 기능/화면 구조를 추출한다.

    입력 state key:
    - input_type
    - text
    - images
    - description

    출력 state key:
    - analysis
    """

    base_parser = PydanticOutputParser(pydantic_object=ScreenAnalysis)
    parser = OutputFixingParser.from_llm(parser=base_parser, llm=get_text_llm())

    if state["input_type"] == "image":
        content: list[dict[str, object]] = [
            {
                "type": "text",
                "text": (
                    "다음 화면 이미지를 분석해 기능 구조를 정리하세요.\n\n"
                    f"{parser.get_format_instructions()}"
                ),
            }
        ]
        if state.get("description"):
            content.append(
                {
                    "type": "text",
                    "text": f"[추가 설명]\n{state['description']}",
                }
            )
        for image_data_url in state.get("images") or []:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url},
                }
            )

        response = get_multimodal_llm().invoke(
            [
                SystemMessage(content=RESEARCHER_SYSTEM),
                HumanMessage(content=content),
            ]
        )
        analysis = parser.invoke(response)
    else:
        input_content = state.get("text") or ""
        if state.get("description"):
            input_content = f"{state['description']}\n\n{input_content}"

        chain = researcher_prompt | get_text_llm() | parser
        analysis = chain.invoke(
            {
                "input_content": input_content,
                "format_instructions": parser.get_format_instructions(),
            }
        )

    updated_state = dict(state)
    updated_state["analysis"] = analysis
    return updated_state
