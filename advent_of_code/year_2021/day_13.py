#!/usr/bin/env python
"""
Part 1
How many dots are visible after completing just the first fold
instruction on your transparent paper?

Part 2
Finish folding the transparent paper according to the instructions.
The manual says the code is always eight capital letters.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial
from typing import Callable


EXAMPLE = """\
6,10
0,14
9,10
0,3
10,4
4,11
6,0
6,12
4,1
0,13
10,12
3,4
3,0
8,4
1,10
2,14
8,10
9,0

fold along y=7
fold along x=5
"""
PART_ONE_EXAMPLE_RESULT = 17
PART_TWO_EXAMPLE_RESULT = """
#####
#...#
#...#
#...#
#####
"""
PART_ONE_RESULT = 743
PART_TWO_RESULT = """
###...##..###..#.....##..#..#.#..#.#...
#..#.#..#.#..#.#....#..#.#.#..#..#.#...
#..#.#....#..#.#....#..#.##...####.#...
###..#....###..#....####.#.#..#..#.#...
#.#..#..#.#....#....#..#.#.#..#..#.#...
#..#..##..#....####.#..#.#..#.#..#.####
"""


@dataclass(frozen=True)
class Pt:
    x: int
    y: int

    @classmethod
    def from_line(cls, line: str):
        x, y = line.split(",")
        return cls(int(x), int(y))


FoldFunc = Callable[[Pt], Pt]


def fold_x(pt: Pt, value: int) -> Pt:
    return pt if pt.x < value else Pt(2 * value - pt.x, pt.y)


def fold_y(pt: Pt, value: int) -> Pt:
    return pt if pt.y < value else Pt(pt.x, 2 * value - pt.y)


def parse(lines: Iterable[str]) -> tuple[list[Pt], list[FoldFunc]]:
    pts = []
    for line in lines:
        if not line:
            break
        pts.append(Pt.from_line(line))
    folds = []
    for line in lines:
        if not line:
            continue
        instruction, value = line.split("=")
        raw_fold_func = fold_x if instruction == "fold along x" else fold_y
        folds.append(partial(raw_fold_func, value=int(value)))

    return pts, folds


def part_one(lines: Iterable[str]) -> int:
    pts, folds = parse(lines)
    # print("PRE FOLD")
    # print(pts)
    # print("FOLD", folds[0])
    p = set(map(folds[0], pts))
    # print("POST FOLD")
    # print(p)
    return len(p)


def to_str(pts: set[Pt]) -> str:
    max_x = -1
    max_y = -1
    for pt in pts:
        if pt.x > max_x:
            max_x = pt.x
        if pt.y > max_y:
            max_y = pt.y
    empty_line = ["."] * (max_x + 1)
    array = [list(empty_line) for _ in range(max_y + 1)]
    for pt in pts:
        array[pt.y][pt.x] = "#"
    return "\n" + "\n".join("".join(line) for line in array) + "\n"


def part_two(lines: Iterable[str]) -> str:
    pts, folds = parse(lines)

    def fold_pt(pt: Pt) -> Pt:
        for func in folds:
            pt = func(pt)
        return pt

    folded_pts = set(map(fold_pt, pts))
    return to_str(folded_pts)
