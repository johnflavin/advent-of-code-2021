import argparse
import importlib
import importlib.resources
import sys
from datetime import datetime
from typing import Callable, Iterable, TextIO

from .util import Part

MainFunc = Callable[[Iterable[str], Part], int]

def import_puzzle_main(year: str | int, day: str | int) -> MainFunc:
    """Find the main function for the puzzle"""
    module = importlib.import_module(f".{year}.{day:02}", package=__package__)
    return module.main


def main(argv):
    parser = argparse.ArgumentParser(description="Run Advent of Code puzzle")
    parser.add_argument(
        "--part", type=int, default=1, required=False, help="Which part of the puzzle to run"
    )
    parser.add_argument(
        "--date", type=str, default=None, required=False, help="Datestamp of puzzle to run (default today)"
    )
    parser.add_argument(
        "--input", type=str, default=None, required=False,
        help="Input file path. Omit to use default input for date. Use \"-\" to read stdin."
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

    puzzle_main = import_puzzle_main(year, day)
    
    # Get input file data
    if args.input is None or args.input == "example":
        # Use default file from package resource
        variant = "input" if args.input is None else "example"
        resource_package = f"{__package__}.{year}.resources"
        resource_name = f"{day:02}.{variant}.txt"
        
        def create_line_generator():
            resource = importlib.resources.files(resource_package).joinpath(resource_name)
            with resource.open() as f:
                yield from f
    elif args.input == "-":
        # Use stdin
        def create_line_generator():
            yield from sys.stdin
    else:
        # Try to read from arg as file path
        def create_line_generator():
            with open(args.input, "r") as f:
                yield from f
    lines = (l.strip() for l in create_line_generator())
    
    part = Part(args.part)
    return puzzle_main(lines, part)


if __name__ == "__main__":
    ret = main(sys.argv[1:])
    sys.exit(ret)