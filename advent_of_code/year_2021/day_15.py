#!/usr/bin/env python
"""
You start in the top left position,
your destination is the bottom right position,
and you cannot move diagonally.
The number at each position is its risk level;
to determine the total risk of an entire path,
add up the risk levels of each position you enter
(that is, don't count the risk level of your starting position unless you enter it;
leaving it adds no risk to your total).

Your goal is to find a path with the lowest total risk.
"""

from collections.abc import Iterable

import networkx

from .day_09 import neighbor_indices


EXAMPLE = """\
1163751742
1381373672
2136511328
3694931569
7463417111
1319128137
1359912421
3125421639
1293138521
2311944581
"""
PART_ONE_EXAMPLE_RESULT = 40
PART_TWO_EXAMPLE_RESULT = 315
PART_ONE_RESULT = 626
PART_TWO_RESULT = 2966


def solution(weights: list[list[int]]) -> int:
    num_rows = len(weights)
    num_cols = len(weights[0])

    graph = networkx.DiGraph()

    for row in range(num_rows):
        for col in range(num_cols):
            pt = (row, col)

            # Add an edge going from each neighbor into this point,
            #  weighted by this point's cost
            graph.add_edges_from(
                (neighbor, pt, {"weight": weights[row][col]})
                for neighbor in neighbor_indices(pt, num_rows, num_cols)
            )
    # Find the shortest (least weighted) path through the graph
    shortest_path = networkx.shortest_path(
        graph, (0, 0), (num_rows - 1, num_cols - 1), "weight"
    )

    # Sum up the weights from all edges traversed on the path
    return (
        sum(weights[path_row][path_col] for path_row, path_col in shortest_path)
        - weights[0][0]
    )


def part_one(lines: Iterable[str]) -> int:
    weights = [[int(x) for x in line] for line in lines]
    return solution(weights)


def part_two(lines: Iterable[str]) -> int:
    base_weights = [[int(x) for x in line] for line in lines]
    base_num_rows = len(base_weights)
    base_num_cols = len(base_weights[0])
    num_rows = base_num_rows * 5
    num_cols = base_num_cols * 5
    weights = [list([0] * num_cols) for _ in range(num_rows)]
    for row in range(num_rows):
        for col in range(num_cols):
            row_tile, base_row = divmod(row, base_num_rows)
            col_tile, base_col = divmod(col, base_num_cols)
            weight = base_weights[base_row][base_col] + row_tile + col_tile
            if weight > 9:
                weight -= 9
            weights[row][col] = weight

    return solution(weights)
