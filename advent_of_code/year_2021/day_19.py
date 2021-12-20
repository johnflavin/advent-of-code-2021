#!/usr/bin/env python
"""
beacons and scanners

scanners can see beacons
only report their positions relative to scanner
scanner doesn't know its own orientation

Part 1
Assemble the map of beacons
how many are there?

Thoughts:
For each scanner x, we get a bunch of scanner x -> beacon_i vectors
    s^x_i
Turn that into beacon -> beacon vectors (aka "diffs")
    b^x_ij = s^x_j - s^x_i
Those beacon vectors are invariant to changes in scanner position.
So if two scanners x, y see the same two beacons, they will both
have an equivalent beacon diff b^x_ij ≍ b^y_kl.
I say "equivalent" rather than "equal" because the beacon diffs
are not invariant to scanner orientation; each of the
24 scanner orientations would produce a different b^x_ij.
We consider two diffs equivalent if we can use one of our 24
rotations to turn one diff into another.

But we would rather not have to check all the rotations for
all the diffs against each other. That's a lot of work.
What we'll do instead is define a "canonical form" for a diff.
We can transform any beacon diff vector into this canonical form
with a few operations. If two diffs share the same canonical form,
we know they are equivalent under some rotation.
I'll pick the canonical form that the coordinates are arranged so they
increase in magnitude from the first to the third, and there will be
at most one negative sign on the third coordinate.
We can quickly apply a rotation using this operation on a vector:
swap two adjacent coordinates and add a negative sign to any coordinate.
By applying this operation any number of times we can generate the entire
set of equivalent rotated vectors. Or we can apply it just a few times
to tranform our diff vectors into canonical form.

Plan so far:
Read all the scanner -> beacon vectors
Find the beacon -> beacon diff vectors for each scanner
Turn all those beacon -> beacon diffs into canonical form
Create a mapping with the keys being the canonical diffs
and the values being a list of (scanner index, from beacon index, to beacon index)
tuples that define which diff created this canonical form.
In this way we can quickly narrow down the candidates we have
to check for which scanners' beacon vectors are potentially
equivalent to which other scanners' beacon vectors.

And we will have to check. Two beacons may have the same diff as
two other beacons by chance. So we need to be sure that for every
diff with the same canonical form, we are verifying that the
underlying beacons are the same.

And how do we do that?
Need to think through it.
Given some diff in canonical form, we will have a list of candidates
to check: (scanner index, from beacon index, to beacon index) tuples.
Let's take a pair of these tuples:
scanner s0, from beacon b0, to beacon b1
scanner s1, from beacon b'0, to beacon b'1
We know that we can rotate the diff of those beacon vectors from
one scanner to the diff from the other scanner.
I.e. there is some rotation R such that
R(b'1 - b'0) = b1 - b0

Matrix multiplication is distributive, so we also have
R(b'1) - R(b'0) = b1 - b0
=> R(b'1) - b1 = R(b'0) - b0
In other words, if two diffs are the same after rotation R,
then the beacon locations that made those diffs are the same
after rotation R.

But to really be sure the scanners are seeing the same beacons,
the puzzle tells us we need to find 12 beacons in common.

NOTE:
This doesn't work yet. I'm not sure it ever will.
I get the right answer for the example but the wrong answer for
my actual input. I do not understand why.
"""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Tuple
from uuid import uuid4


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
PART_TWO_EXAMPLE_RESULT = None
PART_ONE_RESULT = None
PART_TWO_RESULT = None


SCANNER_LINE_PREFIX = "--- scanner "

Vector = Tuple[int, ...]
Matrix = Tuple[Vector, ...]


@dataclass
class DiffSource:
    scanner_idx: int
    from_idx: int
    to_idx: int


def vec_mult(m: Matrix, v: Vector) -> Vector:
    v_len = len(v)
    m_nrows = len(m)
    m_ncols = len(m[0])
    assert v_len == m_ncols

    return tuple(sum(m[r][i] * v[i] for i in range(m_ncols)) for r in range(m_nrows))


def mat_mult(m1: Matrix, m2: Matrix) -> Matrix:
    m1_nrows = len(m1)
    m1_ncols = len(m1[0])
    m2_nrows = len(m2)
    m2_ncols = len(m2[0])
    assert m1_ncols == m2_nrows

    return tuple(
        tuple(
            sum(m1[r][i] * m2[i][c] for i in range(m1_ncols)) for c in range(m2_ncols)
        )
        for r in range(m1_nrows)
    )


# Four rotations around +x axis
ROTATIONS_AROUND_X = (
    # Identity
    (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ),
    # pi/2
    (
        (1, 0, 0),
        (0, 0, -1),
        (0, 1, 0),
    ),
    # pi
    (
        (1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
    ),
    # -pi/2
    (
        (1, 0, 0),
        (0, 0, 1),
        (0, -1, 0),
    ),
)
# 6 rotations taking the x axis to each other axis
ROTATIONS_OF_X = (
    # Identity
    (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ),
    # +x -> +y (p/2 around +z)
    (
        (0, -1, 0),
        (1, 0, 0),
        (0, 0, 1),
    ),
    # +x -> -y (-p/2 around +z)
    (
        (0, 1, 0),
        (-1, 0, 0),
        (0, 0, 1),
    ),
    # +x -> -x (p around +z)
    (
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, 1),
    ),
    # +x -> +z (-p/2 around +y)
    (
        (0, 0, 1),
        (0, 1, 0),
        (-1, 0, 0),
    ),
    # +x -> -z (p/2 around +y)
    (
        (0, 0, 1),
        (0, 1, 0),
        (-1, 0, 0),
    ),
)
ROTATIONS = tuple(
    mat_mult(of_, around) for of_ in ROTATIONS_OF_X for around in ROTATIONS_AROUND_X
)


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
            scanner_beacons.append(tuple(int(x) for x in line.split(",")))
    scanners.append(scanner_beacons)
    return scanners


def diff(a: Vector, b: Vector) -> Vector:
    return tuple(x - y for x, y in zip(a, b))


def make_canonical(diff: Vector) -> Vector:
    """Turn a diff vector of unknown rotation into a "canonical"
    form which is equivalent to the original under some rotation
    in our set.
    If two vectors have the same canonical form we know they are
    both in the equivalence class. This is a faster way to show
    equivalence (or not) of two vectors than trying out all 24
    rotations to see if any work.
    """

    # sort by abs value
    abs_diff = tuple(abs(x) for x in diff)
    min_i = abs_diff.index(min(abs_diff))
    max_i = abs_diff.index(max(abs_diff))
    middle_i = ({0, 1, 2} - {min_i, max_i}).pop()

    # figure out if we need to add a negative sign when swapping
    # if number of swaps is odd, must add negative sign
    idx = (min_i, middle_i, max_i)
    if idx == (0, 1, 2) or idx == (2, 0, 1) or idx == (1, 2, 0):
        diff = (diff[min_i], diff[middle_i], diff[max_i])
    else:
        diff = (diff[min_i], diff[middle_i], -diff[max_i])

    # Ensure at most one negative in third position
    negatives = tuple(x < 0 for x in diff)
    num_negatives = sum(negatives)
    if num_negatives == 1:
        # If it's on the first or second, move it to the third
        if negatives[0]:
            diff = (-diff[0], diff[1], -diff[2])
        elif negatives[1]:
            diff = (diff[0], -diff[1], -diff[2])
    elif num_negatives == 2:
        # Get rid of both negatives
        diff = tuple((-1) ** neg * d for neg, d in zip(negatives, diff))
    elif num_negatives == 3:
        # Get rid of two negatives on first and second
        diff = (-diff[0], -diff[1], diff[2])

    return diff


def generate_beacon_diffs(
    scanners: list[list[Vector]],
) -> dict[Vector, list[DiffSource]]:
    """
    Generate the diff from each beacon position to each other in a scanner's space

    Collect them into a dict keyed on the diff's canonical form.
    That way we can quickly find diffs from one scanner that are equivalent to
    a diff from another scanner.
    """
    unique_diffs: dict[Vector, list[DiffSource]] = defaultdict(list)
    for s_idx, beacons in enumerate(scanners):
        for i, frm in enumerate(beacons):
            for j, to in enumerate(beacons[i + 1 :], start=i + 1):
                diff = make_canonical(tuple(t - f for t, f in zip(frm, to)))
                diff_source = DiffSource(s_idx, i, j)
                unique_diffs[diff].append(diff_source)
    return unique_diffs


# def verify_matches(beacon_match_postions):
#     for R in ROTATIONS:
#         diffs = [
#             tuple(x - y for x in p1 for y in vec_mult(R, p2))
#             for _, p1, _, p2 in beacon_match_postions
#         ]
#         med = median_low(diffs)
#         match_for_real = [d == med for d in diffs]
#         if sum(match_for_real) <= 1:
#             break
#     else:
#         return []
#     return [
#         (idx1, idx2)
#         for (idx1, _, idx2, _), match in zip(beacon_match_postions, match_for_real)
#         if match
#     ]


def match_beacons(scanners: list[list[Vector]]):
    # Initially assume they're all unique
    unique_beacons = {
        (s_idx, b_idx): uuid4()
        for s_idx, scanner_beacons in enumerate(scanners)
        for b_idx in range(len(scanner_beacons))
    }

    # Generate the beacon diffs and identify which scanners have diffs in common
    canonical_diffs = generate_beacon_diffs(scanners)

    # Turn the diff matches into beacon position matches
    matches = defaultdict(set)
    for sources in canonical_diffs.values():
        if len(sources) > 1:
            lowest_source = sources[0]
            for source in sources[1:]:
                matches[(lowest_source.scanner_idx, source.scanner_idx)].update(
                    [
                        (lowest_source.from_idx, source.from_idx),
                        (lowest_source.to_idx, source.to_idx),
                    ]
                )

    # for (scanner1_idx, scanner2_idx), beacon_matches in matches.items():
    #     print(scanner1_idx, scanner2_idx)
    #     print(beacon_matches)

    for (scanner1_idx, scanner2_idx), beacon_matches in sorted(
        matches.items(), key=lambda x: x[0]
    ):
        # if scanner1_idx == 0 and scanner2_idx == 1:
        #     print(scanner1_idx)
        #     for scanner1_beacon_idx, _ in sorted(beacon_matches, key=lambda x: x[0]):
        #         print(scanners[scanner1_idx][scanner1_beacon_idx])
        #     print(scanner2_idx)
        #     for _, scanner2_beacon_idx in sorted(beacon_matches, key=lambda x: x[0]):
        #         print(scanners[scanner2_idx][scanner2_beacon_idx])
        # if len(beacon_matches) >= 12:
        # beacon_match_positions = [
        #     (
        #         scanner1_beacon_idx,
        #         scanners[scanner1_idx][scanner1_beacon_idx],
        #         scanner2_beacon_idx,
        #         scanners[scanner2_idx][scanner2_beacon_idx],
        #     )
        #     for scanner1_beacon_idx, scanner2_beacon_idx in beacon_matches
        # ]
        # for scanner1_beacon_idx, scanner2_beacon_idx in verify_matches(
        #     beacon_match_positions
        # ):

        # I commented out a bunch of stuff where I try to verify whether the
        # matches we found are valid, or check whether there are 12 matches
        # like the puzzle said.
        # I would think that by not doing any of that stuff, I would get too many
        # matches and my number of unique beacons would be too low.
        # But it's the opposite! My numbers are too high!
        # Anyway...
        # This goes through each match and ensures the beacons have the same id
        # in the unique_beacons dict.
        # We always set the value from the lower-indexed scanner to the
        # higher-indexed scanner.
        for scanner1_beacon_idx, scanner2_beacon_idx in beacon_matches:
            unique_beacons[(scanner2_idx, scanner2_beacon_idx)] = unique_beacons[
                (scanner1_idx, scanner1_beacon_idx)
            ]
    return unique_beacons


def part_one(lines: Iterable[str]) -> int:
    scanners = read_lines(lines)
    unique_beacons = match_beacons(scanners)
    # for d, l in unique_diffs.items():
    #     print()
    #     print(d)
    #     print(l)
    # print(unique_diffs)
    return len(set(unique_beacons.values()))


def part_two(lines: Iterable[str]) -> int:
    return 0
