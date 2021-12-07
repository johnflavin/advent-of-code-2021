#!/usr/bin/env python
"""
For example, consider the following horizontal positions:

16,1,2,0,4,2,7,1,2,14
This means there's a crab with horizontal position 16, a crab with horizontal position 1, and so on.

Each change of 1 step in horizontal position of a single crab costs 1 fuel. You could choose any horizontal position to align them all on, but the one that costs the least fuel is horizontal position 2:

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
each change of 1 step in horizontal position costs 1 more unit of fuel than the last: the first step costs 1, the second step costs 2, the third step costs 3, and so on.

Just change the error function from abs(x)
to the sum of all the integers from 1 to abs(x),
i.e. abs(x)*(abs(x) + 1)/2
"""

from collections.abc import Iterable
from numbers import Number
from typing import Callable


def solution(lines: Iterable[str], func: Callable[[Number], Number]) -> int:
    input_line = next(lines)
    numbers = [int(x) for x in input_line.strip().split(",")]

    min_value = float("inf")
    for test in range(min(numbers), max(numbers) + 1):
        value = sum(func(x - test) for x in numbers)
        if value < min_value:
            min_value = value

    return min_value


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, abs)

def part_two(lines: Iterable[str]) -> int:
    func1 = lambda x: int(x*(x+1)/2)
    func = lambda x: func1(abs(x))
    return solution(lines, func)
