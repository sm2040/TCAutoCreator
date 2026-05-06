"""입력 타입 라우팅 로직."""

from __future__ import annotations

from src.graph.state import TCGeneratorState


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
    """HITL 결과에 따라 다음 노드를 결정한다."""

    decision = state.get("user_decision")
    if decision == "approve":
        return "worker"
    if decision == "edit":
        return "worker"
    if decision == "reject":
        if state.get("retries", 0) >= 2:
            return "worker"
        return "strategist"
    raise ValueError("HITL decision이 유효하지 않습니다.")
