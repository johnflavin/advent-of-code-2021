#!/usr/bin/env python
"""
Bingo

The score of the winning board can now be calculated.
Start by finding the sum of all unmarked numbers on that board;
in this case, the sum is 188.
Then, multiply that sum by the number that was just called when the board won, 24,
to get the final score, 188 * 24 = 4512.

Part 2
Figure out which board will win last.
"""

from collections.abc import Iterable


EXAMPLE = """\
7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1

22 13 17 11  0
 8  2 23  4 24
21  9 14 16  7
 6 10  3 18  5
 1 12 20 15 19

 3 15  0  2 22
 9 18 13 17  5
19  8  7 25 23
20 11 10 24  4
14 21 16 12  6

14 21 17 24  4
10 16 15  9 19
18  8 23 26 20
22 11 13  6  5
 2  0 12  3  7
"""
PART_ONE_EXAMPLE_RESULT = 4512
PART_TWO_EXAMPLE_RESULT = 1924
PART_ONE_RESULT = 39902
PART_TWO_RESULT = 26936


class Board:
    unmarked_values_to_pos: dict[int, tuple[int, int]]
    marked_values_to_pos: dict[int, tuple[int, int]]
    row_counts: list[int]
    col_counts: list[int]

    def __init__(self, lines: Iterable[list[int]]):
        self.unmarked_values_to_pos = {}
        self.marked_values_to_pos = {}
        self.row_counts = [0] * 5
        self.col_counts = [0] * 5

        for row, line in enumerate(lines):
            # print(row, line)
            for col, value in enumerate(line):
                self.unmarked_values_to_pos[value] = (row, col)

        # print(self)

    def mark(self, value: int) -> int:
        # print(self.unmarked_values_to_pos)
        # print(value)
        row, col = self.unmarked_values_to_pos.pop(value, (None, None))
        if row is None or col is None:
            return -1

        self.marked_values_to_pos[value] = row, col
        self.row_counts[row] += 1
        self.col_counts[col] += 1

        if self.row_counts[row] == 5 or self.col_counts[col] == 5:
            # Win!
            # print(self)
            return sum(self.unmarked_values_to_pos.keys())

        return -1

    def __str__(self):
        empty_line = [" -  "] * 6
        first_line = [" "] + [f"{cc: ^4}" for cc in self.col_counts]
        lines = [first_line] + [list(empty_line) for _ in range(5)]
        for row, row_count in enumerate(self.row_counts, 1):
            lines[row][0] = f"{row_count: <0}"
        for v, (r, c) in self.unmarked_values_to_pos.items():
            lines[r + 1][c + 1] = f"{v: ^4}"
        for v, (r, c) in self.marked_values_to_pos.items():
            lines[r + 1][c + 1] = f"{v:*^4}"
        return "\n".join(" ".join(line) for line in lines)


def parse_lines(lines: Iterable[str]) -> tuple[list[int], list[Board]]:
    def parse_board(lines_: Iterable[str]) -> Board:
        return Board(parse_board_line(line) for line in lines_)

    def parse_board_line(line: str) -> list[int]:
        return [int(value) for value in line.strip().split()]

    lines = list(lines)

    # First row of lines = draws
    draws = [int(draw) for draw in lines.pop(0).strip().split(",")]

    # Next row is blank
    lines.pop(0)

    # rest of lines are boards
    boards = []
    while len(lines) >= 5:
        boards.append(parse_board(lines[:6]))
        lines = lines[6:]

    return draws, boards


def part_two(lines: Iterable[str]) -> int:

    draws, boards = parse_lines(lines)
    id_board = dict(enumerate(boards, 1))

    result = -1
    value = 0
    for value in draws:
        for idx, board in list(id_board.items()):
            result = board.mark(value)
            if result > -1:
                # print(f"Board {idx}, {result}*{value} = {result*value}")
                del id_board[idx]
        if len(id_board) == 0:
            break

    # print(f"Board {idx}, {result}*{value} = {result*value}")
    return result * value


def part_one(lines: Iterable[str]) -> int:
    draws, boards = parse_lines(lines)

    result = -1
    value = 0
    for value in draws:
        for idx, board in enumerate(boards, 1):
            result = board.mark(value)
            if result > -1:
                # print(f"Board {idx}, {result}*{value} = {result*value}")
                return result * value

    raise RuntimeError("Nobody won")
