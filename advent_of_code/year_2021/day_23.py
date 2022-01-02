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

import itertools
from abc import ABC
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import InitVar, asdict, dataclass, field
from enum import Enum, IntEnum, auto
from queue import PriorityQueue
from typing import Generic, Type, TypeVar


EXAMPLE = """\
#############
#...........#
###B#C#B#D###
  #A#D#C#A#
  #########"""
PART_ONE_EXAMPLE_RESULT = 12521
PART_TWO_EXAMPLE_RESULT = 44169
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


class Location(IntEnum):
    pass


class Part1Location(Location):
    HALL_00 = auto()
    HALL_01 = auto()
    HALL_AB = auto()
    HALL_BC = auto()
    HALL_CD = auto()
    HALL_10 = auto()
    HALL_11 = auto()
    A0 = auto()
    B0 = auto()
    C0 = auto()
    D0 = auto()
    A1 = auto()
    B1 = auto()
    C1 = auto()
    D1 = auto()


class Part2Location(Location):
    HALL_00 = auto()
    HALL_01 = auto()
    HALL_AB = auto()
    HALL_BC = auto()
    HALL_CD = auto()
    HALL_10 = auto()
    HALL_11 = auto()
    A0 = auto()
    B0 = auto()
    C0 = auto()
    D0 = auto()
    A1 = auto()
    B1 = auto()
    C1 = auto()
    D1 = auto()
    A2 = auto()
    B2 = auto()
    C2 = auto()
    D2 = auto()
    A3 = auto()
    B3 = auto()
    C3 = auto()
    D3 = auto()


LocationT = TypeVar("LocationT", bound=Location)
BASE_LOCATION_GRAPH = {
    "A1": {
        "A0": 1,
    },
    "A0": {
        "A1": 1,
        "HALL_01": 2,
        "HALL_AB": 2,
    },
    "B1": {
        "B0": 1,
    },
    "B0": {
        "B1": 1,
        "HALL_AB": 2,
        "HALL_BC": 2,
    },
    "C1": {
        "C0": 1,
    },
    "C0": {
        "C1": 1,
        "HALL_BC": 2,
        "HALL_CD": 2,
    },
    "D1": {
        "D0": 1,
    },
    "D0": {
        "D1": 1,
        "HALL_CD": 2,
        "HALL_10": 2,
    },
    "HALL_00": {
        "HALL_01": 1,
    },
    "HALL_01": {
        "HALL_00": 1,
        "A0": 2,
        "HALL_AB": 2,
    },
    "HALL_10": {
        "HALL_11": 1,
        "D0": 2,
        "HALL_CD": 2,
    },
    "HALL_11": {
        "HALL_10": 1,
    },
    "HALL_AB": {
        "HALL_01": 2,
        "A0": 2,
        "B0": 2,
        "HALL_BC": 2,
    },
    "HALL_BC": {
        "HALL_AB": 2,
        "HALL_CD": 2,
        "B0": 2,
        "C0": 2,
    },
    "HALL_CD": {
        "HALL_BC": 2,
        "HALL_10": 2,
        "C0": 2,
        "D0": 2,
    },
}


@dataclass
class LocationInfo(Generic[LocationT]):
    Loc: Type[LocationT]
    graph: dict[LocationT, dict[LocationT, int]] = field(init=False)
    movement_costs: dict[tuple[LocationT, LocationT], int] = field(init=False)
    end_locs: dict[Apod, list[LocationT]] = field(init=False)

    tunnel_depth: InitVar[int]

    def __post_init__(self, tunnel_depth: int):
        self.graph = self.build_location_graph(tunnel_depth)
        self.movement_costs = self.calculate_move_costs()
        self.end_locs = {
            apod: [self.Loc[f"{apod.name}{i}"] for i in range(tunnel_depth)]
            for apod in Apod
        }

    def move_cost(self, apod: Apod, start: LocationT, end: LocationT) -> int:
        return APOD_MOVE_COSTS[apod] * self.movement_costs[(start, end)]

    def build_location_graph(
        self, tunnel_depth: int
    ) -> dict[LocationT, dict[LocationT, int]]:
        """Build the full location graph"""
        # Build the location graph given the enu
        # Start with the base locations that will always be there.
        location_graph: dict[LocationT, dict[LocationT, int]] = defaultdict(dict)
        for loc0_name, base_loc_dict in BASE_LOCATION_GRAPH.items():
            loc0 = self.Loc[loc0_name]
            for loc1_name, movement_cost in base_loc_dict.items():
                loc1 = self.Loc[loc1_name]
                location_graph[loc0][loc1] = movement_cost

        # Add the locations we defined based on the input, if necessary
        for i in range(2, tunnel_depth):
            for apod in Apod:
                this_loc = self.Loc[f"{apod.name}{i}"]
                above = self.Loc[f"{apod.name}{i-1}"]
                location_graph[this_loc][above] = 1
                location_graph[above][this_loc] = 1

                if i < tunnel_depth - 1:
                    below = self.Loc[f"{apod.name}{i+1}"]
                    location_graph[this_loc][below] = 1
                    location_graph[below][this_loc] = 1

        return location_graph

    def calculate_move_costs(self) -> dict[tuple[LocationT, LocationT], int]:
        costs: dict[tuple[LocationT, LocationT], int] = {}
        frontier: set[tuple[LocationT, LocationT, int]] = set()

        # Prime with zeroth order
        for loc in self.Loc:
            costs[(loc, loc)] = 0

        # prime with first order
        for loc0, loc1_dict in self.graph.items():
            for loc1, cost in loc1_dict.items():
                costs[(loc0, loc1)] = cost
                frontier.add((loc0, loc1, cost))

        # Add all other orders by traversing graph
        while frontier:
            loc0, loc1, cost01 = frontier.pop()

            for loc2, cost12 in self.graph[loc1].items():
                new_pair = (loc0, loc2)
                new_cost = cost01 + cost12
                if new_pair not in costs:
                    frontier.add((loc0, loc2, new_cost))
                    costs[new_pair] = new_cost
                elif costs[(new_pair)] > new_cost:
                    frontier.discard((loc0, loc2, costs[new_pair]))
                    frontier.add((loc0, loc2, new_cost))
                    costs[new_pair] = new_cost

        return costs


# @dataclass(frozen=True, init=False)
class State(ABC):
    # A: tuple[Location, ...]
    # B: tuple[Location, ...]
    # C: tuple[Location, ...]
    # D: tuple[Location, ...]

    num_apods_per_type: int
    current_state_dict: dict[Apod, tuple[Location, ...]]
    occupied_locations: set[Location]

    def __init__(self, locations: Mapping[Apod, Iterable[Location]]):
        self.current_state_dict = {
            apod: tuple(sorted(locations[apod])) for apod in Apod
        }
        self.occupied_locations = set(
            itertools.chain(*self.current_state_dict.values())
        )

    def apod_locs(self, apod: Apod) -> tuple[Location, ...]:
        return self.current_state_dict[apod]

    def neighbors(
        self: "StateT", loc_info: LocationInfo
    ) -> "Iterable[tuple[StateT, int]]":
        # print(f"{current_state_dict=}")

        # Try to move each apod type
        for apod, current_apod_locs in self.current_state_dict.items():
            # Try to move each individual apod within the type
            for current_loc_idx, current_loc in enumerate(current_apod_locs):
                # Find possible next steps
                for next_loc in loc_info.graph[current_loc].keys():
                    # print(f"{current_loc=} {next_loc=}")
                    if next_loc not in self.occupied_locations:
                        cost = loc_info.move_cost(apod, current_loc, next_loc)
                        # print(f"{cost=}")
                        next_locs = tuple(
                            sorted(
                                [
                                    *current_apod_locs[:current_loc_idx],
                                    next_loc,
                                    *current_apod_locs[current_loc_idx + 1 :],
                                ]
                            )
                        )
                        next_state_dict: dict[Apod, Iterable[Location]] = {
                            **self.current_state_dict,
                            apod: next_locs,
                        }
                        # print(f"{next_state_dict}")
                        yield self.__class__(next_state_dict), cost


StateT = TypeVar("StateT", bound=State)


class Part1State(State):
    num_apods_per_type = 2
    # A0: Part1Location
    # A1: Part1Location
    # B0: Part1Location
    # B1: Part1Location
    # C0: Part1Location
    # C1: Part1Location
    # D0: Part1Location
    # D1: Part1Location


class Part2State(State):
    num_apods_per_type = 4
    # A0: Part2Location
    # A1: Part2Location
    # A2: Part2Location
    # A3: Part2Location
    # B0: Part2Location
    # B1: Part2Location
    # B2: Part2Location
    # B3: Part2Location
    # C0: Part2Location
    # C1: Part2Location
    # C2: Part2Location
    # C3: Part2Location
    # D0: Part2Location
    # D1: Part2Location
    # D2: Part2Location
    # D3: Part2Location


@dataclass(frozen=True, order=True)
class PrioritizableState:
    priority: float
    state: State = field(compare=False)

    def neighbors(self, loc_info: LocationInfo) -> Iterable[tuple[State, int]]:
        return self.state.neighbors(loc_info)


def heuristic(s: State, loc_info: LocationInfo) -> int:
    return sum(apod_heuristic(apod, s, loc_info) for apod in Apod)


def apod_heuristic(
    apod: Apod,
    s: State,
    loc_info: LocationInfo,
) -> int:
    """Cost to move the amphipods of type apod from their locations to the end,
    (mostly) ignoring all other amphipods"""
    locs = s.apod_locs(apod)
    all_occupied_locs = s.occupied_locations
    non_apod_locs = all_occupied_locs - set(locs)
    end_locs = loc_info.end_locs[apod]
    end_locs_s = set(end_locs)
    num_end_locs = len(end_locs)
    non_apod_in_end_locs = [end_loc in non_apod_locs for end_loc in end_locs]
    empty_end_locs = [end_loc not in all_occupied_locs for end_loc in end_locs]
    empty_or_non_apod_end_locs = [
        end_loc
        for end_loc, na, empty in zip(end_locs, non_apod_in_end_locs, empty_end_locs)
        if na or empty
    ]

    estimated_costs = [0] * len(locs)
    if locs == end_locs:
        # Fast path if everything is in the right place
        return 0
    for loc_idx, loc in enumerate(locs):
        if loc in end_locs_s:
            # This one is in an end loc of the right type
            end_loc_idx = end_locs.index(loc)

            # Are there any incorrect apods trapped below this one?
            if any(non_apod_in_end_locs[:end_loc_idx]):
                # Need to move this apod out of the way and back.
                # num_end_locs - loc_idx to move up + 2 for the move out to the hall
                unblock_move_cost = 2 + num_end_locs - loc_idx

                # We double it because we need to move out then back
                estimated_costs[loc_idx] = 2 * unblock_move_cost
            # Are there any empties below this?
            elif any(empty_end_locs[:end_loc_idx]):
                # Simply move down
                estimated_costs[loc_idx] = sum(empty_end_locs[:end_loc_idx])
            else:
                # No non-apods and no empties = everything below is correct
                # No move required
                estimated_costs[loc_idx] = 0
        else:
            # Ordinary move
            # We average the cost to move to any end loc
            estimated_costs[loc_idx] = sum(
                loc_info.move_cost(apod, locs[loc_idx], end_loc)
                for end_loc in empty_or_non_apod_end_locs
            ) // len(empty_or_non_apod_end_locs)

    return sum(estimated_costs)


def solve(start: State, end: State, loc_info: LocationInfo) -> tuple[int, list[State]]:
    frontier: PriorityQueue[PrioritizableState] = PriorityQueue()
    frontier.put(PrioritizableState(0, start))
    came_from: dict[State, State] = dict()
    cost_so_far: dict[State, int] = dict()
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current.state == end:
            break

        for next_state, next_state_move_cost in current.neighbors(loc_info):
            new_cost = cost_so_far[current.state] + next_state_move_cost
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                priority = new_cost + heuristic(next_state, loc_info)
                frontier.put(PrioritizableState(priority, next_state))
                came_from[next_state] = current.state

    # unwind path
    path = []
    current_state = end
    while current_state in came_from:
        path.append(current_state)
        current_state = came_from[current_state]
    path.append(start)

    return cost_so_far.get(end, -1), path[::-1]


def pretty_print(state: State, Loc: Type[Location]) -> str:
    loc_strs = {loc: "." for loc in Loc}
    for loc_name, locs in asdict(state).items():
        # locs = cast(tuple[Location, ...], locs)
        for loc in locs:
            loc_strs[loc] = loc_name
    template_top = """\
#############
#{}{}.{}.{}.{}.{}{}#
###{}#{}#{}#{}###"""
    template_bottom = "  #########"
    template_middle = ["  #{}#{}#{}#{}#"] * (1 if len(loc_strs) == 15 else 3)
    template = "\n".join([template_top, *template_middle, template_bottom])
    return template.format(*[loc_strs[loc] for loc in Loc])


def parse_lines(lines: Iterable[str], part: int) -> tuple[State, State, LocationInfo]:
    lines = [line for line in lines if line]
    tunnel_depth = 2 if part == 1 else 4

    # Define the enum of the locations
    Loc: Type[Location] = Part1Location if part == 1 else Part2Location

    # This is a static structure defining the labels for the starting (and ending) locs
    starting_locs = [
        [Loc[f"{apod.name}{idx}"] for apod in Apod] for idx in range(tunnel_depth)
    ]

    # parse the lines to pull out the order of the starting apods
    tunnel_start_line = 2
    tunnel_end = tunnel_start_line + tunnel_depth
    starting_apods = [lines[tunnel_start_line][3:-3].split("#")]
    for line in lines[tunnel_start_line + 1 : tunnel_end]:
        starting_apods.append(line.strip()[1:-1].split("#"))

    # Map starting apods to their location enum values
    apod_to_locs: Mapping[Apod, list[Location]] = defaultdict(list)
    for loc_line, starting_apod_line in zip(starting_locs, starting_apods):
        for loc, starting_apod in zip(loc_line, starting_apod_line):
            apod_to_locs[Apod[starting_apod]].append(loc)
    # Create the starting State
    state_cls = Part1State if part == 1 else Part2State
    start = state_cls(apod_to_locs)

    # ending state: all apods are in their destination locations
    end = state_cls(
        {
            apod: tuple(
                Loc[f"{apod.name}{idx}"] for idx in range(tunnel_depth)  # type:ignore
            )
            for apod in Apod
        }
    )

    # loc_info holds the graph and movement costs
    loc_info = LocationInfo(Loc, tunnel_depth)  # type:ignore

    return start, end, loc_info

    # loc_info holds the graph and movement costs
    loc_info = LocationInfo(Loc, tunnel_depth)  # type:ignore


def solution(lines: Iterable[str], part: int) -> int:
    start, end, loc_info = parse_lines(lines, part)
    cost, path = solve(start, end, loc_info)
    for state in path:
        print(pretty_print(state, loc_info.Loc))
    return cost


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, 1)


def part_two(lines: Iterable[str]) -> int:
    lines = [line for line in lines if line]
    lines = lines[:3] + ["  #D#C#B#A#", "  #D#B#A#C#"] + lines[3:]
    return solution(lines, 2)
