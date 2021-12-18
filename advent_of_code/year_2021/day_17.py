#!/usr/bin/env python
"""
Part 1:
(explains trajectories)
What is the highest y position it reaches on this trajectory?

MATH TIME
target:
tx_min, tx_max, ty_min, ty_max

initial conditions:
(x_0, y_0) = (0, 0)
v_0 = (vx_0, vy_0) is my independent variable

first step
(x_1, y_1) = (vx_0, vy_0)
(vx_1, vy_1) = (vx_0 - 1, vy_0 - 1)

solving x
initial x velocity is vx_0
must be positive or we won't hit the target.
(and if they're sneaky and try to put the target in negative x
space we can flip the x dimension without loss of generality.)
it decreases by 1 each step until it hits zero
That takes vx_0 steps. i.e. if it starts at n, after n steps it goes to 0.
What is x position after those steps?
x_n for all n >= vx_0
x_n = sum_{i=1}^{vx_0}(vx_0 - (i-1))
    = sum_{i=1}^{vx_0}(vx_0 + 1) - sum_{i=1}^{vx_0} i
    = (vx_0 + 1) * vx_0 - vx_0*(vx_0 + 1)/2
    = vx_0 * (vx_0 + 1) / 2
For it to hit the target, that position must be within the bounds
tx_min <= x_n <= tx_max
Honestly, it doesn't have to be at x_n, these bounds
just have to be satisfied for some x_i where y_i also
satisfies its bounds. That i could be less than n.

solving y
vy also decreases by one each step but it never stops
y_i = sum_{j=1}^i (vy_0 - (j-1))
    = sum_{j=1}^i (vy_0 + 1) - sum_{j=1}^i j
    = (vy_0 + 1)*i - i*(i + 1)/2
    = vy_0 * i - i * (i - 1) / 2

So we are solving this, where n is the last step:
ty_min <= vy_0 * n - n * (n - 1) / 2 <= ty_max
tx_min <= vx_0 * n - n * (n - 1) / 2 <= tx_max (if n < vx_0)
tx_min <= (vx_0 + 1) * vx_0 / 2 <= tx_max (if n >= vx_0)

That gets us all initial conditions that produce valid trajectories.
And we want to find the conditions that produce the maximum height:
y_i = vy_0 * i - i * (i - 1) / 2
Let's take the derivative of that with i
dy_i/di = vy_0 - i + 1/2
minimum at dy_i/di = 0
 => i = vy_0 + 1/2
Which is interesting since both i and vy_0 have to be integers...
I'm guessing that is the theoretical max, but since it occurs
between two steps we will get our actual max at the integer i
steps before and after.
Let's try plugging in both i = vy_0 and i = vy_0 + 1 into y_i
y_{vy_0} = vy_0 * vy_0 - vy_0 * (vy_0 - 1) / 2
         = vy_0 * (vy_0 + 1) / 2
y_{vy_0 + 1} = vy_0 * (vy_0 + 1) - (vy_0 + 1) * ((vy_0+1) - 1) / 2
             = (vy_0 + 1) * vy_0 / 2
Both steps are equal heights. And if we look at the examples,
they do all have two steps at the max height
at i = vy_0 and vy_0 + 1.
(Note this all assumes vy_0 is positive. If negative,
then i=0 is the max vy_i and y_i.)

So now we know given a vy_0 what the max height would be.
But we still need to know the range of
vy_0 and vx_0 that would give us a trajectory within the target.

I feel like it might be easier to split into two ranges: one with
n < vx_0 and another with n >= vx_0. I suspect the latter is where
our max height solution will lie, but I'll still look at both.

total steps n >= vx_0
For a solution to be valid we must have n where
the following are true:
ty_min <= vy_0 * n - n * (n - 1) / 2 <= ty_max
tx_min <= (vx_0 + 1) * vx_0 / 2 <= tx_max

In addition, we can say the previous step was not in the target area.
This could in general be in x or in y.
If we say that n is strictly greater than vx_0, that means at step
n-1 vx_{n-1} was still = 0 and x_{n-1} = (vx_0 + 1) * vx_0 / 2.
So at step n-1 we would have the additional constraint that
ty_max < y_{n-1} = vy_0*(n-1) - (n-1)*((n-1) - 1)/2
                 = vy_0 * n - vy_0 - (n-1)*(n - 2) / 2
                 = (vy_0 * n - n * (n - 1) / 2) + n - 1 - vy_0
=> ty_max - n + vy_0 + 1 < vy_0 * n - n * (n - 1) / 2
But we also know the rhs <= ty_max, therefore the lhs is too.
ty_max - n + vy_0 + 1 < ty_max
=> n - 1 > vy_0
So we know that if we assume n - 1 > vx_0, we also know n - 1 > vy_0.
Does that help? Not sure.

Let me think about n < vx_0.
We need to have n > vy_0, because i = vy_0 is where we get our max height.
If we assume the target area is in negative y (which isn't guaranteed by
the problem statement, so maybe a shaky assumption...) then we
can guarantee that we have gone up to some positive y_max = y_{vy_0} and back
down through y = 0 on our way to the negative target range.
Even if the range is not negative but just below y_max, we're still at
n > vy_0.
But we don't necessarily need n > vx_0 if vx_0 > vy_0.
So we don't have to be at terminal x_max = vx_0*(vx_0 + 1)/2.

Here's another angle.
y's steps are symmetric. It will step up by delta_y
vy_0, vy_0 - 1, ..., 1 until it gets to max height at step vy_0,
then a step of 0 change, then back down with
-1, -2, ..., -(vy_0 - 1), -vy_0, -(vy_0 + 1), ...
This is all without any consideration of x.
So it must be the case that after it attains max
height at step vy_0 it returns to height 0 at
step 2*vy_0 + 1.
It first enters the target area at step n, moving down at
speed vy_0 - n.
At step n - 1 it is at height
y_{n-1} = vy_0 * (n - 1) - (n-1) * ((n-1) - 1) / 2
        = (vy_0 + 1) * (n-1) - (n-1) * n / 2
        > ty_max (because it isn't in the target area until step n)
At step n it is at height
y_n = vy_0 * n - n * (n - 1) / 2 <= ty_max
But also y_n >= ty_min => y_n - ty_min >= 0

...hang on a sec. Let's think about this one. We want to
know not about every trajectory that hits the target, we want to know the one
that does it after hitting the maximum y_max (and what that maximum y_max is).
So wouldn't that mean it hits the target "latest", i.e. with the max n?
That intuitively makes sense. It has taken time to go up and come down.
What would it mean to have a max n? It would be an n such that,
any higher, and it wouldn't be possible for any trajectory with any
vx_0, vy_0 to hit the target.
Let's find that...
On this trajectory we're going to miss by going too fast.
At step i=vy_0 we are at y_i = y_max and vy_i = 0.
At some later step j > i we are at height
y_j above the target y_j > ty_max, but then at the next step
y_{j+1} we miss the target and y_{j+1} < ty_min.
=> -y_{j+1} > -ty_min
=> y_j - y_{j+1} > ty_max - ty_min
Subbing in the definition of y_j,
ty_max - ty_min > vy_0 * j - j * (j - 1) / 2 - (vy_0 * (j-1) - (j-1) * ((j-1) - 1) / 2)
                > vy_0 - j + 1
We want this to be a constraint on vy_0 given the target t.
We have to get figure out what step j is. Can do that with
ty_max < vy_j
       < vy_0 * j - j * (j - 1) / 2
       < -j^2/2 + j(vy_0 + 1)/2
=> j^2 - 2*j(vy_0 + 1)/2 < -2*ty_max
=> (j - (vy_0 + 1)/2)^2 - (vy_0 + 1)^2/4 < -2*ty_max
=> (j - (vy_0 + 1)/2)^2 < (vy_0 + 1)^2/4 - 2*ty_max
...I'm not sure this is going anywhere.

Maybe it's time to turn to the computer.
Pick a vy_0.
find y_max = (vy_0 + 1) * vy_0 / 2
Generate the sequence y_i = y_max - i*(i+1)/2.
Do we find any y_i in the target range?
More specifically, do we find an i s.t. y_i < ty_min? If so, invalid.
But how do we know when to stop? What's the theoretical max vy_0?

Breakthrough:
The sequence of y_i heights will all be members of the sequence
of triangular numbers i*(i+1)/2 (sum of all integers from 0 to i).
OEIS A000217 https://oeis.org/A000217

So that means the steps will be
1, 1+2=3, 1+2+3=6, ...

But, crucially, we start that sequence at y_max and _must_ pass through y=0.
So there will be a part above y=0, with some special i such that
y_max = i*(i+1)/2, and a part below y=0 where the steps will be
all the members of the sequence after our special i.
And that i is exactly vy_0.

So given our sequence a_i = i*(i+1)/2,
We will have heights (after the peak)
y_max - a_1, y_max - a_2, ..., y_max - a_{vy_0} = 0,
  y_max - a_{vy_0 + 1} = -vy_0, y_max - a_{vy_0 + 2} = -(2*vy_0 + 1), ...
Will we ever have an i*vy_0 + i - 1 within our y range?
I think the guarantee comes in when our next step beyond 0 would
take us past ty_min.
In the example, vy_0 = 9 and the target area ends at 10.
Thus any vy_0 > 9 would mean once we hit 0 we would be stepping
more than 10 and miss the target.
So that's the key.
max vy_0 = -ty_min - 1.
(I think we can always get an x that would land us in the target area
so I haven't even thought about the initial x.)

I got my input
target area: x=240..292, y=-90..-57

I guessed 89. But that was wrong.
Because that's not the height it reaches, that's its initial velocity.
Height is 89*90/2 = 4005
That was correct.

Part 2
How many distinct initial velocity values cause the probe to be within
the target area after any step?

If one of the sequence of x_i is in the target range
and also y_i is in the target range for the same i,
we've found a good set of initial velocities.

Now we need to consider coupling between x and y.
At least if the number of steps is small.

First let's think of all the vx_0 values that would get
x to a terminal value within the target zone.
i.e. we're thinking that the vy_0 value will be high enough that
vx_i has stepped down to 0.
That takes vx_0 steps to happen, and
the terminal x_n value is vx_0*(vx_0+1)/2.

More generally, the sequence of x_i positions will reach
a(vx_0) by adding vx_0 - i + 1 for all i > 0:
i.e. x_0 = 0, x_1 = vx_0, x_2 = 2*vx_0 - 1, x_3 = 3*vx_0 - 3, ...
x_i = sum_{j=1}^i (vx_0 + 1 - j)
    = (vx_0 + 1) * i - i * (i+1) / 2
    = i * (2*vx_0 - i + 1) / 2
Thus as expected x_{vx_0} = vx_0*(vx_0 + 1)/2

Now let's generate all the possible values.
We know the max height y_max is reached when
we step from 0 to ty_min. That happens with initial
y velocity vy_0 = -ty_min - 1.
What step is that on? We get back to 0 at step
2*vy_0 + 1 = -2*ty_min - 1, so our step into the
target range would be -2*ty_min.

If we have gotten to x_max by that step, and if
x_max is also within the target range, then that
would be a good pair.
We get to x_max at step vx_0 and be at it for all
steps after, so as long as vx_0 < -2*ty_min
we will be at x_max. And as long as
x_max = vx_0*(vx_0 + 1)/2 is in the target range we're good.

We don't necessarily have to get to x_max, though.
But if we don't we will need to hit the target on one
of the x_i = i * (2*vx_0 - i + 1) / 2 values.
That seems more likely when vy_0 is low, since those
high vx_0 values would hit the target on a much earlier step.
We'll consider that later.

possible vx_0 values:
max vy_0 = -ty_min - 1, -ty_min - 2, ..., 1, 0, -1, ..., ty_min
Any vy_0 values from ty_max to ty_min would reach the target area
on step 1. Thus any vx_0 values from tx_min to tx_max would also
make good initial values.
Since x_1 = vx_0 and y_1 = vy_0,
Any pairs v with t_min <= v_0 <= t_max will be good.

Can we generalize?
looking for (tx_min, ty_min) <= (x_i, y_i) <= (tx_max, tx_max)

x_i = i * (2*vx_0 - i + 1) / 2 until i=vx_0, then x_i = x_{vx_0} for the rest
y_i = i * (2*vy_0 - i + 1) / 2

t_min <= (x_i, y_i) <= t_max
(2*t_min/i + i - 1)/2 <= (vx_0, vy_0) <= (2*t_max/i + i - 1)/2
"""

from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial
from itertools import chain, product
from math import ceil, floor, sqrt
from typing import cast

Pt = tuple[int, int]

EXAMPLE = """\
target area: x=20..30, y=-10..-5
"""
PART_TWO_EXAMPLE_PTS_STR = """\
23,-10  25,-9   27,-5   29,-6   22,-6   21,-7   9,0     27,-7   24,-5
25,-7   26,-6   25,-5   6,8     11,-2   20,-5   29,-10  6,3     28,-7
8,0     30,-6   29,-8   20,-10  6,7     6,4     6,1     14,-4   21,-6
26,-10  7,-1    7,7     8,-1    21,-9   6,2     20,-7   30,-10  14,-3
20,-8   13,-2   7,3     28,-8   29,-9   15,-3   22,-5   26,-8   25,-8
25,-6   15,-4   9,-2    15,-2   12,-2   28,-9   12,-3   24,-6   23,-7
25,-10  7,8     11,-3   26,-7   7,1     23,-9   6,0     22,-10  27,-6
8,1     22,-8   13,-4   7,6     28,-6   11,-4   12,-4   26,-9   7,4
24,-10  23,-8   30,-8   7,0     9,-1    10,-1   26,-5   22,-9   6,5
7,5     23,-6   28,-10  10,-2   11,-1   20,-9   14,-2   29,-7   13,-3
23,-5   24,-8   27,-9   30,-7   28,-5   21,-10  7,9     6,6     21,-5
27,-10  7,2     30,-9   21,-8   22,-7   24,-9   20,-6   6,9     29,-5
8,-2    27,-8   30,-5   24,-7"""
EXAMPLE_PART_TWO_PTS = cast(
    set[Pt],
    set(
        tuple(int(x) for x in pair.split(","))
        for pair in PART_TWO_EXAMPLE_PTS_STR.split()
    ),
)
PART_ONE_EXAMPLE_RESULT = 45
PART_TWO_EXAMPLE_RESULT = len(EXAMPLE_PART_TWO_PTS)
PART_ONE_RESULT = 4005
PART_TWO_RESULT = 2953


@dataclass(frozen=True)
class Target:
    x_min: int
    y_min: int
    x_max: int
    y_max: int


def parse_lines(lines: Iterable[str]) -> Target:
    line = next(iter(lines)).strip()
    x, y = [
        [int(x) for x in s[2:].split("..")]
        for s in line.strip()[len("target area: ") :].split(", ")
    ]
    return Target(min(x), min(y), max(x), max(y))


def part_one(lines: Iterable[str]) -> int:
    target = parse_lines(lines)
    return int(-target.y_min * (-target.y_min - 1) / 2)


def vx_0_bound(t: int) -> float:
    """Values of vx_0 that would put x_max in the target range
    From tx_min <= vx_0*(vx_0 + 1)/2 <= tx_max
    complete the square:
    2*tx_min <= (vx_0 + 1/2)^2 - 1/4 <= 2*tx_max
    Therefore:
    sqrt(2*tx_min + 1/4) - 1/2 <= vx_0 <= sqrt(2*tx_max + 1/4) - 1/2
    """
    return -0.5 + sqrt(2 * t + 0.25)


def v0_bound(t: int, i: int) -> float:
    """
    Bounds on values of vy_0 that would put y in the target range on step i.
    Also works for x if i is below vx_0, otherwise x would be at x_max.

    From
    y_i = i * (2*vy_0 - i + 1) / 2
    and ty_min <= y_i <= ty_max
    Therefore:
    ty_min/i + (i - 1)/2 <= vy_0 <= ty_max/i + (i - 1)/2
    """
    return t / i + (i - 1) / 2


def v0_range(t_min: int, t_max: int, i: int) -> Iterable[int]:
    """Values of vy_0 that put y in the target range on step i.
    Also works for x if i is below vx_0, otherwise x would be at x_max"""
    return range(ceil(v0_bound(t_min, i)), floor(v0_bound(t_max, i)) + 1)


def generate_possible_v0(target: Target) -> Iterable[Pt]:
    """All v0 = (vx_0, vy_0) pairs that hit the target"""
    x_max_on_target = set(
        range(ceil(vx_0_bound(target.x_min)), floor(vx_0_bound(target.x_max)) + 1)
    )

    # vy_0 values where y would hit the target on step i
    vys = partial(v0_range, target.y_min, target.y_max)

    # vx_0 values where x would hit the target on step i
    # (including if it got to the target at some step before i and stays)
    def vxs(i: int) -> Iterable[int]:
        # the full range of vx values would not be possible
        # x reaches x_max at step vx, so for any i > vx
        #  x would simply be at x_max
        full_range = v0_range(target.x_min, target.x_max, i)
        yield from filter(lambda vx: vx > i, full_range)

        # Now also include any points where x would be
        # in the range and at x_max at step i
        yield from filter(lambda vx: vx <= i, x_max_on_target)

    return chain.from_iterable(
        product(vys(i), vxs(i)) for i in range(1, -2 * target.y_min + 1)
    )


def part_two(lines: Iterable[str]) -> int:
    target = parse_lines(lines)

    return len(set(generate_possible_v0(target)))
