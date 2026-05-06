"""CLI 기반 HITL 인터페이스."""

from __future__ import annotations

from typing import Any

import typer

from src.models.schemas import TestStrategy


def format_strategy_preview(strategy: TestStrategy) -> str:
    """전략 요약 문자열을 생성한다."""

    lines = [
        "[Strategist 출력]",
        f"총 예상 테스트 케이스 수: {strategy.total_expected_tcs}",
        f"커버리지 기준: {strategy.coverage_focus}",
        "",
        "영역별 전략:",
    ]

    for index, area in enumerate(strategy.areas, start=1):
        lines.append(
            f"{index}. {area.name} | 우선순위: {area.priority} | 예상 TC: {area.expected_tc_count}"
        )
        lines.append(f"   초점: {area.focus}")

    return "\n".join(lines)


def prompt_hitl_decision(strategy: TestStrategy) -> dict[str, Any]:
    """전략 검토 결과를 사용자에게 받아 LangGraph resume payload로 변환한다."""

    typer.echo(format_strategy_preview(strategy))
    decision = typer.prompt(
        "승인(a) / 수정(e) / 거부(r)",
        default="a",
        show_default=True,
    ).strip().lower()

    while decision not in {"a", "approve", "e", "edit", "r", "reject"}:
        decision = typer.prompt("a, e, r 중 하나를 입력해주세요").strip().lower()

    if decision in {"a", "approve"}:
        return {"decision": "approve", "feedback": ""}

    feedback = typer.prompt(
        "피드백을 입력해주세요",
        default="",
        show_default=False,
    ).strip()

    normalized = "edit" if decision in {"e", "edit"} else "reject"
    return {"decision": normalized, "feedback": feedback}
