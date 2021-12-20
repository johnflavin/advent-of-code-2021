#!/usr/bin/env python
"""
beacons and scanners

scanners can see beacons
only report their positions relative to scanner
scanner doesn't know its own orientation

Part 1
Assemble the map of beacons
how many are there?

Part 2
Find the largest Manhattan distance between scanners
"""

import logging
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import combinations, product
from typing import cast


EXAMPLE = """\
--- scanner 0 ---
404,-588,-901
528,-643,409
-838,591,734
390,-675,-793
-537,-823,-458
-485,-357,347
-345,-311,381
-661,-816,-575
-876,649,763
-618,-824,-621
553,345,-567
474,580,667
-447,-329,318
-584,868,-557
544,-627,-890
564,392,-477
455,729,728
-892,524,684
-689,845,-530
423,-701,434
7,-33,-71
630,319,-379
443,580,662
-789,900,-551
459,-707,401

--- scanner 1 ---
686,422,578
605,423,415
515,917,-361
-336,658,858
95,138,22
-476,619,847
-340,-569,-846
567,-361,727
-460,603,-452
669,-402,600
729,430,532
-500,-761,534
-322,571,750
-466,-666,-811
-429,-592,574
-355,545,-477
703,-491,-529
-328,-685,520
413,935,-424
-391,539,-444
586,-435,557
-364,-763,-893
807,-499,-711
755,-354,-619
553,889,-390

--- scanner 2 ---
649,640,665
682,-795,504
-784,533,-524
-644,584,-595
-588,-843,648
-30,6,44
-674,560,763
500,723,-460
609,671,-379
-555,-800,653
-675,-892,-343
697,-426,-610
578,704,681
493,664,-388
-671,-858,530
-667,343,800
571,-461,-707
-138,-166,112
-889,563,-600
646,-828,498
640,759,510
-630,509,768
-681,-892,-333
673,-379,-804
-742,-814,-386
577,-820,562

--- scanner 3 ---
-589,542,597
605,-692,669
-500,565,-823
-660,373,557
-458,-679,-417
-488,449,543
-626,468,-788
338,-750,-386
528,-832,-391
562,-778,733
-938,-730,414
543,643,-506
-524,371,-870
407,773,750
-104,29,83
378,-903,-323
-778,-728,485
426,699,580
-438,-605,-362
-469,-447,-387
509,732,623
647,635,-688
-868,-804,481
614,-800,639
595,780,-596

--- scanner 4 ---
727,592,562
-293,-554,779
441,611,-461
-714,465,-776
-743,427,-804
-660,-479,-426
832,-632,460
927,-485,-438
408,393,-506
466,436,-512
110,16,151
-258,-428,682
-393,719,612
-211,-452,876
808,-476,-593
-575,615,604
-485,667,467
-680,325,-822
-627,-443,-432
872,-547,-609
833,512,582
807,604,487
839,-516,451
891,-625,532
-652,-548,-490
30,-46,-14
"""
PART_ONE_EXAMPLE_RESULT = 79
PART_TWO_EXAMPLE_RESULT = 3621
PART_ONE_RESULT = 326
PART_TWO_RESULT = 10630


logger = logging.getLogger(__name__)


SCANNER_LINE_PREFIX = "--- scanner "


Vector = tuple[int, int, int]


@dataclass(frozen=True)
class CoordinateTransformation:
    rotation_idx: int
    translation: Vector


ROTATIONS: list[Callable[[Vector], Vector]] = [
    # First: 4 rotations around +x
    lambda v: (v[0], v[1], v[2]),  # 0 identity
    lambda v: (v[0], v[2], -v[1]),  # 1 pi/2
    lambda v: (v[0], -v[1], -v[2]),  # 2 pi
    lambda v: (v[0], -v[2], v[1]),  # 3 -pi/2
    # rotate pi/2 around +z, +x -> +y
    # for each top 4: swtich first and second coords, -1 on new second
    lambda v: (v[1], -v[0], v[2]),  # 4
    lambda v: (v[2], -v[0], -v[1]),  # 5
    lambda v: (-v[1], -v[0], -v[2]),  # 6
    lambda v: (-v[2], -v[0], v[1]),  # 7
    # rotate -pi/2 around +z, +x -> -y
    # for each top 4: swtich first and second coords, -1 on new first
    lambda v: (-v[1], v[0], v[2]),  # 8
    lambda v: (-v[2], v[0], -v[1]),  # 9
    lambda v: (v[1], v[0], -v[2]),  # 10
    lambda v: (v[2], v[0], v[1]),  # 11
    # rotate pi around +z, +x -> -x
    # for each top 4: -1 on first and second coords
    lambda v: (-v[0], -v[1], v[2]),  # 12
    lambda v: (-v[0], -v[2], -v[1]),  # 13
    lambda v: (-v[0], v[1], -v[2]),  # 14
    lambda v: (-v[0], v[2], v[1]),  # 15
    # rotate pi/2 around +y, +x -> -z
    # for each top 4: switch first and third coords, -1 on new third
    lambda v: (v[2], v[1], -v[0]),  # 16
    lambda v: (-v[1], v[2], -v[0]),  # 17
    lambda v: (-v[2], -v[1], -v[0]),  # 18
    lambda v: (v[1], -v[2], -v[0]),  # 19
    # rotate -pi/2 around +y, +x -> +z
    # for each top 4: switch first and third coords, -1 on new first
    lambda v: (-v[2], v[1], v[0]),  # 20
    lambda v: (v[1], v[2], v[0]),  # 21
    lambda v: (v[2], -v[1], v[0]),  # 22
    lambda v: (-v[1], -v[2], v[0]),  # 23
]


# If rotation i takes s1 to s2, INVERSE_ROTATIONS[i] takes s2 to s1
INVERSE_ROTATIONS = [
    0,  # 0
    3,  # 1
    2,  # 2
    1,  # 3
    8,  # 4
    23,  # 5
    6,  # 6
    17,  # 7
    4,  # 8
    19,  # 9
    10,  # 10
    21,  # 11
    12,  # 12
    13,  # 13
    14,  # 14
    15,  # 15
    20,  # 16
    7,  # 17
    18,  # 18
    9,  # 19
    16,  # 20
    11,  # 21
    22,  # 22
    5,  # 23
]


def add(a: Vector, b: Vector) -> Vector:
    return cast(Vector, tuple(x + y for x, y in zip(a, b)))


def negative(v: Vector) -> Vector:
    return cast(Vector, tuple(-x for x in v))


def subtract(a: Vector, b: Vector) -> Vector:
    return add(a, negative(b))


def rotate(v: Vector, r: int) -> Vector:
    return ROTATIONS[r](v)


def transform(v: Vector, t: CoordinateTransformation) -> Vector:
    return add(rotate(v, t.rotation_idx), t.translation)


def manhattan_distance(x: Vector, y: Vector) -> int:
    return sum(abs(a - b) for a, b in zip(x, y))


def read_lines(lines: Iterable[str]) -> list[list[Vector]]:
    scanners: list[list[Vector]] = []
    scanner_beacons: list[Vector] = []
    for line in list(lines)[1:]:
        if not line:
            continue
        if line.startswith(SCANNER_LINE_PREFIX):
            scanners.append(scanner_beacons)
            scanner_beacons = []
        else:
            v = cast(Vector, tuple(int(x) for x in line.split(",")))
            scanner_beacons.append(v)
    scanners.append(scanner_beacons)
    return scanners


def match_beacons(
    scanners: list[list[Vector]],
) -> tuple[set[Vector], dict[int, Vector]]:

    # Let's say two scanners overlap.
    # When we rotate one of the scanners, there will be a particular rotation
    #  where it will align with the other.
    # Then all the diffs between those aligned beacons will be the same:
    #  the translation vector from the one scanner to the other.
    # What we should see when we look through the diffs, most of them will have
    #  one or just a few entries.
    # If any have 12 or more, those are the ones where we know we found
    #  an alignment.
    scanner_transformations: dict[
        int, dict[int, CoordinateTransformation]
    ] = defaultdict(dict)
    for (s1_idx, s1_beacons), (s2_idx, s2_beacons) in combinations(
        enumerate(scanners), 2
    ):

        # All the possible rotations of the second scanner
        # relative to the first
        for r in range(len(ROTATIONS)):

            beacon_diffs: dict[Vector, int] = defaultdict(lambda: 0)

            # All the pairs of beacons between the two scanners
            for s1_beacon_pos, s2_beacon_pos in product(s1_beacons, s2_beacons):

                # This is the position scanner 2 would report
                # for this beacon if the scanner were rotated.
                # We are trying all the rotations to find one
                # that matches scanner 1.
                rotated_s2_beacon_pos = rotate(s2_beacon_pos, r)

                # If these two beacons are actually the same
                # and if we have rotated scanner 2 to match scanner 1,
                # then the difference in relative beacon positions is
                # equal to the vector between the scanners.
                # The beacon's position according to s1 minus
                # the beacon's position according to s2 gives us
                # the position of s2 according to s1.
                s1_to_s2 = subtract(s1_beacon_pos, rotated_s2_beacon_pos)

                beacon_diffs[s1_to_s2] += 1

            [(s1_to_s2, count)] = Counter(beacon_diffs).most_common(1)
            if count >= 12:
                # We have a winner.
                # Store the transformations
                # Vec in scanner 2 space rotated + translated -> Vec in scanner 1 space
                scanner_transformations[s2_idx][s1_idx] = CoordinateTransformation(
                    r, s1_to_s2
                )

                # # Also generate the inverse transformation
                inverse_r = INVERSE_ROTATIONS[r]
                s2_to_s1 = negative(rotate(s1_to_s2, inverse_r))
                scanner_transformations[s1_idx][s2_idx] = CoordinateTransformation(
                    inverse_r,
                    s2_to_s1,
                )

                # Can stop checking rotations for this pair of scanners
                break

    # The goal is to transform all the beacon positions into scanner 0 space
    # We put them all into a set, which will only keep unique positions
    # First, though, we need to know the order to transform scanner spaces
    # Most of them can't see space 0. But there will be some chain of transformations
    #  we can do to take points from S_0 -> S_1 -> ... -> S_N = 0
    # To do this, we construct an ordering.
    # (I tried using graphlib.TopologicalSorter but it didn't do what I wanted.)
    # We will add 0 first, then anyone who knows how to get to 0, then
    # anyone who knows how to get to those, until we've added everyone.
    # Then we translate in the reverse of that order (so 0 comes last).
    transformation_graph = {
        k: set(v.keys()) for k, v in scanner_transformations.items()
    }
    scanners_to_transform = set(range(1, len(scanners)))
    reversed_transformation_order = [0]
    while scanners_to_transform:
        for s1_idx in list(reversed_transformation_order):
            # Add everything that knows how to reach this scanner's space
            for s2_idx in transformation_graph.get(s1_idx, ()):
                if s2_idx not in reversed_transformation_order:
                    reversed_transformation_order.append(s2_idx)
            scanners_to_transform.discard(s1_idx)

    transformation_order = reversed_transformation_order[::-1]

    unique_beacon_positions: dict[int, set[Vector]] = defaultdict(set)
    scanner_positions: dict[int, dict[int, Vector]] = defaultdict(dict)
    for s2_idx in transformation_order:
        beacon_positions = scanners[s2_idx]

        # Dump all this scanner's unrotated untranslated positions into the set
        unique_beacon_positions[s2_idx].update(beacon_positions)

        # A scanner's position in its own space is always 0
        scanner_positions[s2_idx][s2_idx] = (0, 0, 0)

        # Transform these positions into every other space we understand
        for s1_idx, transformation in scanner_transformations[s2_idx].items():
            unique_beacon_positions[s1_idx].update(
                transform(v, transformation) for v in unique_beacon_positions[s2_idx]
            )
            scanner_positions[s1_idx].update(
                {
                    s_idx: transform(s_pos, transformation)
                    for s_idx, s_pos in scanner_positions[s2_idx].items()
                }
            )

    # Return the positions of all unique beacons transformed into the frame of scanner 0
    return unique_beacon_positions[0], scanner_positions[0]


def part_one(lines: Iterable[str]) -> int:
    scanners = read_lines(lines)
    unique_beacons, _ = match_beacons(scanners)
    return len(unique_beacons)


def part_two(lines: Iterable[str]) -> int:
    scanners = read_lines(lines)
    _, scanner_positions = match_beacons(scanners)

    return max(
        manhattan_distance(s1, s2)
        for s1, s2 in combinations(scanner_positions.values(), 2)
    )
