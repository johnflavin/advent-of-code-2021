#!/usr/bin/env python
"""
The navigation subsystem syntax is made of several lines containing chunks.
Some lines are incomplete, but others are corrupted.

Part 1
Find and discard the corrupted lines first.
A corrupted line is one where a chunk closes with the wrong character.

To calculate the syntax error score for a line, take the first
illegal character on the line and look it up in the following table:

): 3 points.
]: 57 points.
}: 1197 points.
>: 25137 points.

Find the first illegal character in each corrupted line of the navigation subsystem.
What is the total syntax error score for those errors?

Part 2
Now, discard the corrupted lines. The remaining lines are incomplete.
To repair the navigation subsystem, you just need to figure out the
sequence of closing characters that complete all open chunks in the line.

The score is determined by considering the completion string character-by-character.
Start with a total score of 0. Then, for each character, multiply the total score by 5
and then increase the total score by the point value given for the character in the
following table:

): 1 point.
]: 2 points.
}: 3 points.
>: 4 points.

the winner is found by sorting all of the scores and then taking the middle score.
(There will always be an odd number of scores to consider.)
"""

from collections.abc import Iterable
from statistics import median


EXAMPLE = """\
[({(<(())[]>[[{[]{<()<>>
[(()[<>])]({[<{<<[]>>(
{([(<{}[<>[]}>{[]{[(<()>
(((({<>}<{<{<>}{[]{[]{}
[[<[([]))<([[{}[[()]]]
[{[{({}]{}}([{[{{{}}([]
{<[[]]>}<{[{[{[]{()[[[]
[<(<(<(<{}))><([]([]()
<{([([[(<>()){}]>(<<{{
<{([{{}}[<[[[<>{}]]]>[]]
"""
PART_ONE_EXAMPLE_RESULT = 26397
PART_TWO_EXAMPLE_RESULT = 288957
PART_ONE_RESULT = 411471
PART_TWO_RESULT = 3122628974


ILLEGAL_SCORES = {
    ")": 3,
    "]": 57,
    "}": 1197,
    ">": 25137,
}
# I know I'm going to look these up by opener rather than closer,
# so let's just flip them manually
INCOMPLETE_SCORES = {
    "(": 1,
    "[": 2,
    "{": 3,
    "<": 4,
}
OPENERS_FOR_CLOSERS = {
    ")": "(",
    "]": "[",
    "}": "{",
    ">": "<",
}
OPENERS = set(OPENERS_FOR_CLOSERS.values())


def find_illegal_score(line: str) -> int:
    stack = []
    for c in line:
        if c in OPENERS:
            stack.append(c)
        else:
            top = stack.pop(-1)
            if OPENERS_FOR_CLOSERS[c] != top:
                # This chunk is illegal
                return ILLEGAL_SCORES[c]

    # If we got here, we didn't find anything illegal
    return 0


def part_one(lines: Iterable[str]) -> int:
    return sum(find_illegal_score(line) for line in lines if line)


def find_incomplete_score(line: str) -> int | None:
    stack = []
    for c in line:
        if c in OPENERS:
            stack.append(c)
        else:
            top = stack.pop(-1)
            if OPENERS_FOR_CLOSERS[c] != top:
                # This chunk is illegal
                return None

    # If we got here, we didn't find anything illegal
    # Now pop all the openers off the stack and find the score for their closers
    score = 0
    for opener in reversed(stack):
        closer_score = INCOMPLETE_SCORES[opener]
        score = score * 5 + closer_score
    return score


def part_two(lines: Iterable[str]) -> int:
    scores = [
        score
        for line in lines
        if line and (score := find_incomplete_score(line)) is not None
    ]

    return median(scores)
