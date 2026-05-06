"""Finalizer 노드 구현."""

from __future__ import annotations

from src.graph.state import TCGeneratorState
from src.models.schemas import TestCase


def finalizer_node(state: TCGeneratorState) -> TCGeneratorState:
    """중복을 정리하고 최종 번호를 재부여한다.

    입력 state key:
    - test_cases

    출력 state key:
    - final_test_cases
    """

    test_cases = state.get("test_cases") or []
    deduplicated: list[TestCase] = []
    seen_keys: set[tuple[str, str, str, str]] = set()

    for test_case in test_cases:
        dedupe_key = (
            test_case.major_category,
            test_case.middle_category,
            test_case.minor_category,
            test_case.expected_result,
        )
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        deduplicated.append(test_case)

    renumbered = [
        test_case.model_copy(update={"no": index})
        for index, test_case in enumerate(deduplicated, start=1)
    ]

    updated_state = dict(state)
    updated_state["final_test_cases"] = renumbered
    return updated_state
