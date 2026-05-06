"""CLI 진입점을 제공한다."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import typer
from langgraph.types import Command

from src.config import load_settings
from src.graph.builder import build_graph
from src.hitl.cli_prompt import prompt_hitl_decision
from src.models.schemas import TestStrategy
from src.output.csv_writer import write_test_cases_to_csv


app = typer.Typer(help="기획서 기반 테스트 케이스 초안 생성 도구")


def _resolve_hitl_interrupt(graph, config: dict[str, object]) -> None:
    """그래프 interrupt를 CLI 입력으로 해소한다."""

    while True:
        snapshot = graph.get_state(config)
        tasks = snapshot.tasks or ()
        interrupts = [
            interrupt_obj
            for task in tasks
            for interrupt_obj in task.interrupts
        ]
        if not interrupts:
            return

        payload = interrupts[0].value
        if payload.get("kind") != "strategy_review":
            raise ValueError("지원하지 않는 HITL interrupt payload입니다.")

        strategy = TestStrategy.model_validate(payload["strategy"])
        resume_value = prompt_hitl_decision(strategy)
        graph.invoke(Command(resume=resume_value), config)


@app.command()
def doctor() -> None:
    """환경 설정 로딩 여부를 확인한다."""

    settings = load_settings()
    typer.echo("설정 로딩 성공")
    typer.echo(f"텍스트 모델: {settings.model_text}")
    typer.echo(f"멀티모달 모델: {settings.model_multimodal}")
    typer.echo(f"LangSmith 프로젝트: {settings.langsmith_project}")


@app.command()
def generate(
    text: str | None = typer.Option(
        None,
        "--text",
        help="테스트 케이스를 생성할 기획/요구사항 텍스트",
    ),
    image: list[Path] | None = typer.Option(
        None,
        "--image",
        help="분석할 이미지 파일 경로. 여러 번 지정할 수 있습니다.",
    ),
    pdf: Path | None = typer.Option(
        None,
        "--pdf",
        help="분석할 PDF 파일 경로",
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        help="이미지/PDF에 대한 추가 설명",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help="출력 CSV 경로. 지정하지 않으면 outputs/ 아래에 자동 생성됩니다.",
    ),
) -> None:
    """텍스트, 이미지, PDF 입력으로 테스트 케이스 CSV를 생성한다."""

    selected_inputs = sum(
        [
            1 if text else 0,
            1 if image else 0,
            1 if pdf else 0,
        ]
    )
    if selected_inputs != 1:
        typer.secho(
            "--text, --image, --pdf 중 하나만 지정해주세요.",
            fg="red",
        )
        raise typer.Exit(code=1)

    if text:
        input_type = "text"
        raw_input = text
    elif image:
        input_type = "image"
        raw_input = "\n".join(str(path) for path in image)
    else:
        input_type = "pdf"
        raw_input = str(pdf)

    initial_state = {
        "input_type": input_type,
        "raw_input": raw_input,
        "description": description,
        "text": None,
        "images": None,
        "analysis": None,
        "strategy": None,
        "user_decision": None,
        "user_feedback": None,
        "retries": 0,
        "test_cases": None,
        "final_test_cases": None,
    }
    graph = build_graph()
    config = {"configurable": {"thread_id": str(uuid4())}}

    try:
        result = graph.invoke(initial_state, config)
        _resolve_hitl_interrupt(graph, config)
        result = graph.get_state(config).values
        test_cases = result.get("final_test_cases") or []
    except (FileNotFoundError, ValueError) as exc:
        typer.secho(str(exc), fg="red")
        raise typer.Exit(code=1) from exc

    output_path = write_test_cases_to_csv(test_cases, str(output) if output else None)

    typer.echo(f"{len(test_cases)}개의 테스트 케이스를 생성했습니다.")
    typer.echo(f"CSV 저장 위치: {output_path.resolve()}")


if __name__ == "__main__":
    app()
