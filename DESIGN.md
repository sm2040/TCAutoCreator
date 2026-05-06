# TC Auto-Creator Design

## 1. 문서의 목적

이 문서는 `TC Auto-Creator` 프로젝트의 설계 원칙과 의사결정 기록이다.  
코드만으로는 드러나지 않는 "왜 이렇게 설계했는가"를 남겨, 여러 세션에 걸친 AI 코딩 협업에서도 일관성을 유지하는 것이 목적이다.

- `Test Case AutoCreator_Implementation Plan.md`: 무엇을 만들 것인가
- `TASKS.md`: 지금 무엇을 하고 있는가
- `DESIGN.md`: 어떤 원칙으로 만들 것인가

## 2. 핵심 설계 원칙

### 2.1 점진적 복잡도

처음부터 완전한 시스템을 만들지 않는다.  
가장 단순한 동작 가능한 버전부터 시작해 Phase 단위로 복잡도를 올린다.

- 초기에는 단일 LLM 기반 파이프라인부터 시작한다.
- 멀티 에이전트, HITL, 멀티모달 기능은 이후 Phase에서 도입한다.

### 2.2 사람과 AI의 협업

LLM의 결과를 100% 신뢰하지 않는다.

- 핵심 의사결정 지점에는 사람이 개입하는 `HITL`을 기본 패턴으로 둔다.
- 자동화의 목표는 사람을 대체하는 것이 아니라, 판단을 빠르게 만드는 것이다.

### 2.3 모델 중립성

특정 모델 제공자에 종속되지 않는다.

- OpenRouter를 통해 모델 접근을 추상화한다.
- 모델 변경은 환경 변수 수준에서 가능해야 한다.
- 단계별로 다른 모델을 사용하더라도, 선택 로직은 `llm_clients.py`에 격리한다.

### 2.4 관찰 가능성 우선

디버깅 가능성을 초기부터 확보한다.

- LangSmith 추적을 `Phase 1`부터 활성화한다.
- "왜 이런 결과가 나왔는지" 추적할 수 없는 코드는 지양한다.

### 2.5 명시적 상태 관리

노드 간 데이터 전달은 항상 명시적으로 처리한다.

- LangGraph의 `State` 객체로 노드 간 데이터를 주고받는다.
- 전역 변수, 모듈 레벨 상태, 숨겨진 사이드 이펙트를 사용하지 않는다.

## 3. 아키텍처 의사결정

### 3.1 왜 LangGraph인가

대안:

- 순수 LangChain
- 자체 오케스트레이션 구현
- AutoGen
- CrewAI

결정 근거:

- 입력 타입별 분기, Strategist 재시도, HITL이 모두 필요하다.
- LangChain의 일직선 파이프라인만으로는 장기적으로 한계가 있다.
- LangChain 부품은 그대로 활용하면서 그래프 구조만 추가할 수 있다.
- `State`와 `Checkpointer`를 통해 세션 간 영속성을 자연스럽게 도입할 수 있다.
- AutoGen, CrewAI는 추상화 수준이 높아 디버깅이 더 어렵다.

### 3.2 왜 OpenRouter인가

대안:

- 각 모델 제공자 API 직접 연동
- AWS Bedrock
- LiteLLM

결정 근거:

- 단일 API 키와 단일 결제로 다양한 모델 접근이 가능하다.
- 무료 모델(`:free`)을 활용해 초기 비용을 낮출 수 있다.
- OpenAI 호환 API라 `langchain-openai`를 그대로 활용할 수 있다.
- 멀티모달 모델과 텍스트 모델을 하나의 인터페이스에서 교체 가능하다.

### 3.3 왜 Pydantic 출력 강제인가

대안:

- 정규식 파싱
- JSON 모드만 사용
- 자유 텍스트 후처리

결정 근거:

- 테스트 케이스는 정형 데이터이므로 스키마 강제가 자연스럽다.
- `PydanticOutputParser`를 통해 검증과 구조화를 동시에 얻는다.
- 코드와 출력 구조가 동기화되어 IDE 지원과 타입 안정성을 확보할 수 있다.
- 스키마 변경 시 한 곳만 수정하면 전체 파이프라인에 반영된다.

### 3.4 왜 CSV 출력인가

대안:

- Google Sheets 직접 연동
- JSON
- Excel (`.xlsx`)

결정 근거:

- 추가 인증 없이 즉시 동작한다.
- Excel, Google Sheets, Numbers에서 모두 열 수 있다.
- `UTF-8 with BOM`으로 저장해 Excel 한글 깨짐 가능성을 줄인다.
- 이후 Google Sheets 연동은 출력 어댑터 확장으로 대응할 수 있다.

## 4. 코드 컨벤션

### 4.1 네이밍

- 클래스: `PascalCase`
  - 예: `TestCase`, `TCGeneratorState`
- 함수/변수: `snake_case`
  - 예: `generate_test_cases`, `raw_input`
- 상수: `UPPER_SNAKE_CASE`
  - 예: `DEFAULT_MODEL`, `MAX_RETRIES`
- 파일명: `snake_case.py`
- 노드 함수: `{role}_node`
  - 예: `researcher_node`, `worker_node`

### 4.2 타입 힌트

- 모든 함수 시그니처에 반환 타입까지 포함해 타입 힌트를 작성한다.
- `Optional`, `List`, `Dict` 등은 `typing`에서 import한다.
- LangGraph 상태는 `TypedDict`로 정의한다.

### 4.3 Docstring

- 모든 public 함수와 클래스에 docstring을 작성한다.
- 스타일은 "한 줄 요약 + 필요시 상세 설명"을 기본으로 한다.
- 노드 함수 docstring에는 아래를 포함한다.
  - 역할
  - 입력 State 키
  - 출력 State 키

### 4.4 Import 순서

아래 순서를 지킨다.

1. 표준 라이브러리
2. 서드파티 라이브러리
3. 로컬 모듈

각 그룹 사이는 빈 줄로 구분한다.

### 4.5 한국어 사용 기준

- 코드, 변수명, 함수명: 영어
- 사용자 메시지(CLI 출력, 에러 메시지): 한국어
- 프롬프트: 한국어
- 주석: 한국어 또는 영어 허용
- Docstring: 한국어 권장

## 5. 에러 처리 정책

### 5.1 기본 원칙

- 예외는 가능한 한 `raise`한다.
- 실패를 `None`으로 숨기지 않는다.
- 사용자 입력 오류는 명확한 한국어 메시지로 안내 후 종료한다.
- LLM 호출의 일시적 실패는 모델 인스턴스의 재시도 옵션에 위임한다.

### 5.2 재시도 위치

- LLM 호출 자체 실패: 모델 인스턴스 레벨의 `max_retries`
- Pydantic 파싱 실패: `OutputFixingParser` 또는 `RetryOutputParser`
- 비즈니스 로직 재시도: LangGraph 그래프 레벨에서 명시적으로 표현

### 5.3 로깅

- 라이브러리: 표준 `logging`
- 레벨:
  - `DEBUG`: 개발 중 상세 진단
  - `INFO`: 주요 이벤트
  - `WARNING`: 이상 동작
  - `ERROR`: 처리 가능한 실패
  - `CRITICAL`: 시스템 중단

LangSmith가 LLM 추적을 담당하므로, 동일한 입출력을 중복 로깅하지 않는다.

### 5.4 Phase별 에러 처리 강도

- `Phase 1 ~ 5`: happy path 위주, 명백한 입력 오류 중심
- `Phase 6`: 파일 없음, API 실패, 형식 오류 등 엣지 케이스 보강

## 6. 프롬프트 작성 원칙

### 6.1 위치

모든 프롬프트는 `src/prompts/` 디렉터리에 별도 파일로 분리한다.

- 노드 함수 안에 프롬프트를 인라인으로 작성하지 않는다.

### 6.2 구조

예시:

```python
from langchain_core.prompts import ChatPromptTemplate

RESEARCHER_SYSTEM = """당신은 QA 전문가입니다.
주어진 기획서를 분석하여 테스트해야 할 기능 영역과 UI 요소를 추출합니다."""

RESEARCHER_USER_TEMPLATE = """다음 기획서를 분석하세요:
{input_content}

다음 형식으로 답하세요:
{format_instructions}"""

researcher_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RESEARCHER_SYSTEM),
        ("user", RESEARCHER_USER_TEMPLATE),
    ]
)
```

### 6.3 변수 주입

- 동적 값은 `{variable_name}` 형식으로 주입한다.
- 출력 스키마는 `{format_instructions}`로 전달한다.
- 항상 유지되어야 하는 규칙은 시스템 메시지에 둔다.

### 6.4 언어

- 프롬프트는 한국어로 작성한다.
- 생성되는 테스트 케이스도 한국어를 기본으로 한다.

### 6.5 길이

- 시스템 메시지는 짧고 명확하게 유지한다.
- 상세 지시는 사용자 메시지 또는 포맷 지시로 분리한다.

## 7. 의존성 추가 정책

### 7.1 우선순위

1. 표준 라이브러리로 가능한가
2. 이미 사용 중인 라이브러리로 가능한가
3. 그래도 부족할 때만 새 의존성을 추가하는가

### 7.2 추가 시 기록

새 의존성을 추가할 때는 이 문서의 "의사결정 로그"에 이유를 기록한다.

### 7.3 금지된 의존성

- 무거운 로컬 ML 라이브러리 (`transformers`, `torch` 등)
- GUI 라이브러리 (`tkinter`, `PyQt` 등)
- 별도 DB 서버 (`PostgreSQL`, `MongoDB` 등)

MVP 범위에서는 API 기반 추론, CLI, 파일 기반 저장으로 충분하다.

## 8. 금지 사항

다음은 명시적으로 금지한다.

- API 키 하드코딩
- 프롬프트 인라인 작성
- 전역 변수로 상태 공유
- 광범위한 `try-except`로 예외 삼키기
- 디버깅용 `print()` 남발
- Pydantic 모델 없이 `dict`만으로 핵심 데이터 전달
- 노드 함수 내부에서 LLM 인스턴스 직접 생성
- CSV 컬럼 순서 임의 변경

허용되는 방식:

- API 키는 `.env` + `python-dotenv`
- 프롬프트는 `src/prompts/`
- 상태는 LangGraph `State` 또는 명시적 인자
- CLI 메시지는 `typer.echo` 우선

## 9. 의사결정 로그

형식:

```text
[YYYY-MM-DD] 결정 - 근거
```

현재 기록:

- 초기 설계 결정은 이 문서의 2~8 섹션에 통합 반영함
- `[2026-05-06] Phase 2는 단일 LLM 기반 직선 파이프라인으로 먼저 구현`
  - 근거: 전체 LangGraph 구조로 확장하기 전에 CSV 생성의 핵심 가치와 출력 스키마를 빠르게 검증하기 위함
