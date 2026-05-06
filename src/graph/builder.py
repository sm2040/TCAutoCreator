"""TC 생성 그래프 조립."""

from __future__ import annotations

from typing import Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.agents.finalizer import finalizer_node
from src.agents.researcher import researcher_node
from src.agents.strategist import strategist_node
from src.agents.worker import worker_node
from src.graph.router import route_input, route_post_review
from src.graph.state import TCGeneratorState
from src.hitl.protocol import build_strategy_review_payload
from src.loaders.image_loader import load_images
from src.loaders.pdf_loader import load_pdf_text
from src.loaders.text_loader import load_text_input


def text_loader_node(state: TCGeneratorState) -> TCGeneratorState:
    """텍스트 입력을 정리해 state에 적재한다."""

    updated_state = dict(state)
    updated_state["text"] = load_text_input(state["raw_input"])
    return updated_state


def image_loader_node(state: TCGeneratorState) -> TCGeneratorState:
    """이미지 입력 경로를 data URL 목록으로 변환한다."""

    image_paths = [line for line in state["raw_input"].splitlines() if line.strip()]
    updated_state = dict(state)
    updated_state["images"] = load_images(image_paths)
    return updated_state


def pdf_loader_node(state: TCGeneratorState) -> TCGeneratorState:
    """PDF 입력에서 텍스트를 추출해 state에 적재한다."""

    updated_state = dict(state)
    updated_state["text"] = load_pdf_text(state["raw_input"])
    return updated_state


def hitl_review_node(state: TCGeneratorState) -> TCGeneratorState:
    """Strategist 결과를 사용자 검토에 맡긴다.

    `interrupt()`로 그래프를 정지시키고, CLI(또는 다른 인터페이스)가
    `Command(resume=...)`로 재개할 때까지 대기한다.

    입력 state key:
    - strategy
    - retries
    - user_feedback (직전 라운드 피드백)

    출력 state key:
    - user_decision
    - user_feedback (이번 라운드 피드백으로 갱신)
    - retries (reject일 때만 +1)
    """

    strategy = state.get("strategy")
    if strategy is None:
        raise ValueError("HITL 실행 전에 strategy가 필요합니다.")

    payload = build_strategy_review_payload(
        strategy=strategy,
        retries=state.get("retries", 0),
        user_feedback=state.get("user_feedback") or "",
    )
    review_payload = interrupt(payload)

    if not isinstance(review_payload, dict):
        raise ValueError("HITL resume 값은 dict여야 합니다.")

    decision = review_payload.get("decision", "approve")
    feedback = review_payload.get("feedback", "") or ""

    updated_state = dict(state)
    updated_state["user_decision"] = decision
    updated_state["user_feedback"] = feedback
    if decision == "reject":
        updated_state["retries"] = state.get("retries", 0) + 1
    return updated_state


def build_graph(checkpointer: Optional[BaseCheckpointSaver] = None):
    """TC 생성 LangGraph를 조립한다.

    Args:
        checkpointer: 그래프 상태 영속화를 담당할 checkpointer.
            지정하지 않으면 `MemorySaver()`를 사용한다.
            테스트나 영속 saver(SQLite 등) 교체를 위해 외부에서 주입할 수 있다.
    """

    graph = StateGraph(TCGeneratorState)

    graph.add_node("text_loader", text_loader_node)
    graph.add_node("image_loader", image_loader_node)
    graph.add_node("pdf_loader", pdf_loader_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("strategist", strategist_node)
    graph.add_node("hitl_review", hitl_review_node)
    graph.add_node("worker", worker_node)
    graph.add_node("finalizer", finalizer_node)

    graph.add_conditional_edges(
        START,
        route_input,
        {
            "text_loader": "text_loader",
            "image_loader": "image_loader",
            "pdf_loader": "pdf_loader",
        },
    )

    graph.add_edge("text_loader", "researcher")
    graph.add_edge("image_loader", "researcher")
    graph.add_edge("pdf_loader", "researcher")
    graph.add_edge("researcher", "strategist")
    graph.add_edge("strategist", "hitl_review")
    graph.add_conditional_edges(
        "hitl_review",
        route_post_review,
        {
            "worker": "worker",
            "strategist": "strategist",
        },
    )
    graph.add_edge("worker", "finalizer")
    graph.add_edge("finalizer", END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
