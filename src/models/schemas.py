"""TC Auto-Creator의 정형 데이터 스키마."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """표준 테스트 케이스 한 건."""

    no: int = Field(description="TC 일련번호")
    major_category: str = Field(description="대분류 (기능 영역)")
    middle_category: str = Field(description="중분류 (세부 기능)")
    minor_category: str = Field(description="소분류 (구체적 시나리오)")
    precondition: str = Field(description="사전조건")
    steps: str = Field(description="재현절차 (1. 2. 3. 형식)")
    expected_result: str = Field(description="기대결과")
    actual_result: str = Field(default="", description="실제결과 (빈 칸)")
    note: str = Field(default="", description="비고")


class TestCaseBatch(BaseModel):
    """테스트 케이스 목록 응답."""

    test_cases: List[TestCase] = Field(description="생성된 테스트 케이스 목록")


class ScreenAnalysis(BaseModel):
    """입력 자료에서 추출한 화면/기능 분석 결과."""

    screen_name: str = Field(description="화면명 또는 문서 구간명")
    feature_areas: List[str] = Field(description="기능 영역 목록")
    ui_elements: List[str] = Field(description="주요 UI 요소 목록")
    user_actions: List[str] = Field(description="사용자 액션 목록")
    edge_cases_hint: List[str] = Field(description="예외 케이스 힌트")


class StrategyArea(BaseModel):
    """기능 영역별 테스트 전략."""

    name: str = Field(description="기능 영역명")
    focus: str = Field(description="해당 영역에서 중점적으로 볼 관점")
    expected_tc_count: int = Field(description="예상 테스트 케이스 수")
    priority: str = Field(description="우선순위")


class TestStrategy(BaseModel):
    """전체 테스트 케이스 생성 전략."""

    areas: List[StrategyArea] = Field(description="영역별 테스트 전략")
    total_expected_tcs: int = Field(description="전체 예상 테스트 케이스 수")
    coverage_focus: str = Field(description="커버리지 중심 설명")
