"""입력 타입 및 HITL 결과 라우팅 로직."""

from __future__ import annotations

from src.graph.state import TCGeneratorState
from src.hitl.protocol import (
    DECISION_APPROVE,
    DECISION_EDIT,
    DECISION_REJECT,
    MAX_HITL_RETRIES,
)


def route_input(state: TCGeneratorState) -> str:
    """입력 타입에 따라 다음 로더 노드명을 반환한다."""

    input_type = state["input_type"]
    if input_type == "text":
        return "text_loader"
    if input_type == "image":
        return "image_loader"
    if input_type == "pdf":
        return "pdf_loader"
    raise ValueError(f"지원하지 않는 input_type입니다: {input_type}")


def route_post_review(state: TCGeneratorState) -> str:
    """HITL 결과에 따라 다음 노드를 결정한다.

    - approve: 사용자가 전략을 승인 → 그대로 worker
    - edit: 사용자가 전략에 수정 의견 제시 → 그대로 worker (피드백은 state에 보관)
    - reject: 사용자가 전략을 거부 → 재시도 한도 내라면 strategist 재실행,
      한도를 넘겼으면 worker로 강제 진행
    """

    decision = state.get("user_decision")
    if decision == DECISION_APPROVE:
        return "worker"
    if decision == DECISION_EDIT:
        return "worker"
    if decision == DECISION_REJECT:
        if state.get("retries", 0) >= MAX_HITL_RETRIES:
            return "worker"
        return "strategist"
    raise ValueError(f"HITL decision이 유효하지 않습니다: {decision!r}")
