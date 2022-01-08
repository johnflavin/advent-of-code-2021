"""

"""

from collections import Counter
from collections.abc import Iterable


EXAMPLE = """))((((("""
PART_ONE_EXAMPLE_RESULT = 3
PART_TWO_EXAMPLE_RESULT = 1
PART_ONE_RESULT = 280
PART_TWO_RESULT = None


def part_one(lines: Iterable[str]) -> int:
    lines = list(lines)
    c = Counter(lines[0])
    return c["("] - c[")"]


def part_two(lines: Iterable[str]) -> int:
    line = list(lines)[0]
    running_total = 0
    for idx, c in enumerate(line, start=1):
        running_total += 1 if c == "(" else -1
        if running_total < 0:
            return idx
    return 0
