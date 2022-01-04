#!/usr/bin/env python
"""
Given definitions of lines by their end points like
0,9 -> 5,9
determine the number of points where at least two lines overlap.

part 1: ignore slopes
part 2: consider slopes
"""

import itertools
from collections import Counter
from collections.abc import Iterable
from math import copysign


EXAMPLE = """\
0,9 -> 5,9
8,0 -> 0,8
9,4 -> 3,4
2,2 -> 2,1
7,0 -> 7,4
6,4 -> 2,0
0,9 -> 2,9
3,4 -> 1,4
0,0 -> 8,8
5,5 -> 8,2
"""
PART_ONE_EXAMPLE_RESULT = 5
PART_TWO_EXAMPLE_RESULT = 12
PART_ONE_RESULT = 4745
PART_TWO_RESULT = 18442

LineBounds = tuple[int, int, int, int]
Point = tuple[int, int]


def sgn(x: int) -> int:
    return int(copysign(1, x))


def parse_line(line: str) -> LineBounds:
    """
    Given a string
    <start_x>,<start_y> -> <end_x>,<end_y>
    return the int start and end values as a tuple
    start_x, end_x, start_y, end_y

    example:
    >>> parse_line("0,9 -> 5,9")
    (0, 5, 9, 9)
    """
    start, end = line.split(" -> ")
    start_x, start_y = start.split(",")
    end_x, end_y = end.split(",")
    return int(start_x), int(end_x), int(start_y), int(end_y)


def line_bounds_to_points(
    start_x: int, end_x: int, start_y: int, end_y: int, skip_slopes: bool = True
) -> Iterable[Point]:
    """
    Given the start and end x and y values of a line,
    return an iterable over (x, y) points on that line.

    >>> list(line_bounds_to_points(0, 5, 9, 9))
    [(0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9)]

    If skip_slopes is True, then we return an empty iterable
    for any input where neither x nor y is fixed.
    ("fixed" meaning start_* == end_*)

    We also assume (given the statement of the puzzle)
    that if we are on a slope and both x and y are changing,
    then both x and y will either increase or decrease by 1
    from one point to the next.
    i.e. given *_diff = end_* - start_* then
    whenever y_diff and x_diff are both non-zero then
    y_diff / x_diff = ±1

    But we do not check this.
    """
    x_diff = end_x - start_x
    y_diff = end_y - start_y

    if x_diff != 0 and y_diff != 0 and skip_slopes:
        return ()

    # Are x and y increasing or decreasing?
    # Need to know whether to add 1 or subtract 1 to generate sequence.
    x_step = sgn(x_diff)
    y_step = sgn(y_diff)

    # x and y sequences
    x_range = range(start_x, end_x + x_step, x_step)
    y_range = range(start_y, end_y + y_step, y_step)

    # We want to generate the x and y sequences independently and zip them.
    # Problem: zip will truncate to shortest length sequence.
    # We have three scenarios:
    # 1. x changes and y does not
    # 2. y changes and x does not
    # 3. (slope) x and y both change BUT SEQUENCES HAVE SAME LENGTH
    # In 3 zip is trivial. Just zip sequences together and things will work.
    # In 1 and 2 zip will only give us one point.
    #  But we can use itertools.repeat to turn the static dimension
    #  one-element sequence into a sequence of the same length as the other.
    # (Could also use itertools.zip_longest, but I think this is fine.)
    x_repeat = 1 if x_diff != 0 else abs(y_diff) + 1
    y_repeat = 1 if y_diff != 0 else abs(x_diff) + 1
    x_sequence = itertools.repeat(x_range, x_repeat)
    y_sequence = itertools.repeat(y_range, y_repeat)

    # Now we zip (but we need to use chain to pull out nested elements from repeat)
    pts = zip(
        itertools.chain.from_iterable(x_sequence),
        itertools.chain.from_iterable(y_sequence),
    )
    # pts = list(pts)
    # print(pts)
    return pts


def solution(lines: Iterable[str], skip_slopes: bool) -> int:
    # Count occurrences of points
    # We use chain because we get 1 sequence of points per line,
    #  but we just want to count all points together
    c = Counter(
        itertools.chain.from_iterable(
            line_bounds_to_points(*parse_line(line), skip_slopes=skip_slopes)
            for line in lines
            if line
        )
    )
    # print(c)

    # sum points that occur more than once
    return sum(1 for count in c.values() if count > 1)


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, skip_slopes=True)


def part_two(lines: Iterable[str]) -> int:
    return solution(lines, skip_slopes=False)
