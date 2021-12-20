#!/usr/bin/env python
"""
We get an "image enhancement algorithm" and an "image"

# -> 1
. -> 0

The image starts embedded in an infinite sea of .
We "enhance" the image by taking a 3x3 kernel at each pixel,
interpreting the .s and #s as 0s and 1s,
and building them into a single binary number which we use as
the index into the algorithm to find the value of the pixel.

Part 1:
Apply this algorithm to the image twice.
How many pixels are turned on in the resulting image?

Sneaky puzzle master had to make it so index 0 of the input is a # and
index 511 is a .
That means the infinite sea of . flips to a # on every odd-numbered
application then back to a . on the subsequent even number.
Have to take that into account or the pixel values around the edge will
be wrong.

Part 2:
Apply 50 times.
"""

import logging
from collections.abc import Iterable


EXAMPLE = """\
..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#....#..#..##..###..######.###...####..#..#####..##..#.#####...##.#.#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..#####.....#.#....###..#.##......#.....#..#..#..##..#...##.######.####.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.##..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#.....####.#..#..#.##.#....##..#.####....##...##..#...#......#.#.......#.......##..####..#...#.#.#...##..#.#..###..#####........#..####......#..#

#..#.
#....
##..#
..#..
..###
"""
PART_ONE_EXAMPLE_RESULT = 35
PART_TWO_EXAMPLE_RESULT = 3351
PART_ONE_RESULT = 5316
PART_TWO_RESULT = 16728


Algo = list[int]
Image = list[list[int]]

logger = logging.getLogger(__name__)


def binarize(dot_hash: str) -> list[int]:
    return [0 if s == "." else 1 for s in dot_hash]


def parse_lines(lines: Iterable[str]) -> tuple[Algo, Image]:
    lines = list(lines)
    algo = binarize(lines[0])

    image = [binarize(line) for line in lines[2:]]

    return algo, image


def expand(image: Image, fill_value: int) -> Image:
    ncols = len(image[0]) + 4
    expanded = [[fill_value] * ncols for _ in range(2)]
    expanded.extend(
        [[fill_value, fill_value] + row + [fill_value, fill_value] for row in image]
    )
    expanded.extend([[fill_value] * ncols for _ in range(2)])
    return expanded


def apply(algo: Algo, image: Image, fill_value: int) -> Image:
    expanded = expand(image, fill_value)
    new_image = []
    for r in range(len(image) + 2):
        row = [fill_value] * (len(image) + 2)
        for c in range(len(image) + 2):
            image_values = [
                expanded[r_][c_] for r_ in range(r, r + 3) for c_ in range(c, c + 3)
            ]
            algo_index = sum(
                2 ** i * val for i, val in enumerate(reversed(image_values))
            )
            row[c] = algo[algo_index]
        new_image.append(row)

    return new_image


def image_str(image: Image) -> str:
    return "\n".join("".join("#" if v else "." for v in row) for row in image)


def part_one(lines: Iterable[str]) -> int:
    algo, image = parse_lines(lines)
    logger.debug("Image:\n" + image_str(image))
    new_image = apply(algo, image, False)
    logger.debug("Step 1:\n" + image_str(new_image))
    new_image = apply(algo, new_image, algo[0])
    logger.debug("Step 2:\n" + image_str(new_image))
    # new_image = apply_(apply_(image))
    return sum(sum(row) for row in new_image)


def part_two(lines: Iterable[str]) -> int:
    algo, image = parse_lines(lines)
    for i in range(50):
        image = apply(algo, image, algo[0] * (i % 2))
    return sum(sum(row) for row in image)
