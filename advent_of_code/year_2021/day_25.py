#!/usr/bin/env python
"""
Every step, the sea cucumbers in the east-facing herd attempt to move
forward one location, then the sea cucumbers in the south-facing herd attempt
to move forward one location.

Due to strong water currents in the area,
sea cucumbers that move off the right edge of the map appear on the left edge,
and sea cucumbers that move off the bottom edge of the map appear on the top edge.

Part 1:
What is the first step on which no sea cucumbers move?
"""

from collections.abc import Iterable
from dataclasses import dataclass, field


EXAMPLE = """\
v...>>.vv>
.vv>>.vv..
>>.>v>...v
>>v>>.>.v.
v>v.vv.v..
>.>>..v...
.vv..>.>v.
v.v..>>v.v
....v..v.>
"""
PART_ONE_EXAMPLE_RESULT = 58
PART_TWO_EXAMPLE_RESULT = None
PART_ONE_RESULT = 389
PART_TWO_RESULT = None

Pt = tuple[int, int]
Pts = set[Pt]


@dataclass
class State:
    rights: Pts
    downs: Pts
    all_: Pts = field(init=False)
    num_rows: int
    num_cols: int
    counter: int = field(default=0)

    def __post_init__(self):
        self._set_all()

    def _set_all(self):
        self.all_ = self.rights | self.downs

    def update(self) -> bool:
        self.counter += 1

        updated = False

        # update rights
        new_pts: Pts = set()
        for pt in self.rights:
            new_pt = (pt[0], (pt[1] + 1) % self.num_cols)
            new_pts.add(new_pt if new_pt not in self.all_ else pt)
        updated = updated or not self.rights == new_pts
        self.rights = new_pts
        self._set_all()

        # update downs
        new_pts = set()
        for pt in self.downs:
            new_pt = ((pt[0] + 1) % self.num_rows, pt[1])
            new_pts.add(new_pt if new_pt not in self.all_ else pt)
        updated = updated or not self.downs == new_pts
        self.downs = new_pts
        self._set_all()

        return updated


def pretty_print(state: State):
    print("Step ", state.counter)
    for row in range(state.num_rows):
        line: list[str] = []
        for col in range(state.num_cols):
            pt = (row, col)
            if pt in state.rights:
                line.append(">")
            elif pt in state.downs:
                line.append("v")
            else:
                line.append(".")
        print("".join(line))


def parse_lines(lines: Iterable[str]) -> State:
    lines = list(lines)
    num_rows = len(lines)
    num_cols = len(lines[0])
    rights: Pts = set()
    downs: Pts = set()
    for row, line in enumerate(lines):
        for col, val in enumerate(line):
            pt = (row, col)
            if val == "v":
                downs.add(pt)
            elif val == ">":
                rights.add(pt)

    return State(rights, downs, num_rows, num_cols)


def part_one(lines: Iterable[str]) -> int:
    state = parse_lines(lines)
    while state.update():
        # pretty_print(state)
        pass
    return state.counter


def part_two(lines: Iterable[str]) -> int:
    return 0
