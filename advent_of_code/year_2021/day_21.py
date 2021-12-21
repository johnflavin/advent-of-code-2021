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


@dataclass(frozen=True)
class PlayerState:
    player_idx: int
    position: int
    score: int

    def move(self, new_pos: int) -> "PlayerState":
        return PlayerState(
            player_idx=self.player_idx, position=new_pos, score=self.score + new_pos
        )


@dataclass(frozen=True)
class GameState:
    score_goal: int
    next_turn_player: PlayerState
    other_player: PlayerState

    @property
    def players(self) -> list[PlayerState]:
        return [self.next_turn_player, self.other_player]

    @property
    def is_finished(self) -> bool:
        return self.winner is not None

    @property
    def winner(self) -> PlayerState | None:
        for p in self.players:
            if p.score >= self.score_goal:
                return p
        return None

    @property
    def winning_score(self) -> int | None:
        winner = self.winner
        return winner.score if winner else None

    @property
    def loser(self) -> PlayerState | None:
        winner = self.winner
        if winner is None:
            return None
        for p in self.players:
            if p != winner:
                return p
        return None

    @property
    def losing_score(self) -> int | None:
        loser = self.loser
        return loser.score if loser else None

    def move(self, new_pos) -> "GameState":
        return GameState(
            score_goal=self.score_goal,
            next_turn_player=self.other_player,
            other_player=self.next_turn_player.move(new_pos),
        )


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


def parse_lines(lines: Iterable[str]) -> list[PlayerState]:
    return [
        PlayerState(
            player_idx=int(line.split(" ")[1]),
            position=int(line.split(": ")[-1]),
            score=0,
        )
        for line in lines
    ]


def play_deterministic(game: GameState) -> FinishedGame:
    die = deterministic_die_gen()
    board_spaces = 10

    die_rolls = 0
    while not game.is_finished:
        die_rolls += 3
        rolls = list(islice(die, 3))
        move = sum(rolls)
        new_pos = (game.next_turn_player.position + move) % board_spaces or board_spaces
        game = game.move(new_pos)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Player {game.other_player.player_idx} "
                f"rolls {rolls[0]}+{rolls[1]}+{rolls[2]} "
                f"and moves {move} "
                f"for a total score of {game.other_player.score}."
            )

    winning_score = game.winning_score
    losing_score = game.losing_score
    assert winning_score is not None and losing_score is not None
    return FinishedGame(winning_score, losing_score, die_rolls)


def part_one(lines: Iterable[str]) -> int:

    players = parse_lines(lines)
    start = GameState(1000, *players)
    finished_game = play_deterministic(start)
    return finished_game.low_score * finished_game.num_die_rolls


def part_two(lines: Iterable[str]) -> int:
    return 0
