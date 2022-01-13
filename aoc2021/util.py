import importlib
import importlib.resources
from enum import Enum
from pathlib import Path
from typing import Iterable, Protocol, cast

import requests


RESOURCES = Path(__package__).parent / "resources"
INPUT_RESOURCES = RESOURCES / "inputs"
SESSION_COOKIE_FILE = RESOURCES / "session.txt"

YEAR = 2021


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


def import_puzzle_module(day: str | int) -> PuzzleModule:
    """Find the main function for the puzzle"""
    module = importlib.import_module(f".day_{day:02}", package=__package__)
    return cast(PuzzleModule, module)


def download_puzzle_data(day: str | int) -> bytes:
    url = f"https://adventofcode.com/{YEAR}/day/{day}/input"
    cookie = read_session_cookie()

    r = requests.get(url, cookies={"session": cookie})
    try:
        r.raise_for_status()
    except requests.RequestException as e:
        print(e.response.status_code, e.response.text)
        raise SystemExit(f"Could not load data for {YEAR}-12-{day:02}")
    return r.content


def read_session_cookie() -> str:

    with open(SESSION_COOKIE_FILE, "r") as f:
        return f.read().strip()


def find_input_file(day: str | int) -> Path:
    return INPUT_RESOURCES / f"{YEAR}-12-{day:02}.txt"


def get_input_file_lines(day: str | int) -> Iterable[str]:
    input_file = find_input_file(day)
    if not input_file.exists():
        with open(input_file, "wb") as f:
            f.write(download_puzzle_data(day))

    def inner():
        with input_file.open("r") as f:
            yield from f

    return map(lambda l: l.strip(), inner())
