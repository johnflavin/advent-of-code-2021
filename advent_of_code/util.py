from typing import Iterable, Protocol


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
