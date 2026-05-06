"""LangGraph 상태 스키마."""

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from src.models.schemas import ScreenAnalysis, TestCase, TestStrategy


class TCGeneratorState(TypedDict):
    """TC 생성 그래프의 공용 상태."""

    input_type: Literal["image", "text", "pdf"]
    raw_input: str
    description: Optional[str]
    text: Optional[str]
    images: Optional[List[str]]
    analysis: Optional[ScreenAnalysis]
    strategy: Optional[TestStrategy]
    user_decision: Optional[Literal["approve", "edit", "reject"]]
    user_feedback: Optional[str]
    retries: int
    test_cases: Optional[List[TestCase]]
    final_test_cases: Optional[List[TestCase]]
