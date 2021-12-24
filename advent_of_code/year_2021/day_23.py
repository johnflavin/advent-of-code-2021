#!/usr/bin/env python
"""
A bunch of amphpods in different rooms. They want to be sorted.
Take different amounts of energy to move.

Part 1:
What is the least energy required to organize the amphipods?

Here's what I'm thinking. This is a pathfinding problem, and I can use
A* to find the solution. But it won't be finding the path of a
single amphipod to its destination. We will find a path through a
state space where:
* Each node is a state representing the positions of all amphipods
* The edges between nodes represent a move an amphipod can make

The tricky part here is the number of states. There are a huge number
of potential states. I'm not sure the exact number, but
it's something like (15 8) (choose 8 locations for the 8 amphipods) times
4! (from the different ways to place an A, B, C, or D in each space).
Which is on the order of a million or so? Many of them would be inaccessible
from the starting position so we could certainly prune them, which would
limit the size of the state space somewhat. But I just don't
know if it would be worth it to pregenerate all the states vs create them when
we get to them.

I'll come back to that question in a bit.

We need a few things for any search algorithm:
* Nodes/States: the positions of all the amphipods
* Edges/Moves: Moves that amphipods can make to take them from one state to another
* Weights: The cost of each move
* Start: A particular state that we are given to start from
* End: A particular state that we are trying to reach

If we're doing A* we also need a heuristic: A way to determine
how close a given state is to the end state. This is used to determine
which states to give priority to when checking for new states.
Typically on a grid the heuristic would be a distance. But we'll have to get
a bit more creative to create a heuristic in our state space. I don't
know the best way. But I'm thinking I could maybe use the distance of each amphipod
from its goal position, with an additional penality if one is in the correct state but
blocking one that is in an incorrect goal space. And maybe the cost of the moves
should also be factored in?

I'm looking at this guide to A*:
https://www.redblobgames.com/pathfinding/a-star/introduction.html
The A* algorithm is guaranteed to find the best path if the heuristic is "admissable"
(https://en.wikipedia.org/wiki/Admissible_heuristic) i.e. the heuristic to reach
the goal from state n is always less than or equal to the true cost to reach the
goal from state n.
That makes me think the heuristic should be the cost to move all the amphipods
into the correct spots, ignoring any interactions. Like "how many spaces are you away
from your goal space, and what does it cost to move there".
As if they can move through each other. That will always be less than or equal
to the true cost, since they will definitely need to move at least that many spaces.

"""

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from functools import cache
from queue import PriorityQueue


EXAMPLE = """\
#############
#...........#
###B#C#B#D###
  #A#D#C#A#
  #########
"""
PART_ONE_EXAMPLE_RESULT = 12521
PART_TWO_EXAMPLE_RESULT = None
PART_ONE_RESULT = 19046
PART_TWO_RESULT = None


class Apod(Enum):
    A = auto()
    B = auto()
    C = auto()
    D = auto()


APOD_MOVE_COSTS = {
    Apod.A: 1,
    Apod.B: 10,
    Apod.C: 100,
    Apod.D: 1000,
}


class Location(Enum):
    HALL_LEFT_LEFT = auto()
    HALL_LEFT_RIGHT = auto()
    HALL_AB = auto()
    HALL_BC = auto()
    HALL_CD = auto()
    HALL_RIGHT_LEFT = auto()
    HALL_RIGHT_RIGHT = auto()
    A_UP = auto()
    B_UP = auto()
    C_UP = auto()
    D_UP = auto()
    A_DOWN = auto()
    B_DOWN = auto()
    C_DOWN = auto()
    D_DOWN = auto()


@dataclass(frozen=True)
class EndLocation:
    down: Location
    up: Location


END_LOCATIONS = {
    Apod.A: EndLocation(
        Location.A_DOWN,
        Location.A_UP,
    ),
    Apod.B: EndLocation(
        Location.B_DOWN,
        Location.B_UP,
    ),
    Apod.C: EndLocation(
        Location.C_DOWN,
        Location.C_UP,
    ),
    Apod.D: EndLocation(
        Location.D_DOWN,
        Location.D_UP,
    ),
}


LOCATION_GRAPH = {
    Location.A_DOWN: {
        Location.A_UP: 1,
    },
    Location.A_UP: {
        Location.A_DOWN: 1,
        Location.HALL_LEFT_RIGHT: 2,
        Location.HALL_AB: 2,
    },
    Location.B_DOWN: {
        Location.B_UP: 1,
    },
    Location.B_UP: {
        Location.B_DOWN: 1,
        Location.HALL_AB: 2,
        Location.HALL_BC: 2,
    },
    Location.C_DOWN: {
        Location.C_UP: 1,
    },
    Location.C_UP: {
        Location.C_DOWN: 1,
        Location.HALL_BC: 2,
        Location.HALL_CD: 2,
    },
    Location.D_DOWN: {
        Location.D_UP: 1,
    },
    Location.D_UP: {
        Location.D_DOWN: 1,
        Location.HALL_CD: 2,
        Location.HALL_RIGHT_LEFT: 2,
    },
    Location.HALL_LEFT_LEFT: {
        Location.HALL_LEFT_RIGHT: 1,
    },
    Location.HALL_LEFT_RIGHT: {
        Location.HALL_LEFT_LEFT: 1,
        Location.A_UP: 2,
        Location.HALL_AB: 2,
    },
    Location.HALL_RIGHT_LEFT: {
        Location.HALL_RIGHT_RIGHT: 1,
        Location.D_UP: 2,
        Location.HALL_CD: 2,
    },
    Location.HALL_RIGHT_RIGHT: {
        Location.HALL_RIGHT_LEFT: 1,
    },
    Location.HALL_AB: {
        Location.HALL_LEFT_RIGHT: 2,
        Location.A_UP: 2,
        Location.B_UP: 2,
        Location.HALL_BC: 2,
    },
    Location.HALL_BC: {
        Location.HALL_AB: 2,
        Location.HALL_CD: 2,
        Location.B_UP: 2,
        Location.C_UP: 2,
    },
    Location.HALL_CD: {
        Location.HALL_BC: 2,
        Location.HALL_RIGHT_LEFT: 2,
        Location.C_UP: 2,
        Location.D_UP: 2,
    },
}


def calculate_move_costs() -> dict[tuple[Location, Location], int]:
    costs: dict[tuple[Location, Location], int] = {}
    frontier: set[tuple[Location, Location, int]] = set()

    # Prime with zeroth order
    for loc in Location:
        costs[(loc, loc)] = 0

    # prime with first order
    for start, end_dict in LOCATION_GRAPH.items():
        for end, cost in end_dict.items():
            costs[(start, end)] = cost
            frontier.add((start, end, cost))

    while frontier:
        start, end0, cost0 = frontier.pop()

        for end1, cost1 in LOCATION_GRAPH[end0].items():
            new_pair = (start, end1)
            new_cost = cost0 + cost1
            if new_pair not in costs:
                frontier.add((start, end1, new_cost))
                costs[new_pair] = new_cost
            elif costs[(new_pair)] > new_cost:
                frontier.discard((start, end1, costs[new_pair]))
                frontier.add((start, end1, new_cost))
                costs[new_pair] = new_cost

    return costs


# Cost to move directly from one location to another, if such a move
# is available, without taking into account different amphipod costs
LOCATION_MOVE_COSTS = calculate_move_costs()


@cache
def heuristic(
    a0: Location,
    a1: Location,
    b0: Location,
    b1: Location,
    c0: Location,
    c1: Location,
    d0: Location,
    d1: Location,
) -> int:

    all_locs_set = {a0, a1, b0, b1, c0, c1, d0, d1}
    return sum(
        apod_heuristic(apod, loc_pair, all_locs_set - set(loc_pair))
        for apod, loc_pair in zip(Apod, ((a0, a1), (b0, b1), (c0, c1), (d0, d1)))
    )


def apod_heuristic(
    apod: Apod, loc_pair: tuple[Location, Location], non_apod_locs: set[Location]
) -> int:
    """Cost to move the two amphipods of type apod from their locations to the end,
    (mostly) ignoring all other amphipods"""
    end_locs = END_LOCATIONS[apod]

    if loc_pair[0] == end_locs.down or loc_pair[1] == end_locs.down:
        # At least one of them is in the correct place. Awesome.
        other_idx = int(loc_pair[0] == end_locs.down)
        other = loc_pair[other_idx]

        if other == end_locs.up:
            # These two are in the right place. No moves = no cost.
            return 0
        else:
            # Cost to move the other one to the upper end loc
            return move_cost(apod, other, end_locs.up)
    elif (
        loc_pair[0] == end_locs.up or loc_pair[1] == end_locs.up
    ) and end_locs.down in non_apod_locs:
        # We have one in the correct upper location, but it is blocking
        # a wrong one below it.
        # We would need to move the correct one out and back costing 2 each way.
        unblock_move_cost = 4
        not_end_loc = loc_pair[1] if loc_pair[0] == end_locs.up else loc_pair[0]
        return APOD_MOVE_COSTS[apod] * (
            unblock_move_cost + LOCATION_MOVE_COSTS[not_end_loc, end_locs.down]
        )
    else:
        # Ordinary move
        # Average the cost of each to move to the bottom or the top
        return (
            sum(
                move_cost(apod, loc, end_locs.down) + move_cost(apod, loc, end_locs.up)
                for loc in loc_pair
            )
            // 2
        )


def move_cost(apod: Apod, start: Location, end: Location) -> int:
    return APOD_MOVE_COSTS[apod] * LOCATION_MOVE_COSTS[(start, end)]


@dataclass(frozen=True, init=False)
class State:
    a0: Location
    a1: Location
    b0: Location
    b1: Location
    c0: Location
    c1: Location
    d0: Location
    d1: Location

    def __init__(
        self,
        a0: Location,
        a1: Location,
        b0: Location,
        b1: Location,
        c0: Location,
        c1: Location,
        d0: Location,
        d1: Location,
    ):
        object.__setattr__(self, "a0", a0 if a0.value < a1.value else a1)
        object.__setattr__(self, "a1", a0 if a0.value > a1.value else a1)
        object.__setattr__(self, "b0", b0 if b0.value < b1.value else b1)
        object.__setattr__(self, "b1", b0 if b0.value > b1.value else b1)
        object.__setattr__(self, "c0", c0 if c0.value < c1.value else c1)
        object.__setattr__(self, "c1", c0 if c0.value > c1.value else c1)
        object.__setattr__(self, "d0", d0 if d0.value < d1.value else d1)
        object.__setattr__(self, "d1", d0 if d0.value > d1.value else d1)

    def move(self, loc_name: str, new_loc: Location) -> "State":
        return State(**{**asdict(self), loc_name: new_loc})

    def neighbors(self) -> Iterable[tuple["State", int]]:
        current_locs_dict = asdict(self)
        currently_occupied_locs = set(current_locs_dict.values())
        for loc_name, current_loc in current_locs_dict.items():
            for next_loc in LOCATION_GRAPH[current_loc].keys():
                if next_loc not in currently_occupied_locs:
                    apod = (
                        Apod.A
                        if loc_name[0] == "a"
                        else Apod.B
                        if loc_name[0] == "b"
                        else Apod.C
                        if loc_name[0] == "c"
                        else Apod.D
                    )
                    cost = move_cost(apod, current_loc, next_loc)
                    yield State(**{**current_locs_dict, loc_name: next_loc}), cost


@dataclass(frozen=True, order=True)
class PrioritizableState:
    priority: float
    state: State = field(compare=False)

    def neighbors(self) -> Iterable[tuple["State", int]]:
        return self.state.neighbors()


END = State(
    Location.A_DOWN,
    Location.A_UP,
    Location.B_DOWN,
    Location.B_UP,
    Location.C_DOWN,
    Location.C_UP,
    Location.D_DOWN,
    Location.D_UP,
)


def state_heuristic(s: State) -> int:
    return heuristic(s.a0, s.a1, s.b0, s.b1, s.c0, s.c1, s.d0, s.d1)


def solve(start: State) -> tuple[int, list[State]]:
    frontier: PriorityQueue[PrioritizableState] = PriorityQueue()
    frontier.put(PrioritizableState(0, start))
    came_from: dict[State, State] = dict()
    cost_so_far: dict[State, int] = dict()
    # came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current.state == END:
            break

        for next_state, next_state_move_cost in current.neighbors():
            new_cost = cost_so_far[current.state] + next_state_move_cost
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                priority = new_cost + state_heuristic(next_state)
                frontier.put(PrioritizableState(priority, next_state))
                came_from[next_state] = current.state

    # unwind path
    path = []
    current_state = END
    while current_state in came_from:
        path.append(current_state)
        current_state = came_from[current_state]
    path.append(start)

    return cost_so_far.get(END, -1), path[::-1]


def pretty_print(state: State) -> str:
    loc_strs = {loc: "." for loc in Location}
    loc_strs[state.a0] = "A"
    loc_strs[state.a1] = "A"
    loc_strs[state.b0] = "B"
    loc_strs[state.b1] = "B"
    loc_strs[state.c0] = "C"
    loc_strs[state.c1] = "C"
    loc_strs[state.d0] = "D"
    loc_strs[state.d1] = "D"
    return """\
#############
#{}{}.{}.{}.{}.{}{}#
###{}#{}#{}#{}###
  #{}#{}#{}#{}#
  #########""".format(
        *[loc_strs[loc] for loc in Location]
    )


def parse_lines(lines: Iterable[str]) -> State:
    lines = list(lines)
    up_locs = lines[2][3:-3].split("#")
    down_locs = lines[3].strip()[1:-1].split("#")
    locs: dict[str, list[Location]] = {"A": [], "B": [], "C": [], "D": []}
    for letter, loc in zip(
        up_locs + down_locs,
        (
            Location.A_UP,
            Location.B_UP,
            Location.C_UP,
            Location.D_UP,
            Location.A_DOWN,
            Location.B_DOWN,
            Location.C_DOWN,
            Location.D_DOWN,
        ),
    ):
        locs[letter].append(loc)
    return State(
        *locs["A"],
        *locs["B"],
        *locs["C"],
        *locs["D"],
    )


def part_one(lines: Iterable[str]) -> int:
    start = parse_lines(lines)
    cost, path = solve(start)
    for state in path:
        print(pretty_print(state))
    return cost


def part_two(lines: Iterable[str]) -> int:
    return 0
