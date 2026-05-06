"""Worker 프롬프트 템플릿."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


WORKER_SYSTEM = """당신은 숙련된 QA 엔지니어입니다.
주어진 기획/요구사항 자료를 바탕으로 실제로 바로 검토 가능한 테스트 케이스 초안을 작성하세요.
반드시 한국어로 작성하고, 중복 없이 기능/예외/검증 관점을 균형 있게 포함하세요."""

WORKER_USER_TEMPLATE = """다음 기획 또는 요구사항 텍스트를 분석해 테스트 케이스를 생성하세요.

[입력 텍스트]
{input_content}

[작성 규칙]
1. 테스트 케이스는 표준 QA 문서처럼 구체적으로 작성합니다.
2. 재현절차는 "1. ...\\n2. ...\\n3. ..." 형식으로 작성합니다.
3. 실제결과(actual_result)와 비고(note)는 비워둡니다.
4. no는 1부터 시작하는 연속 번호를 사용합니다.
5. 기능 정상 흐름뿐 아니라 입력 오류, 경계값, 예외 흐름도 포함합니다.
6. 추측이 필요한 경우 과도한 가정보다 일반적인 웹/앱 서비스 기준으로 보수적으로 작성합니다.

[출력 형식]
{format_instructions}"""

WORKER_MULTIMODAL_INSTRUCTIONS = """다음 화면 이미지 또는 시각 자료를 분석해 테스트 케이스를 생성하세요.

[작성 규칙]
1. 화면에 보이는 기능, 입력 요소, 버튼, 상태 변화를 바탕으로 테스트 케이스를 작성합니다.
2. 추측이 필요한 경우 UI에서 합리적으로 유추 가능한 범위 안에서만 작성합니다.
3. 재현절차는 "1. ...\\n2. ...\\n3. ..." 형식으로 작성합니다.
4. 실제결과(actual_result)와 비고(note)는 비워둡니다.
5. no는 1부터 시작하는 연속 번호를 사용합니다.
6. 정상 흐름, 예외 흐름, 입력 검증, 화면 상태 변화를 균형 있게 포함합니다.
7. 추가 설명이 주어진 경우 이미지와 함께 종합해서 해석합니다.

[출력 형식]
{format_instructions}"""

worker_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", WORKER_SYSTEM),
        ("user", WORKER_USER_TEMPLATE),
    ]
)
