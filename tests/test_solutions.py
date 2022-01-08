from datetime import datetime

import pytest

from advent_of_code.util import (
    Part,
    PuzzleModule,
    get_input_file_lines,
    import_puzzle_module,
)

FIRST_YEAR = 2021


def pytest_generate_tests(metafunc):
    # Find puzzle modules
    # Parametrize test func
    now = datetime.now()

    def generate_year_days():
        start_year = FIRST_YEAR
        end_year = now.year - 1 if now.month < 12 else now.year
        years = range(start_year, end_year + 1)
        start_day = 1
        current_year_end_day = 25 if now.month < 12 else now.day
        prior_year_end_day = 25

        for year in years:
            if now.year > year:
                days = range(start_day, prior_year_end_day + 1)
            else:
                days = range(start_day, current_year_end_day + 1)
            for day in days:
                yield (year, day)

    metafunc.parametrize(
        "puzzle_module,input_file_lines,part",
        [
            (
                import_puzzle_module(year, day),
                list(get_input_file_lines(year, day)),
                part,
            )
            for year, day in generate_year_days()
            for part in Part
        ],
    )


def test_puzzle_solution(
    puzzle_module: PuzzleModule, input_file_lines: list[str], part: Part
):
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    raw_example = puzzle_module.EXAMPLE.strip()
    if not raw_example:
        pytest.skip("No example")
    example = iter(raw_example.split("\n"))

    expected_example_result = (
        puzzle_module.PART_ONE_EXAMPLE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE_RESULT
    )
    if not expected_example_result:
        pytest.skip("No example result")

    actual_example_result = puzzle_func(example)
    assert expected_example_result == actual_example_result

    actual_puzzle_result = puzzle_func(iter(input_file_lines))
    expected_puzzle_result = (
        puzzle_module.PART_ONE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_RESULT
    )

    if expected_puzzle_result is not None:
        assert expected_puzzle_result == actual_puzzle_result
