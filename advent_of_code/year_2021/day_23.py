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
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from queue import PriorityQueue

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


@dataclass(frozen=True, order=True)
class Apod:
    name: str
    move_cost: int
    destination_x: int


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Apods(OrderedEnum):
    A = Apod("A", 1, 2)
    B = Apod("B", 10, 4)
    C = Apod("C", 100, 6)
    D = Apod("D", 1000, 8)


@dataclass(frozen=True, order=True)
class Location:
    y: int
    x: int

    def __post_init__(self):
        if self.y == 0:
            assert self.x in {0, 1, 3, 5, 7, 9, 10}
        else:
            assert self.x in {2, 4, 6, 8}

    @property
    def in_hallway(self):
        return self.y == 0

    def distance(self, other: "Location") -> int:
        if self.y == 0 or other.y == 0 or self.x == other.x:
            # Move in x then down tunnel
            return abs(self.x - other.x) + abs(self.y - other.y)
        else:
            # Have to move up to hallway then down again
            return self.y + abs(self.x - other.x) + other.y


@dataclass(frozen=True, order=True)
class ApodState:
    apod_enum: Apods
    location: Location

    @property
    def apod(self) -> Apod:
        return self.apod_enum.value

    def move(self, new_location: Location) -> "ApodState":
        return ApodState(apod_enum=self.apod_enum, location=new_location)

    @property
    def at_destination(self) -> bool:
        return (
            not self.location.in_hallway and self.location.x == self.apod.destination_x
        )

    @property
    def destination_x(self) -> int:
        return self.apod.destination_x

    @property
    def move_cost(self) -> int:
        return self.apod.move_cost

    @property
    def in_hallway(self) -> bool:
        return self.location.in_hallway

    @property
    def heuristic_distance(self) -> int:
        x_distance = abs(self.destination_x - self.location.x)
        y_distance = self.location.y
        return x_distance + ((y_distance + 1) if x_distance == 0 else 0)

    @property
    def heuristic(self) -> int:
        return self.heuristic_distance * self.move_cost

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.apod.name}, {self.location})"

    def __repr__(self) -> str:
        return self.__str__()


@cache
def build_location_graph(
    tunnel_depth: int,
) -> dict[Location, list[Location]]:
    graph = {
        # Hallway left left
        Location(x=0, y=0): [
            Location(x=1, y=0),
        ],
        # Hallway left right
        Location(x=1, y=0): [
            Location(x=0, y=0),
            Location(x=2, y=1),
            Location(x=3, y=0),
        ],
        # Hallway AB
        Location(y=0, x=3): [
            Location(y=0, x=1),
            Location(y=1, x=2),
            Location(y=1, x=4),
            Location(y=0, x=5),
        ],
        # Hallway BC
        Location(y=0, x=5): [
            Location(y=0, x=3),
            Location(y=1, x=4),
            Location(y=1, x=6),
            Location(y=0, x=7),
        ],
        # Hallway CD
        Location(y=0, x=7): [
            Location(y=0, x=5),
            Location(y=1, x=6),
            Location(y=1, x=8),
            Location(y=0, x=9),
        ],
        # Hallway right left
        Location(y=0, x=9): [
            Location(y=0, x=7),
            Location(y=1, x=8),
            Location(y=0, x=10),
        ],
        # Hallway right right
        Location(y=0, x=10): [
            Location(y=0, x=9),
        ],
    }

    # Add tunnels
    for apod in Apods:
        tunnel_x = apod.value.destination_x
        # tunnel top
        graph[Location(y=1, x=tunnel_x)] = [
            Location(x=tunnel_x - 1, y=0),
            Location(x=tunnel_x + 1, y=0),
            Location(x=tunnel_x, y=2),
        ]

        # tunnel middle
        for depth in range(2, tunnel_depth):
            graph[Location(x=tunnel_x, y=depth)] = [
                Location(x=tunnel_x, y=depth + 1),
                Location(x=tunnel_x, y=depth - 1),
            ]

        # tunnel bottom
        graph[Location(x=tunnel_x, y=tunnel_depth)] = [
            Location(x=tunnel_x, y=tunnel_depth - 1)
        ]
    # print(graph)
    return graph


def calculate_distances(tunnel_depth: int) -> dict[tuple[Location, Location], int]:
    graph = build_location_graph(tunnel_depth)
    distances: dict[tuple[Location, Location], int] = {}
    frontier: set[tuple[Location, Location, int]] = set()

    # prime with zeroth and first order
    for loc0, loc1s in graph.items():
        distances[(loc0, loc0)] = 0

        for loc1 in loc1s:
            distance = loc0.distance(loc1)
            distances[(loc0, loc1)] = distance
            frontier.add((loc0, loc1, distance))

    # Add all other orders by traversing graph
    while frontier:
        loc0, loc1, dist01 = frontier.pop()

        for loc2 in graph[loc1]:
            new_pair = (loc0, loc2)
            new_distance = dist01 + loc1.distance(loc2)
            if new_pair not in distances:
                frontier.add((loc0, loc2, new_distance))
                distances[new_pair] = new_distance
            elif distances[new_pair] > new_distance:
                frontier.discard((loc0, loc2, distances[new_pair]))
                frontier.add((loc0, loc2, new_distance))
                distances[new_pair] = new_distance

    # for locs, dist in distances.items():
    #     print(locs, dist)
    return distances


@cache
def all_locations(tunnel_depth: int) -> list[Location]:
    return sorted(build_location_graph(tunnel_depth).keys())


@dataclass
class GraphInfo:
    tunnel_depth: int
    graph: dict[Location, list[Location]] = field(init=False)
    distance: dict[tuple[Location, Location], int] = field(init=False)

    def __post_init__(self):
        self.graph = build_location_graph(self.tunnel_depth)
        self.distance = calculate_distances(self.tunnel_depth)

    def direct_move_cost(self, apod_state: ApodState, destination: Location) -> int:
        return (
            self.distance[(apod_state.location, destination)]
            * apod_state.apod.move_cost
        )


def pretty_print_template(tunnel_depth: int) -> str:
    top = "#############"
    hallway_template = "#{}{}.{}.{}.{}.{}{}#"
    tunnel_top_template = "###{}#{}#{}#{}###"
    tunnel_depths_templates = ["  #{}#{}#{}#{}#"] * (tunnel_depth - 1)
    bottom = "  #########"
    return "\n".join(
        [
            top,
            hallway_template,
            tunnel_top_template,
            *tunnel_depths_templates,
            bottom,
        ]
    )


@dataclass(frozen=True, order=True)
class BoardState:
    apod_states: frozenset[ApodState]

    def is_occupied(self, location: Location) -> bool:
        return location in self.apods_by_location.keys()

    @property
    def heuristic(self) -> int:
        return sum(apod_state.heuristic for apod_state in self.apod_states)

    @property
    def tunnel_depth(self) -> int:
        return len(self.apod_states) // len(Apods)

    @property
    @cache
    def apods_by_location(self) -> dict[Location, Apod]:
        return {apod_state.location: apod_state.apod for apod_state in self.apod_states}

    @cache
    def apod_at_location(self, location: Location) -> "Apod | None":
        return self.apods_by_location.get(location)

    @property
    @cache
    def non_terminal_apod_states(self) -> set[ApodState]:
        return {apod_state for apod_state in self.apod_states if True}

    def pretty_print(self) -> str:

        sorted_apods = sorted(self.apod_states, key=lambda s: s.location)
        # print(sorted_apods)
        all_locs = all_locations(self.tunnel_depth)
        next_apod = sorted_apods.pop(0)
        loc_strs = ["."] * len(all_locs)
        for idx, loc in enumerate(all_locs):
            if loc == next_apod.location:
                loc_strs[idx] = next_apod.apod.name
                try:
                    next_apod = sorted_apods.pop(0)
                except IndexError:
                    break
            # print(loc, loc_strs[-1])

        template = pretty_print_template(self.tunnel_depth)
        return template.format(*loc_strs)

    def neighbors(self, graph: GraphInfo) -> Iterable[tuple["BoardState", int]]:
        """Generate legal successor states and their costs"""

        def generate_moves(pod: ApodState) -> Iterable[Location]:
            # Do a mini graph traversal with just this one apod
            frontier: set[Location] = set(graph.graph[pod.location])
            have_seen: set[Location] = {pod.location}
            valid_destinations: set[Location] = set()
            while frontier:
                loc = frontier.pop()

                # can't move into occupied spaces
                if self.is_occupied(loc):
                    continue

                # Can we move to this space? Through it?
                if loc.y == 0:
                    # We can always move in the hallway
                    valid_destinations.add(loc)

                    # Mark that we've seen this one
                    have_seen.add(loc)

                    # Add its next steps to the frontier.
                    for next_loc in graph.graph[loc]:
                        if next_loc not in have_seen:
                            frontier.add(next_loc)

                elif loc.x != pod.destination_x:  # Not our tunnel
                    # Are we already in the tunnel? And is this move up?
                    if loc.x != pod.location.x or loc.y > pod.location.y:
                        # This is either entering the wrong tunnel or moving down
                        # when we should be moving up. Invalid.
                        continue

                    # We have no reason to end a turn here, so it isn't a
                    # valid destination. But we might have reason to move through here.
                    # We will continue on and check other positions from here.
                    have_seen.add(loc)

                    # Add its next steps to the frontier.
                    for next_loc in graph.graph[loc]:
                        if next_loc not in have_seen:
                            frontier.add(next_loc)
                else:  # Yes our tunnel
                    # We can move in our tunnel if it isn't occupied by any
                    # incorrect apods.
                    # And if so, we will move to the lowest unoccupied space.
                    lowest_unoccupied: "Location | None" = None
                    for depth in range(self.tunnel_depth, 0, -1):
                        tunnel_loc = Location(y=depth, x=loc.x)
                        apod_in_tunnel_loc = self.apod_at_location(tunnel_loc)
                        if apod_in_tunnel_loc is None:
                            # unoccupied
                            if lowest_unoccupied is None:
                                lowest_unoccupied = tunnel_loc
                        elif apod_in_tunnel_loc != pod.apod:
                            # occupied, incorrect apod
                            break
                        else:
                            # occupied, correct apod
                            pass
                    else:
                        # We didn't find any incorrect apods
                        # That means we can move somewhere in the tunnel
                        assert lowest_unoccupied is not None
                        valid_destinations.add(lowest_unoccupied)

                        # Mark that we've seen this one
                        have_seen.add(loc)

                        # Add its next steps to the frontier, but only if they aren't
                        # also in this tunnel (because we know we would just
                        # do the same thing with them and find the same lowest position)
                        for next_loc in graph.graph[loc]:
                            if (
                                next_loc not in have_seen
                                and next_loc.x != pod.destination_x
                            ):
                                frontier.add(next_loc)

            return valid_destinations

        # loop through legal successor states
        for apod_state in self.non_terminal_apod_states:
            other_states = {other for other in self.apod_states if other != apod_state}
            for next_loc in generate_moves(apod_state):
                # print(next_loc)
                cost = graph.direct_move_cost(apod_state, next_loc)
                new_states = frozenset({apod_state.move(next_loc), *other_states})
                yield self.__class__(new_states), cost


def end_state(tunnel_depth: int) -> BoardState:
    return BoardState(
        frozenset(
            ApodState(
                location=Location(x=apod.value.destination_x, y=depth), apod_enum=apod
            )
            for apod in Apods
            for depth in range(1, tunnel_depth + 1)
        )
    )


@dataclass(frozen=True, order=True)
class PrioritizableState:
    priority: float
    state: BoardState = field(compare=False)

    def neighbors(self, graph: GraphInfo) -> Iterable[tuple[BoardState, int]]:
        return self.state.neighbors(graph)


def solve(
    start: BoardState, end: BoardState, graph: GraphInfo
) -> tuple[int, list[BoardState]]:
    frontier: PriorityQueue[PrioritizableState] = PriorityQueue()
    frontier.put(PrioritizableState(0, start))
    came_from: dict[BoardState, BoardState] = dict()
    cost_so_far: dict[BoardState, int] = dict()
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current.state == end:
            # print("at end")
            break

        for next_state, next_state_move_cost in current.neighbors(graph):
            new_cost = cost_so_far[current.state] + next_state_move_cost
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                came_from[next_state] = current.state
                priority = new_cost + next_state.heuristic
                frontier.put(PrioritizableState(priority, next_state))

        # debug_num_steps += 1

    # unwind path
    path = []
    current_state = end
    while current_state in came_from:
        path.append(current_state)
        current_state = came_from[current_state]
    path.append(start)

    return cost_so_far.get(end, -1), path[::-1]


def parse_lines(
    lines: Iterable[str], tunnel_depth: int
) -> tuple[BoardState, BoardState, GraphInfo]:
    lines = [line.strip() for line in lines if line]

    apod_chars = set("ABCD")
    apod_states: list[ApodState] = []
    for depth, line in enumerate(lines[2:], start=1):
        if line.startswith("###"):
            line = line[2:-2]
        for x, c in enumerate(line, start=1):
            if c in apod_chars:
                try:
                    loc = Location(x=x, y=depth)
                except AssertionError:
                    print(f"{line=} {depth=} {x=} {c=}")
                    raise
                apod_states.append(ApodState(location=loc, apod_enum=Apods[c]))

    # print(apod_states)
    start = BoardState(frozenset(apod_states))
    # print(start)
    graph_info = GraphInfo(tunnel_depth)

    return start, end_state(tunnel_depth), graph_info


def solution(lines: Iterable[str], tunnel_depth: int) -> int:
    start, end, graph = parse_lines(lines, tunnel_depth)

    cost, path = solve(start, end, graph)
    for state in path:
        print(state.pretty_print())
    return cost


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, 2)


def part_two(lines: Iterable[str]) -> int:
    lines = [line for line in lines if line]
    lines = lines[:3] + ["  #D#C#B#A#", "  #D#B#A#C#"] + lines[3:]
    return solution(lines, 4)
