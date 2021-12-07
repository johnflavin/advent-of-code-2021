import argparse
import importlib
import importlib.resources
import sys
from datetime import datetime
from enum import Enum
from types import ModuleType
from typing import Iterable

class Variant(Enum):
    INPUT = "input"
    EXAMPLE = "example"
    EXAMPLE_RESULTS = "example_results"

class Part(Enum):
    ONE = 1
    TWO = 2


def import_puzzle_module(year: str | int, day: str | int) -> ModuleType:
    """Find the main function for the puzzle"""
    return importlib.import_module(f".{year}.{day:02}", package=__package__)


def download_puzzle_data(year: str | int, day: str | int):
    import requests

    input_resource = find_resource_file(year, day, Variant.INPUT)

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    cookie = read_session_cookie(year)

    r = requests.get(url, cookies={"session": cookie})
    try:
        r.raise_for_status()
    except requests.RequestException as e:
        print(e.response.status_code, e.response.text)
        raise SystemExit(f"Could not load data for {year}-12-{day:02}")
    with open(input_resource, "wb") as f:
        f.write(r.content)


def read_session_cookie(year: str | int) -> str:
    resource_package = f"{__package__}.{year}.resources"
    resource_name = "session.txt"
    session_cookie_file = importlib.resources.files(resource_package).joinpath(resource_name)
    with open(session_cookie_file, "r") as f:
        return f.read().strip()


def create_line_generator(openable) -> Iterable[str]:
    def inner():
        with open(openable, "r") as f:
            yield from f
    return map(lambda l: l.strip(), inner())


def find_resource_file(
    year: str | int, day: str | int, variant: Variant
) -> Iterable[str]:
    resource_package = f"{__package__}.{year}.resources"
    resource_name = f"{day:02}.{variant.value}.txt"
    return importlib.resources.files(resource_package).joinpath(resource_name)


def resource_file_lines(
    year: str | int, day: str | int, variant: Variant
) -> Iterable[str]:
    resource = find_resource_file(year, day, variant)
    if not resource.exists():
        if variant == Variant.INPUT:
            download_puzzle_data(year, day)
        else:
            raise ValueError(f"No {variant.value} file for {year}-12-{day} at {resource}")
    return create_line_generator(resource)


def run_puzzle_func(year: str | int, day: str | int, part: Part, example_only: bool) -> int:
    puzzle_module = import_puzzle_module(year, day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    example_result = puzzle_func(resource_file_lines(year, day, Variant.EXAMPLE))
    expected_example_result = list(resource_file_lines(year, day, Variant.EXAMPLE_RESULTS))[part.value - 1]
    expected_example_result = int(expected_example_result)

    example_correct = example_result == expected_example_result
    if example_only:
        eq = "=" if example_correct else "≠"
        success_or_fail_emoji = "\u2705" if example_correct else "\u274C"
        return f"{example_result} {eq} {expected_example_result} {success_or_fail_emoji}"
    assert example_correct, f"Failed example: {example_result} ≠ {expected_example_result}"

    input_lines = resource_file_lines(year, day, Variant.INPUT)
    return puzzle_func(input_lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Run Advent of Code puzzle")
    parser.add_argument(
        "--part", type=int, default=1, required=False, help="Which part of the puzzle to run"
    )
    parser.add_argument(
        "--date", type=str, default=None, required=False, help="Datestamp of puzzle to run (default today)"
    )
    parser.add_argument(
        "--example", action="store_true", default=False,
        help="Use the example input, not the full input"
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

    print(run_puzzle_func(year, day, part, args.example))
    
    return 0


if __name__ == "__main__":
    ret = main(sys.argv[1:])
    sys.exit(ret)