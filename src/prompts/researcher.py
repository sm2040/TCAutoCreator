"""Researcher 프롬프트 템플릿."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


RESEARCHER_SYSTEM = """당신은 QA 분석가입니다.
입력 자료를 바탕으로 테스트해야 할 화면/기능 구조를 먼저 정리하는 역할을 맡고 있습니다.
반드시 한국어로 답하고, 추측은 최소화하며 실제로 보이거나 읽히는 정보에 집중하세요."""

RESEARCHER_USER_TEMPLATE = """다음 기획 또는 요구사항 자료를 분석하세요.

[입력 자료]
{input_content}

아래 항목을 구조화해서 정리하세요.
- screen_name: 화면명 또는 문서 주제
- feature_areas: 주요 기능 영역
- ui_elements: 주요 UI 요소 또는 핵심 구성 요소
- user_actions: 사용자가 수행 가능한 주요 액션
- edge_cases_hint: 테스트 시 확인할 만한 예외/경계 상황 힌트

[출력 형식]
{format_instructions}"""

researcher_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RESEARCHER_SYSTEM),
        ("user", RESEARCHER_USER_TEMPLATE),
    ]
)
