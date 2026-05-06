# TC Auto-Creator

기획서(텍스트, 이미지, PDF)를 입력받아 QA 테스트 케이스 초안을 생성하는 CLI 프로젝트입니다.

## 현재 범위

현재는 `Phase 4`의 LangGraph 기반 입력 라우팅/에이전트 분리 구조까지 구현된 상태입니다.

- 프로젝트 구조
- 환경 변수 로딩
- OpenRouter/LangSmith 설정 모델
- Pydantic 스키마
- LLM 클라이언트 팩토리
- LangGraph 기반 `Input Router → Loader → Researcher → Strategist → Worker → Finalizer` 흐름
- 텍스트 입력 기반 TC 생성 체인
- 이미지 입력 기반 TC 생성 체인
- PDF 입력 기반 TC 생성 체인
- CSV 저장

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

## 구조

문서 기반 설계는 아래 파일을 기준으로 합니다.

- `DESIGN.md`
- `TASKS.md`
- `Test Case AutoCreator_Implementation Plan.md`
