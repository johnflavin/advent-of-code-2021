import argparse
import importlib
import importlib.resources
import sys
from datetime import datetime
from enum import Enum
from types import ModuleType
from typing import Iterable

import pyperclip


class Part(Enum):
    ONE = 1
    TWO = 2


class PuzzleError(Exception):
    pass


SUCCESS_EMOJI = "\u2705"
FAILURE_EMOJI = "\u274C"


def import_puzzle_module(year: str | int, day: str | int) -> ModuleType:
    """Find the main function for the puzzle"""
    return importlib.import_module(f".{year}.{day:02}", package=__package__)


def download_puzzle_data(year: str | int, day: str | int) -> bytes:
    import requests

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    cookie = read_session_cookie(year)

    r = requests.get(url, cookies={"session": cookie})
    try:
        r.raise_for_status()
    except requests.RequestException as e:
        print(e.response.status_code, e.response.text)
        raise SystemExit(f"Could not load data for {year}-12-{day:02}")
    return r.content


def read_session_cookie(year: str | int) -> str:
    resource_package = f"{__package__}.{year}.resources"
    resource_name = "session.txt"
    session_cookie_file = importlib.resources.files(resource_package).joinpath(
        resource_name
    )
    with open(session_cookie_file, "r") as f:
        return f.read().strip()


def find_input_file(year: str | int, day: str | int) -> Iterable[str]:
    resource_package = f"{__package__}.{year}.resources"
    resource_name = f"{day:02}.input.txt"
    return importlib.resources.files(resource_package).joinpath(resource_name)


def input_file_lines(year: str | int, day: str | int) -> Iterable[str]:
    input_file = find_input_file(year, day)
    if not input_file.exists():
        with open(input_file, "wb") as f:
            f.write(download_puzzle_data(year, day))

    def inner():
        with open(input_file, "r") as f:
            yield from f

    return map(lambda l: l.strip(), inner())


def puzzle_result_output(expected: int | str, actual: int | str) -> tuple[str, bool]:
    correct = expected == actual
    eq = "=" if correct else "≠"
    emoji = SUCCESS_EMOJI if correct else FAILURE_EMOJI
    return f"actual {actual} {eq} expected {expected} {emoji}", correct


def run_puzzle_func(year: str | int, day: str | int, part: Part) -> tuple[str, int]:
    puzzle_module = import_puzzle_module(year, day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    example = iter(puzzle_module.EXAMPLE.split("\n"))
    expected_example_result = (
        puzzle_module.PART_ONE_EXAMPLE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE_RESULT
    )

    actual_example_result = puzzle_func(example)
    example_output, example_is_correct = puzzle_result_output(
        expected_example_result, actual_example_result
    )
    example_output = f"Example: {example_output}"
    if not example_is_correct:
        return example_output, 1

    puzzle = input_file_lines(year, day)
    actual_puzzle_result = puzzle_func(puzzle)
    expected_puzzle_result = (
        puzzle_module.PART_ONE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_RESULT
    )

    if expected_puzzle_result is None:
        if actual_puzzle_result is not None:
            pyperclip.copy(actual_puzzle_result)
            puzzle_output = f"Puzzle result copied to clipboard: {actual_puzzle_result}"
        else:
            # Assume that if the function returns None we printed something
            puzzle_output = ""
        exit_code = 0
    else:
        puzzle_output, puzzle_is_correct = puzzle_result_output(
            expected_puzzle_result, actual_puzzle_result
        )
        puzzle_output = f"Puzzle: {puzzle_output}"
        exit_code = not puzzle_is_correct

    return f"Part {part.value}\n{example_output}\n{puzzle_output}", exit_code


def main(argv):
    parser = argparse.ArgumentParser(description="Run Advent of Code puzzle")
    parser.add_argument(
        "--part",
        type=int,
        default=1,
        required=False,
        help="Which part of the puzzle to run",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        required=False,
        help="Datestamp of puzzle to run (default today)",
    )
    args = parser.parse_args(argv)

    # Determine date of puzzle to run and import main from there
    datestamp = args.date
    if datestamp is None:
        # Use current date and time to figure out puzzle to run
        now = datetime.now()
        year = now.year

        # Puzzles release at 12 am eastern, so 11 pm local time
        # If it's later than that we want to run tomorrow's puzzle
        day = now.day if now.hour < 23 else now.day + 1
    else:
        year, _, day = datestamp.split("-")

    part = Part(args.part)

    output_str, exit_code = run_puzzle_func(year, day, part)
    print(output_str)

    return exit_code


if __name__ == "__main__":
    ret = main(sys.argv[1:])
    sys.exit(ret)
