"""테스트 케이스 CSV 출력 유틸리티."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.models.schemas import TestCase


CSV_HEADERS = [
    "No.",
    "대분류",
    "중분류",
    "소분류",
    "사전조건",
    "재현절차",
    "기대결과",
    "실제결과",
    "비고",
]


def build_output_path(output_path: str | None = None) -> Path:
    """출력 경로를 결정한다."""

    if output_path:
        return Path(output_path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("outputs") / f"tc_output_{timestamp}.csv"


def _to_csv_row(test_case: TestCase) -> dict[str, str | int]:
    """TestCase를 CSV 행으로 변환한다."""

    return {
        "No.": test_case.no,
        "대분류": test_case.major_category,
        "중분류": test_case.middle_category,
        "소분류": test_case.minor_category,
        "사전조건": test_case.precondition,
        "재현절차": test_case.steps,
        "기대결과": test_case.expected_result,
        "실제결과": test_case.actual_result,
        "비고": test_case.note,
    }


def write_test_cases_to_csv(
    test_cases: Iterable[TestCase],
    output_path: str | None = None,
) -> Path:
    """테스트 케이스 목록을 UTF-8 BOM CSV로 저장한다."""

    path = build_output_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for test_case in test_cases:
            writer.writerow(_to_csv_row(test_case))

    return path
