# TC Auto-Creator

기획서(텍스트, 이미지, PDF)를 입력받아 QA 테스트 케이스 초안을 생성하는 CLI 프로젝트입니다.

## 현재 범위

현재는 `Phase 6`까지 목표한 모든 기능(품질 보강 및 HITL 포함)이 완료된 MVP 완성 상태입니다.

- 환경 변수 및 OpenRouter/LangSmith 연동
- Pydantic 스키마 및 LLM 클라이언트 팩토리
- LangGraph 기반 워크플로우 (`Input Router → Loader → Researcher → Strategist → HITL → Worker → Finalizer`)
- 텍스트/이미지/PDF 다양한 입력 소스 처리
- **HITL (Human-in-the-Loop)**: 테스트 전략 생성 직후 사용자 개입(승인/수정/거부) 기능
- **자동 에러 복구**: `OutputFixingParser`를 통한 LLM 파싱 오류 자동 재시도 및 수정
- 출력 전용 CSV 저장 및 사전 경로 검증

## 빠른 시작

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
cp .env.example .env
```

`.env`에 `OPENROUTER_API_KEY`와 `LANGSMITH_API_KEY`를 채운 뒤 아래 명령으로 연결을 확인할 수 있습니다.

```bash
python -c "from src.models.llm_clients import get_text_llm; print(get_text_llm().invoke('안녕').content)"
```

텍스트에서 테스트 케이스 CSV를 생성하려면:

```bash
.venv/bin/python -m src.cli generate \
  --text "사용자가 이메일과 비밀번호를 입력해 로그인할 수 있다. 비밀번호가 틀리면 오류 메시지를 보여준다." \
  --output outputs/sample_tcs.csv
```

이미지에서 테스트 케이스 CSV를 생성하려면:

```bash
.venv/bin/python -m src.cli generate \
  --image tests/fixtures/login_mock.png \
  --description "로그인 화면 시안" \
  --output outputs/sample_tcs_image.csv
```

PDF에서 테스트 케이스 CSV를 생성하려면:

```bash
.venv/bin/python -m src.cli generate \
  --pdf tests/fixtures/simple_spec.pdf \
  --output outputs/sample_tcs_pdf.csv
```

## HITL (Human-in-the-Loop) 흐름

`generate` 명령어를 실행하면, LLM이 문서를 분석한 뒤 **Strategist**가 테스트 전략(예상 TC 수, 커버리지 방향 등)을 먼저 화면에 출력하고 대기합니다.

```
검토 결과를 입력해주세요 - 승인(a) / 수정(e) / 거부(r) [a]:
```

- **a (승인)**: 해당 전략을 바탕으로 테스트 케이스를 생성합니다.
- **e (수정)**: 예) "간편결제 케이스를 더 추가해 줘" 처럼 피드백을 주면, 이를 반영해 전략을 재수립합니다.
- **r (거부)**: 해당 전략을 폐기하고, 다시 분석하여 새로운 전략을 제시합니다.

## 구조

문서 기반 설계는 아래 파일을 기준으로 합니다.

- `DESIGN.md`
- `TASKS.md`
- `Test Case AutoCreator_Implementation Plan.md`
