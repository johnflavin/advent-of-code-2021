#!/usr/bin/env python
"""
https://adventofcode.com/2021/day/1

part 1
count the number of times a depth measurement increases from the previous measurement

PART 2
consider sums of a three-measurement sliding window
"""

import itertools
from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T")


EXAMPLE = """\
199
200
208
210
200
207
240
269
260
263
"""
PART_ONE_EXAMPLE_RESULT = 7
PART_TWO_EXAMPLE_RESULT = 5
PART_ONE_RESULT = 1583
PART_TWO_RESULT = 1627


def count_increases(lines: Iterable[int]) -> int:
    return sum((a < b) for a, b in sliding_window(lines))


def sliding_window(iterable: Iterable[T], n: int = 2) -> Iterable[tuple[T, ...]]:
    """Create a new iterable sliding window over a given iterable
    Taken from
    https://napsterinblue.github.io/notes/python/internals/itertools_sliding_window/
    """
    iterables = itertools.tee(iterable, n)

    for iterable, num_skipped in zip(iterables, itertools.count()):
        for _ in range(num_skipped):
            next(iterable, None)

    return zip(*iterables)


def part_one(lines: Iterable[str]) -> int:
    ints = (int(x) for x in lines if x)
    return count_increases(ints)


def part_two(lines: Iterable[str]) -> int:
    ints = (int(x) for x in lines if x)
    ints = (sum(window) for window in sliding_window(ints, 3))
    return count_increases(ints)
