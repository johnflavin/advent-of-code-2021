#!/usr/bin/env python
"""
Fish create a new fish every 7 days
We get a sequence "ticks": how many days until each fish makes a new fish
On tick 0, reset tick to 6 and make a new fish with tick 8

part 1: how many fish after 80 days
part 2: how many fish after 256 days
"""

from collections import Counter
from collections.abc import Iterable


def solution(lines: Iterable[str], num_days: int) -> int:
    line = next(lines)

    # Convert line to int
    # This is of len = initial num fish
    # Can't store it this way as we update or our memory will explode
    raw_ticks = (int(x) for x in line.split(","))

    # Count how many have given number of ticks
    tick_counts = Counter(raw_ticks)

    # Store number at given tick
    # This will never grow, so our memory stays bounded
    # Only the values stored in here will grow
    state = [0]*9
    for tick, count in tick_counts.items():
        state[tick] = count

    # Update the ticks for each day
    for _ in range(num_days):
        # all ticks at zero will spawn
        num_spawn = state[0]
        
        # drop the count at tick n to tick n-1 for n > 0
        state[:8] = state[1:]
        
        # Spawn new at tick = 8
        state[8] = num_spawn
        
        # After spawn, reset ticks at 0 back to 6
        state[6] += num_spawn

    # Number of fish is total number at all tick states
    return sum(state)


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, 80)


def part_two(lines: Iterable[str]) -> int:
    return solution(lines, 256)
