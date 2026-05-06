# 제목 없음

날짜: 2026년 5월 6일

# Test Case Auto-Creator: Implementation Plan

## 1. 프로젝트 개요

### 1.1 목적

기획서(이미지·텍스트·PDF)를 입력받아 QA 팀이 즉시 활용 가능한 테스트 케이스 초안을 자동 생성하는 도구. 수동 작성 대비 시간을 대폭 단축하고, 팀 전체의 TC 품질 일관성을 확보하는 것이 목표.

### 1.2 사용자

- **1차 사용자**: QA 엔지니어 (TC 초안을 받아 검토·보완)
- **운영 환경**: 팀 공유용 도구. 초기에는 CLI 기반, 추후 Slack 통합 가능

### 1.3 성공 기준

- 기획서 1건당 5분 이내에 TC 초안 생성
- 생성된 TC의 70% 이상이 추가 수정 없이 사용 가능
- 표준 TC 양식 준수 (아래 1.4 참고)

### 1.4 표준 출력 양식

TC는 아래 컬럼을 가진 표 형태로 출력한다.

| 컬럼 | 설명 |
| --- | --- |
| No. | TC 일련번호 (1부터 시작) |
| 대분류 | 기능 영역 (예: 로그인, 결제) |
| 중분류 | 세부 기능 (예: 이메일 로그인) |
| 소분류 | 구체적 시나리오 (예: 비밀번호 오류) |
| 사전조건 | 테스트 실행 전 필요한 조건 |
| 재현절차 | 단계별 실행 순서 (번호 매김) |
| 기대결과 | 예상되는 정상 동작 |
| 실제결과 | 빈 칸으로 출력 (QA가 직접 작성) |
| 비고 | 추가 메모 (빈 칸 가능) |

## 2. 기술 스택

| 카테고리 | 선택 | 비고 |
| --- | --- | --- |
| 언어 | Python 3.11+ |  |
| 코어 프레임워크 | LangGraph + LangChain | 멀티 에이전트 워크플로우 |
| 모델 게이트웨이 | OpenRouter | 다양한 모델을 단일 API로 |
| 모델 (멀티모달) | Gemini 2.5 Flash 또는 Claude Sonnet | 이미지 분석용 |
| 모델 (텍스트) | DeepSeek-V3 또는 Qwen 2.5 | 텍스트 처리용 (저비용) |
| LLM 통합 | `langchain-openai` (OpenRouter용 base_url) |  |
| PDF 처리 | `pypdf` 또는 `pdfplumber` |  |
| 이미지 처리 | `Pillow` (전처리), base64 인코딩 |  |
| 출력 파싱 | Pydantic + LangChain `PydanticOutputParser` |  |
| 출력 형식 | CSV (1차), Google Sheets (2차) |  |
| 관찰성 | LangSmith (무료 티어) |  |
| CLI | `click` 또는 `typer` |  |
| 환경 변수 | `python-dotenv` | API 키 관리 |

## 3. 입력 형태

MVP는 세 가지 입력만 지원한다.

**이미지 입력**: PNG, JPG 파일 경로. 단일 이미지 또는 여러 이미지 동시 입력 가능. 멀티모달 모델로 직접 분석.

**텍스트 입력**: 마크다운, 일반 텍스트, 또는 CLI에서 직접 입력. 그대로 LLM 컨텍스트에 주입.

**PDF 입력**: PDF 파일 경로. 텍스트 추출 + 이미지 추출(있을 경우)을 동시 처리.

URL 입력, Figma 입력은 MVP 범위에서 제외. 추후 확장.

## 4. 시스템 아키텍처

### 4.1 전체 워크플로우

LangGraph로 구성된 단방향 + 조건부 분기 + HITL 그래프.

```
Copy[Entry]
   ↓
[Input Router] ──분기──→ [Image Loader] / [Text Loader] / [PDF Loader]
                              ↓
                         [Researcher]
                              ↓
                        [Strategist]
                              ↓
                    [HITL: 사용자 확인]
                         ↓        ↓
                    (승인)    (거부/수정)
                       ↓        ↓
                   [Worker]  [Strategist 재실행]
                       ↓
                    [Finalizer]
                       ↓
                   [CSV 저장]
                       ↓
                    [End]
```

### 4.2 노드별 상세 명세

### Node 1: Input Router

- **입력**: 사용자가 CLI로 전달한 입력 (파일 경로 또는 텍스트)
- **역할**: 입력 타입 판별 후 적절한 Loader로 분기 (Conditional Edge)
- **출력 (State 업데이트)**: `input_type` ("image" | "text" | "pdf"), `raw_input`

### Node 2a: Image Loader

- **역할**: 이미지 파일을 읽어 base64로 인코딩, 멀티모달 모델 입력 형식으로 변환
- **출력**: `images: List[str]` (base64 인코딩된 이미지 목록)

### Node 2b: Text Loader

- **역할**: 텍스트 입력을 그대로 State에 저장 (필요시 길이 제한 처리)
- **출력**: `text: str`

### Node 2c: PDF Loader

- **역할**: PDF에서 텍스트 추출, 페이지별 이미지도 추출 (선택적)
- **라이브러리**: `pypdf` 또는 `pdfplumber` (텍스트), `pdf2image` (이미지 추출)
- **출력**: `text: str`, `images: List[str]` (있을 경우)

### Node 3: Researcher

- **모델**: Gemini 2.5 Flash 또는 Claude Sonnet (멀티모달 필요)
- **역할**: 입력 자료를 분석하여 화면/기능 구조를 식별
- **출력**: `analysis: dict` (화면 영역, 주요 기능, UI 요소, 사용자 액션 목록)
- **프롬프트 핵심**: "이 기획서에서 테스트해야 할 기능 영역과 UI 요소, 사용자 액션을 구조화해서 추출해줘"

### Node 4: Strategist

- **모델**: 텍스트 모델 (DeepSeek 또는 Qwen)
- **역할**: 분석 결과를 바탕으로 TC 생성 전략 수립 (어떤 영역에 어떤 관점의 테스트를 몇 개 정도 만들지)
- **출력**: `strategy: dict` (영역별 테스트 방향, 예상 TC 수, 우선순위)

### Node 5: HITL Checkpoint

- **역할**: Strategist의 전략을 사용자에게 보여주고 승인/수정/거부 받기
- **인터페이스**: CLI에서 전략을 출력하고 키보드 입력 대기 (`approve` / `edit` / `reject`)
- **구현**: LangGraph의 `interrupt()` 사용
- **분기**: 승인 → Worker, 거부 → Strategist 재실행, 수정 → 사용자 입력 반영 후 Worker

### Node 6: Worker

- **모델**: 텍스트 모델 (DeepSeek 또는 Qwen)
- **역할**: 확정된 전략에 따라 실제 TC를 표준 양식으로 생성
- **출력 형식**: Pydantic 스키마(아래 5.1)로 강제
- **출력**: `test_cases: List[TestCase]`

### Node 7: Finalizer

- **역할**: 중복 제거, 일련번호 부여, 최종 정렬
- **출력**: `final_test_cases: List[TestCase]`

### Node 8: CSV Writer (그래프 외부)

- **역할**: 최종 TC를 CSV 파일로 저장
- **파일명**: `tc_output_{timestamp}.csv`
- **인코딩**: UTF-8 with BOM (Excel 호환성)

### 4.3 State 정의

LangGraph의 모든 노드가 공유하는 State.

```python
Copyclass TCGeneratorState(TypedDict):
    # 입력
    input_type: Literal["image", "text", "pdf"]
    raw_input: str  # 파일 경로 또는 텍스트

    # 로더 출력
    text: Optional[str]
    images: Optional[List[str]]  # base64

    # 분석 결과
    analysis: Optional[dict]
    strategy: Optional[dict]

    # HITL
    user_decision: Optional[Literal["approve", "edit", "reject"]]
    user_feedback: Optional[str]
    retries: int  # Strategist 재시도 횟수 (최대 2회)

    # 결과
    test_cases: Optional[List[dict]]
    final_test_cases: Optional[List[dict]]
```

## 5. 데이터 스키마

### 5.1 TestCase Pydantic 모델

```python
Copyfrom pydantic import BaseModel, Field
from typing import Optional

class TestCase(BaseModel):
    no: int = Field(description="TC 일련번호")
    major_category: str = Field(description="대분류 (기능 영역)")
    middle_category: str = Field(description="중분류 (세부 기능)")
    minor_category: str = Field(description="소분류 (구체적 시나리오)")
    precondition: str = Field(description="사전조건")
    steps: str = Field(description="재현절차 (1. 2. 3. 형식)")
    expected_result: str = Field(description="기대결과")
    actual_result: str = Field(default="", description="실제결과 (빈 칸)")
    note: str = Field(default="", description="비고")
```

### 5.2 분석 결과 스키마

```python
Copyclass ScreenAnalysis(BaseModel):
    screen_name: str
    feature_areas: List[str]  # 기능 영역 목록
    ui_elements: List[str]    # 버튼, 입력 필드 등
    user_actions: List[str]   # 사용자가 수행 가능한 액션
    edge_cases_hint: List[str]  # 예외 케이스 힌트
```

### 5.3 전략 스키마

```python
Copyclass TestStrategy(BaseModel):
    areas: List[dict]  # 각 영역별 {name, focus, expected_tc_count, priority}
    total_expected_tcs: int
    coverage_focus: str  # "기능 중심" 등
```

## 6. 프로젝트 구조

```
Copytc-auto-creator/
├── .env.example              # API 키 템플릿
├── README.md
├── pyproject.toml            # 의존성 (uv 또는 poetry)
├── src/
│   ├── __init__.py
│   ├── cli.py                # CLI 진입점
│   ├── config.py             # 설정 로딩 (환경 변수, 모델 선택)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py        # Pydantic 모델 (TestCase 등)
│   │   └── llm_clients.py    # OpenRouter LLM 인스턴스 팩토리
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
│   │   ├── state.py          # TCGeneratorState 정의
│   │   ├── builder.py        # LangGraph 그래프 조립
│   │   └── router.py         # Input Router 로직
│   ├── hitl/
│   │   └── cli_prompt.py     # CLI 기반 HITL 인터페이스
│   ├── output/
│   │   └── csv_writer.py
│   └── prompts/
│       ├── researcher.py     # 프롬프트 템플릿
│       ├── strategist.py
│       └── worker.py
├── tests/
│   ├── fixtures/             # 테스트용 샘플 입력
│   └── test_*.py
└── outputs/                  # 생성된 CSV 저장
```

## 7. 환경 설정

### 7.1 필요한 환경 변수 (.env)

```
CopyOPENROUTER_API_KEY=sk-or-v1-...
LANGSMITH_API_KEY=ls__...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=tc-auto-creator

# 모델 선택 (선택적, 기본값 있음)
MODEL_MULTIMODAL=google/gemini-2.5-flash
MODEL_TEXT=deepseek/deepseek-chat
```

### 7.2 의존성 (pyproject.toml 핵심)

```
Copypython = "^3.11"
langchain = "^0.3"
langgraph = "^0.2"
langchain-openai = "^0.2"
pydantic = "^2.0"
pypdf = "^5.0"
pdfplumber = "^0.11"
pillow = "^11.0"
typer = "^0.15"
python-dotenv = "^1.0"
```

## 8. CLI 인터페이스

### 8.1 기본 사용법

```bash
Copy# 이미지 입력
tc-creator --image path/to/screen.png --description "로그인 화면"

# 텍스트 입력
tc-creator --text "사용자가 이메일과 비밀번호로 로그인하는 화면..."

# PDF 입력
tc-creator --pdf path/to/spec.pdf

# 출력 파일 지정
tc-creator --image screen.png --output my_tcs.csv
```

### 8.2 HITL 흐름 예시

```
Copy[Strategist 출력]
다음 영역에 대해 TC를 생성합니다:
1. 이메일 로그인 (예상 TC: 8개) - 우선순위: 높음
2. 비밀번호 찾기 (예상 TC: 5개) - 우선순위: 중간
3. 소셜 로그인 (예상 TC: 6개) - 우선순위: 중간

승인하시겠습니까? [a]pprove / [e]dit / [r]eject:
```

## 9. 단계별 구현 계획

각 Phase는 독립적으로 동작 가능한 산출물이 나오도록 구성. AI에게 작업 시킬 때 Phase 단위로 잘라서 진행 권장.

### Phase 1: 기본 인프라 (1~2일)

- 프로젝트 구조 생성, 의존성 설정
- `.env` 로딩과 OpenRouter LLM 클라이언트 (`llm_clients.py`)
- Pydantic 스키마 정의 (`schemas.py`)
- LangSmith 연결 검증 (간단한 LLM 호출 테스트)
- **검증**: `python -c "from src.models.llm_clients import get_text_llm; print(get_text_llm().invoke('hi'))"`

### Phase 2: 단일 LLM TC 생성 (텍스트만, 그래프 없음) (1~2일)

- LangChain LCEL로 "텍스트 입력 → Worker 프롬프트 → Pydantic 파싱 → CSV 저장"의 일직선 파이프라인
- 멀티 에이전트, HITL, 멀티모달 다 빼고 가장 단순하게
- **검증**: 텍스트 한 단락 입력하면 CSV 파일 생성됨

### Phase 3: 입력 확장 (이미지, PDF) (2~3일)

- Image Loader, PDF Loader 구현
- Worker 프롬프트가 멀티모달 입력도 받을 수 있도록 확장
- 멀티모달 모델로 교체
- **검증**: 이미지/PDF 입력으로 TC 생성됨

### Phase 4: LangGraph로 다중 에이전트 분리 (2~3일)

- State 정의
- Researcher, Strategist, Worker, Finalizer 노드로 분리
- Input Router (Conditional Edge) 추가
- 그래프 조립 (`builder.py`)
- **검증**: 입력 → 분석 → 전략 → 생성 → 저장 흐름이 LangGraph로 동작

### Phase 5: HITL 추가 (1~2일)

- `interrupt()`를 Strategist 후에 배치
- CLI에서 사용자 입력 받는 인터페이스
- 거부 시 재시도 로직 (최대 2회)
- Checkpointer 설정 (SQLite)
- **검증**: 전략 단계에서 멈추고 사용자 응답 후 재개

### Phase 6: 마무리와 품질 개선 (2~3일)

- 프롬프트 튜닝 (실제 기획서로 테스트)
- 에러 핸들링과 재시도
- README 작성
- 팀에게 시범 공개
- **검증**: 실제 기획서로 사용 가능한 수준의 TC 생성 확인

## 10. AI 바이브코딩 시 주의사항

이 문서를 AI에게 줄 때 다음 원칙을 따르면 결과가 더 좋다.

**Phase 단위로 잘라서 요청**한다. 한 번에 전체를 만들라고 하면 품질이 떨어진다. "Phase 1만 먼저 구현해줘"처럼 명확히 범위를 지정한다.

**검증 단계를 먼저 통과시킨 뒤 다음 Phase로 진행**한다. 각 Phase 끝에 명시된 검증 명령이 실제로 동작하는지 확인하고 다음으로 넘어간다.

**프롬프트는 별도 파일(`src/prompts/`)에 분리**해서 관리한다. AI가 코드를 만들 때 프롬프트를 코드 안에 박아두기 쉬운데, 분리해두면 나중에 튜닝이 훨씬 쉽다.

**에러 핸들링은 처음부터 완벽하게 하지 않는다**. Phase 1~5에서는 happy path 위주로 만들고, Phase 6에서 에러 처리를 보강한다. 처음부터 try-except가 많으면 코드가 복잡해져 디버깅이 어려워진다.

**LangSmith 추적을 1단계부터 켜둔다**. 무료 티어로 충분하고, AI가 만든 코드가 실제로 어떻게 동작하는지 시각적으로 보면서 디버깅할 수 있다.

## 11. 향후 확장 (MVP 이후)

다음 기능은 MVP에 포함하지 않으며, 안정화 후 검토.

- URL 입력 (Playwright로 스크린샷)
- Figma 링크 입력 (Figma API)
- Slack 봇 통합
- Google Sheets 직접 출력
- RAG 기반 도메인 특화 (기존 TC를 지식베이스로 활용)
- 워커 동적 확장 (Director 노드 추가)
- 멀티 에이전트 모델 차등 배치 최적화