#!/usr/bin/env python
"""

"""

import logging
from collections import deque
from collections.abc import Iterable
from copy import deepcopy
from enum import Enum
from itertools import permutations
from typing import cast


EXAMPLE = """\
[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
[[[5,[2,8]],4],[5,[[9,9],0]]]
[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
[[[[5,4],[7,7]],8],[[8,3],8]]
[[9,3],[[9,9],[6,[4,9]]]]
[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]
"""
PART_ONE_EXAMPLE_RESULT = 4140
PART_TWO_EXAMPLE_RESULT = 3993
PART_ONE_RESULT = 4347
PART_TWO_RESULT = 4721


logger = logging.getLogger(__name__)


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"


class Pair:
    _left: "Pair | int"
    _right: "Pair | int"

    parent: "Pair | None" = None

    def __init__(self, left: "Pair | int", right: "Pair | int"):
        self.left = left
        self.right = right

        if isinstance(self.left, Pair):
            self.left.parent = self
        if isinstance(self.right, Pair):
            self.right.parent = self

    @property
    def depth(self) -> int:
        return 0 if self.parent is None else self.parent.depth + 1

    @property
    def root(self) -> "Pair":
        if self.parent is None:
            return self
        return self.parent.root

    @property
    def left(self) -> "Pair | int":
        return self._left

    @left.setter
    def left(self, value: "Pair | int"):
        self._left = value
        if isinstance(self._left, Pair):
            self._left.parent = self

    @property
    def is_left(self) -> bool:
        return self.parent is not None and self.parent.left == self

    @property
    def right(self) -> "Pair | int":
        return self._right

    @right.setter
    def right(self, value: "Pair | int"):
        self._right = value
        if isinstance(self._right, Pair):
            self._right.parent = self

    @property
    def is_right(self) -> bool:
        return self.parent is not None and self.parent.right == self

    def __str__(self) -> str:
        return f"[{self.left},{self.right}]"

    def __repr__(self) -> str:
        return f"[{self.left},{self.right}]"

    def __add__(self, __o: object):
        if not type(self) == type(__o):
            if isinstance(__o, int):
                # This makes sum work, since 0 + Pair[...] -> Pair[...]
                return self
            raise ValueError(f"Can't add type {type(self)} and {type(__o)}")
        logger.debug("Adding")
        logger.debug(f"  {self}")
        logger.debug(f"+ {__o}")
        assert isinstance(__o, Pair)
        new_pair = Pair(self, __o)
        apply_rules(new_pair)
        logger.debug(f"= {new_pair}")
        return new_pair

    def __radd__(self, other: object):
        """Need for sum, since sum starts with 0 + ..."""
        return self.__add__(other)

    def __len__(self) -> int:
        return 3 * (
            len(self.left) if isinstance(self.left, Pair) else self.left
        ) + 2 * (len(self.right) if isinstance(self.right, Pair) else self.right)


def _add(value: int, pair: Pair, direction: Direction):
    opposite_direction = (
        Direction.RIGHT if direction == Direction.LEFT else Direction.LEFT
    )
    d_str = direction.value
    opp_d_str = opposite_direction.value
    if getattr(pair, f"is_{d_str}", False):
        # Continue down the stack
        assert pair.parent is not None
        _add(value, pair.parent, direction)
        return
    elif getattr(pair, f"is_{opp_d_str}", False):
        # We go down to parent, then check its "direction" element
        # Two possibilities:
        # 1. We find a number right away, and we add our number to it
        # 2. We move up to parent."direction", then take the "opposite
        #     direction" element up the stack until we get to a number
        if isinstance(getattr(pair.parent, d_str), int):
            base = pair.parent
            attr = d_str
        else:
            next = getattr(pair.parent, d_str)  # We know this first one is a Pair
            while isinstance(getattr(next, opp_d_str), Pair):
                next = getattr(next, opp_d_str)
            base = next
            attr = opp_d_str
        logger.debug(f"Adding {value} to {base} {attr}")
        setattr(base, attr, value + getattr(base, attr))
        return
    logger.debug(f"We got to the root. Dropping {value}.")


def add_left(pair: Pair):
    """Add the value to the next number to the left"""
    assert isinstance(pair.left, int)
    _add(pair.left, pair, Direction.LEFT)


def add_right(pair: Pair):
    """Add the value to the next number to the right"""
    assert isinstance(pair.right, int)
    _add(pair.right, pair, Direction.RIGHT)


def explode(pair: Pair) -> bool:
    """Explode a pair. Return if we changed anything or not."""
    did_explode = False
    if pair.depth == 4:
        logger.debug(f"Exploding {pair}")
        # Take the left element from pair and add it to the next int left,
        #  take the right element and add it to the next int right
        add_left(pair)
        add_right(pair)

        # Set this pair to 0 on the parent
        for d in Direction:
            if getattr(pair.parent, d.value) == pair:
                setattr(pair.parent, d.value, 0)
        logger.debug(f"{pair.root}")
        did_explode = True
    else:
        if isinstance(pair.left, Pair):
            did_explode = explode(pair.left)
        if not did_explode and isinstance(pair.right, Pair):
            did_explode = explode(pair.right)

    return did_explode


def split(pair: Pair) -> bool:
    """Split a pair. Return if we changed anything or not."""

    def _split(pair_: Pair, direction: Direction) -> bool:
        d_str = direction.value
        if isinstance(getattr(pair_, d_str), int):
            if getattr(pair_, d_str) >= 10:
                # split!
                logger.debug(f"Split {getattr(pair_, d_str)}")
                div, rem = divmod(getattr(pair_, d_str), 2)
                setattr(pair_, d_str, Pair(div, div + rem))
                logger.debug(f"{pair_.root}")
                return True
            return False
        else:
            return split(getattr(pair_, d_str))

    return _split(pair, Direction.LEFT) or _split(pair, Direction.RIGHT)


def apply_rules(pair: Pair) -> Pair:
    while True:
        if explode(pair):
            continue
        if split(pair):
            continue
        break
    return pair


def parse_pair(encoded_pair: str) -> Pair:
    queue: deque[int | Pair] = deque()
    # rights: deque[int | Pair] = deque()
    # current: int | Pair = -1
    for c in encoded_pair:
        if c == "[" or c == ",":
            continue
        elif c == "]":
            right = queue.pop()
            left = queue.pop()
            queue.append(Pair(left, right))
        else:
            queue.append(int(c))
    assert len(queue) == 1
    pair = queue.pop()
    assert isinstance(pair, Pair)
    # return apply_rules(pair)
    return pair


def part_one(lines: Iterable[str]) -> int:
    s = sum(parse_pair(line) for line in lines)
    logger.debug(str(s))
    assert isinstance(s, Pair)
    return len(s)


def part_two(lines: Iterable[str]) -> int:
    numbers = [parse_pair(line) for line in lines]

    # Need to copy the numbers before they are added, otherwise
    #  applying the rules from one add will change the numbers to be
    #  added next time
    number_pairs = [
        (deepcopy(left), deepcopy(right)) for left, right in permutations(numbers, 2)
    ]

    sums = (cast(Pair, sum(pair)) for pair in number_pairs)
    mags = (len(s) for s in sums)
    return max(mags)
