#!/usr/bin/env python
"""
Bingo

The score of the winning board can now be calculated. Start by finding the sum of all unmarked numbers on that board; in this case, the sum is 188. Then, multiply that sum by the number that was just called when the board won, 24, to get the final score, 188 * 24 = 4512.

Part 2
Figure out which board will win last.
"""

from collections.abc import Iterable
from itertools import islice
from typing import Optional, TypeVar

T = TypeVar("T")


class Board:
    unmarked_values_to_pos: dict[int, tuple[int, int]]
    marked_values_to_pos: dict[int, tuple[int, int]]
    row_counts: list[int]
    col_counts: list[int]
    
    def __init__(self, lines: Iterable[list[int]]):
        self.unmarked_values_to_pos = {}
        self.marked_values_to_pos = {}
        self.row_counts = [0]*5
        self.col_counts = [0]*5

        for row, line in enumerate(lines):
            # print(row, line)
            for col, value in enumerate(line):
                self.unmarked_values_to_pos[value] = (row, col)
                
        # print(self)
                
    def mark(self, value: int) -> Optional[int]:
        # print(self.unmarked_values_to_pos)
        # print(value)
        row, col = self.unmarked_values_to_pos.pop(value, (None, None))
        if row is None or col is None:
            return
            
        self.marked_values_to_pos[value] = row, col
        self.row_counts[row] += 1
        self.col_counts[col] += 1
        
        if self.row_counts[row] == 5 or self.col_counts[col] == 5:
            return self.calculate_win(value)
        
        return None
        
    def calculate_win(self, value: int):
        return sum(self.unmarked_values_to_pos.keys())
        
    def __str__(self):
        empty_line = ["-"]*6
        first_line = [" "] + [f"{cc: ^4}" for cc in self.col_counts]
        lines = [first_line] + [list(empty_line) for _ in range(5)]
        for row, row_count in enumerate(self.row_counts, 1):
            lines[row][0] = f"{row_count: <0}"
        for v, (r, c) in self.unmarked_values_to_pos.items():
            lines[r+1][c+1] = f"{v: ^4}"
        for v, (r, c) in self.marked_values_to_pos.items():
            lines[r+1][c+1] = f"{v:*^4}"
        return "\n".join(" ".join(l) for l in lines)


def parse_lines(lines: Iterable[str]) -> tuple[list[int], list[Board]]:
    
    def chunk(iterable: Iterable[T], n: int) -> Iterable[tuple[T]]:
        args = [iter(iterable)]*n
        return zip(*args)
    
    def parse_board(lines_: Iterable[str]) -> Board:
        return Board(parse_board_line(line) for line in lines_)

    def parse_board_line(line: str) -> list[int]:
        return [int(value) for value in line.strip().split()]
    
    # row of draws
    draws = [int(draw) for draw in next(lines).strip().split(",")]
    
    # rest of lines are boards
    boards = [parse_board(list(line_chunk[1:])) for line_chunk in chunk(lines, 6)]
    
    return draws, boards

def part_two(lines: Iterable[str]) -> int:
    
    draws, boards = parse_lines(lines)
    id_board = dict(enumerate(boards, 1))

    for value in draws:
        for idx, board in list(id_board.items()):
            result = board.mark(value)
            if result is not None:
                # print(f"Board {idx}, {result}*{value} = {result*value}")
                del id_board[idx]
        if len(id_board) == 0:
            break

    # print(f"Board {idx}, {result}*{value} = {result*value}")
    return result*value


def part_one(lines: Iterable[str]) -> int:
    draws, boards = parse_lines(lines)
    
    for value in draws:
        for idx, board in enumerate(boards, 1):
            result = board.mark(value)
            if result is not None:
                # print(f"Board {idx}, {result}*{value} = {result*value}")
                return result*value

    raise RuntimeError("Nobody won")
    