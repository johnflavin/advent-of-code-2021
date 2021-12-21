#!/usr/bin/env python
"""
Dirac dice
Circular board labeled 1 through 10
Roll dice three times and move according to the sum (wrap from 10 -> 1)
Add the space you land on to your score
Game ends when a player reaches 1000

Part 1
Use a deterministic die: d100 that always rolls 1, 2, 3, ..., 99, 100, 1, 2, ...
what do you get if you multiply the score of the losing player
by the number of times the die was rolled during the game?

Part 2
Rolling the die splits the universe into three copies:
one where the outcome of the roll was 1, one where it was 2, and one where it was 3.
Find the player that wins in more universes;
in how many universes does that player win?
"""

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import islice


EXAMPLE = """\
Player 1 starting position: 4
Player 2 starting position: 8
"""
PART_ONE_EXAMPLE_RESULT = 739785
PART_TWO_EXAMPLE_RESULT = 444356092776315
PART_ONE_RESULT = 432450
PART_TWO_RESULT = None


logger = logging.getLogger(__name__)


@dataclass
class Player:
    position: int
    score: int


@dataclass
class FinishedGame:
    high_score: int
    low_score: int
    num_die_rolls: int


def deterministic_die_gen():
    i = 0
    while True:
        yield (i % 100) + 1
        i += 1


def parse_lines(lines: Iterable[str]) -> list[Player]:
    return [Player(position=int(line.split(": ")[-1]), score=0) for line in lines]


def play(players: list[Player]) -> FinishedGame:
    die = deterministic_die_gen()
    p = 0
    die_rolls = 0
    while players[p].score < 1000 and players[not p].score < 1000:
        die_rolls += 3
        rolls = list(islice(die, 3))
        move = sum(rolls)

        new_pos = (players[p].position + move) % 10
        new_pos = new_pos or 10

        players[p].position = new_pos
        players[p].score += new_pos

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Player {p+1} "
                f"rolls {rolls[0]}+{rolls[1]}+{rolls[2]} "
                f"and moves {move} to space {new_pos} "
                f"for a total score of {players[p].score}."
            )

        p = int(not p)

    return FinishedGame(players[not p].score, players[p].score, die_rolls)


def part_one(lines: Iterable[str]) -> int:

    players = parse_lines(lines)
    finished_game = play(players)
    return finished_game.low_score * finished_game.num_die_rolls


def part_two(lines: Iterable[str]) -> int:
    return 0
