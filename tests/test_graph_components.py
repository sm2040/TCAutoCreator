"""그래프 구성요소 단위 테스트."""

from src.agents.finalizer import finalizer_node
from src.graph.router import route_input, route_post_review
from src.models.schemas import TestCase


def test_route_input_returns_expected_loader() -> None:
    assert route_input({"input_type": "text", "raw_input": "", "description": None, "text": None, "images": None, "analysis": None, "strategy": None, "user_decision": None, "user_feedback": None, "retries": 0, "test_cases": None, "final_test_cases": None}) == "text_loader"
    assert route_input({"input_type": "image", "raw_input": "", "description": None, "text": None, "images": None, "analysis": None, "strategy": None, "user_decision": None, "user_feedback": None, "retries": 0, "test_cases": None, "final_test_cases": None}) == "image_loader"
    assert route_input({"input_type": "pdf", "raw_input": "", "description": None, "text": None, "images": None, "analysis": None, "strategy": None, "user_decision": None, "user_feedback": None, "retries": 0, "test_cases": None, "final_test_cases": None}) == "pdf_loader"


def test_finalizer_deduplicates_and_renumbers() -> None:
    state = {
        "input_type": "text",
        "raw_input": "sample",
        "description": None,
        "text": "sample",
        "images": None,
        "analysis": None,
        "strategy": None,
        "user_decision": None,
        "user_feedback": None,
        "retries": 0,
        "test_cases": [
            TestCase(
                no=9,
                major_category="로그인",
                middle_category="정상 로그인",
                minor_category="성공",
                precondition="계정 존재",
                steps="1. 입력\n2. 클릭",
                expected_result="로그인 성공",
            ),
            TestCase(
                no=10,
                major_category="로그인",
                middle_category="정상 로그인",
                minor_category="성공",
                precondition="계정 존재",
                steps="1. 입력\n2. 클릭",
                expected_result="로그인 성공",
            ),
        ],
        "final_test_cases": None,
    }

    result = finalizer_node(state)

    assert result["final_test_cases"] is not None
    assert len(result["final_test_cases"]) == 1
    assert result["final_test_cases"][0].no == 1


def test_route_post_review_handles_decisions() -> None:
    assert route_post_review({"user_decision": "approve", "retries": 0}) == "worker"
    assert route_post_review({"user_decision": "edit", "retries": 0}) == "worker"
    assert route_post_review({"user_decision": "reject", "retries": 0}) == "strategist"
    assert route_post_review({"user_decision": "reject", "retries": 2}) == "worker"
