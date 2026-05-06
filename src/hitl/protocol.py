"""HITL interrupt 페이로드 스키마와 공유 상수.

`hitl_review_node`(LangGraph)와 CLI(`_resolve_hitl_interrupt`)는 같은 페이로드
구조를 주고받아야 한다. 이 모듈은 그 단일 출처(SSOT)를 제공한다.

- `INTERRUPT_KIND_STRATEGY_REVIEW`: payload 식별자
- `MAX_HITL_RETRIES`: 거부(reject) 후 Strategist 재실행 가능 횟수
- `build_strategy_review_payload`: 노드 측 페이로드 빌더
- `parse_strategy_review_payload`: CLI 측 페이로드 파서
- `ReviewPayload`, `ReviewDecision`: 타입 정의
"""

from __future__ import annotations

from typing import Any, Literal, Mapping, TypedDict

from src.models.schemas import TestStrategy


# 사용자 결정 정식 값
DECISION_APPROVE = "approve"
DECISION_EDIT = "edit"
DECISION_REJECT = "reject"

ReviewDecision = Literal["approve", "edit", "reject"]

# interrupt 페이로드 식별자
INTERRUPT_KIND_STRATEGY_REVIEW = "strategy_review"

# Strategist 거부 후 재시도 가능한 최대 횟수.
# 이 값에 도달하면 router는 사용자가 거부하더라도 worker로 강제 진행한다.
MAX_HITL_RETRIES = 2


class ReviewPayload(TypedDict):
    """Strategist 검토 요청 페이로드."""

    kind: Literal["strategy_review"]
    strategy: dict[str, Any]
    retries: int
    max_retries: int
    user_feedback: str


def build_strategy_review_payload(
    strategy: TestStrategy,
    retries: int,
    user_feedback: str,
) -> ReviewPayload:
    """그래프 노드에서 사용자에게 보낼 검토 페이로드를 만든다."""

    return ReviewPayload(
        kind=INTERRUPT_KIND_STRATEGY_REVIEW,
        strategy=strategy.model_dump(mode="json"),
        retries=int(retries),
        max_retries=MAX_HITL_RETRIES,
        user_feedback=user_feedback or "",
    )


def parse_strategy_review_payload(
    payload: Mapping[str, Any],
) -> tuple[TestStrategy, int, int, str]:
    """CLI에서 받은 interrupt 페이로드를 검증하고 분해한다.

    Returns:
        ``(strategy, retries, max_retries, previous_feedback)`` 튜플.
    """

    if not isinstance(payload, Mapping):
        raise ValueError("HITL interrupt payload는 매핑이어야 합니다.")

    kind = payload.get("kind")
    if kind != INTERRUPT_KIND_STRATEGY_REVIEW:
        raise ValueError(
            f"지원하지 않는 HITL interrupt 종류입니다: {kind!r}"
        )

    strategy_data = payload.get("strategy")
    if strategy_data is None:
        raise ValueError("HITL interrupt payload에 strategy가 비어 있습니다.")

    strategy = TestStrategy.model_validate(strategy_data)
    retries = int(payload.get("retries", 0) or 0)
    max_retries = int(payload.get("max_retries", MAX_HITL_RETRIES) or MAX_HITL_RETRIES)
    previous_feedback = str(payload.get("user_feedback", "") or "")

    return strategy, retries, max_retries, previous_feedback
