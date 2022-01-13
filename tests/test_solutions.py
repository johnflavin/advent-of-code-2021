import pytest

from advent_of_code_2021.util import (
    Part,
    PuzzleModule,
    get_input_file_lines,
    import_puzzle_module,
)


def pytest_generate_tests(metafunc):
    # Find puzzle modules
    # Parametrize test func
    metafunc.parametrize(
        "puzzle_module,input_file_lines,part",
        [
            (
                import_puzzle_module(day),
                list(get_input_file_lines(day)),
                part,
            )
            for day in range(1, 26)
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
