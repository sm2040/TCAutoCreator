# TC Auto-Creator Tasks

## 현재 상태

- 프로젝트: `TC Auto-Creator`
- 현재 Phase: `MVP 완료` (Phase 6 달성)
- 상태: HITL 흐름 완성, 프롬프트 튜닝 및 예외 처리, 회귀 검증 완료
- 최종 업데이트: `2026-05-07`

## 진행 중

- (MVP 완성으로 인한 대기)

### 향후 기능 추가 (MVP 이후)
- URL 입력 (스크린샷 연동) 지원
- Figma API 연동 지원
- Slack 봇 통합
- Google Sheets 연동
- RAG 기반 도메인 특화 TC

## 완료

### 프로젝트 기본 구조

- 프로젝트 폴더 구조 생성
- `src/`, `tests/`, `outputs/` 디렉터리 구성
- 패키지 초기화 파일 추가

### 환경 및 의존성

- `pyproject.toml` 작성
- `.venv` 생성
- editable install로 의존성 설치
- `.env.example` 작성
- `.gitignore` 작성

### Phase 1 구현

- [src/config.py](/Users/smjung/Documents/TCAutoCreator/src/config.py) 작성
- [src/models/llm_clients.py](/Users/smjung/Documents/TCAutoCreator/src/models/llm_clients.py) 작성
- [src/models/schemas.py](/Users/smjung/Documents/TCAutoCreator/src/models/schemas.py) 작성
- 기본 CLI([src/cli.py](/Users/smjung/Documents/TCAutoCreator/src/cli.py)) 작성
- README 초안 작성

### Phase 2 구현

- [src/prompts/worker.py](/Users/smjung/Documents/TCAutoCreator/src/prompts/worker.py) 작성
- [src/agents/worker.py](/Users/smjung/Documents/TCAutoCreator/src/agents/worker.py) 작성
- [src/output/csv_writer.py](/Users/smjung/Documents/TCAutoCreator/src/output/csv_writer.py) 작성
- `generate` CLI 명령 추가
- 샘플 CSV 파일 `outputs/phase2_smoke.csv` 생성 확인

### Phase 3 구현

- [src/loaders/text_loader.py](/Users/smjung/Documents/TCAutoCreator/src/loaders/text_loader.py) 작성
- [src/loaders/image_loader.py](/Users/smjung/Documents/TCAutoCreator/src/loaders/image_loader.py) 작성
- [src/loaders/pdf_loader.py](/Users/smjung/Documents/TCAutoCreator/src/loaders/pdf_loader.py) 작성
- `Worker` 멀티모달 입력 경로 추가
- CLI `generate` 명령에 `--image`, `--pdf`, `--description` 추가
- 테스트 fixture 이미지/PDF 추가
- `gpt-oss-20b:free` 기준 이미지/PDF 실검증 완료

### Phase 4 구현

- [src/graph/state.py](/Users/smjung/Documents/TCAutoCreator/src/graph/state.py) 확장
- [src/graph/router.py](/Users/smjung/Documents/TCAutoCreator/src/graph/router.py) 구현
- [src/graph/builder.py](/Users/smjung/Documents/TCAutoCreator/src/graph/builder.py) 구현
- [src/agents/researcher.py](/Users/smjung/Documents/TCAutoCreator/src/agents/researcher.py) 구현
- [src/agents/strategist.py](/Users/smjung/Documents/TCAutoCreator/src/agents/strategist.py) 구현
- [src/agents/finalizer.py](/Users/smjung/Documents/TCAutoCreator/src/agents/finalizer.py) 구현
- `generate` CLI를 LangGraph 실행 기반으로 전환
- `Researcher → Strategist → Worker → Finalizer` 노드 체인 연결
- 텍스트/이미지/PDF 입력 라우팅 실검증 완료

### Phase 5 구현

- Strategist 결과 승인/수정/거부 인터페이스 구현 (`src/hitl/cli_prompt.py`)
- `interrupt()` 기반 재개 흐름 연결 (`src/graph/builder.py`)
- Checkpointer 구성 및 resume 루프 보호 연결 (`src/cli.py`)
- 거부 시 재시도 로직 추가 및 `MAX_HITL_RETRIES` 적용 (`src/graph/router.py`)

### Phase 6 구현

- 프롬프트 튜닝 (Researcher/Strategist/Worker 가이드라인 및 출력 규칙 강화)
- 파싱 에러 방지용 `OutputFixingParser` 적용 (Worker, Strategist, Researcher)
- 존재하지 않는 파일 읽기 사전 방지 (Pre-validation)
- 복잡한 엣지 케이스 포함 기획서(`tests/fixtures/complex_spec.md`) 회귀 검증 완료
- README.md 정리 및 HITL 사용성 문서화 완료

### 로컬 검증 완료 항목

- `python3 -m compileall src tests` 통과
- `.venv/bin/python -m src.cli --help` 통과
- `.venv/bin/python -c "from src.models.llm_clients import get_text_llm; print('llm module ok')"` 통과
- CSV writer 단독 스모크 테스트 통과
- 텍스트 입력 실검증: `outputs/sample_tcs_gptoss20b_free.csv` 생성
- 이미지 입력 실검증: `outputs/sample_tcs_image.csv` 생성
- PDF 입력 실검증: `outputs/sample_tcs_pdf.csv` 생성
- LangGraph 텍스트 입력 실검증: `outputs/phase4_text_graph.csv` 생성
- LangGraph 이미지 입력 실검증: `outputs/phase4_image_graph.csv` 생성
- LangGraph PDF 입력 실검증: `outputs/phase4_pdf_graph.csv` 생성
- Phase 6 텍스트 및 예외 흐름(수정 요청) 회귀 검증 성공

## 막힌 부분 / 결정 필요 사항

- PDF의 이미지 추출은 아직 미구현 (추후 고도화 시 진행 필요)
- `pytest`는 아직 도입 전이며, 현재 CLI 테스트로 갈음함

## 다음 세션 시작 시 컨텍스트

다음 세션에서는 팀원 시연 및 피드백 적용을 진행하거나 MVP 이후의 추가 기능(URL/Figma 확장 등)을 시작할 수 있습니다.

## 자주 쓰는 명령

### 환경 셋업

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -e .
```

### Phase 1 검증

```bash
.venv/bin/python -c "from src.models.llm_clients import get_text_llm; print(get_text_llm().invoke('안녕').content)"
```

### Phase 3 CLI 실행

```bash
.venv/bin/python -m src.cli generate --text "테스트할 기획서 내용..."
.venv/bin/python -m src.cli generate --image path/to/screen.png --description "로그인 화면"
.venv/bin/python -m src.cli generate --pdf path/to/spec.pdf
```

### LangSmith 확인

- 대시보드: [smith.langchain.com](https://smith.langchain.com)
- 프로젝트명: `tc-auto-creator`

## 메모

- 멀티 페이지 PDF의 이미지 추출 전략을 검토할 것
- Strategist 단계에서 한국어 출력 강제 전략을 따로 둘지 검토할 것
