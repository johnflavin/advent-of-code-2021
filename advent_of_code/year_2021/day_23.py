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

import heapq
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from enum import Enum
from functools import cached_property, wraps

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


def cached_class(klass):
    """Decorator to cache class instances by constructor arguments.

    We "tuple-ize" the keyword arguments dictionary since
    dicts are mutable; keywords themselves are strings and
    so are always hashable, but if any arguments (keyword
    or positional) are non-hashable, that set of arguments
    is not cached.
    """
    cache = {}

    @wraps(klass, assigned=("__name__", "__module__"), updated=())
    class _decorated(klass):
        # The wraps decorator can't do this because __doc__
        # isn't writable once the class is created
        __doc__ = klass.__doc__

        def __new__(cls, *args, **kwds):
            key = (cls,) + args + tuple(kwds.items())
            try:
                inst = cache.get(key, None)
            except TypeError:
                # Can't cache this set of arguments
                inst = key = None
            if inst is None:
                # Technically this is cheating, but it works,
                # and takes care of initializing the instance
                # (so we can override __init__ below safely);
                # calling up to klass.__new__ would be the
                # "official" way to create the instance, but
                # that raises DeprecationWarning if there are
                # args or kwds and klass does not override
                # __new__ (which most classes don't), because
                # object.__new__ takes no parameters (and in
                # Python 3 the warning will become an error)
                inst = klass(*args, **kwds)
                # This makes isinstance and issubclass work
                # properly
                object.__setattr__(inst, "__class__", cls)
                if key is not None:
                    cache[key] = inst
            return inst

        def __init__(self, *args, **kwds):
            # This will be called every time __new__ is
            # called, so we skip initializing here and do
            # it only when the instance is created above
            pass

    return _decorated


@cached_class
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


@dataclass(frozen=True)
class ApodState:
    apod_enum: Apods
    location: Location
    done: bool = field(default=False)

    @property
    def apod(self) -> Apod:
        return self.apod_enum.value

    def move(self, new_location: Location) -> "ApodState":
        return ApodState(apod_enum=self.apod_enum, location=new_location)

    @cached_property
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
        # Distance from current x to destination x
        x_distance = abs(self.destination_x - self.location.x)

        # Distance from current y depth to hallway (depth 0)
        y_distance = self.location.y

        # If we're in our tunnel, distance is 0
        # Otherwise we need distance up to hallway, over to tunnel, then 1 to enter
        return 0 if x_distance == 0 else x_distance + y_distance + 1

    @cached_property
    def heuristic(self) -> int:
        return self.move_cost * self.heuristic_distance


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


def calculate_distances(
    graph: dict[Location, list[Location]]
) -> dict[Location, dict[Location, int]]:
    distances: dict[Location, dict[Location, int]] = defaultdict(dict)
    frontier: set[tuple[Location, Location]] = set()

    # prime with zeroth and first order
    for loc0, loc1s in graph.items():
        distances[loc0][loc0] = 0

        for loc1 in loc1s:
            distance = loc0.distance(loc1)
            distances[loc0][loc1] = distance
            frontier.add((loc0, loc1))

    # Add all other orders by traversing graph
    while frontier:
        loc0, loc1 = frontier.pop()

        for loc2 in graph[loc1]:
            new_distance = distances[loc0][loc1] + loc1.distance(loc2)
            if loc2 not in distances[loc0] or distances[loc0][loc2] > new_distance:
                frontier.add((loc0, loc2))
                distances[loc0][loc2] = new_distance

    # for locs, dist in distances.items():
    #     print(locs, dist)
    return distances


@dataclass
class GraphInfo:
    tunnel_depth: int
    graph: dict[Location, list[Location]] = field(init=False)
    distances: dict[Location, dict[Location, int]] = field(init=False)
    all_locs: list[Location] = field(init=False)

    def __post_init__(self):
        self.graph = build_location_graph(self.tunnel_depth)
        self.distances = calculate_distances(self.graph)
        self.all_locs = sorted(self.graph.keys())


@dataclass(frozen=True)
class BoardState:
    apod_states: frozenset[ApodState]

    @cached_property
    def apod_by_location(self) -> dict[Location, ApodState]:
        return {apod_state.location: apod_state for apod_state in self.apod_states}

    @cached_property
    def occupied_locations(self) -> set[Location]:
        return set(self.apod_by_location.keys())

    def is_occupied(self, location: Location) -> bool:
        return location in self.occupied_locations

    @cached_property
    def heuristic(self) -> int:
        return sum(apod_state.heuristic for apod_state in self.apod_states)

    @property
    def tunnel_depth(self) -> int:
        return len(self.apod_states) // len(Apods)

    # def move(self, apod_state: ApodState, new_loc: Location) -> "BoardState":
    #     return BoardState(
    #         frozenset(
    #             other if other != apod_state else apod_state.move(new_loc)
    #             for other in self.apod_states
    #         )
    #     )

    def is_destination_valid(self, apod_state: ApodState, loc: Location) -> bool:
        """Can we move into this space?"""

        return not (
            self.is_occupied(loc)
            or (loc.y > apod_state.location.y and loc.x != apod_state.destination_x)
        )

    def generate_next_states(
        self, apod_state: ApodState, graph: GraphInfo
    ) -> Iterable[tuple[ApodState, int]]:
        frontier = set(graph.graph[apod_state.location])
        have_seen = {apod_state.location}
        potential_destinations: set[Location] = set()
        while frontier:
            loc = frontier.pop()
            have_seen.add(loc)
            if not self.is_destination_valid(apod_state, loc):
                continue
            potential_destinations.add(loc)
            frontier.update(
                next_loc for next_loc in graph.graph[loc] if next_loc not in have_seen
            )

        if not potential_destinations:
            return ()

        # "potential_destinations" is everywhere we could possibly move.
        # Let's filter it down to a few options.
        # If we're in any tunnel we must move to the hallway.
        # If we're in the hallway we must move into our tunnel.
        # And we can only move into our tunnel if there are no other apod types in it.
        if apod_state.in_hallway:
            # Check if it is possible to move into our tunnel.
            tunnel_destinations = {
                loc
                for loc in potential_destinations
                if loc.x == apod_state.destination_x
            }
            if not tunnel_destinations:
                return ()

            # We know we could move into our tunnel. But should we?
            for depth in range(self.tunnel_depth, 0, -1):
                tunnel_loc = Location(y=depth, x=apod_state.destination_x)
                apod_at_tunnel_loc = self.apod_by_location.get(tunnel_loc)
                if apod_at_tunnel_loc is None and tunnel_loc in tunnel_destinations:
                    # We haven't found any different apods yet,
                    # and we just found an empty spot that we can reach.
                    # This is the only place we should go, and then we should stop.

                    next_state = ApodState(
                        apod_enum=apod_state.apod_enum, location=tunnel_loc, done=True
                    )
                    yield next_state, apod_state.move_cost * graph.distances[
                        apod_state.location
                    ][tunnel_loc]
                elif (
                    apod_at_tunnel_loc is not None
                    and apod_at_tunnel_loc.apod != apod_state.apod
                ):
                    # We found an apod that isn't the correct type. Can't move here,
                    # can't move anywhere
                    return ()
        else:
            # Must move into the hallway
            for loc in potential_destinations:
                if loc.in_hallway:
                    yield apod_state.move(loc), apod_state.move_cost * graph.distances[
                        apod_state.location
                    ][loc]

    def neighbors(self, graph: GraphInfo) -> Iterable[tuple["BoardState", int]]:
        """Generate legal successor states and their costs"""

        # loop through legal successor states
        # for apod_state in self.non_terminal_apod_states:
        for apod_state in self.apod_states:
            if apod_state.done:
                continue
            # print(apod_state)
            # for next_loc in generate_valid_moves(apod_state):
            # for next_loc in graph.graph[apod_state.location]:
            for next_state, cost in self.generate_next_states(apod_state, graph):
                # print(apod_state, next_loc)
                yield BoardState(
                    frozenset(
                        other if other != apod_state else next_state
                        for other in self.apod_states
                    )
                ), cost


def end_state(tunnel_depth: int) -> BoardState:
    return BoardState(
        frozenset(
            ApodState(
                location=Location(x=apod.value.destination_x, y=depth),
                apod_enum=apod,
                done=True,
            )
            for apod in Apods
            for depth in range(1, tunnel_depth + 1)
        )
    )


@dataclass(frozen=True, order=True)
class BoardStateWithPriority:
    state: BoardState = field(compare=False)
    cost: int = field(compare=False)
    priority: int = field(init=False)

    def __post_init__(self):
        priority = self.cost + self.state.heuristic
        object.__setattr__(self, "priority", priority)


@dataclass(frozen=True)
class CameFrom:
    state: BoardState
    cost: int


def solve(
    start: BoardState, end: BoardState, graph: GraphInfo
) -> tuple[int, list[BoardState]]:
    frontier: list[BoardStateWithPriority] = []
    heapq.heappush(frontier, BoardStateWithPriority(start, 0))
    history: dict[BoardState, CameFrom] = {start: CameFrom(None, 0)}  # type: ignore

    while len(frontier) > 0:
        current_prioritizable_state = heapq.heappop(frontier)
        current_state = current_prioritizable_state.state

        if current_state == end:
            # print("at end")
            break

        came_from = history[current_state]

        for next_state, relative_move_cost in current_state.neighbors(graph):
            absolute_move_cost = came_from.cost + relative_move_cost
            if (
                next_state not in history
                or absolute_move_cost < history[next_state].cost
            ):
                history[next_state] = CameFrom(current_state, absolute_move_cost)
                heapq.heappush(
                    frontier, BoardStateWithPriority(next_state, absolute_move_cost)
                )

        # debug_num_steps += 1

    # unwind path
    path = []
    current_state = end
    while current_state in history:
        path.append(current_state)
        current_state = history[current_state].state
    # path.append(start)

    end_history = history.get(end)
    end_cost = end_history.cost if end_history else -1
    return end_cost, path[::-1]


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

    # Check if any apods are already in the correct space
    # We iterate through each tunnel, bottom up
    rows = list(zip(*[zip(range(len(apod_states)), apod_states)] * 4))
    for apod_enum, tunnel_apods in zip(Apods, zip(*reversed(rows))):
        apod = apod_enum.value
        for tunnel_apod_idx, tunnel_apod in tunnel_apods:
            if tunnel_apod.apod == apod:
                apod_states[tunnel_apod_idx] = replace(tunnel_apod, done=True)
            else:
                break

    # print(apod_states)
    start = BoardState(frozenset(apod_states))
    # print(start)
    graph_info = GraphInfo(tunnel_depth)

    return start, end_state(tunnel_depth), graph_info


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


def pretty_print(state: BoardState, graph: GraphInfo) -> str:

    sorted_apods = sorted(state.apod_states, key=lambda s: s.location)
    # print(sorted_apods)
    next_apod = sorted_apods.pop(0)
    loc_strs = ["."] * len(graph.all_locs)
    for idx, loc in enumerate(graph.all_locs):
        if loc == next_apod.location:
            loc_strs[idx] = next_apod.apod.name
            try:
                next_apod = sorted_apods.pop(0)
            except IndexError:
                break
        # print(loc, loc_strs[-1])

    template = pretty_print_template(state.tunnel_depth)
    return template.format(*loc_strs)


def solution(lines: Iterable[str], tunnel_depth: int) -> int:
    start, end, graph = parse_lines(lines, tunnel_depth)

    cost, path = solve(start, end, graph)
    for state in path:
        print(pretty_print(state, graph))
    return cost


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, 2)


def part_two(lines: Iterable[str]) -> int:
    lines = [line for line in lines if line]
    lines = lines[:3] + ["  #D#C#B#A#", "  #D#B#A#C#"] + lines[3:]
    return solution(lines, 4)
