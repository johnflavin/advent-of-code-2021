#!/usr/bin/env python
"""
Sequence of steps that turn on or off a voxel.

Part 1:
in the region x=-50..50,y=-50..50,z=-50..50, how many cubes are on?
"""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from itertools import product


EXAMPLE = """\
on x=-20..26,y=-36..17,z=-47..7
on x=-20..33,y=-21..23,z=-26..28
on x=-22..28,y=-29..23,z=-38..16
on x=-46..7,y=-6..46,z=-50..-1
on x=-49..1,y=-3..46,z=-24..28
on x=2..47,y=-22..22,z=-23..27
on x=-27..23,y=-28..26,z=-21..29
on x=-39..5,y=-6..47,z=-3..44
on x=-30..21,y=-8..43,z=-13..34
on x=-22..26,y=-27..20,z=-29..19
off x=-48..-32,y=26..41,z=-47..-37
on x=-12..35,y=6..50,z=-50..-2
off x=-48..-32,y=-32..-16,z=-15..-5
on x=-18..26,y=-33..15,z=-7..46
off x=-40..-22,y=-38..-28,z=23..41
on x=-16..35,y=-41..10,z=-47..6
off x=-32..-23,y=11..30,z=-14..3
on x=-49..-5,y=-3..45,z=-29..18
off x=18..30,y=-20..-8,z=-3..13
on x=-41..9,y=-7..43,z=-33..15
on x=-54112..-39298,y=-85059..-49293,z=-27449..7877
on x=967..23432,y=45373..81175,z=27513..53682
"""
PART_ONE_EXAMPLE_RESULT = 590784
PART_TWO_EXAMPLE_RESULT = 2758514936282235
PART_ONE_RESULT = 611378
PART_TWO_RESULT = None


@dataclass(frozen=True)
class Range:
    low: int
    high: int

    def __add__(self, other: "Range" | "MultiRange") -> "MultiRange":
        ...


@dataclass(frozen=True)
class MultiRange:
    r = list[Range]

    def __add__(self, other: "Range | MultiRange") -> "MultiRange":
        ...


@dataclass(frozen=True)
class Pt:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class AxisRegion:
    low: int
    high: int

    def range(self):
        return range(self.low, self.high + 1)


@dataclass(frozen=True)
class Volume:
    x: AxisRegion
    y: AxisRegion
    z: AxisRegion

    @property
    def axes(self) -> tuple[AxisRegion, AxisRegion, AxisRegion]:
        return (self.x, self.y, self.z)

    def points(self) -> Iterable[Pt]:
        return product(*tuple(b.range() for b in self.axes))


OnPts = set[Pt]


class Instruction(Enum):
    ON = auto()
    OFF = auto()


def parse_line(line: str) -> tuple[set[Pt], Instruction]:
    instruction_str, bounds_str = line.split(" ")

    bounds = Volume(
        *[
            AxisRegion(*[int(b) for b in axis_bounds_str[2:].split("..")])
            for axis_bounds_str in bounds_str.split(",")
        ]
    )
    pts = (
        set(bounds.points())
        if all(a.low >= -50 and a.high <= 50 for a in bounds.axes)
        else set()
    )

    return pts, Instruction.ON if instruction_str == "on" else Instruction.OFF


def execute_line(line: str, currently_on: OnPts) -> OnPts:
    pts, instruction = parse_line(line)
    op = set.union if instruction == Instruction.ON else set.difference
    return op(currently_on, pts)


def part_one(lines: Iterable[str]) -> int:
    currently_on: set[Pt] = set()
    for line in lines:
        currently_on = execute_line(line, currently_on)
    return len(currently_on)


def part_two(lines: Iterable[str]) -> int:
    return 0
