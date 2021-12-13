#!/usr/bin/env python
"""
Build a graph

Part 1:
Find all paths from "start" to "end".
Nodes with capitals can be visited any number of times
Nodes with lowercase only once

Part 2:
Each path can visit a single lowercase node twice
"""

import itertools
from collections import defaultdict
from collections.abc import Iterable


EXAMPLE = """\
start-A
start-b
A-c
A-b
b-d
A-end
b-end
"""
PART_ONE_EXAMPLE_RESULT = 10
PART_TWO_EXAMPLE_RESULT = 36
PART_ONE_RESULT = 4749
PART_TWO_RESULT = 123054


Node = str
Graph = dict[Node, set[Node]]
Path = list[Node]

START = "start"
END = "end"


def build_graph(lines: Iterable[str]) -> Graph:
    graph: Graph = defaultdict(lambda: set())
    for line in lines:
        if not line:
            continue
        left, right = line.split("-")
        if right != START and left != END:
            graph[left].add(right)
        if right != END and left != START:
            graph[right].add(left)
    return graph


def find_paths_from(
    node: Node,
    graph: Graph,
    current_path: Path | None = None,
    can_visit_one_lower: bool = False,
) -> Iterable[Path]:
    current_path = current_path or []

    if node.lower() == node and node in current_path:
        if can_visit_one_lower:
            # We are currently revisiting a lowercase node
            # That uses us our one for this path
            # The rest of the paths are not allowed to revisit
            #  any lowercase nodes
            can_visit_one_lower = False
        else:
            # This would result in an invalid path
            return []

    # We can say this node is cool to go on the path
    current_path = [*current_path, node]
    # print(f"{node=} {current_path=}")

    if node == END:
        # Found it!
        return [current_path]

    # Join together all the valid paths after this one
    return itertools.chain.from_iterable(
        find_paths_from(next, graph, current_path, can_visit_one_lower)
        for next in graph[node]
    )


def solution(lines: Iterable[str], can_visit_one_lower: bool = False) -> int:
    graph = build_graph(lines)

    paths = find_paths_from(START, graph, can_visit_one_lower=can_visit_one_lower)

    return len(list(paths))


def part_one(lines: Iterable[str]) -> int:
    return solution(lines)


def part_two(lines: Iterable[str]) -> int:
    return solution(lines, can_visit_one_lower=True)
