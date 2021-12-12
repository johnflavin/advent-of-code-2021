#!/usr/bin/env python
"""
The energy level of each octopus is a value between 0 and 9.

- First, the energy level of each octopus increases by 1.
- Then, any octopus with an energy level greater than 9 flashes.
  This increases the energy level of all adjacent octopuses by 1,
  including octopuses that are diagonally adjacent. If this causes an
  octopus to have an energy level greater than 9, it also flashes.
  This process continues as long as new octopuses keep having their energy
  level increased beyond 9. (An octopus can only flash at most once per step.)
- Finally, any octopus that flashed during this step has its energy level set to 0,
  as it used all of its energy to flash.

Part 1
How many total flashes are there after 100 steps?

Part 2
What is the first step during which all octopuses flash?
"""

from collections.abc import Callable, Iterable
from functools import cache, partial
from itertools import product

Pt = tuple[int, int]
Neighbors = Iterable[Pt]
NeighborsFunc = Callable[[Pt], Neighbors]
Values = list[list[int]]


@cache
def neighbor_indices(pt: Pt, max_row_idx: int, max_col_idx: int) -> Neighbors:
    """Adjacent + diagonal points"""
    row_idx, col_idx = pt
    if pt == (0, 0):  # top left
        return (0, 1), (1, 1), (1, 0)
    elif pt == (0, max_col_idx):  # Top right
        return (1, max_col_idx), (1, max_col_idx - 1), (0, max_col_idx - 1)
    elif pt == (max_row_idx, max_col_idx):  # Bottom right
        return (
            (max_row_idx, max_col_idx - 1),
            (max_row_idx - 1, max_col_idx - 1),
            (max_row_idx - 1, max_col_idx),
        )
    elif pt == (max_row_idx, 0):  # bottom left
        return (
            (max_row_idx - 1, 0),
            (max_row_idx - 1, 1),
            (max_row_idx, 1),
        )
    elif row_idx == 0:  # First row inner
        return (
            (0, col_idx + 1),
            (1, col_idx + 1),
            (1, col_idx),
            (1, col_idx - 1),
            (0, col_idx - 1),
        )
    elif row_idx == max_row_idx:  # last row inner
        return (
            (max_row_idx, col_idx - 1),
            (max_row_idx - 1, col_idx - 1),
            (max_row_idx - 1, col_idx),
            (max_row_idx - 1, col_idx + 1),
            (max_row_idx, col_idx + 1),
        )
    elif col_idx == 0:  # first col inner
        return (
            (row_idx - 1, col_idx),
            (row_idx - 1, col_idx + 1),
            (row_idx, col_idx + 1),
            (row_idx + 1, col_idx + 1),
            (row_idx + 1, col_idx),
        )
    elif col_idx == max_col_idx:  # last col inner
        return (
            (row_idx + 1, col_idx),
            (row_idx + 1, col_idx - 1),
            (row_idx, col_idx - 1),
            (row_idx - 1, col_idx - 1),
            (row_idx - 1, col_idx),
        )
    else:  # bulk
        return (
            (row_idx - 1, col_idx),
            (row_idx - 1, col_idx + 1),
            (row_idx, col_idx + 1),
            (row_idx + 1, col_idx + 1),
            (row_idx + 1, col_idx),
            (row_idx + 1, col_idx - 1),
            (row_idx, col_idx - 1),
            (row_idx - 1, col_idx - 1),
        )


def update(pt: Pt, values: Values, to_zero: bool = False) -> bool:
    """Update value. Either increment or reset to zero.
    Return whether this point will flash, i.e. new value > 9.
    """
    # print(f"Updating {pt}")
    row_idx, col_idx = pt
    if to_zero:
        values[row_idx][col_idx] = 0
    else:
        values[row_idx][col_idx] += 1

    return values[row_idx][col_idx] > 9

def update_and_flash(values: Values, neighbors_func: NeighborsFunc) -> int:
    """Update values and flash. Return number of flashes this turn."""

    # Step 1: Add one to all
    # Keep track of which will flash so we can flash them in step 2
    will_flash: set[Pt] = set()
    for pt in product(range(len(values)), range(len(values))):
        pt_will_flash = update(pt, values)

        if pt_will_flash:
            will_flash.add(pt)

    # Step 2: Do flashes, track the additions to neighbors
    did_flash: set[Pt] = set()
    while will_flash:
        flash_pt = will_flash.pop()

        for flash_pt_neighbor in neighbors_func(flash_pt):
            neighbor_will_flash = update(flash_pt_neighbor, values)

            # If a neighbor would flash, check if we already tracked
            #  its flash so we don't flash any point more than once
            if neighbor_will_flash and flash_pt_neighbor not in did_flash:
                will_flash.add(flash_pt_neighbor)

        # The flash is done now
        did_flash.add(flash_pt)

    # Step 3: Reset flashed points to zero
    for pt in did_flash:
        update(pt, values, to_zero=True)

    # Return number of points that flashed
    return len(did_flash)


def setup(lines: Iterable[str]) -> tuple[Values, NeighborsFunc, int]:
    values = [[int(x) for x in line] for line in lines]
    num_rows = len(values)
    num_cols = len(values[0])
    neighbors_func = partial(
        neighbor_indices,
        max_row_idx = num_rows - 1,
        max_col_idx = num_cols - 1,
    )
    return values, neighbors_func, num_rows*num_cols


def part_one(lines: Iterable[str]) -> int:
    values, neighbors_func, _ = setup(lines)

    return sum(update_and_flash(values, neighbors_func) for _ in range(100))


def part_two(lines: Iterable[str]) -> int:
    values, neighbors_func, size = setup(lines)

    num_flashed = 0
    step = 0
    while num_flashed < size:
        step += 1
        num_flashed = update_and_flash(values, neighbors_func)

    return step
