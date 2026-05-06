## 목적

이 문서는 Codex가 이 저장소에서 작업할 때 따라야 하는 최소 실행 규칙이다.

이 프로젝트는 기획서(텍스트, 이미지, PDF)를 입력받아 QA용 테스트 케이스 초안을 생성하는 CLI 기반 MVP다.
현재 범위를 넘지 않고, 기존 설계를 유지하면서, 작은 단위로 구현하는 것을 기본 원칙으로 한다.

---

## 우선순위

지시가 충돌하면 아래 순서를 따른다.

1. 사용자의 최신 지시
2. `TASKS.md`
3. `DESIGN.md`
4. `Test Case AutoCreator_Implementation Plan.md`

판단 기준:
- 지금 당장 무엇을 할지 → `TASKS.md`
- 어떻게 구현할지 → `DESIGN.md`
- 전체 구조와 방향 → Implementation Plan

---

## 현재 상태

현재 프로젝트는 **Phase 2**까지 기본 구현이 진행된 상태다.
다음 우선 작업은 **Phase 1/2의 실제 API 검증 마무리 후 Phase 3 입력 확장 준비**다.

사용자가 별도 지시하지 않으면, Codex는 현재 phase 범위 안에서만 작업한다.
미래 phase 기능을 미리 대량 구현하지 않는다.

---

## Codex가 해야 하는 일

Codex는 아래 작업을 수행한다.

- 폴더와 파일 생성
- 설정 파일 작성
- 반복적인 기본 코드 뼈대 작성
- 타입 힌트가 있는 함수/클래스 골격 작성
- 테스트 코드 작성
- 명확한 범위의 기능 구현
- 작은 단위 리팩토링
- 단순 버그 수정

예시:
- `__init__.py`
- `pyproject.toml`
- `.env.example`
- CLI 기본 구조
- logging 기본 설정
- Pydantic 모델 골격
- LangGraph state 골격
- CSV writer 기본 구조
- 테스트 템플릿

---

## Codex가 혼자 결정하면 안 되는 일

아래는 사용자가 명시적으로 요청하지 않으면 바꾸지 않는다.

- 핵심 아키텍처
- LangGraph 워크플로우 구조
- State 계약
- 출력 스키마
- CSV 컬럼 순서
- HITL 흐름
- 모델 선택 전략
- 프롬프트 전략
- 대형 의존성 추가
- GUI / 웹 UI / DB 서버 도입
- MVP 범위 확장

더 좋아 보인다는 이유만으로 구조를 바꾸지 않는다.
구조적 판단이 필요하면 먼저 사용자에게 묻는다.

---

## 작업 시작 전 필수 확인 문서

새 세션에서 작업 시작 전 아래 문서를 먼저 읽는다.

- `TASKS.md`
- `DESIGN.md`
- `Test Case AutoCreator_Implementation Plan.md`

---

## 프로젝트 범위

MVP 입력은 아래 3가지만 지원한다.

- 텍스트
- 이미지
- PDF

기본 출력은 CSV다.

사용자 요청이 없으면 아래는 범위 밖으로 본다.

- URL 입력
- Figma 입력
- 웹앱화
- Slack 연동
- Google Sheets 기본 출력화

---

## 아키텍처 고정 규칙

의도된 흐름은 아래와 같다.

1. Input Router
2. Loader (Image / Text / PDF)
3. Researcher
4. Strategist
5. HITL Checkpoint
6. Worker
7. Finalizer
8. CSV Writer

이 구조는 단순 일직선 체인이 아니다.
라우팅, 사용자 확인, 재시도가 가능한 그래프 구조를 유지한다.

사용자 승인 없이 이 구조를 단순화하거나 제거하지 않는다.

---

## 상태 관리 규칙

노드 간 데이터는 모두 명시적으로 전달한다.

허용:
- `TypedDict` 기반 state
- 명확한 함수 입출력
- 스키마 기반 데이터 전달

금지:
- 전역 상태
- 모듈 레벨 mutable state
- 숨겨진 사이드 이펙트
- 임시 해킹성 연결

---

## 파일 구조 규칙

특별한 지시가 없으면 아래 구조를 따른다.

```text
tc-auto-creator/
├── .env.example
├── README.md
├── AGENTS.md
├── TASKS.md
├── DESIGN.md
├── Test Case AutoCreator_Implementation Plan.md
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── llm_clients.py
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── image_loader.py
│   │   ├── text_loader.py
│   │   └── pdf_loader.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── researcher.py
│   │   ├── strategist.py
│   │   ├── worker.py
│   │   └── finalizer.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── builder.py
│   │   └── router.py
│   ├── hitl/
│   │   ├── __init__.py
│   │   └── cli_prompt.py
│   ├── output/
│   │   ├── __init__.py
│   │   └── csv_writer.py
│   └── prompts/
│       ├── __init__.py
│       ├── researcher.py
│       ├── strategist.py
│       └── worker.py
├── tests/
│   ├── fixtures/
│   └── test_*.py
└── outputs/
```

필요성이 명확하지 않으면 디렉터리 구조를 임의 변경하지 않는다.

---

## 코드 규칙

- 클래스: `PascalCase`
- 함수/변수: `snake_case`
- 상수: `UPPER_SNAKE_CASE`
- 파일명: `snake_case.py`
- 노드 함수명: `{role}_node`

모든 public 함수는 타입 힌트를 작성한다. 반환 타입도 명시한다.

public 함수와 클래스에는 docstring을 작성한다. 노드 함수 docstring에는 아래를 포함한다.

- 역할
- 입력 state key
- 출력 state key

import 순서:

1. 표준 라이브러리
2. 서드파티
3. 로컬 모듈

---

## 언어 규칙

- 코드 식별자: 영어
- 사용자용 CLI 메시지: 한국어
- 사용자용 에러 메시지: 한국어
- 프롬프트: 한국어
- docstring: 한국어 권장
- 주석: 한국어 또는 영어 가능

---

## 스키마 / 출력 규칙

테스트 케이스는 자유 텍스트가 아니라 정형 데이터다. Pydantic 모델을 사용한다.

CSV 컬럼 순서는 아래를 유지한다.

1. No.
2. 대분류
3. 중분류
4. 소분류
5. 사전조건
6. 재현절차
7. 기대결과
8. 실제결과
9. 비고

추가 규칙:

- `실제결과` 기본값은 빈 칸
- `비고`는 빈 칸 가능
- CSV 인코딩은 UTF-8 with BOM
- 컬럼 순서는 승인 없이 변경하지 않는다

---

## 프롬프트 규칙

모든 프롬프트는 `src/prompts/` 아래에 둔다.

하지 말 것:

- 노드 코드 안에 긴 프롬프트 인라인 작성
- 아무 파일에나 프롬프트 숨기기
- 프롬프트 언어를 임의로 바꾸기

---

## LLM / 설정 규칙

LLM 인스턴스 생성은 반드시 `src/models/llm_clients.py`에 모은다. 노드 안에서 직접 생성하지 않는다.

환경 변수 기반 설정만 사용한다. 비밀값을 코드에 하드코딩하지 않는다.

---

## 에러 처리 규칙

- 예외를 광범위하게 삼키지 않는다
- 디버깅 가능한 형태로 실패를 드러낸다
- 사용자에게 보이는 에러는 한국어로 쓴다
- logging을 사용한다
- 디버깅용 `print()` 남발 금지

재시도 원칙:

- LLM 호출 일시 실패 → 모델/클라이언트 레벨
- 파싱 실패 → parser 레벨
- 비즈니스 로직 재시도 → graph 레벨

---

## 의존성 규칙

의존성 추가 우선순위:

1. 표준 라이브러리
2. 이미 쓰는 의존성
3. 꼭 필요할 때만 새 의존성

다음은 사용자 승인 없이 추가하지 않는다.

- 무거운 ML 프레임워크
- GUI 라이브러리
- 외부 DB 서버 관련 의존성

새 의존성이 필요하면 먼저 사용자에게 이유를 설명하고 확인받는다.

---

## HITL 규칙

사람 검토는 선택 기능이 아니라 핵심 기능이다.

Strategist 결과는 Worker 전에 검토 가능해야 한다. 최소한 아래 흐름을 유지한다.

- approve
- edit
- reject

구현 편의 때문에 이 단계를 제거하거나 우회하지 않는다.

---

## 작업 방식

Codex는 작은 단위로 작업한다.

권장 단위:

- 하나의 작은 기능
- 하나의 좁은 파일 묶음
- 하나의 phase 하위 작업

작업 후에는 아래를 짧게 보고한다.

1. 변경 파일
2. 변경 내용
3. 변경 이유
4. 검증 방법
5. 다음 추천 작업

요청받지 않은 대규모 선행 구현은 하지 않는다.

---

## TASKS.md 규칙

기본적으로 `TASKS.md`를 자동 수정하지 않는다. 사용자가 명시적으로 관리까지 맡긴 경우에만 업데이트한다.

업데이트 시에는:

- 완료 항목을 사실대로 표시
- 다음 작업을 명확히 유지
- blocker를 짧고 사실만 기록

허위 진행 상황을 쓰지 않는다.

---

## 검증 기준

### Phase 1 검증

```bash
Copypython -c "from src.models.llm_clients import get_text_llm; print(get_text_llm().invoke('안녕').content)"
```

기대 결과:

- 한국어 응답 출력
- LangSmith 추적 가능

### Phase 2 이후 검증

```bash
Copypython -m src.cli --text "테스트할 기획서 내용..."
```

기대 결과:

- TC 초안 생성
- CSV 파일 저장

아직 검증 가능한 상태가 아니면 그렇게 명확히 말한다.

---

## 언제 사용자에게 물어볼지

아래 경우에는 추측하지 말고 먼저 질문한다.

- 문서끼리 충돌할 때
- 핵심 구조 변경이 필요할 때
- 현재 phase를 넘는 작업일 때
- 새 의존성이 필요할 때
- 출력 스키마를 바꿔야 할 때
- graph/HITL 구조를 바꿔야 할 때
- 파일 구조를 크게 바꿔야 할 때

---

## 기본 실행 루프

각 작업은 기본적으로 아래 순서를 따른다.

1. 관련 문서 읽기
2. 현재 범위 확인
3. 필요한 파일만 수정
4. 변경 최소화
5. 검증 또는 검증 방법 제시
6. 변경 사항 요약
7. 추측성 추가 작업 없이 종료

---

## 최종 원칙

이 저장소는 phase 기반으로 점진적으로 발전시킨다.

Codex는 다음을 우선한다.

- 명확성
- 명시적 계약
- 디버깅 가능성
- 작은 단위의 검증 가능한 변경
- 기존 설계 유지

Codex는 다음을 목표로 삼지 않는다.

- 과한 선행 구현
- 조용한 아키텍처 변경
- 사람 검토 없는 자동화 확대
- 화려하지만 유지보수 어려운 구조
