"""TC 생성 그래프 조립."""

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.agents.finalizer import finalizer_node
from src.agents.researcher import researcher_node
from src.agents.strategist import strategist_node
from src.agents.worker import worker_node
from src.graph.router import route_input, route_post_review
from src.graph.state import TCGeneratorState
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
    """Strategist 결과를 사용자 검토에 맡긴다."""

    strategy = state.get("strategy")
    if strategy is None:
        raise ValueError("HITL 실행 전에 strategy가 필요합니다.")

    review_payload = interrupt(
        {
            "kind": "strategy_review",
            "strategy": strategy.model_dump(mode="json"),
            "retries": state.get("retries", 0),
            "user_feedback": state.get("user_feedback") or "",
        }
    )

    decision = review_payload.get("decision", "approve")
    feedback = review_payload.get("feedback", "")

    updated_state = dict(state)
    updated_state["user_decision"] = decision
    updated_state["user_feedback"] = feedback
    if decision == "reject":
        updated_state["retries"] = state.get("retries", 0) + 1
    return updated_state


def build_graph():
    """Phase 4용 LangGraph를 조립한다."""

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

    return graph.compile(checkpointer=MemorySaver())
