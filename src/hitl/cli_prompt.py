"""CLI 기반 HITL 인터페이스.

Strategist 결과를 사용자에게 보여주고, 승인 / 수정 / 거부 결정을 받아
LangGraph `interrupt()` resume payload로 변환한다.
"""

from __future__ import annotations

from typing import Any, Mapping

import typer

from src.hitl.protocol import (
    DECISION_APPROVE,
    DECISION_EDIT,
    DECISION_REJECT,
    MAX_HITL_RETRIES,
    parse_strategy_review_payload,
)
from src.models.schemas import TestStrategy


# 짧은 단축키 → 정식 결정값 매핑
_DECISION_ALIASES: dict[str, str] = {
    "a": DECISION_APPROVE,
    "approve": DECISION_APPROVE,
    "e": DECISION_EDIT,
    "edit": DECISION_EDIT,
    "r": DECISION_REJECT,
    "reject": DECISION_REJECT,
}


def format_strategy_preview(
    strategy: TestStrategy,
    retries: int = 0,
    previous_feedback: str = "",
    max_retries: int = MAX_HITL_RETRIES,
) -> str:
    """전략 요약 문자열을 생성한다.

    Args:
        strategy: 검토 대상 테스트 전략.
        retries: 지금까지 거부 후 재시도된 횟수.
        previous_feedback: 직전 라운드에서 사용자가 남긴 피드백.
        max_retries: 거부 가능 최대 횟수. 안내 문구에 사용된다.
    """

    lines = [
        typer.style("[Strategist 출력]", fg=typer.colors.CYAN, bold=True),
        f"총 예상 테스트 케이스 수: {strategy.total_expected_tcs}",
        f"커버리지 기준: {strategy.coverage_focus}",
    ]

    if retries > 0:
        remaining = max(max_retries - retries, 0)
        lines.append(
            typer.style(
                f"재시도 라운드: {retries} (남은 거부 가능 횟수: {remaining})",
                fg=typer.colors.YELLOW,
            )
        )
        if previous_feedback:
            lines.append(
                typer.style(
                    f"직전 피드백: {previous_feedback}",
                    fg=typer.colors.YELLOW,
                )
            )

    lines.extend(["", typer.style("영역별 전략:", bold=True)])

    for index, area in enumerate(strategy.areas, start=1):
        lines.append(
            f"{index}. {area.name} | 우선순위: {area.priority} | 예상 TC: {area.expected_tc_count}"
        )
        lines.append(f"   초점: {area.focus}")

    return "\n".join(lines)


def _normalize_decision(raw: str) -> str | None:
    """입력 문자열을 정식 결정 값으로 변환한다. 잘못된 입력이면 None."""

    return _DECISION_ALIASES.get(raw.strip().lower())


def _prompt_decision() -> str:
    """승인/수정/거부 중 하나를 받아 정식 결정 값으로 반환한다."""

    while True:
        raw = typer.prompt(
            "검토 결과를 입력해주세요 - 승인(a) / 수정(e) / 거부(r)",
            default="a",
            show_default=True,
        )
        decision = _normalize_decision(raw)
        if decision is not None:
            return decision
        typer.secho(
            "a, e, r 중 하나를 입력해주세요.",
            fg=typer.colors.RED,
        )


def _prompt_feedback(decision: str) -> str:
    """edit/reject 결정에 대한 피드백을 받는다. 빈 입력이면 재질문."""

    if decision == DECISION_EDIT:
        message = "어떻게 수정할지 구체적으로 적어주세요"
    else:
        message = "거부 사유와 보강이 필요한 부분을 적어주세요"

    while True:
        feedback = typer.prompt(message, default="", show_default=False).strip()
        if feedback:
            return feedback
        typer.secho(
            "피드백은 비워둘 수 없습니다. 한 줄이라도 입력해주세요.",
            fg=typer.colors.RED,
        )


def prompt_hitl_decision(
    strategy: TestStrategy,
    retries: int = 0,
    previous_feedback: str = "",
    max_retries: int = MAX_HITL_RETRIES,
) -> dict[str, Any]:
    """전략 검토 결과를 사용자에게 받아 LangGraph resume payload로 변환한다.

    Args:
        strategy: 사용자에게 보여줄 테스트 전략.
        retries: 거부 후 재시도된 횟수. 안내 문구에만 사용된다.
        previous_feedback: 직전 라운드에서 받은 피드백. 안내 문구에만 사용된다.
        max_retries: 거부 가능 최대 횟수. 안내 문구에만 사용된다.

    Returns:
        ``{"decision": "approve|edit|reject", "feedback": str}`` 형태의 dict.
        approve일 때 feedback은 빈 문자열이다.
    """

    typer.echo(
        format_strategy_preview(
            strategy,
            retries=retries,
            previous_feedback=previous_feedback,
            max_retries=max_retries,
        )
    )
    typer.echo("")

    decision = _prompt_decision()

    if decision == DECISION_APPROVE:
        typer.secho("전략을 승인했습니다. Worker 단계로 진행합니다.", fg=typer.colors.GREEN)
        return {"decision": DECISION_APPROVE, "feedback": ""}

    feedback = _prompt_feedback(decision)

    if decision == DECISION_EDIT:
        typer.secho(
            "수정 의견을 반영해 후속 단계를 진행합니다.",
            fg=typer.colors.GREEN,
        )
    else:
        remaining = max(max_retries - (retries + 1), 0)
        typer.secho(
            f"전략을 거부했습니다. Strategist를 재실행합니다. (남은 거부 가능 횟수: {remaining})",
            fg=typer.colors.YELLOW,
        )

    return {"decision": decision, "feedback": feedback}


def parse_review_payload(payload: Mapping[str, Any]) -> TestStrategy:
    """`hitl_review_node`가 발행한 interrupt payload를 검증하고 전략을 복원한다.

    하위 호환을 위해 strategy만 반환한다. retries / max_retries / feedback이
    필요하다면 ``protocol.parse_strategy_review_payload``를 직접 사용한다.
    """

    strategy, _retries, _max_retries, _feedback = parse_strategy_review_payload(payload)
    return strategy
