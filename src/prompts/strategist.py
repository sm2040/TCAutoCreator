"""Strategist 프롬프트 템플릿."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


STRATEGIST_SYSTEM = """당신은 QA 테스트 전략가입니다.
분석 결과를 바탕으로 어떤 영역에 어떤 관점의 테스트 케이스를 만들지 계획합니다.
반드시 한국어로 답하고, 지나치게 장황하지 않게 실무적으로 정리하세요."""

STRATEGIST_USER_TEMPLATE = """다음 분석 결과를 바탕으로 테스트 케이스 생성 전략을 수립하세요.

[분석 결과]
{analysis_summary}

[사용자 피드백]
{user_feedback}

[전략 수립 규칙]
1. 핵심 기능 영역을 누락하지 않습니다.
2. 정상 흐름, 예외 흐름, 입력 검증, 상태 변화를 균형 있게 포함합니다.
3. total_expected_tcs는 현실적인 개수로 제안합니다.
4. areas 항목의 priority는 높음/중간/낮음 중 하나로 작성합니다.

[출력 형식]
{format_instructions}"""

strategist_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", STRATEGIST_SYSTEM),
        ("user", STRATEGIST_USER_TEMPLATE),
    ]
)
