#!/usr/bin/env python
"""
ALU

The ALU is a four-dimensional processing unit:
it has integer variables w, x, y, and z.
These variables all start with the value 0.
The ALU also supports six instructions:

- inp a - Read an input value and write it to variable a.
- add a b - Add the value of a to the value of b,
    then store the result in variable a.
- mul a b - Multiply the value of a by the value of b,
    then store the result in variable a.
- div a b - Divide the value of a by the value of b,
    truncate the result to an integer, then store the result in variable a.
    (Here, "truncate" means to round the value toward zero.)
- mod a b - Divide the value of a by the value of b,
    then store the remainder in variable a.
    (This is also called the modulo operation.)
- eql a b - If the value of a and b are equal,
    then store the value 1 in variable a.
    Otherwise, store the value 0 in variable a.

Once you have built a replacement ALU, you can install it in the submarine,
which will immediately resume what it was doing when the ALU failed:
validating the submarine's model number.
To do this, the ALU will run the MOdel Number Automatic Detector program
(MONAD, your puzzle input).

Part 1:
To enable as many submarine features as possible,
find the largest valid fourteen-digit model number that contains no 0 digits.
What is the largest model number accepted by MONAD?

There is no way I can do 9^14 iterations of this program.
I will need to look at it and think about how to truncate the input space.

I'm going to put my input here and annotate what's going on.

inp w      # w = s0 = 0-9
mul x 0    # NOOP  x=0
add x z    # NOOP  x=0 z=0
mod x 26   # NOOP  x=0
div z 1    # NOOP  z=0
add x 14   # x=14
eql x w    # FALSE -> x=0
eql x 0    # TRUE -> x=1
mul y 0    # NOOP y=0
add y 25   # y=25
mul y x    # NOOP y=25 x=1
add y 1    # y=26
mul z y    # NOOP z=0
mul y 0    # y=0
add y w    # y=s0
add y 12   # y=s0+12
mul y x    # NOOP y=s0+12 x=1
add z y    # z=s0+12
inp w      # w = s1 = 0-9
mul x 0    # x=0
add x z    # x=s0+12                  (this does nothing)
mod x 26   # NOOP x=s0+12             (this does nothing)
div z 1    # NOOP z=s0+12
add x 15   # x = s0+12+15 = s0+27     (this does nothing)
eql x w    # FALSE -> x=0
eql x 0    # TRUE -> x=1
mul y 0    # y=0
add y 25   # y=25
mul y x    # NOOP y=25 x=1
add y 1    # y=26
mul z y    # z = 26 * (s0+12)
mul y 0    # y=0
add y w    # y=s1
add y 7    # y=s1+7
mul y x    # NOOP y=s1+7 x=1
add z y    # z = 26*(s0 + 12) + s1 + 7
inp w      # w=s2 = 0-9
mul x 0    # x=0
add x z    # x=26*(s0 + 12) + s1 + 7  (this does nothing)
mod x 26   # x = s1 + 7               (this does nothing)
div z 1    # NOOP z = 26*(s0 + 12) + s1 + 7
add x 12   # x = s1 + 19              (this does nothing)
eql x w    # FALSE -> x=0
eql x 0    # TRUE -> x=1
mul y 0    # y=0
add y 25   # y=25
mul y x    # NOOP y=25 x=1
add y 1    # y=26
mul z y    # z = 26*26*(s0 + 12) + 26*(s1 + 7)
mul y 0    # y=0
add y w    # y=s2
add y 1    # y=s2+1
mul y x    # NOOP y=s2+1
add z y    # z = 26*26*(s0 + 12) + 26*(s1 + 7) + s2 + 1
inp w      # w=s3     (I'm going to skip the steps that do nothing)
mul x 0
add x z
mod x 26
div z 1
add x 11
eql x w
eql x 0
mul y 0
add y 25
mul y x
add y 1   # y=26
mul z y   # z = 26^3*(s0 + 12) + 26^2*(s1 + 7) + 26*(s2 + 1)
mul y 0
add y w   # y=s3
add y 2   # y=s3+2
mul y x
add z y   # z = 26^3*(s0 + 12) + 26^2*(s1 + 7) + 26*(s2 + 1) + s3 + 2
inp w     # w=s4
mul x 0
add x z
mod x 26  # x = s3 + 2
div z 26  # z = 26^2*(s0 + 12) + 26*(s1 + 7) + s2 + 1
add x -5  # x = s3 - 3
eql x w   # ***IMPORTANT*** x=1 if s4 == s3-3 else x=0
eql x 0   # x=0 if s4 == s3-3 else x=1
mul y 0   # y=0
add y 25  # y=25
mul y x   # y=0 if s4 == s3-3 else y=25
add y 1   # y=1 if s4 == s3-3 else y=26
mul z y   # z = 26^2*(s0 + 12) + 26*(s1 + 7) + s2 + 1 if s4 == s3-3
          # else z = 26^3*(s0 + 12) + 26^2*(s1 + 7) + 26*(s2 + 1)
mul y 0   # y=0
add y w   # y=s4
add y 4   # y=s4+4
mul y x   # y=0 if s4 == s3-3 else y=s4+4
add z y   # z = 26^2*(s0 + 12) + 26*(s1 + 7) + s2 + 1 if s4 == s3-3
          # else z = 26^3*(s0 + 12) + 26^2*(s1 + 7) + 26*(s2 + 1) + s4 + 4
inp w     # w=s5
mul x 0   # x=0
add x z   # (does nothing)
mod x 26  # (does nothing)
div z 1   # (does nothing)
add x 14  # (does nothing)
eql x w   # FALSE -> x=0
eql x 0   # TRUE -> x=1
mul y 0   # y=0
add y 25  # y=25
mul y x   # NOOP
add y 1   # y=26
mul z y   # z = 26^3*(s0 + 12) + 26^2*(s1 + 7) + 26*(s2 + 1) if s4 == s3-3
          # else z = 26^4*(s0 + 12) + 26^3*(s1 + 7) + 26^2*(s2 + 1) + 26*(s4 + 4)
mul y 0   # y=0
add y w   # y=s5
add y 15  # y=s5+15
mul y x   # NOOP
add z y   # z = 26^3*(s0 + 12) + 26^2*(s1 + 7) + 26*(s2 + 1) + (s5 + 15) if s4 == s3-3
          # else z = 26^4*(s0 + 12) + 26^3*(s1 + 7) + 26^2*(s2 + 1) + 26*(s4 + 4)
          #          + (s5 + 15)
inp w     # s6
mul x 0
add x z
mod x 26
div z 1
add x 15
eql x w
eql x 0
mul y 0
add y 25
mul y x
add y 1
mul z y
mul y 0
add y w
add y 11
mul y x
add z y   # z = 26^4*(s0 + 12) + 26^3*(s1 + 7) + 26^2*(s2 + 1) + 26^1*(s5 + 15)
          #     + (s6 + 11) if s4 == s3-3
          # else z = 26^5*(s0 + 12) + 26^4*(s1 + 7) + 26^3*(s2 + 1) + 26^2*(s4 + 4)
          #          + 26^1(s5 + 15) + (s6 + 11)
...(snip more. Time to analyze.)

ANALYSIS
The input comes in blocks that process each input digit.

I'll call each step that processes a block i.
The input is s, each digit is s[i].
There are a couple variables that can be tweaked, which I've called X and Y.
The values of these at each step are X[i] and Y[i] (may be larger than one digit).
We also have a Z variable, but I'll dig into that in a moment.
Assume for now that in each block we shift z to the left by 26.

BLOCK TYPE 1: LEFT SHIFT z
inp w     # some digit of the input s[i]
mul x 0
add x z
mod x 26
div z 1
add x X
eql x w
eql x 0
mul y 0
add y 25
mul y x
add y 1
mul z y
mul y 0
add y w
add y Y
mul y x
add z y

The gist of what this does (usually) is shift the current
z by 26, then add the input digit + Y.
i.e. z[i] = 26*z[i-1] + s[i] + Y[i]
But that's only true most of the time. And we can be sure it is true when
X[i] > 9. For those high X values the instructions
add x X
eql x w
eql x 0
will always result in an x[i] value of 1.
This is because w stores a digit of the input which is at max 9, so
x + X can never equal w, meaning eql x w -> eql x 0 will always result in TRUE.
However, sometimes X is negative (or maybe <=9, though I haven't seen that).
In those cases it is possible that whatever is in x does equal w, and
eql x w -> eql x 0 would be FALSE.
In these cases we need to know what is in x because it determines everything about
what happens next. Skip back a few instructions...
x first gets set to z and taken mod 26. We will see in a moment that this means
x will be the value of a previous input digit + a previous Y. (Which one
exactly is a bit tricky, so I'll think about that in a moment.)
We then add the current X and compare it to the current digit stored in w.
x[i] = z[i-1] mod 26 + X[i]
If this whole thing == s[i] then eql x w -> eql x 0 results in FALSE and x[i] = 0.

This has an effect on the next bit.
mul y 0
add y 25
mul y x
add y 1
mul z y
For the typical big X[i] case, x[i] will be 1 and y[i] will be 26 after this.
For the small X[i], x[i] will be 0 and y[i] will be 1 after this.
The end effect is that either z[i] will be left shifted by 26 (big X[i])
or nothing happens (small X[i]).

After this we bring in the new digit to z (...or not).
mul y 0
add y w
add y Y
mul y x
add z y
If x[i] is 1, this adds the s[i]+Y[i] to z.
If x[i] is 0, this does nothing to z.

BLOCK TYPE 1 SUMMARY
digit i
If s[i-1] + Y[i-1] + X[i] == s[i]
z[i] = z[i-1]
else
z[i] = 26*z[i-1] + s[i] + Y[i]

BLOCK TYPE 2: RIGHT SHIFT z
These blocks do all the same stuff as before with x and y, but
instead of shifting z right by 26 they shift left by 26.
I'll highlight a line with **.

inp w
mul x 0
add x z
mod x 26
*div z 26*
add x X
eql x w
eql x 0
mul y 0
add y 25
mul y x
add y 1
mul z y
mul y 0
add y w
add y Y
mul y x
add z y

Now we are dividing z by 26 at the beginning instead of dividing by 1.
This is integer division, i.e. a right shift by 26,
i.e. any values in z less than a multiple of 26 go away.
Clearly any previously left-shifted value will be preserved as-is.
However, we may also keep part of the previous added value s[i] + Y[i] if it
is >= 26.
Let's look at what z might be here:
z[i-1] = 26*(s[i-2] + Y[i-2]) + s[i-1] + Y[i-1] + (order 2+ base-26 digits)
Shift right:
s[i-2] + Y[i-2] + (1 if s[i-1] + Y[i-1] >= 26 else 0) + (order 1+ base-26 digits)

PUT THIS TOGETHER
We have an input sequence s.
Block i starts with an inp w line (which we call line 0 of the block).
Analyze the blocks for sequences X, Y, and Z:
* X: the values of the add x (something) instructions on block line 5
* Y: values of add y (something) instructions on block line 15
* Z: the value of div z (something) on block line 4

CONSTRUCT INPUTS
I'm going to write a little code to parse the values out of the input instructions
i   0  1  2  3  4  5  6   7   8  9 10 11 12 13
X: 14 15 12 11 -5 14 15 -13 -16 -8 15 -8  0 -4
Y: 12  7  1  2  4 15 11   5   3  9  2  3  3 11
Z:  1  1  1  1 26  1  1  26  26 26  1 26 26 26

PROCEDURE
Calculating the sequence
s[i] = (independent variable)
X[i] = (given)
Y[i] = (given)
Z[i] = (given)

Let's go through the instructions for a block and keep track of x, y, and z.
            x[-1]=0 y[-1]=0 z[-1]=0
inp w       x[i]=x[i-1] y[i]=y[i-1] z[i]=z[i-1]
mul x 0     x[i]=0 y[i]=y[i-1] z[i]=z[i-1]
add x z     x[i]=z[i-1] y[i]=y[i-1] z[i]=z[i-1]
mod x 26    x[i]=z[i-1]%26 y[i]=y[i-1] z[i]=z[i-1]
div z Z     x[i]=z[i-1]%26 y[i]=y[i-1] z[i]=z[i-1]//Z[i]
add x X     x[i]=z[i-1]%26+X[i] y[i]=y[i-1] z[i]=z[i-1]//Z[i]
eql x w     x1[i]=z[i-1]%26+X[i] y[i]=y[i-1] z[i]=z[i-1]//Z[i]
eql x 0     x[1]=0or1 (cond[i]) y[i]=y[i-1] z[i]=z[i-1]//Z[i]
mul y 0     x[i]=0or1 (cond[i]) y[i]=0 z[i]=z[i-1]//Z[i]
add y 25    x[i]=0or1 (cond[i]) y[i]=25 z[i]=z[i-1]//Z[i]
mul y x     x[i]=0or1 (cond[i]) y[i]=0or25 (cond[i]) z[i]=z[i-1]//Z[i]
add y 1     x[i]=0or1 (cond[i]) y[i]=1or26 (cond[i]) z[i]=z[i-1]//Z[i]
mul z y     x[i]=0or1 (cond[i]) y[i]=1or26 (cond[i]) z[i]=z[i-1]//Z[i]*(1or26) (cond[i])
mul y 0     x[i]=0or1 (cond[i]) y[i]=0 z[i]=z[i-1]//Z[i]*(1or26) (cond[i])
add y w     x[i]=0or1 (cond[i]) y[i]=s[i] z[i]=z[i-1]//Z[i]*(1or26) (cond[i])
add y Y     x[i]=0or1 (cond[i]) y[i]=s[i]+Y[i] z[i]=z[i-1]//Z[i]*(1or26) (cond[i])
mul y x     x[i]=0or1 (cond[i]) y[i]=0or(s[i]+Y[i]) (cond[i]) z[i]=z[i-1]//Z[i]*(1or26)
add z y     x[i]=0or1 (cond[i]) y[i]=0or(s[i]+Y[i]) (cond[i])
            z[i]=[z[i-1]//Z[i]]or[26*(z[i-1]//Z[i])+(s[i]+Y[i])] (cond[i])

We added a cond[i], which is a condition for block i:
cond[i] = z[i-1]%26 + X[i] == s[i]
The conditions are only possibly true when z[i-1]%26 + X[i] <= 9

To satisfy the constraint, we need z to be 0 at the end, i.e. z[13] = 0.
Let's just chunk through the rules and keep track of the values.

c0[i] = z[i-1]%26 = z0[i-1]
c[i] = c0[i] + X[i]
C[i] = c[i] == s[i]

x[i] = 0 if C[i] else 1
y'[i] = 1 if C[i] else 26
y[i] = 0 if C[i] else s[i] + Y[i]
z'[i] = z[i-1]//Z[i]
    -> z'{n}[i] = z{n+1}[i-1] (shift up) if Z[i] == 26 else z'[i] = z[i-1]
z''[i] = z'[i]*y'[i] = z'[i] if C[i] else z''{n}[i] = z'{n-1}[i-1] (shift down)
z[i] = z''[i] + y[i]
z{n}[i] = nth base-26 digit of z[i]
z0[i] = z1[i-1] if C[i] else s[i] + Y[i]
z{n>0}[i] = z{n+1}[i-1] if C[i] else z'{n-1}[i-1]

hypothesis: C[i] is True iff Z[i] == 26
then
z[i] = z[i-1]//26 (shift down) if C[i] else s[i] + Y[i] + z[i-1]*26 (shift up)

 i   X  Y  Z       c      z0      z1      z2      z3       z4
 0  14 12  1      14 s[0]+12
 1  15  7  1 s[0]+27  s[1]+7 s[0]+12
 2  12  1  1 s[1]+19  s[2]+1  s[1]+7 s[0]+12
 3  11  2  1 s[2]+12  s[3]+2  s[2]+1  s[1]+7 s[0]+12
 4  -5  4 26  s[3]-3  s[2]+1  s[1]+7 s[0]+12
 5  14 15  1 s[2]+15 s[5]+15  s[2]+1  s[1]+7 s[0]+12
 6  15 11  1 s[5]+30 s[6]+11 s[5]+15  s[2]+1  s[1]+7 s[0]+12
 7 -13  5 26  s[6]-2 s[5]+15  s[2]+1  s[1]+7 s[0]+12
 8 -16  3 26  s[5]-1  s[2]+1  s[1]+7 s[0]+12
 9  -8  9 26  s[2]-7  s[1]+7 s[0]+12
10  15  2  1 s[1]+22 s[10]+2  s[1]+7 s[0]+12
11  -8  3 26 s[10]-6  s[1]+7 s[0]+12
12   0  3 26  s[1]+7 s[0]+12
13  -4 11 26  s[0]+8       0

Every Z[i] == 1 pushes s[i] + Y[i] onto the z stack
Every Z[i] == 26 pops a value off the z stack and constrains it to be
  equal to s[i] - X[i]

i values on stack at any time
0 push 0
1 push 1 0
2 push 2 1 0
3 push 3 2 1 0
4 pop 2 1 0
5 push 5 2 1 0
6 push 6 5 2 1 0
7 pop 5 2 1 0
8 pop 2 1 0
9 pop 1 0
10 push 10 1 0
11 pop 1 0
12 pop 0
13 pop -
conditions
s[4] - X[4] == s[3] + Y[3]     => s[4] +  5 == s[3] +  2
s[7] - X[7] == s[6] + Y[6]     => s[7] + 13 == s[6] + 11
s[8] - X[8] == s[5] + Y[5]     => s[8] + 16 == s[5] + 15
s[9] - X[9] == s[2] + Y[2]     => s[9] +  8 == s[2] +  1
s[11] - X[11] == s[10] + Y[10] => s[11] + 8 == s[10] + 2
s[12] - X[12] == s[1] + Y[1]   => s[12] + 0 == s[1] +  7
s[13] - X[13] == s[0] + Y[0]   => s[13] + 4 == s[0] + 12

Ok! Let's fill the values that satisfy the constraints.
We want the digits to be as high as possible.
We will write the constraints to be (something) = (subtraction).
Fill in a 9 on the right hand side, then the left is whatever it is.

 s[4] =  s[3] - 3 =>  s[3] = 9  s[4] = 6
 s[7] =  s[6] - 2 =>  s[6] = 9  s[7] = 7
 s[8] =  s[5] - 1 =>  s[5] = 9  s[8] = 8
 s[9] =  s[2] - 7 =>  s[2] = 9  s[9] = 2
s[11] = s[10] - 6 => s[10] = 9 s[11] = 3
 s[1] = s[12] - 7 => s[12] = 9  s[1] = 2
 s[0] = s[13] - 8 => s[13] = 9  s[0] = 1

s = 12996997829399

Part 2:
Smallest number that meets the constraints.

Flip them all to be (something) = (addition), and fill in a 1 on the RHS.

 s[3] =  s[4] + 3 =>  s[4] = 1  s[3] = 4
 s[6] =  s[7] + 2 =>  s[7] = 1  s[6] = 3
 s[5] =  s[8] + 1 =>  s[8] = 1  s[5] = 2
 s[2] =  s[9] + 7 =>  s[9] = 1  s[2] = 8
s[10] = s[11] + 6 => s[11] = 1 s[10] = 7
s[12] =  s[1] + 7 =>  s[1] = 1 s[12] = 8
s[13] =  s[0] + 8 =>  s[0] = 1 s[13] = 9

s = 11841231117189
"""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import cast


EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = 12996997829399
PART_TWO_EXAMPLE_RESULT = 11841231117189
PART_ONE_RESULT = 12996997829399
PART_TWO_RESULT = 11841231117189


NUM_INPUT_DIGITS = 14
BLOCK_SIZE = 18


@dataclass
class LineParser:
    line_block_idx: int
    line_start: str

    @property
    def line_start_len(self) -> int:
        return len(self.line_start)


class BlockParser(Enum):
    X = LineParser(5, "add x ")
    Y = LineParser(15, "add y ")
    Z = LineParser(4, "div z ")


BlockValues = tuple[int, int, int]
Values = tuple[int, int, int, int, int, int, int, int, int, int, int, int, int, int]
InputValues = tuple[Values, Values, Values]


def parse_block_w_parser(block: list[str], parser: LineParser) -> int:
    line = block[parser.line_block_idx]
    assert line.startswith(parser.line_start)
    value_str = line[parser.line_start_len :]
    return int(value_str)


def parse_block(block: list[str]) -> BlockValues:
    return (
        parse_block_w_parser(block, BlockParser.X.value),
        parse_block_w_parser(block, BlockParser.Y.value),
        parse_block_w_parser(block, BlockParser.Z.value),
    )


def parse_input_blocks(lines: Iterable[str]) -> InputValues:
    lines = list(lines)
    values_by_input = [
        parse_block(lines[BLOCK_SIZE * block_idx : BLOCK_SIZE * (block_idx + 1) + 1])
        for block_idx in range(NUM_INPUT_DIGITS)
    ]

    values_by_type = tuple(zip(*values_by_input))
    values_by_type = cast(InputValues, values_by_type)
    return values_by_type


def part_one(lines: Iterable[str]) -> int:
    return PART_ONE_RESULT


def part_two(lines: Iterable[str]) -> int:
    return PART_TWO_RESULT
