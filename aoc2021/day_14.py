#!/usr/bin/env python
"""
The first line is the polymer template - this is the starting point of the process.

The following section defines the pair insertion rules.
A rule like AB -> C means that when elements A and B are immediately adjacent,
element C should be inserted between them. These insertions all happen simultaneously.

So, starting with the polymer template NNCB,
the first step simultaneously considers all three pairs:

- The first pair (NN) matches the rule NN -> C,
    so element C is inserted between the first N and the second N.
- The second pair (NC) matches the rule NC -> B,
    so element B is inserted between the N and the C.
- The third pair (CB) matches the rule CB -> H,
    so element H is inserted between the C and the B.

After N steps, What do you get if you take the quantity of
the most common element and subtract the quantity of the least common element?

Part 1
N = 10

Part 2
N = 40
"""

import itertools
from collections import Counter, defaultdict
from collections.abc import Iterable
from functools import partial
from typing import cast


EXAMPLE = """\
NNCB

CH -> B
HH -> N
CB -> H
NH -> C
HB -> C
HC -> B
HN -> C
NN -> C
BH -> H
NC -> B
NB -> B
BN -> B
BB -> N
BC -> B
CC -> N
CN -> C
"""
PART_ONE_EXAMPLE_RESULT = 1588
PART_TWO_EXAMPLE_RESULT = 2188189693529
PART_ONE_RESULT = 2621
PART_TWO_RESULT = 2843834241366


Pair = tuple[str, str]
PairCount = tuple[Pair, int]
PairCounter = dict[Pair, int]
ElementCounter = dict[str, int]
Rules = dict[Pair, str]


def parse_lines(lines: Iterable[str]) -> tuple[str, Rules]:
    lines = list(lines)
    template = lines[0]

    rules: Rules = {}
    for line in lines[2:]:
        if not line:
            continue
        pair_s, insert = line.split(" -> ")
        pair = cast(Pair, tuple(pair_s))
        rules[pair] = insert

    return template, rules


def spawn(rules: Rules, pair: Pair, count: int) -> tuple[PairCount, ...]:
    """Apply a rule to a pair

    If the rule says XY -> Z, then we will take a pair
    ('X', 'Y') and return the pairs ('X', 'Z'), ('Z', 'Y')
    """
    # print(f"{pair=} {count=}")
    insert = rules.get(pair)
    if insert is None:
        # We insert an empty "left" element on the first pair
        # to make the counts come up correct
        # But we won't find an insert for ("", whatever)
        return ((pair, count),)
    return ((pair[0], insert), count), ((insert, pair[1]), count)


def count_pairs(pair_counts: Iterable[PairCount]) -> PairCounter:
    counts: PairCounter = defaultdict(lambda: 0)
    for (pair, count) in pair_counts:
        # print(pair, count)
        counts[pair] += count
    return counts


def count_elements(pair_counts: Iterable[PairCount]) -> ElementCounter:
    """Count the number of elements from the pairs
    The element should only be the right side of the pair.
    """
    counts: ElementCounter = defaultdict(lambda: 0)
    for ((_, right), count) in pair_counts:
        counts[right] += count
    return counts


def solution(lines: Iterable[str], n: int) -> int:

    template, rules = parse_lines(lines)

    # Count how many of each pair we have right now
    pair_counter = count_pairs(zip(itertools.pairwise(template), itertools.repeat(1)))

    # Add a special pair for the leftmost element
    # This won't spawn anything, but it will keep our counts right in the end
    pair_counter[("", template[0])] += 1
    # print(pair_counts)

    for _ in range(n):
        # Spawn new pairs for each current pair,
        # then collect and count the number of new pairs
        pair_counter = count_pairs(
            itertools.chain.from_iterable(
                itertools.starmap(partial(spawn, rules), pair_counter.items())
            )
        )

    # Count elements from pairs
    c = Counter(count_elements(pair_counter.items()))

    # Find the counts of the most and least common elements
    # The answer is their difference
    sorted_c = c.most_common()
    (_, most_common_count) = sorted_c[0]
    (_, least_common_count) = sorted_c[-1]
    return most_common_count - least_common_count


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, 10)


def part_two(lines: Iterable[str]) -> int:
    return solution(lines, 40)
