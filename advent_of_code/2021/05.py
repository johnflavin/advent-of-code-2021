#!/usr/bin/env python
"""
determine the number of points where at least two lines overlap.

part 1: ignore slopes
part 2: consider slopes
"""

import itertools
from collections import Counter
from collections.abc import Iterable
from math import copysign
from typing import Optional, TypeVar

Point = tuple[int]

def parse_lines(lines: Iterable[str]) -> Iterable[tuple[int]]:

    def parse_line(line: str) -> tuple[int]:
        start, end = line.split(" -> ")
        start_x, start_y = start.split(",")
        end_x, end_y = end.split(",")
        return int(start_x), int(end_x), int(start_y), int(end_y)
        
    for line in lines:
        # print(line)
        yield parse_line(line)


def line_bounds_to_points(
    start_x: int,
    end_x: int,
    start_y: int,
    end_y: int,
    skip_slopes: bool = True
) -> Iterable[Point]:
    x_diff = end_x - start_x
    y_diff = end_y - start_y
    
    if x_diff != 0 and y_diff != 0 and skip_slopes:
        return ()

    x_step = int(copysign(1, x_diff))
    y_step = int(copysign(1, y_diff))
    x_repeat = 1 if x_diff != 0 else abs(y_diff)+1
    y_repeat = 1 if y_diff != 0 else abs(x_diff)+1
    pts = zip(
        itertools.chain.from_iterable(itertools.repeat(range(start_x, end_x + x_step, x_step), x_repeat)),
        itertools.chain.from_iterable(itertools.repeat(range(start_y, end_y + y_step, y_step), y_repeat))
    )
    # pts = list(pts)
    # print(pts)
    return pts


def part_two(lines: Iterable[str]) -> int:
    # Count occurrences of points
    c = Counter(
        itertools.chain.from_iterable(
            line_bounds_to_points(*line_bounds, skip_slopes=False) for line_bounds in parse_lines(lines)
        )
    )
    # print(c)
    
    # sum points that occur more than once
    return sum(1 for count in c.values() if count > 1)


def part_one(lines: Iterable[str]) -> int:
    # Count occurrences of points
    c = Counter(
        itertools.chain.from_iterable(
            line_bounds_to_points(*line_bounds) for line_bounds in parse_lines(lines)
        )
    )
    # print(c)
    
    # sum points that occur more than once
    return sum(1 for count in c.values() if count > 1)
