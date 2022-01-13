import argparse
import logging
import sys
from datetime import datetime

import pyperclip

from .util import (
    Part,
    import_puzzle_module,
    get_input_file_lines,
)


class PuzzleError(Exception):
    pass


SUCCESS_EMOJI = "\u2705"
FAILURE_EMOJI = "\u274C"


def puzzle_result_output(expected: int | str, actual: int | str) -> tuple[str, bool]:
    correct = expected == actual
    eq = "=" if correct else "≠"
    emoji = SUCCESS_EMOJI if correct else FAILURE_EMOJI
    return f"actual {actual} {eq} expected {expected} {emoji}", correct


def run_puzzle_func(day: str | int, part: Part) -> tuple[str, int]:
    puzzle_module = import_puzzle_module(day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    example = iter(puzzle_module.EXAMPLE.strip().split("\n"))
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

    puzzle = get_input_file_lines(day)
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
    g = parser.add_argument_group()
    g.add_argument(
        "--part",
        type=int,
        default=1,
        required=False,
        help="Which part of the puzzle to run",
    )
    g.add_argument(
        "--both",
        action="store_true",
        required=False,
        help="Run both parts",
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
    day = datetime.now().day if datestamp is None else datestamp.split("-")[-1]
    if args.both:
        exit_code = 0
        for part in Part:
            output_str, exit_code_ = run_puzzle_func(day, part)
            print(output_str)
            exit_code = exit_code or exit_code_

    else:
        part = Part(args.part)

        output_str, exit_code = run_puzzle_func(day, part)
        print(output_str)

    return exit_code


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    # logging.getLogger(__package__).setLevel(logging.DEBUG)
    ret = main(sys.argv[1:])
    sys.exit(ret)
