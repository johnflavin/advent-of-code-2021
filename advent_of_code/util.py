import importlib
import importlib.resources
from enum import Enum
from pathlib import Path
from typing import Iterable, Protocol, cast

import requests


class PuzzleModule(Protocol):
    EXAMPLE: str
    PART_ONE_EXAMPLE_RESULT: int | str
    PART_TWO_EXAMPLE_RESULT: int | str
    PART_ONE_RESULT: int | str | None
    PART_TWO_RESULT: int | str | None

    def part_one(self, lines: Iterable[str]) -> int | str:
        ...

    def part_two(self, lines: Iterable[str]) -> int | str:
        ...


class Part(Enum):
    ONE = 1
    TWO = 2


def import_puzzle_module(year: str | int, day: str | int) -> PuzzleModule:
    """Find the main function for the puzzle"""
    module = importlib.import_module(f".year_{year}.day_{day:02}", package=__package__)
    return cast(PuzzleModule, module)


def download_puzzle_data(year: str | int, day: str | int) -> bytes:
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
    resource_package = f"{__package__}.year_{year}.resources"
    resource_name = "session.txt"
    session_cookie_file = importlib.resources.files(resource_package).joinpath(
        resource_name
    )
    assert isinstance(session_cookie_file, Path)
    with open(session_cookie_file, "r") as f:
        return f.read().strip()


def find_input_file(year: str | int, day: str | int) -> Path:
    resource_package = f"{__package__}.year_{year}.resources"
    resource_name = f"day_{day:02}.input.txt"
    resource = importlib.resources.files(resource_package).joinpath(resource_name)
    assert isinstance(resource, Path)
    return resource


def get_input_file_lines(year: str | int, day: str | int) -> Iterable[str]:
    input_file = find_input_file(year, day)
    if not input_file.exists():
        with open(input_file, "wb") as f:
            f.write(download_puzzle_data(year, day))

    def inner():
        with input_file.open("r") as f:
            yield from f

    return map(lambda l: l.strip(), inner())
