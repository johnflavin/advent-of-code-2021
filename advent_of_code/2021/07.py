#!/usr/bin/env python
"""
For example, consider the following horizontal positions:

16,1,2,0,4,2,7,1,2,14
This means there's a crab with horizontal position 16, a crab with horizontal
position 1, and so on.

Each change of 1 step in horizontal position of a single crab costs 1 fuel. You could
choose any horizontal position to align them all on, but the one that costs the least
fuel is horizontal position 2:

Move from 16 to 2: 14 fuel
Move from 1 to 2: 1 fuel
Move from 2 to 2: 0 fuel
Move from 0 to 2: 2 fuel
Move from 4 to 2: 2 fuel
Move from 2 to 2: 0 fuel
Move from 7 to 2: 5 fuel
Move from 1 to 2: 1 fuel
Move from 2 to 2: 0 fuel
Move from 14 to 2: 12 fuel
This costs a total of 37 fuel.

My thinking:
given a set of numbers a = {a_0, a_1, ..., a_{n-1}},
find f = {f_0, f_1, ..., f_{n-1}} such that a_i - f_i = x
for all i and some x, and s = sum(abs(f)) is minimized.

hypothesis: x is the median of a
That works out for the example, as the median of the example set is 2.
But does it work generally? I think not.

Ok... this is a linear regression problem.
In linear regression you have points (x_i, y_i) and you want
to find a linear function f such that f(x_i) ≈ y_i subject to some minimum error.
In our case the y_i are the given values and x_i is nothing.
We model this as f(x) = 0*x + b.
So in other words b ≈ y_i for all i.
And we minimize using Least Absolute Deviations rather than Least Squares.

...I think there isn't a way to solve this in a closed form. We just have to go
through and try different things.

part 2:
each change of 1 step in horizontal position costs 1 more unit of fuel than the last:
the first step costs 1, the second step costs 2, the third step costs 3, and so on.

Just change the error function from abs(x)
to the sum of all the integers from 1 to abs(x),
i.e. abs(x)*(abs(x) + 1)/2
"""

import importlib
from collections.abc import Iterable
from functools import cache, partial
from typing import Callable


EXAMPLE = """\
16,1,2,0,4,2,7,1,2,14
"""
PART_ONE_EXAMPLE_RESULT = 37
PART_TWO_EXAMPLE_RESULT = 168
PART_ONE_RESULT = 348664
PART_TWO_RESULT = 100220525

first_day = importlib.import_module(".01", __package__)


StepTriple = tuple[int, int, int]
RawFunc = Callable[[list[int], int], int]
Func = Callable[[int], int]


@cache
def abs_cache(x):
    return abs(x)


@cache
def sum_abs_cache(x):
    a = abs_cache(x)
    return int(a * (a + 1) / 2)


@cache
def func_part1(values: tuple[int], step: int) -> int:
    return sum(abs_cache(x - step) for x in values)


@cache
def func_part2(values: tuple[int], step: int) -> int:
    return sum(sum_abs_cache(x - step) for x in values)


def func_triple(step_triple: StepTriple, func: Func) -> tuple[int, int]:
    """check if values are increasing or decreasing for these steps,
    or if we've found the min in the middle.
    if increasing, we should step left. return -1 and the value
    if decreasing, we should step right. return 1 and the value
    if the min is in the middle we have found our value. return 0 and the value

    We return the value every time so we can keep a consistent api, even though
    we only use the value when the step signal is 0."""

    left_result, mid_result, right_result = tuple(map(func, step_triple))
    if left_result > mid_result and right_result > mid_result:
        return 0, mid_result
    elif left_result > mid_result and mid_result > right_result:
        return 1, mid_result
    elif left_result < mid_result and mid_result < right_result:
        return -1, mid_result
    raise RuntimeError(
        "Something isn't right."
        f"{step_triple=} {left_result=} {mid_result=} {right_result=}"
    )


def binary_search(
    step_triples: list[StepTriple], func: Func, low_idx=0, high_idx=None
) -> int:
    if high_idx is None:
        high_idx = len(step_triples)
    while low_idx < high_idx:
        idx = (low_idx + high_idx) // 2
        step_triple = step_triples[idx]
        result, value = func_triple(step_triple, func)
        # print(f"{result=} {step_triple=} mid_value={value}")
        if result > 0:
            low_idx = idx + 1
        elif result < 0:
            high_idx = idx
        else:
            return value
    return None


def solution(lines: Iterable[str], func: RawFunc) -> int:
    input_line = next(lines)
    numbers = [int(x) for x in input_line.strip().split(",")]

    dressed_func = partial(func, tuple(numbers))

    # as a naive start, we just try every possible step value
    # Even if some are far less likely than others
    steps = range(min(numbers), max(numbers) + 1)
    step_triples = list(first_day.sliding_window(steps, 3))

    lowest_value = binary_search(step_triples, dressed_func)

    if lowest_value is None:
        raise RuntimeError("Something went wrong")

    return lowest_value


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, func_part1)


def part_two(lines: Iterable[str]) -> int:
    return solution(lines, func_part2)
