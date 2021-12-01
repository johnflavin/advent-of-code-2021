#!/usr/bin/env python
"""
https://adventofcode.com/2021/day/1

suppose you had the following report:

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

count the number of times a depth measurement increases from the previous measurement

PART 2
consider sums of a three-measurement sliding window

Usage:
    python 2021-12-01.py 2021-12-01.input.txt [window]
"""

import itertools
import sys
from collections.abc import Iterable

def count_increases(lines: list[int]) -> int:
    return sum((a < b) for a, b in sliding_window(lines))


def sliding_window(iterable, n=2):
    """Create a new iterable sliding window over a given iterable
    Taken from https://napsterinblue.github.io/notes/python/internals/itertools_sliding_window/
    """
    iterables = itertools.tee(iterable, n)
    
    for iterable, num_skipped in zip(iterables, itertools.count()):
        for _ in range(num_skipped):
            next(iterable, None)
    
    return zip(*iterables)


def get_file_lines(input_file: str) -> Iterable[str]:
    """Open a file and iterate over its lines"""
    with open(input_file, "r") as f:
        yield from f.readlines()


def main():
    input_file = sys.argv[1]
    do_window = len(sys.argv) > 2 and sys.argv[2].lower() == "window"
    lines = (int(ls) for l in get_file_lines(input_file) if (ls := l.strip()))
    if do_window:
        lines = (sum(window) for window in sliding_window(lines, 3))
    print(count_increases(lines))
    

if __name__ == "__main__":
    main()
    