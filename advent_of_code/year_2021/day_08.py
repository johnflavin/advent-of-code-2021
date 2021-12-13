#!/usr/bin/env python
"""
This one is a lot to summarize

Part 1: In the output values, how many times do digits 1, 4, 7, or 8 appear?
Part 2: do the full decode, sum all output digits
"""

from collections.abc import Iterable


EXAMPLE = """\
be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce
"""
PART_ONE_EXAMPLE_RESULT = 26
PART_TWO_EXAMPLE_RESULT = 61229
PART_ONE_RESULT = 284
PART_TWO_RESULT = 973499


def part_one(lines: Iterable[str]) -> int:
    num_uniques = 0
    for line in lines:
        if not line:
            continue
        calibrations, outputs = line.split(" | ")
        num_uniques += sum(
            1
            for output in outputs.split()
            if (l := len(output)) == 2 or l == 3 or l == 4 or l == 7
        )
    return num_uniques


def decode_line(line: str) -> int:
    calibrations, outputs = line.split(" | ")
    calibrations = [set(cal) for cal in calibrations.split()]
    mapping = [""] * 10

    # First find uniques
    for cal in calibrations:
        len_cal = len(cal)
        if len_cal == 2:
            mapping[1] = cal
        elif len_cal == 3:
            mapping[7] = cal
        elif len_cal == 4:
            mapping[4] = cal
        elif len_cal == 7:
            mapping[8] = cal

    # Distinguish 6, 9, and 0
    for cal in calibrations:
        if len(cal) == 6:
            # 6, 9, or 0

            # Both 9 and 0 have all the members from 1
            # 6 does not
            if mapping[1] - cal:
                # Only 6
                mapping[6] = cal
            else:
                # 9 or 0

                # 9 has one member left when we subtract 7 and 4, 0 has two
                if len(cal - mapping[7] - mapping[4]) == 1:
                    # only 9
                    mapping[9] = cal
                else:
                    # only 0
                    mapping[0] = cal

    # Distinguish 2, 3, and 5
    for cal in calibrations:
        if len(cal) == 5:
            # 2, 3, or 5

            # 5 has all members in common with 6
            # 2 and 3 do not
            if cal - mapping[6]:
                # 2 or 3
                # 3 has both members from one, 2 does not
                if mapping[1] - cal:
                    # only 2
                    mapping[2] = cal
                else:
                    # only 3
                    mapping[3] = cal
            else:
                # Only 5
                mapping[5] = cal

    # Use the mapping to turn outputs into integers
    return sum(
        10 ** i * mapping.index(set(output))
        for i, output in enumerate(reversed(outputs.split()))
    )


def part_two(lines: Iterable[str]) -> int:
    return sum(decode_line(line) for line in lines if line)
