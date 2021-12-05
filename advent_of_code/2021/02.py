#!/usr/bin/env python
"""

forward X increases the horizontal position by X units.
down X increases the depth by X units.
up X decreases the depth by X units.

For example:

forward 5
down 5
forward 8
up 3
down 8
forward 2

After following these instructions, you would have a horizontal position of 15 and a depth of 10. (Multiplying these together produces 150.)

PART 2
In addition to horizontal position and depth, you'll also need to track a third value, aim, which also starts at 0. The commands also mean something entirely different than you first thought:

down X increases your aim by X units.
up X decreases your aim by X units.
forward X does two things:
It increases your horizontal position by X units.
It increases your depth by your aim multiplied by X.

"""

from collections.abc import Iterable


def position_from_lines(lines: Iterable[str], part2: bool = False) -> tuple[int, int]:
    horiz = 0
    depth = 0
    aim = 0
    for line in lines:
        # print(line)
        direction, x = line.split()
        x = int(x)
        match direction:
            case "forward":
                horiz += x
                if part2:
                    depth += aim * x
            case "up":
                if not part2:
                    depth = max(depth - x, 0)
                else:
                    aim -= x
            case "down":
                if not part2:
                    depth += x
                else:
                    aim += x
        # print(f"{horiz=} {depth=}")

    return horiz, depth


def part_one(lines: Iterable[str]) -> int:
    horiz, depth = position_from_lines(lines, part2=False)
    return horiz*depth


def part_two(lines: Iterable[str]) -> int:
    horiz, depth = position_from_lines(lines, part2=True)
    return horiz*depth
    