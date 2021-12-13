#!/usr/bin/env python
"""
Find all of the low points on your heightmap.

Part 1
The risk level of a low point is 1 plus its height.
What is the sum of the risk levels of all low points on your heightmap?

Part 2
A basin is all locations that eventually flow downward to a single low point.
Therefore, every low point has a basin, although some basins are very small.
Locations of height 9 do not count as being in any basin,
and all other locations will always be part of exactly one basin.

What do you get if you multiply together the sizes of the three largest basins?
"""

from collections.abc import Callable, Iterable
from functools import cache, partial


EXAMPLE = """\
2199943210
3987894921
9856789892
8767896789
9899965678
"""
PART_ONE_EXAMPLE_RESULT = 15
PART_TWO_EXAMPLE_RESULT = 1134
PART_ONE_RESULT = 506
PART_TWO_RESULT = 931200

Pt = tuple[int, int]
Neighbors = Iterable[Pt]
Heights = tuple[tuple[int]]
NeighborsFunc = Callable[[Pt], Neighbors]
Basin = list[Pt]


@cache
def neighbor_indices(pt: Pt, max_row_idx: int, max_col_idx: int) -> Neighbors:
    row_idx, col_idx = pt
    # print(f"{row_idx=} {col_idx=}")
    if pt == (0, 0):
        # top left
        # print("top left")
        return (0, 1), (1, 0)
    elif pt == (0, max_col_idx):
        # Top right
        # print("top right")
        return (1, max_col_idx), (0, max_col_idx - 1)
    elif pt == (max_row_idx, max_col_idx):
        # Bottom right
        # print("bottom right")
        return (max_row_idx, max_col_idx - 1), (max_row_idx - 1, max_col_idx)
    elif pt == (max_row_idx, 0):
        # bottom left
        # print("bottom left")
        return (max_row_idx - 1, 0), (max_row_idx, 1)
    elif row_idx == 0:
        # First row inner
        return (0, col_idx + 1), (1, col_idx), (0, col_idx - 1)
    elif row_idx == max_row_idx:
        # last row inner
        return (
            (max_row_idx, col_idx - 1),
            (max_row_idx - 1, col_idx),
            (max_row_idx, col_idx + 1),
        )
    elif col_idx == 0:
        # first col inner
        return (
            (row_idx - 1, col_idx),
            (row_idx, col_idx + 1),
            (row_idx + 1, col_idx),
        )
    elif col_idx == max_col_idx:
        # last col inner
        return (
            (row_idx + 1, col_idx),
            (row_idx, col_idx - 1),
            (row_idx - 1, col_idx),
        )
    else:
        # bulk
        return (
            (row_idx - 1, col_idx),
            (row_idx, col_idx + 1),
            (row_idx + 1, col_idx),
            (row_idx, col_idx - 1),
        )


def process_lines(lines: Iterable[str]) -> tuple[Heights, NeighborsFunc]:
    heights = tuple(tuple(int(x) for x in line) for line in lines if line)

    num_rows = len(heights)
    num_cols = len(heights[0])
    neighbors_func = partial(
        neighbor_indices, max_row_idx=num_rows - 1, max_col_idx=num_cols - 1
    )

    return heights, neighbors_func


def low_points(
    heights: Heights, neighbors_func: NeighborsFunc
) -> Iterable[tuple[Pt], int]:

    for row_idx, row in enumerate(heights):
        for col_idx, value in enumerate(row):
            neighbors = tuple(neighbors_func((row_idx, col_idx)))
            neighbor_vals = tuple(
                heights[neighbor_row_idx][neighbor_col_idx]
                for neighbor_row_idx, neighbor_col_idx in neighbors
            )

            for neighbor_val in neighbor_vals:
                if value >= neighbor_val:
                    # this is not lowest
                    # print(f"{row_idx},{col_idx} {value} > {neighbor_val}")
                    break
            else:
                # It's lower than all its neighbors
                # print(f"LOW POINT {row_idx},{col_idx} {value}")
                yield (row_idx, col_idx), value


def part_one(lines: Iterable[str]) -> int:
    return sum(1 + l for _, l in low_points(*process_lines(lines)))


def build_basin(low_pt: Pt, heights: Heights, neighbors_func: NeighborsFunc) -> Basin:
    basin: set[Pt] = set()
    unchecked: set[Pt] = {low_pt}

    while unchecked:
        pt = unchecked.pop()
        row_idx, col_idx = pt

        # Check: am I in the basin? or am I on the edge?
        value = heights[row_idx][col_idx]
        if value == 9:
            # I am on an edge
            pass
        else:
            # I am part of the basin. Check my neighbors.
            basin.add(pt)
            unchecked.update(
                neighbor for neighbor in neighbors_func(pt) if neighbor not in basin
            )

        # print(f"{basin=}\n{unchecked=}")
    # print("DONE WITH BASIN")
    return list(basin)


def part_two(lines: Iterable[str]) -> int:
    heights, neighbors_func = process_lines(lines)

    basins: list[Basin] = [
        build_basin(low_pt, heights, neighbors_func)
        for low_pt, _ in low_points(heights, neighbors_func)
    ]
    basin_sizes = [len(basin) for basin in basins]

    prod = 1
    for size in sorted(basin_sizes)[-3:]:
        prod *= size
    return prod
